"""
Pathway Hybrid RAG Implementation
Combines structured data processing with document retrieval
"""
import pathway as pw
import os
from typing import List, Dict, Any, Optional


class HybridRAGIndexer:
    """
    Hybrid indexing system that combines:
    1. Structured financial data (ADE extraction)
    2. Full document text chunks (for RAG retrieval)
    """
    
    def __init__(self, index_dir: str = "./pathway_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.embedder = None
        self.llm = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedder and LLM for RAG"""
        try:
            # Use OpenAI-compatible embeddings (can switch to local models)
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                # For now, use a simple sentence-based approach
                # In production, use pathway.xpacks.llm.embedders
                self.embedder = "simple"  # Placeholder
                self.llm = "gemini"
            else:
                print("⚠️ No GEMINI_API_KEY found, RAG will be limited")
        except Exception as e:
            print(f"⚠️ Failed to initialize RAG models: {e}")
    
    def index_document(self, task_id: str, doc_id: str, markdown: str, 
                      extraction_json: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """
        Index a document with both structured and unstructured data
        
        Args:
            task_id: Task identifier
            doc_id: Document identifier
            markdown: Full markdown text from ADE
            extraction_json: Structured financial fields
            metadata: Additional metadata (filename, etc.)
        
        Returns:
            Success status
        """
        try:
            # Split markdown into chunks for RAG
            chunks = self._chunk_text(markdown)
            
            # Create index entries
            index_entries = []
            for i, chunk in enumerate(chunks):
                entry = {
                    "task_id": task_id,
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "text": chunk,
                    "type": "text_chunk",
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }
                index_entries.append(entry)
            
            # Add structured data as a special entry
            structured_entry = {
                "task_id": task_id,
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_structured",
                "text": self._format_structured_data(extraction_json),
                "type": "structured_data",
                "metadata": {
                    **metadata,
                    "extraction": extraction_json
                }
            }
            index_entries.append(structured_entry)
            
            # Save to pathway-compatible format
            self._save_to_index(task_id, index_entries)
            
            print(f"✅ Indexed document {doc_id} with {len(chunks)} chunks + structured data")
            return True
            
        except Exception as e:
            print(f"❌ Failed to index document {doc_id}: {e}")
            return False
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
        
        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, newline, or other sentence boundary
                boundary = text.rfind('.', start, end)
                if boundary == -1:
                    boundary = text.rfind('\n', start, end)
                if boundary != -1 and boundary > start:
                    end = boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def _format_structured_data(self, extraction: Dict[str, Any]) -> str:
        """Format structured financial data as searchable text"""
        parts = []
        for key, value in extraction.items():
            if value:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)
    
    def _save_to_index(self, task_id: str, entries: List[Dict[str, Any]]):
        """Save index entries to JSON file for Pathway"""
        import json
        index_file = os.path.join(self.index_dir, f"{task_id}_index.json")
        
        # Load existing or create new
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                existing = json.load(f)
        else:
            existing = []
        
        # Append new entries
        existing.extend(entries)
        
        # Save
        with open(index_file, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def search(self, task_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the index for relevant chunks
        
        Args:
            task_id: Task to search within
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant chunks with scores
        """
        try:
            import json
            index_file = os.path.join(self.index_dir, f"{task_id}_index.json")
            
            if not os.path.exists(index_file):
                print(f"⚠️ No index found for task {task_id}")
                return []
            
            # Load index
            with open(index_file, 'r') as f:
                entries = json.load(f)
            
            # Simple keyword-based search (can be enhanced with embeddings)
            query_lower = query.lower()
            results = []
            
            for entry in entries:
                text = entry.get("text", "").lower()
                
                # Simple scoring based on keyword matches
                score = 0
                for word in query_lower.split():
                    if len(word) > 3:  # Skip short words
                        score += text.count(word)
                
                if score > 0:
                    results.append({
                        **entry,
                        "score": score
                    })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def get_context_for_query(self, task_id: str, query: str, 
                             include_structured: bool = True) -> Dict[str, Any]:
        """
        Get relevant context for a query combining RAG results and structured data
        
        Args:
            task_id: Task identifier
            query: User query
            include_structured: Include structured financial data
        
        Returns:
            Dictionary with context, sources, and structured data
        """
        results = self.search(task_id, query, top_k=5)
        
        context_chunks = []
        sources = []
        structured_data = {}
        
        for result in results:
            if result["type"] == "text_chunk":
                context_chunks.append(result["text"])
                sources.append({
                    "doc_id": result["doc_id"],
                    "filename": result["metadata"].get("filename", "Unknown"),
                    "chunk_index": result["metadata"].get("chunk_index", 0)
                })
            elif result["type"] == "structured_data" and include_structured:
                structured_data = result["metadata"].get("extraction", {})
        
        return {
            "context": "\n\n---\n\n".join(context_chunks),
            "sources": sources,
            "structured_data": structured_data,
            "num_results": len(results)
        }


# Global indexer instance
_indexer: Optional[HybridRAGIndexer] = None

def get_indexer() -> HybridRAGIndexer:
    """Get or create global indexer instance"""
    global _indexer
    if _indexer is None:
        _indexer = HybridRAGIndexer()
    return _indexer


def index_document(task_id: str, doc_id: str, markdown: str, 
                  extraction_json: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
    """Convenience function to index a document"""
    indexer = get_indexer()
    return indexer.index_document(task_id, doc_id, markdown, extraction_json, metadata)


def search_documents(task_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to search documents"""
    indexer = get_indexer()
    return indexer.search(task_id, query, top_k)


def get_rag_context(task_id: str, query: str) -> Dict[str, Any]:
    """Convenience function to get RAG context for a query"""
    indexer = get_indexer()
    return indexer.get_context_for_query(task_id, query)
