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
            
        # Join all context with clear separation
        context_str = "\n\n".join([
            f"--- CONTEXT {i+1} ---\n{text.strip()}"
            for i, text in enumerate(context) if text.strip()
        ])
        
        # Create a more structured prompt
        return f"""You are an expert in Ayurveda providing remedies and health advice. 
Use the following context to answer the question. If the context doesn't contain 
enough information, say "I don't have enough information about this in my knowledge base."

CONTEXT:
{context_str}

QUESTION: {prompt}

INSTRUCTIONS:
1. Provide a clear, concise answer based on the context
2. If the context mentions specific remedies, list them clearly
3. Include relevant details like preparation methods and usage instructions
4. If the context doesn't contain enough information, say so

ANSWER:"""
    
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
        """Generate text using Gemini 2.0 Flash API with enhanced context handling."""
        if not self.gemini_config:
            raise ValueError("Gemini configuration not available")
            
        url = f"{self.gemini_config.api_base}/gemini-2.0-flash:generateContent"
        params = {'key': self.gemini_config.api_key}
        
        # Enhanced system instruction for better responses
        system_instruction = """You are an expert in Ayurveda and natural remedies. 
        Provide accurate, helpful, and safe information based on the provided context. 
        If the context doesn't contain enough information, clearly state that.
        Be specific about dosages, preparations, and usage instructions when possible."""
        
        payload = {
            'contents': [{
                'role': 'user',
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'temperature': min(0.7, kwargs.get('temperature', 0.5)),  # Cap temperature for more factual responses
                'maxOutputTokens': kwargs.get('max_tokens', 1000),
                'topP': 0.9,  # Slightly more focused than default
                'topK': 40,
                'stopSequences': ['---']  # Prevent model from making up additional context
            },
            'safetySettings': [
                {
                    'category': 'HARM_CATEGORY_HARASSMENT',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_HATE_SPEECH',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    'threshold': 'BLOCK_NONE'
                },
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_NONE'
                }
            ],
            'systemInstruction': {
                'parts': [{'text': system_instruction}]
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
