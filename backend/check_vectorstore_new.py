import os
import sys
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_vectorstore(vectorstore_dir: str = "vectorstore"):
    """Check the contents of the vector store and test search functionality."""
    vectorstore_path = Path(vectorstore_dir)
    
    # Check if vector store directory exists
    if not vectorstore_path.exists():
        logger.error(f"Vector store directory not found: {vectorstore_path}")
        return
    
    # List all files in the vector store directory
    logger.info(f"Files in {vectorstore_path}:")
    for f in vectorstore_path.glob("*"):
        logger.info(f"- {f.name} ({f.stat().st_size} bytes)")
    
    # Try to load the vector store
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Try both possible index file names
    index_files = ["faiss_index", "index"]
    
    for index_name in index_files:
        faiss_file = vectorstore_path / f"{index_name}.faiss"
        pkl_file = vectorstore_path / f"{index_name}.pkl"
        
        if faiss_file.exists() and pkl_file.exists():
            try:
                logger.info(f"\nTrying to load vector store with index: {index_name}")
                vectorstore = FAISS.load_local(
                    folder_path=str(vectorstore_path),
                    embeddings=embeddings,
                    index_name=index_name,
                    allow_dangerous_deserialization=True
                )
                
                # Test search
                logger.info("\nTesting search with query: 'remedy for cold'")
                results = vectorstore.similarity_search_with_score("remedy for cold", k=3)
                
                if not results:
                    logger.warning("No results found for query")
                else:
                    logger.info(f"Found {len(results)} results:")
                    for i, (doc, score) in enumerate(results):
                        logger.info(f"\nResult {i+1} (Score: {1.0 - score:.2f}):")
                        logger.info(f"Content: {doc.page_content[:200]}...")
                        logger.info(f"Metadata: {doc.metadata}")
                
                return  # Successfully loaded and tested
                
            except Exception as e:
                logger.error(f"Error loading vector store with index '{index_name}': {str(e)}")
                continue
    
    logger.error("Failed to load any vector store index")

if __name__ == "__main__":
    check_vectorstore()
