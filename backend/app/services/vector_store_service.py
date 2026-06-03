import chromadb
from typing import List, Dict, Any
import os

class VectorStoreService:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            # Use the app's vector_db directory
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.persist_directory = os.path.join(app_dir, "vector_db", "chroma")
        else:
            self.persist_directory = persist_directory
        
        # Ensure the directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Use new ChromaDB client API
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(name="energy_documents")
    
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
    
    def search(self, query: str, k: int = 5, query_embedding: List[float] = None) -> List[Dict[str, Any]]:
        """Search for similar documents with confidence threshold"""
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
        return [
                {
                    "content": doc,
                    "metadata": meta if meta else {}
                }
                for doc, meta in zip(documents, metadatas)
            ]
    
    def persist(self):
        """Persist the database to disk"""
        # PersistentClient handles persistence automatically
        pass