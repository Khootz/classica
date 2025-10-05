"""
Pathway Hybrid RAG Implementation
Combines structured data processing with document retrieval
Now with semantic search using sentence transformers
"""
import pathway as pw
import os
import numpy as np
from typing import List, Dict, Any, Optional

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Using keyword search only.")
    print("   Install with: pip install sentence-transformers")


class HybridRAGIndexer:
    """
    Hybrid indexing system that combines:
    1. Structured financial data (ADE extraction)
    2. Full document text chunks (for RAG retrieval)
    3. Semantic embeddings for better search (if available)
    """
    
    def __init__(self, index_dir: str = "./pathway_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.embedder = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding model for semantic search"""
        if EMBEDDINGS_AVAILABLE:
            try:
                # Use lightweight but effective model
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Initialized semantic search with all-MiniLM-L6-v2")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                self.embedder = None
        else:
            self.embedder = None
    
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
            
            # Create index entries with embeddings
            index_entries = []
            for i, chunk in enumerate(chunks):
                entry = {
                    "task_id": task_id,
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "text": chunk,
                    "type": "text_chunk",
                    "embedding": self._generate_embedding(chunk),  # Add embedding
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }
                index_entries.append(entry)
            
            # Add structured data as a special entry
            structured_text = self._format_structured_data(extraction_json)
            structured_entry = {
                "task_id": task_id,
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_structured",
                "text": structured_text,
                "type": "structured_data",
                "embedding": self._generate_embedding(structured_text),  # Add embedding
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
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        if self.embedder and text:
            try:
                embedding = self.embedder.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                print(f"⚠️ Embedding generation failed: {e}")
                return None
        return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
        except:
            return 0.0
    
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
    
    def search(self, task_id: str, query: str, top_k: int = 5, use_semantic: bool = True) -> List[Dict[str, Any]]:
        """
        Search the index for relevant chunks using hybrid search (semantic + keyword)
        
        Args:
            task_id: Task to search within
            query: Search query
            top_k: Number of results to return
            use_semantic: Use semantic search if embeddings available
        
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
            
            # Generate query embedding for semantic search
            query_embedding = None
            if use_semantic and self.embedder:
                query_embedding = self._generate_embedding(query)
            
            results = []
            query_lower = query.lower()
            
            for entry in entries:
                text = entry.get("text", "").lower()
                
                # Keyword-based scoring
                keyword_score = 0
                for word in query_lower.split():
                    if len(word) > 3:  # Skip short words
                        keyword_score += text.count(word)
                
                # Semantic scoring (if available)
                semantic_score = 0.0
                if query_embedding and entry.get("embedding"):
                    semantic_score = self._cosine_similarity(query_embedding, entry["embedding"])
                
                # Hybrid score: combine semantic (70%) + keyword (30%)
                if query_embedding and entry.get("embedding"):
                    # Normalize keyword score to 0-1 range (assuming max 20 occurrences)
                    normalized_keyword = min(keyword_score / 20.0, 1.0)
                    final_score = (semantic_score * 0.7) + (normalized_keyword * 0.3)
                    score_type = "hybrid"
                else:
                    # Fall back to keyword only
                    final_score = keyword_score
                    score_type = "keyword"
                
                if final_score > 0:
                    results.append({
                        **entry,
                        "score": final_score,
                        "score_type": score_type,
                        "keyword_score": keyword_score,
                        "semantic_score": semantic_score
                    })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            
            if results:
                print(f"🔍 Search mode: {results[0].get('score_type', 'unknown')}")
            
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
