"""
TF-IDF based retrieval for KB chunks.
"""

import os
import pickle
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from src.database import get_connection


STORAGE_DIR = "storage"
INDEX_FILE = os.path.join(STORAGE_DIR, "kb_index.pkl")


class KBRetriever:
    """TF-IDF based retriever for KB chunks."""
    
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.chunks = []
        self.loaded = False
    
    def build_index(self, chunks: List[Dict]):
        """Build TF-IDF index from chunks."""
        if not chunks:
            print("⚠️  No chunks to index")
            return
        
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]
        
        # Build TF-IDF matrix
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Save index
        os.makedirs(STORAGE_DIR, exist_ok=True)
        with open(INDEX_FILE, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix,
                'chunks': self.chunks
            }, f)
        
        self.loaded = True
        print(f"✅ Built TF-IDF index for {len(chunks)} chunks")
    
    def load_index(self):
        """Load pre-built index from disk."""
        if not os.path.exists(INDEX_FILE):
            # Build from database
            print("📚 Index not found, building from database...")
            chunks = self._load_chunks_from_db()
            if chunks:
                self.build_index(chunks)
            return
        
        with open(INDEX_FILE, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.tfidf_matrix = data['tfidf_matrix']
            self.chunks = data['chunks']
        
        self.loaded = True
        print(f"✅ Loaded TF-IDF index with {len(self.chunks)} chunks")
    
    def _load_chunks_from_db(self) -> List[Dict]:
        """Load chunks from database."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_id, title, category, text, compressed_text
            FROM kb_chunks
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve top-k relevant chunks for query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            category: Optional category filter
            
        Returns:
            List of relevant chunks with scores
        """
        if not self.loaded:
            self.load_index()
        
        if not self.chunks:
            return []
        
        # Filter by category if specified
        if category and category != "All":
            filtered_indices = [
                i for i, chunk in enumerate(self.chunks)
                if chunk['category'] == category
            ]
            if not filtered_indices:
                return []
            
            filtered_chunks = [self.chunks[i] for i in filtered_indices]
            filtered_matrix = self.tfidf_matrix[filtered_indices]
        else:
            filtered_chunks = self.chunks
            filtered_matrix = self.tfidf_matrix
            filtered_indices = list(range(len(self.chunks)))
        
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Compute similarity
        similarities = cosine_similarity(query_vec, filtered_matrix).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            chunk = filtered_chunks[idx].copy()
            chunk['score'] = float(similarities[idx])
            results.append(chunk)
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        if not self.loaded:
            self.load_index()
        
        categories = set(chunk['category'] for chunk in self.chunks)
        return sorted(list(categories))


# Global retriever instance
_retriever = None


def get_retriever() -> KBRetriever:
    """Get global retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = KBRetriever()
    return _retriever


if __name__ == "__main__":
    from src.database import init_database
    from src.kb_pipeline import build_kb_index
    
    init_database()
    build_kb_index()
    
    # Test retrieval
    retriever = get_retriever()
    results = retriever.retrieve("How do I reset my password?", top_k=3)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['title']} (score: {result['score']:.3f})")
