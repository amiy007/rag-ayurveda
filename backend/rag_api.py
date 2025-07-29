import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from model_manager import ModelManager

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

class GenerateRequest(BaseModel):
    query: str
    context: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(1000, gt=0)

class GenerateResponse(BaseModel):
    response: str
    model: str
    metadata: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    generated_response: Optional[GenerateResponse] = None

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
            cls._instance.model_manager = ModelManager()
            cls._instance._vectorstore = None
        return cls._instance
    
    def get_vectorstore(self) -> FAISS:
        """Get or create the FAISS vector store."""
        if not hasattr(self, '_vectorstore') or self._vectorstore is None:
            try:
                # Create directory if it doesn't exist
                self.vectorstore_dir.mkdir(parents=True, exist_ok=True)
                
                # Check if vector store files exist
                index_file = self.vectorstore_dir / "index.faiss"
                if index_file.exists():
                    self._vectorstore = FAISS.load_local(
                        folder_path=str(self.vectorstore_dir),
                        embeddings=self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info(f"Loaded existing vector store from {self.vectorstore_dir}")
                else:
                    raise FileNotFoundError("No existing vector store found")
                    
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                # Create a minimal vector store with a dummy document
                self._vectorstore = FAISS.from_texts(
                    texts=["This is a placeholder document. Please add your documents to the vector store."],
                    embedding=self.embeddings
                )
                # Don't save the dummy vector store to avoid overwriting
                logger.warning("Created in-memory vector store with placeholder document")
                
        if self._vectorstore is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize vector store. Please ensure documents have been processed."
            )
            
        return self._vectorstore
        
    async def search_similar_documents(self, query: str, k: int = 5, score_threshold: float = 0.5) -> List[dict]:
        """Search for similar documents in the vector store."""
        try:
            logger.info(f"Searching for query: {query}")
            vectorstore = self.get_vectorstore()
            
            # Check if we have a valid vector store
            if vectorstore is None:
                logger.error("Vector store is None")
                return []
                
            if not hasattr(vectorstore, 'similarity_search_with_score'):
                logger.error(f"Vector store missing similarity_search_with_score method. Available methods: {dir(vectorstore)}")
                return []
            
            try:
                logger.info("Executing similarity search...")
                docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
                logger.info(f"Found {len(docs_and_scores)} results")
                
                # Format results with similarity scores (1.0 - distance)
                results = []
                for doc, score in docs_and_scores:
                    similarity = 1.0 - score  # Convert distance to similarity
                    if similarity >= score_threshold:
                        results.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
                            "score": float(similarity)
                        })
                
                return results
                
            except Exception as search_error:
                logger.error(f"Error during similarity search: {str(search_error)}")
                # Return empty results if search fails
                return []
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_similar_documents: {str(e)}")
            # Return empty list instead of failing
            return []
    
    async def generate_response(self, query: str, context: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate a response using the best available model."""
        try:
            response = await self.model_manager.generate_response(
                prompt=query,
                context=context or [],
                **kwargs
            )
            return {
                "response": response.text,
                "model": response.model,
                "metadata": response.metadata
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Ayurvedic Remedies RAG API is running"}

@app.post("/search")
async def search_remedies(
    query: str = Query(..., description="Search query for Ayurvedic remedies"),
    k: int = Query(5, description="Number of results to return"),
    score_threshold: float = Query(0.3, description="Minimum similarity score (0-1)"),
    generate_response: bool = Query(True, description="Whether to generate a response using the model"),
    model: Optional[str] = Query(None, description="Specific model to use (e.g., 'mistral', 'gemini')"),
    temperature: float = Query(0.7, description="Model temperature (0-1)", ge=0.0, le=1.0),
    max_tokens: int = Query(1000, description="Maximum number of tokens to generate", gt=0),
    vectorstore_manager: VectorStoreManager = Depends(VectorStoreManager)
):
    """
    Search for Ayurvedic remedies based on the query and optionally generate a response.
    """
    try:
        # Search for similar documents
        results = await vectorstore_manager.search_similar_documents(
            query=query,
            k=k,
            score_threshold=score_threshold
        )
        
        # Generate response if requested and we have results
        generated = None
        if generate_response and results:
            try:
                # Use the top results as context
                context = [result["content"] for result in results[:3]]  # Use top 3 results as context
                generated = await vectorstore_manager.generate_response(
                    query=query,
                    context=context,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                logger.warning(f"Model response generation failed: {str(e)}")
        
        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            total_results=len(results),
            generated_response=GenerateResponse(**generated) if generated else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_remedies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while searching for remedies: {str(e)}"
        )

@app.post("/generate")
async def generate_text(
    request: GenerateRequest,
    vectorstore_manager: VectorStoreManager = Depends(VectorStoreManager)
) -> GenerateResponse:
    """
    Generate text using the best available model with optional context.
    """
    try:
        result = await vectorstore_manager.generate_response(
            query=request.query,
            context=request.context,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return GenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating text: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)