"""Response generation using GPT-4 API."""
from openai import OpenAI
from typing import List, Dict, Tuple
from loguru import logger


class ResponseGenerator:
    """Generate responses using GPT-4 with RAG context."""
    
    def __init__(self, model: str = "gpt-4-turbo"):
        """
        Initialize response generator.
        
        Args:
            model: OpenAI model to use
        """
        self.client = OpenAI()
        self.model = model
        logger.info(f"Initialized ResponseGenerator with model: {model}")

    def generate(
        self,
        query: str,
        retrieved_docs: List[Dict],
        prompt_template: str,
        strategy: str = "standard"
    ) -> Tuple[str, List[Dict]]:
        """
        Generate a response based on retrieved documents.
        
        Args:
            query: User query
            retrieved_docs: Retrieved relevant documents
            prompt_template: Prompt template to use
            strategy: Prompt strategy (standard, json, few-shot, cot)
            
        Returns:
            Tuple of (response, citations)
        """
        # Prepare context from retrieved documents
        context = self._format_context(retrieved_docs)
        
        # Format prompt
        prompt = prompt_template.format(context=context, question=query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Research Copilot, an expert academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract citations from metadata
            citations = self._extract_citations(retrieved_docs)
            
            logger.info(f"Generated response using {strategy} strategy")
            return answer, citations
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _format_context(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved documents into context string."""
        context_parts = []
        for doc in retrieved_docs:
            metadata = doc.get("metadata", {})
            source = f"{metadata.get('paper_title', 'Unknown')} ({metadata.get('year', 'N/A')})"
            context_parts.append(f"Source: {source}\n{doc['text']}")
        
        return "\n\n".join(context_parts)

    def _extract_citations(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Extract citation information from retrieved documents."""
        citations = []
        seen = set()
        
        for doc in retrieved_docs:
            metadata = doc.get("metadata", {})
            paper_id = metadata.get("paper_id", "unknown")
            
            if paper_id not in seen:
                citations.append({
                    "paper": metadata.get("paper_title", "Unknown"),
                    "authors": metadata.get("authors", "Unknown"),
                    "year": metadata.get("year", "N/A"),
                    "doi": metadata.get("doi", "N/A"),
                    "page": metadata.get("page_number", "N/A")
                })
                seen.add(paper_id)
        
        return citations
