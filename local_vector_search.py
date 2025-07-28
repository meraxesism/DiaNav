import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer

class LocalVectorSearch:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize local vector search with sentence-transformers"""
        print(f"Loading local embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        self.dtc_embeddings = {}
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using local model"""
        try:
            # Use the local model to generate embeddings
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def create_dtc_embeddings(self, dtc_index: Dict) -> Dict:
        """Create embeddings for all DTC codes and their descriptions"""
        print("Creating local embeddings for DTC codes...")
        
        for dtc_code, dtc_data in dtc_index.items():
            # Create comprehensive text for embedding
            text = f"{dtc_code} {dtc_data['dtc_code_line']} {dtc_data['full_block']}"
            
            # Get embedding
            embedding = self.get_embedding(text)
            if embedding:
                self.dtc_embeddings[dtc_code] = {
                    'embedding': embedding,
                    'dtc_code': dtc_code,
                    'dtc_code_line': dtc_data['dtc_code_line'],
                    'full_block': dtc_data['full_block']
                }
                print(f"✓ Created embedding for {dtc_code}")
            else:
                print(f"✗ Failed to create embedding for {dtc_code}")
        
        print(f"Created embeddings for {len(self.dtc_embeddings)} DTC codes")
        return self.dtc_embeddings
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Perform semantic search for DTC codes based on query"""
        if not self.dtc_embeddings:
            print("No DTC embeddings available. Run create_dtc_embeddings() first.")
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            print("Failed to get query embedding")
            return []
        
        # Calculate similarities
        similarities = []
        for dtc_code, dtc_info in self.dtc_embeddings.items():
            similarity = cosine_similarity(
                [query_embedding], 
                [dtc_info['embedding']]
            )[0][0]
            
            similarities.append({
                'dtc_code': dtc_code,
                'dtc_code_line': dtc_info['dtc_code_line'],
                'similarity': similarity,
                'full_block': dtc_info['full_block']
            })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top k results
        return similarities[:top_k]
    
    def save_embeddings(self, filepath: str = "local_dtc_embeddings.json"):
        """Save embeddings to file"""
        # Convert numpy arrays to lists for JSON serialization
        serializable_embeddings = {}
        for dtc_code, dtc_info in self.dtc_embeddings.items():
            serializable_embeddings[dtc_code] = {
                'embedding': dtc_info['embedding'],
                'dtc_code_line': dtc_info['dtc_code_line'],
                'full_block': dtc_info['full_block']
            }
        
        with open(filepath, 'w') as f:
            json.dump(serializable_embeddings, f, indent=2)
        print(f"Saved local embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str = "local_dtc_embeddings.json"):
        """Load embeddings from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.dtc_embeddings = data
            print(f"Loaded local embeddings for {len(self.dtc_embeddings)} DTC codes")
            return True
        else:
            print(f"Local embeddings file {filepath} not found")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize local vector search
    local_vector_search = LocalVectorSearch()
    
    # Example queries to test
    test_queries = [
        "seat movement problem",
        "LIN bus communication error", 
        "electrical fault",
        "communication issue",
        "B1087"
    ]
    
    print("Local Vector Search Test")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = local_vector_search.semantic_search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['dtc_code']} - {result['dtc_code_line']}")
            print(f"     Similarity: {result['similarity']:.3f}")
            print(f"     Snippet: {result['full_block'][:100]}...") 