"""ChromaDB vector store implementation with in-memory fallback.

This module attempts to use ChromaDB. If ChromaDB fails to import or
initialize (common on newer Python versions due to pydantic incompatibilities),
it falls back to a lightweight in-memory vector store with the same interface
used by the pipeline. The in-memory store supports `create_collection`,
`add_documents`, `query`, and `get_collection_info`.
"""
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    _HAS_CHROMADB = True
except Exception as e:
    chromadb = None  # type: ignore
    _HAS_CHROMADB = False
    logger.warning(f"ChromaDB not available, using in-memory vector store fallback: {e}")


class ChromaVectorStore:
    """Wrapper exposing a vector store interface; uses ChromaDB when available
    or an in-memory store otherwise.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        if _HAS_CHROMADB:
            try:
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = None
                logger.info(f"Initialized ChromaDB at {persist_directory}")
                self._mode = "chroma"
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed, falling back to in-memory: {e}")
                self._init_inmemory()
        else:
            self._init_inmemory()

    def _init_inmemory(self):
        self._mode = "inmemory"
        # collections: name -> dict with lists ids, documents, embeddings, metadatas
        self._collections: Dict[str, Dict] = {}
        logger.info("Initialized in-memory vector store")

    def create_collection(self, name: str):
        if self._mode == "chroma":
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created/retrieved Chroma collection: {name}")
        else:
            if name not in self._collections:
                self._collections[name] = {
                    "ids": [],
                    "documents": [],
                    "embeddings": [],
                    "metadatas": []
                }
            logger.info(f"Created/retrieved in-memory collection: {name}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict]
    ):
        if self._mode == "chroma":
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} documents to Chroma collection")
        else:
            # assume a single default collection
            # create it if missing
            name = list(self._collections.keys())[0] if self._collections else "research_papers"
            if name not in self._collections:
                self.create_collection(name)
            col = self._collections[name]
            col["ids"].extend(ids)
            col["documents"].extend(documents)
            col["embeddings"].extend(embeddings)
            col["metadatas"].extend(metadatas)
            logger.info(f"Added {len(ids)} documents to in-memory collection '{name}'")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        if self._mode == "chroma":
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

        # In-memory query: cosine similarity over stored embeddings
        name = list(self._collections.keys())[0] if self._collections else None
        if name is None:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        col = self._collections[name]

        # optional metadata filter
        indices = list(range(len(col["embeddings"])))
        if where:
            def match(md: Dict) -> bool:
                for k, v in where.items():
                    if md.get(k) != v:
                        return False
                return True
            indices = [i for i in indices if match(col["metadatas"][i])]

        import numpy as _np

        q = _np.array(query_embedding, dtype=float)
        docs = []
        metas = []
        dists = []

        sims = []
        for i in indices:
            emb = _np.array(col["embeddings"][i], dtype=float)
            # cosine similarity
            denom = (_np.linalg.norm(q) * _np.linalg.norm(emb))
            sim = float(_np.dot(q, emb) / denom) if denom != 0 else 0.0
            sims.append((i, sim))

        sims.sort(key=lambda x: x[1], reverse=True)
        top = sims[:n_results]

        for i, sim in top:
            docs.append(col["documents"][i])
            metas.append(col["metadatas"][i])
            # distances expected as 1 - similarity to be consistent with other stores
            dists.append(1.0 - sim)

        return {"documents": [docs], "metadatas": [metas], "distances": [dists]}

    def get_collection_info(self) -> Dict:
        if self._mode == "chroma":
            return self.client.get_collection_info() if hasattr(self.client, 'get_collection_info') else {}
        info = {name: {"n_items": len(col["ids"])} for name, col in self._collections.items()}
        return info
