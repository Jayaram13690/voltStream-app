import os
import json
from .pdf_service import PDFService
from .embedding_service import EmbeddingService
from .vector_store_service import VectorStoreService

class AutoIngestService:
    """Automatic PDF ingestion with change detection"""

    HASH_FILE = "document_hash.json"

    def __init__(self, pdf_path: str = "document/Solar_Energy_Report.pdf"):
        self.pdf_path = pdf_path
        self.hash_file = os.path.join(os.path.dirname(pdf_path), self.HASH_FILE)

    def get_current_hash(self) -> str:
        """Get hash of current document"""
        pdf_service = PDFService(self.pdf_path)
        return pdf_service.get_document_hash(self.pdf_path)

    def get_stored_hash(self) -> str:
        """Get previously stored hash"""
        if not os.path.exists(self.hash_file):
            return ""

        with open(self.hash_file, 'r') as f:
            data = json.load(f)
            return data.get('hash', "")

    def store_hash(self, hash_value: str):
        """Store current document hash"""
        os.makedirs(os.path.dirname(self.hash_file), exist_ok=True)
        with open(self.hash_file, 'w') as f:
            json.dump({"hash": hash_value, "pdf_path": self.pdf_path}, f)

    def check_for_changes(self) -> bool:
        """Check if document has changed"""
        current_hash = self.get_current_hash()
        stored_hash = self.get_stored_hash()

        if not current_hash:
            print("DEBUG: Document not available for hash comparison - skipping auto-ingestion")
            return False

        if current_hash != stored_hash:
            print(f"Document changed: {self.pdf_path}")
            print(f"Old hash: {stored_hash[:8]}...")
            print(f"New hash: {current_hash[:8]}...")
            return True

        print("Document unchanged")
        return False

    def auto_ingest_if_changed(self):
        """Automatically ingest if document changed"""
        if not self.check_for_changes():
            print("DEBUG: Document unchanged, skipping ingestion")
            return False

        print("Starting automatic ingestion...")
        try:
            # Load and split PDF
            pdf_service = PDFService(self.pdf_path)
            documents = pdf_service.load_pdf()
            print(f"DEBUG: Loaded {len(documents)} document pages")
            
            chunks = pdf_service.split_text(documents, chunk_size=750, chunk_overlap=150)
            print(f"DEBUG: Split into {len(chunks)} chunks")

            # Generate embeddings
            embedding_service = EmbeddingService()
            embeddings = []
            embedding_failures = 0
            for i, chunk in enumerate(chunks):
                embedding = embedding_service.generate_embedding(chunk.page_content)
                if embedding:
                    embeddings.append(embedding)
                else:
                    embedding_failures += 1
                    print(f"DEBUG: Failed to generate embedding for chunk {i+1}")

            print(f"DEBUG: Generated {len(embeddings)} embeddings ({embedding_failures} failures)")

            # Store in ChromaDB
            vector_store = VectorStoreService()
            vector_store.add_documents(chunks, embeddings)
            
            # Verify collection
            try:
                collection_count = vector_store.collection.count()
                print(f"DEBUG: Collection now has {collection_count} documents")
            except Exception as e:
                print(f"DEBUG: Could not verify collection count: {e}")

            # Update hash file
            self.store_hash(self.get_current_hash())

            print(f"Auto-ingestion completed: {len(chunks)} chunks")
            return True

        except Exception as e:
            print(f"Auto-ingestion failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False