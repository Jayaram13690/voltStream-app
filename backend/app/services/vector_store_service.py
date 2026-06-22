from app.core import sqlite_patch

import sqlite3

print("=" * 50)
print("VECTOR STORE SQLITE VERSION:", sqlite3.sqlite_version)
print("=" * 50)


import chromadb
import shutil
from typing import List, Dict, Any
import os

class VectorStoreService:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            source_db = "/var/task/app/vector_db/chroma"
            target_db = "/tmp/chroma"

            # Copy only on cold start
            if not os.path.exists(target_db):
                shutil.copytree(source_db, target_db)
            
            print("DB COPIED SUCCESSFULLY")
            print("FILES:", os.listdir(target_db))

            self.persist_directory = target_db
            print("=" * 60)
            print("USING CHROMA:", self.persist_directory)
            print("=" * 60)
            # Use the app's vector_db directory
            # app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # self.persist_directory = os.path.join(app_dir, "vector_db", "chroma")
        else:
            self.persist_directory = persist_directory
        
        # Ensure the directory exists
        # os.makedirs(self.persist_directory, exist_ok=True)
        
        # Use new ChromaDB client API
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(name="energy_documents")
        print("=" * 60)
        print("COLLECTION COUNT:", self.collection.count())
        print("=" * 60)
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]] = None):
        """Add documents to vector store"""
        if not documents:
            return
        
        # Extract metadata and texts - handle both dict and Document objects
        metadatas = []
        texts = []
        for doc in documents:
            if hasattr(doc, 'metadata'):
                # Document object
                metadatas.append(doc.metadata if doc.metadata else {})
                texts.append(doc.page_content if doc.page_content else "")
            else:
                # Dictionary
                metadatas.append(doc.get("metadata", {}))
                texts.append(doc.get("page_content", ""))
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        if embeddings:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        else:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
    
    def search(self, query: str, k: int = 5, query_embedding: List[float] = None, confidence_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents with confidence threshold"""
        
        # Debug: Check collection status
        try:
            collection_count = self.collection.count()
            print(f"DEBUG: Collection has {collection_count} documents")
        except Exception as e:
            print(f"DEBUG: Error checking collection count: {e}")
        
        if query_embedding:
            # Use pre-computed embedding with distances
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "distances", "metadatas"]
            )
        else:
            # Use ChromaDB's default embedding with distances
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "distances", "metadatas"]
            )
        
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        print(f"DEBUG: Raw retrieval results - {len(documents)} documents found")
        
        # Filter results based on confidence threshold
        # Convert distances to similarity scores (lower distance = higher similarity)
        filtered_results = []
        for doc, meta, distance in zip(documents, metadatas, distances):
            # Convert distance to similarity score (simple inverse relationship)
            # Distance range is typically 0-2 for cosine similarity in ChromaDB
            similarity_score = max(0, 1 - distance/2)  # Normalize to 0-1 range
            
            print(f"DEBUG: Document similarity: {similarity_score:.3f}, distance: {distance:.3f}, threshold: {confidence_threshold:.3f}")
            
            if similarity_score >= confidence_threshold:
                filtered_results.append({
                    "content": doc,
                    "metadata": meta if meta else {},
                    "distance": distance,
                    "similarity_score": similarity_score
                })
        
        print(f"DEBUG: After filtering - {len(filtered_results)} documents pass threshold")
        return filtered_results
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Get all document IDs
            all_ids = [id for id in self.collection.get()['ids']]
            
            # Delete all documents if collection is not empty
            if all_ids:
                self.collection.delete(ids=all_ids)
                print(f"DEBUG: Cleared {len(all_ids)} documents from collection")
            else:
                print("DEBUG: Collection was already empty")
            return True
        except Exception as e:
            print(f"DEBUG: Error clearing collection: {e}")
            return False

    def persist(self):
        """Persist the database to disk"""
        # PersistentClient handles persistence automatically
        pass