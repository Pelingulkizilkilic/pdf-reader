# app/rag/vector_store.py
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
import pickle
import os
import logging
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


def create_faiss_index(chunks: List[str], metadata: List[Dict] = None) -> Dict[str, Any]:
    """
    Create FAISS index with OpenAI embeddings
    """
    try:
        # Get embeddings from OpenAI
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = openai_service.generate_embeddings(chunks)
        
        # Wait for async function if needed
        if hasattr(embeddings, '__await__'):
            import asyncio
            embeddings = asyncio.run(embeddings)
        
        # Convert to numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_np.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_np)
        
        # Prepare result
        result = {
            'index': index,
            'chunks': chunks,
            'embeddings': embeddings_np,
            'metadata': metadata if metadata else [],
            'dimension': dimension,
            'chunk_count': len(chunks)
        }
        
        logger.info(f"FAISS index created with {len(chunks)} chunks, dimension {dimension}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating FAISS index: {e}")
        
        # Fallback to random embeddings for testing
        logger.warning("Using random embeddings as fallback")
        return create_faiss_index_fallback(chunks, metadata)


def create_faiss_index_fallback(chunks: List[str], metadata: List[Dict] = None) -> Dict[str, Any]:
    """Fallback method with random embeddings"""
    # Random embeddings for testing
    dimension = 384  # text-embedding-3-small dimension
    embeddings_np = np.random.randn(len(chunks), dimension).astype('float32')
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    return {
        'index': index,
        'chunks': chunks,
        'embeddings': embeddings_np,
        'metadata': metadata if metadata else [],
        'dimension': dimension,
        'chunk_count': len(chunks),
        'is_fallback': True
    }


def search_similar_chunks(vector_store: Dict, question: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Search for similar chunks using question embedding
    """
    try:
        # Get embedding for the question
        question_embeddings = openai_service.generate_embeddings([question])
        
        # Wait for async if needed
        if hasattr(question_embeddings, '__await__'):
            import asyncio
            question_embeddings = asyncio.run(question_embeddings)
        
        question_vector = np.array(question_embeddings[0]).astype('float32').reshape(1, -1)
        
        # Search in FAISS index
        distances, indices = vector_store['index'].search(question_vector, min(k, len(vector_store['chunks'])))
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(vector_store['chunks']):
                results.append({
                    'text': vector_store['chunks'][idx],
                    'metadata': vector_store['metadata'][idx] if idx < len(vector_store['metadata']) else {},
                    'distance': float(distances[0][i]),
                    'rank': i + 1,
                    'chunk_index': int(idx)
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        # Fallback: return first k chunks
        return [
            {
                'text': vector_store['chunks'][i],
                'metadata': vector_store['metadata'][i] if i < len(vector_store['metadata']) else {},
                'distance': 1.0,
                'rank': i + 1,
                'chunk_index': i,
                'error': str(e)
            }
            for i in range(min(k, len(vector_store['chunks'])))
        ]


def save_vector_store(vector_store: Dict, filepath: str):
    """Save vector store to disk"""
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(vector_store, f)
        return True
    except Exception as e:
        logger.error(f"Error saving vector store: {e}")
        return False


def load_vector_store(filepath: str) -> Dict:
    """Load vector store from disk"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")
        return None