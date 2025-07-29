import os
import logging
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ayurvedic Remedies RAG API",
    description="API for querying Ayurvedic home remedies using RAG",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchResult(BaseModel):
    content: str
    metadata: dict
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int

# Initialize models and utilities
class VectorStoreManager:
    _instance = None
    
    def __new__(cls, vectorstore_dir: str = "vectorstore"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.vectorstore_dir = Path(vectorstore_dir)
            cls._instance.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            cls._instance.vectorstore = None
        return cls._instance
    
    def get_vectorstore(self):
        """Get or load the FAISS vector store."""
        if self.vectorstore is None:
            try:
                self.vectorstore = FAISS.load_local(
                    folder_path=str(self.vectorstore_dir),
                    index_name="faiss_index",
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Successfully loaded FAISS vector store")
            except Exception as e:
                logger.error(f"Error loading FAISS vector store: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to load the vector store. Please ensure the PDF has been processed first."
                )
        return self.vectorstore

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Ayurvedic Remedies RAG API is running"}

@app.get("/search", response_model=SearchResponse)
async def search_remedies(
    query: str = Query(..., description="Search query for Ayurvedic remedies"),
    k: int = Query(5, description="Number of results to return"),
    score_threshold: float = Query(0.5, description="Minimum similarity score (0-1)"),
    vectorstore_manager: VectorStoreManager = Depends(VectorStoreManager)
):
    """
    Search for Ayurvedic remedies based on the query.
    """
    try:
        # Get the vector store
        vectorstore = vectorstore_manager.get_vectorstore()
        
        # Perform similarity search
        docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
        
        # Filter results by score threshold and format response
        results = []
        for doc, score in docs_and_scores:
            if score >= score_threshold:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
        
        return SearchResponse(
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching for remedies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while searching for remedies: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)