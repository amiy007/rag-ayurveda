import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Ayurvedic documents
SAMPLE_DOCUMENTS = [
    {
        "content": "Turmeric (Curcuma longa) is a golden-yellow spice with powerful anti-inflammatory and antioxidant properties. It contains curcumin, which helps reduce inflammation and may help with conditions like arthritis and digestive issues.",
        "metadata": {"source": "ayurveda_herbs", "type": "herb"}
    },
    {
        "content": "Ashwagandha (Withania somnifera) is an adaptogenic herb that helps the body manage stress. It's known to boost energy, improve sleep, and support the immune system.",
        "metadata": {"source": "ayurveda_herbs", "type": "herb"}
    },
    {
        "content": "Triphala is a traditional Ayurvedic herbal formulation consisting of three fruits: Amalaki (Emblica officinalis), Bibhitaki (Terminalia bellirica), and Haritaki (Terminalia chebula). It's commonly used for digestive health and detoxification.",
        "metadata": {"source": "ayurveda_formulas", "type": "formula"}
    },
    {
        "content": "Abhyanga is the practice of self-massage with warm oil. It helps improve circulation, promote relaxation, and support the lymphatic system. Best performed before morning bath.",
        "metadata": {"source": "ayurveda_practices", "type": "practice"}
    },
    {
        "content": "Doshas are the three fundamental energies that govern our physiology: Vata (air/space), Pitta (fire/water), and Kapha (water/earth). Balancing these doshas is key to maintaining health in Ayurveda.",
        "metadata": {"source": "ayurveda_principles", "type": "concept"}
    }
]

def initialize_vectorstore(vectorstore_dir: str = "vectorstore") -> FAISS:
    """Initialize the FAISS vector store with sample documents."""
    # Create directory if it doesn't exist
    vectorstore_path = Path(vectorstore_dir)
    vectorstore_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Convert documents to Document objects
    docs = [
        Document(
            page_content=doc["content"],
            metadata=doc["metadata"]
        )
        for doc in SAMPLE_DOCUMENTS
    ]
    
    try:
        # Create and save the vector store
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(folder_path=str(vectorstore_path))
        logger.info(f"Successfully initialized vector store with {len(docs)} documents at {vectorstore_path}")
        return vectorstore
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        vectorstore = initialize_vectorstore()
        print("Vector store initialized successfully!")
        print(f"Number of documents: {vectorstore.index.ntotal}")
    except Exception as e:
        print(f"Failed to initialize vector store: {str(e)}")
