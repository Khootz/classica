"""
Hybrid RAG System with Semantic Search
Combines sentence-transformers embeddings with keyword matching for optimal retrieval
"""

import os
import json
from typing import List, Dict, Any

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ sentence-transformers not available. Install with: pip install sentence-transformers")


class PathwayRAG:
    """Hybrid RAG system with semantic + keyword search"""
    
    def __init__(self):
        self.index = {}  # {task_id: {doc_id: {chunks: [], metadata: {}}}}
        self.embedding_model = None
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Loaded embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                EMBEDDINGS_AVAILABLE = False
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate semantic embedding for text"""
        if not self.embedding_model or not EMBEDDINGS_AVAILABLE:
            return []
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            print(f"⚠️ Similarity computation failed: {e}")
            return 0.0
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def index_document(self, task_id: str, doc_id: str, markdown: str, extraction_json: dict, metadata: dict):
        """
        Index a document for RAG retrieval
        - Chunks markdown into searchable pieces
        - Generates embeddings for semantic search
        - Stores structured extraction data
        """
        if task_id not in self.index:
            self.index[task_id] = {}
        
        # Chunk the markdown
        chunks = self._chunk_text(markdown)
        
        # Generate embeddings for each chunk
        chunk_data = []
        for idx, chunk in enumerate(chunks):
            embedding = self._generate_embedding(chunk) if EMBEDDINGS_AVAILABLE else []
            chunk_data.append({
                "text": chunk,
                "embedding": embedding,
                "chunk_index": idx
            })
        
        # Also embed structured extraction keys
        structured_chunks = []
        for key, value in extraction_json.items():
            if value:
                text = f"{key}: {value}"
                embedding = self._generate_embedding(text) if EMBEDDINGS_AVAILABLE else []
                structured_chunks.append({
                    "text": text,
                    "embedding": embedding,
                    "field": key,
                    "value": value
                })
        
        self.index[task_id][doc_id] = {
            "chunks": chunk_data,
            "structured": structured_chunks,
            "metadata": metadata
        }
        
        print(f"✅ Indexed {len(chunk_data)} chunks + {len(structured_chunks)} structured fields for doc {doc_id}")
    
    def search(self, task_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search: semantic + keyword matching
        Returns top_k most relevant chunks with scores
        """
        if task_id not in self.index:
            return []
        
        query_embedding = self._generate_embedding(query) if EMBEDDINGS_AVAILABLE else []
        query_lower = query.lower()
        
        all_results = []
        
        # Search across all documents in this task
        for doc_id, doc_data in self.index[task_id].items():
            # Search markdown chunks
            for chunk_info in doc_data["chunks"]:
                # Semantic score (if available)
                semantic_score = 0.0
                if query_embedding and chunk_info.get("embedding"):
                    semantic_score = self._cosine_similarity(query_embedding, chunk_info["embedding"])
                
                # Keyword score (simple term overlap)
                chunk_lower = chunk_info["text"].lower()
                query_terms = set(query_lower.split())
                chunk_terms = set(chunk_lower.split())
                common_terms = query_terms.intersection(chunk_terms)
                keyword_score = len(common_terms) / max(len(query_terms), 1)
                
                # Hybrid score: 70% semantic, 30% keyword
                if EMBEDDINGS_AVAILABLE and query_embedding:
                    final_score = (semantic_score * 0.7) + (keyword_score * 0.3)
                    score_type = "hybrid"
                else:
                    final_score = keyword_score
                    score_type = "keyword"
                
                all_results.append({
                    "doc_id": doc_id,
                    "text": chunk_info["text"],
                    "score": final_score,
                    "score_type": score_type,
                    "chunk_index": chunk_info["chunk_index"],
                    "filename": doc_data["metadata"].get("filename", "unknown"),
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_score
                })
        
        # Sort by score and return top_k
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]
    
    def get_rag_context(self, task_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Get RAG context for a query (wrapper for backward compatibility)
        Returns: {context: str, sources: List[dict]}
        """
        results = self.search(task_id, query, top_k)
        
        if not results:
            return {"context": "", "sources": []}
        
        context_parts = []
        sources = []
        
        for idx, result in enumerate(results, 1):
            context_parts.append(f"[Source {idx}] {result['text']}")
            sources.append({
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
                "score_type": result["score_type"]
            })
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources
        }


# Global instance
_rag_instance = None

def get_instance():
    """Get global RAG instance (singleton pattern)"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = PathwayRAG()
    return _rag_instance


# Module-level API for backward compatibility
def index_document(task_id: str, doc_id: str, markdown: str, extraction_json: dict, metadata: dict):
    """Index a document"""
    instance = get_instance()
    instance.index_document(task_id, doc_id, markdown, extraction_json, metadata)


def search(task_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant chunks"""
    instance = get_instance()
    return instance.search(task_id, query, top_k)


def get_rag_context(task_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    """Get RAG context for query"""
    instance = get_instance()
    return instance.get_rag_context(task_id, query, top_k)
