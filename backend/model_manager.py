import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ModelResponse(BaseModel):
    text: str
    model: str
    metadata: Dict[str, Any] = {}

class GeminiConfig(BaseModel):
    api_key: str = Field(..., description="API key for Gemini")
    model_name: str = Field("gemini-2.0-flash", description="Gemini model name")
    api_base: str = Field("https://generativelanguage.googleapis.com/v1beta/models")

class ModelManager:
    """Manages model inference with Ollama and Gemini fallback."""
    
    def __init__(self):
        self.ollama_available = self._check_ollama()
        self.gemini_config = self._load_gemini_config()
        
    def _check_ollama(self) -> bool:
        try:
            return requests.get("http://localhost:11434/api/version", timeout=5).status_code == 200
        except:
            return False
            
    def _load_gemini_config(self) -> Optional[GeminiConfig]:
        if api_key := os.getenv("GEMINI_API_KEY"):
            return GeminiConfig(api_key=api_key)
        logger.warning("GEMINI_API_KEY not found in .env")
        return None
    
    async def generate_response(self, prompt: str, context: List[str] = None, **kwargs) -> ModelResponse:
        full_prompt = self._format_prompt(prompt, context or [])
        
        # Try Ollama first
        if self.ollama_available:
            try:
                return await self._call_ollama(full_prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")
                self.ollama_available = False
        
        # Fall back to Gemini
        if self.gemini_config:
            try:
                return await self._call_gemini(full_prompt, **kwargs)
            except Exception as e:
                logger.error(f"Gemini failed: {e}")
                
        raise RuntimeError("No available models")
    
    def _format_prompt(self, prompt: str, context: List[str]) -> str:
        if not context:
            return prompt
        ctx = "\n\n".join(f"Context {i+1}: {c}" for i, c in enumerate(context))
        return f"""Use this context to answer the question:
{ctx}

Question: {prompt}
Answer:"""
    
    async def _call_ollama(self, prompt: str, model: str = "mistral", **kwargs) -> ModelResponse:
        import ollama
        response = await ollama.AsyncClient().generate(
            model=model,
            prompt=prompt,
            options={'temperature': 0.7, 'num_predict': 1000, **kwargs}
        )
        return ModelResponse(
            text=response['response'].strip(),
            model=f"ollama/{model}",
            metadata={'tokens': response.get('eval_count', 0)}
        )
    
    async def _call_gemini(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate text using Gemini 2.0 Flash API."""
        if not self.gemini_config:
            raise ValueError("Gemini configuration not available")
            
        url = f"{self.gemini_config.api_base}/gemini-2.0-flash:generateContent"
        params = {'key': self.gemini_config.api_key}
        
        payload = {
            'contents': [{
                'role': 'user',
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'temperature': kwargs.get('temperature', 0.7),
                'maxOutputTokens': kwargs.get('max_tokens', 1000),
                'topP': 0.95,
                'topK': 40
            }
        }
        
        response = requests.post(url, params=params, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        text = ''
        if 'candidates' in result and result['candidates']:
            text = result['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
        return ModelResponse(
            text=text.strip(),
            model="gemini/gemini-2.0-flash",
            metadata={}
        )
