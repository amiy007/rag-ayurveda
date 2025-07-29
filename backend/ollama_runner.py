import os
import logging
import json
from typing import Dict, List, Optional, Union
import subprocess
from pathlib import Path

import requests
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaConfig(BaseModel):
    """Configuration for Ollama API."""
    base_url: str = Field("http://localhost:11434", description="Base URL for Ollama API")
    model: str = Field("mistral", description="Default model to use for generation")
    temperature: float = Field(0.7, description="Sampling temperature (0-2)")
    max_tokens: int = Field(2000, description="Maximum number of tokens to generate")
    top_p: float = Field(0.9, description="Nucleus sampling parameter")

class OllamaClient:
    """Client for interacting with Ollama's API."""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize the Ollama client."""
        self.config = config or OllamaConfig()
        self.session = requests.Session()
        
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Ollama API.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Override any config parameters
            
        Returns:
            Generated text from the model
        """
        # Update config with any overrides
        config = self.config.model_copy(update=kwargs)
        
        # Prepare the request payload
        payload = {
            "model": config.model,
            "prompt": prompt,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            },
            "stream": False
        }
        
        try:
            # Make the API request
            url = f"{config.base_url}/api/generate"
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            # Parse and return the response
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise RuntimeError(f"Failed to generate text: {str(e)}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Have a conversation with the model using chat format.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Override any config parameters
            
        Returns:
            The model's response as a string
        """
        # Update config with any overrides
        config = self.config.model_copy(update=kwargs)
        
        # Prepare the request payload
        payload = {
            "model": config.model,
            "messages": messages,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            },
            "stream": False
        }
        
        try:
            # Make the API request
            url = f"{config.base_url}/api/chat"
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            # Parse and return the response
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama chat API: {str(e)}")
            raise RuntimeError(f"Failed to generate chat response: {str(e)}")

def check_ollama_installed() -> bool:
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return "version" in result.stdout.lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def ensure_ollama_model(model_name: str = "mistral"):
    """Ensure the specified Ollama model is available, pull if needed."""
    try:
        logger.info(f"Checking if model '{model_name}' is available...")
        subprocess.run(
            ["ollama", "show", "--modelfile", model_name],
            capture_output=True,
            check=True
        )
        logger.info(f"Model '{model_name}' is already available.")
    except subprocess.CalledProcessError:
        logger.info(f"Model '{model_name}' not found. Pulling from Ollama hub...")
        try:
            subprocess.run(
                ["ollama", "pull", model_name],
                check=True
            )
            logger.info(f"Successfully pulled model '{model_name}'.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull model '{model_name}': {str(e)}")
            raise RuntimeError(f"Failed to pull model '{model_name}'. Please check your internet connection and try again.")

if __name__ == "__main__":
    # Example usage
    if not check_ollama_installed():
        print("Ollama is not installed. Please install it from https://ollama.ai/")
    else:
        try:
            # Ensure the default model is available
            ensure_ollama_model("mistral")
            
            # Initialize the client
            client = OllamaClient()
            
            # Test generation
            prompt = "Explain what Ayurveda is in one paragraph."
            print(f"Prompt: {prompt}")
            
            response = client.generate(prompt)
            print("\nResponse:")
            print(response)
            
            # Test chat
            messages = [
                {"role": "user", "content": "What are the key principles of Ayurveda?"}
            ]
            chat_response = client.chat(messages)
            print("\nChat Response:")
            print(chat_response)
            
        except Exception as e:
            print(f"Error: {str(e)}")