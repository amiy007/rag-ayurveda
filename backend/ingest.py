import os
import logging
from typing import List, Optional
from pathlib import Path

import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFIngestor:
    def __init__(self, data_dir: str = "data", vectorstore_dir: str = "vectorstore"):
        """Initialize the PDF ingestor with directories for data and vectorstore."""
        self.data_dir = Path(data_dir)
        self.vectorstore_dir = Path(vectorstore_dir)
        self.vectorstore_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Document]:
        """Extract text from a PDF file and return LangChain Documents."""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            
            # Extract text from each page
            documents = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    # Create a document for each page
                    metadata = {
                        "source": pdf_path.name,
                        "page": page_num + 1,
                    }
                    documents.append(Document(page_content=text, metadata=metadata))
            
            return documents
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise

    def process_pdf(self, pdf_filename: str) -> None:
        """Process a PDF file and create/update FAISS vector store."""
        try:
            pdf_path = self.data_dir / pdf_filename
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Extract text from PDF
            documents = self.extract_text_from_pdf(pdf_path)
            if not documents:
                raise ValueError("No text could be extracted from the PDF")
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split PDF into {len(chunks)} chunks")
            
            # Create or load FAISS vector store
            vectorstore_path = self.vectorstore_dir / "faiss_index"
            
            if vectorstore_path.exists():
                # Load existing vector store and add new documents
                logger.info("Loading existing FAISS vector store")
                db = FAISS.load_local(
                    folder_path=str(self.vectorstore_dir),
                    index_name="faiss_index",
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Adding new documents to existing vector store")
                db.add_documents(chunks)
            else:
                # Create new vector store
                logger.info("Creating new FAISS vector store")
                db = FAISS.from_documents(chunks, self.embeddings)
            
            # Save the vector store
            db.save_local(
                folder_path=str(self.vectorstore_dir),
                index_name="faiss_index"
            )
            
            logger.info(f"Successfully created/updated FAISS vector store at {self.vectorstore_dir}")
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

def main():
    """Main function to process the PDF and create embeddings."""
    try:
        # Initialize the ingestor
        ingestor = PDFIngestor()
        
        # Process the Ayurvedic Home Remedies PDF
        pdf_filename = "Ayurvedic-Home-Remedies-English.pdf"
        ingestor.process_pdf(pdf_filename)
        
        print("PDF processing and vector store creation completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()