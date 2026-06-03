#!/usr/bin/env python3

import os
import sys
import argparse

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from services.pdf_service import PDFService
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService

def ingest_pdf(pdf_path: str = "document/Solar_Energy_Report.pdf"):
    """Ingest PDF into ChromaDB vector store with optimal parameters"""
    print(f"Starting PDF ingestion from: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Step 1: Load and split PDF
    print("Loading PDF...")
    pdf_service = PDFService(pdf_path)
    documents = pdf_service.load_pdf()
    chunks = pdf_service.split_text(documents)
    print(f"Created {len(chunks)} chunks from PDF")
    
    # Step 2: Generate embeddings
    print("Generating embeddings...")
    embedding_service = EmbeddingService()
    embeddings = []
    
    for chunk in chunks:
        embedding = embedding_service.generate_embedding(chunk.page_content)
        if embedding:
            embeddings.append(embedding)
    
    print(f"Generated {len(embeddings)} embeddings")
    
    # Step 3: Store in ChromaDB
    print("Storing in ChromaDB...")
    vector_store = VectorStoreService()
    vector_store.add_documents(chunks, embeddings)
    vector_store.persist()
    
    print("PDF ingestion completed successfully!")
    print(f"- Loaded PDF: {pdf_path}")
    print(f"- Created {len(chunks)} chunks")
    print(f"- Generated {len(embeddings)} embeddings")
    print(f"- Stored in ChromaDB at vector_db/chroma")

if __name__ == "__main__":
    # Parse command line argument
    parser = argparse.ArgumentParser(description="Ingest PDF into ChromaDB")
    parser.add_argument("pdf_path", nargs="?", default="document/Solar_Energy_Report.pdf",help="Path to PDF file to ingest")
    args = parser.parse_args()
    ingest_pdf(args.pdf_path)