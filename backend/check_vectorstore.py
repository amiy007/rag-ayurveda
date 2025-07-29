import os
import logging
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_vectorstore(vectorstore_dir: str = "vectorstore"):
    """Check if the vector store exists and can be loaded."""
    vectorstore_path = Path(vectorstore_dir)
    
    # Check if vector store files exist
    index_file = vectorstore_path / "index.faiss"
    index_file_pkl = vectorstore_path / "index.pkl"
    
    print(f"Checking vector store at: {vectorstore_path.absolute()}")
    print(f"Index file exists: {index_file.exists()}")
    print(f"PKL file exists: {index_file_pkl.exists()}")
    
    if not index_file.exists() or not index_file_pkl.exists():
        print("Error: Vector store files are missing")
        return
    
    # Try to load the vector store
    try:
        print("\nAttempting to load vector store...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vectorstore = FAISS.load_local(
            folder_path=str(vectorstore_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        
        print("Successfully loaded vector store!")
        print(f"Number of documents: {vectorstore.index.ntotal}")
        
        # Try a simple search
        print("\nTesting search...")
        results = vectorstore.similarity_search_with_score("turmeric", k=2)
        print(f"Found {len(results)} results")
        for i, (doc, score) in enumerate(results):
            print(f"\nResult {i+1} (Score: {1.0 - score:.2f}):")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
            
    except Exception as e:
        print(f"\nError loading vector store: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_vectorstore()
