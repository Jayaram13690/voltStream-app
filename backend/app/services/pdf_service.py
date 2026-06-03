from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
import hashlib

class PDFService:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def load_pdf(self) -> List:
        """Load PDF file and extract text pages"""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {self.pdf_path}")
        
        loader = PyPDFLoader(self.pdf_path)
        return loader.load()
    
    def split_text(self, documents: List, chunk_size: int = 500, chunk_overlap: int = 100) -> List:
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)

    def get_document_hash(self, pdf_path: str) -> str:
        """Generate hash of PDF file for change detection"""
        if not os.path.exists(pdf_path):
            return ""

        hash_sha256 = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()