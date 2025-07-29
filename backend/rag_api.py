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
                logger.info(f"Initializing vector store from {self.vectorstore_dir}")
                
                # Create directory if it doesn't exist
                self.vectorstore_dir.mkdir(parents=True, exist_ok=True)
                
                # Try both possible index file names
                index_names = ["faiss_index", "index"]
                loaded = False
                
                for index_name in index_names:
                    index_file = self.vectorstore_dir / f"{index_name}.faiss"
                    pkl_file = self.vectorstore_dir / f"{index_name}.pkl"
                    
                    logger.info(f"Checking for vector store files with index name '{index_name}' in {self.vectorstore_dir}:")
                    logger.info(f"- {index_name}.faiss exists: {index_file.exists()}")
                    logger.info(f"- {index_name}.pkl exists: {pkl_file.exists()}")
                    
                    if index_file.exists() and pkl_file.exists():
                        try:
                            logger.info(f"Both index files found for '{index_name}', attempting to load vector store...")
                            self._vectorstore = FAISS.load_local(
                                folder_path=str(self.vectorstore_dir),
                                embeddings=self.embeddings,
                                index_name=index_name,
                                allow_dangerous_deserialization=True
                            )
                            logger.info(f"Successfully loaded vector store with {self._vectorstore.index.ntotal} documents")
                            loaded = True
                            break  # Successfully loaded, exit the loop
                        except Exception as load_error:
                            logger.error(f"Error loading vector store with index '{index_name}': {str(load_error)}", exc_info=True)
                            continue  # Try the next index name
                
                if not loaded:
                    logger.warning("No valid vector store index found. Creating in-memory vector store with placeholder document.")
                    self._vectorstore = FAISS.from_texts(
                        texts=["This is a placeholder document. Please add your documents to the vector store."],
                        embedding=self.embeddings
                    )
                    logger.warning(f"Created new vector store with {self._vectorstore.index.ntotal} documents")
                    
            except Exception as e:
                logger.error(f"Error in get_vectorstore: {str(e)}")
                logger.info("Creating in-memory vector store with placeholder document")
                # Create a minimal vector store with a dummy document
                self._vectorstore = FAISS.from_texts(
                    texts=["This is a placeholder document. Please add your documents to the vector store."],
                    embedding=self.embeddings
                )
                logger.warning(f"Created new vector store with {self._vectorstore.index.ntotal} documents")
                
        if self._vectorstore is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize vector store. Please ensure documents have been processed."
            )
            
        return self._vectorstore
        
    async def search_similar_documents(self, query: str, k: int = 5, score_threshold: float = 0.5) -> List[dict]:
        """Search for similar documents in the vector store."""
        try:
            logger.info(f"Searching for query: '{query}' with k={k}, score_threshold={score_threshold}")
            
            # Get the vector store
            vectorstore = self.get_vectorstore()
            logger.info(f"Vector store type: {type(vectorstore).__name__}")
            
            # Check if we have a valid vector store
            if vectorstore is None:
                logger.error("Vector store is None")
                return []
                
            if not hasattr(vectorstore, 'similarity_search_with_score'):
                available_methods = [m for m in dir(vectorstore) if not m.startswith('_')]
                logger.error(f"Vector store missing similarity_search_with_score. Available methods: {available_methods}")
                return []
            
            try:
                logger.info(f"Executing similarity search with query: '{query}'")
                docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
                logger.info(f"Search completed. Found {len(docs_and_scores)} raw results")
                
                # Format results with similarity scores (1.0 - distance)
                results = []
                for i, (doc, score) in enumerate(docs_and_scores):
                    try:
                        similarity = 1.0 - score  # Convert distance to similarity
                        if similarity >= score_threshold:
                            result = {
                                "content": doc.page_content,
                                "metadata": {},
                                "score": float(similarity)
                            }
                            
                            # Safely get metadata
                            if hasattr(doc, 'metadata') and doc.metadata:
                                result["metadata"] = doc.metadata
                            
                            logger.debug(f"Result {i+1} - Score: {similarity:.2f}")
                            results.append(result)
                        
                    except Exception as e:
                        logger.warning(f"Error processing search result {i+1}: {str(e)}")
                        continue
                
                logger.info(f"Returning {len(results)} filtered results (from {len(docs_and_scores)} total)")
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
        
        # Generate response if requested
        generated = None
        if generate_response:
            try:
                if results:
                    # Use the top results as context
                    context = [result["content"] for result in results[:3]]  # Use top 3 results as context
                    prompt = query
                else:
                    # No relevant results found, use LLM with a note about limited context
                    context = []
                    prompt = f"{query} \n\nNote: I couldn't find specific information in my knowledge base about this topic. " \
                            f"Here's a general response, but please consult with a healthcare professional " \
                            f"for personalized advice.\n\n"
                
                generated = await vectorstore_manager.generate_response(
                    query=prompt,
                    context=context,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                logger.warning(f"Model response generation failed: {str(e)}")
                if not results:
                    # If we have no results and generation fails, provide a helpful message
                    generated = {
                        "response": "I couldn't find specific information about this in my knowledge base. " \
                                  "Please consult with a qualified healthcare professional for personalized advice.",
                        "model": "fallback",
                        "metadata": {"warning": "No relevant context found and model generation failed"}
                    }
        
        # Ensure results are properly formatted
        formatted_results = []
        for r in results:
            try:
                formatted_results.append(SearchResult(
                    content=r.get('content', ''),
                    metadata=r.get('metadata', {}),
                    score=r.get('score', 0.0)
                ))
            except Exception as e:
                logger.warning(f"Error formatting result: {str(e)}")
                continue
                
        return SearchResponse(
            results=formatted_results,
            total_results=len(formatted_results),
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