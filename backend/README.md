# Ayurvedic Remedies RAG Backend

This is the backend service for the Ayurvedic Remedies chatbot, which uses Retrieval-Augmented Generation (RAG) to provide accurate and contextual responses about Ayurvedic remedies.

## Features

- **Vector Search**: Uses FAISS for efficient similarity search of Ayurvedic remedies
- **Model Integration**: Supports both local (Ollama) and cloud (Gemini) language models
- **Flexible API**: RESTful endpoints for searching remedies and generating responses
- **Context-Aware**: Uses retrieved context to generate more accurate responses

## Prerequisites

- Python 3.8+
- Ollama (for local model inference, optional)
- Google Cloud account with Gemini API access (for cloud model, optional)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file and update with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required for Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Configure Ollama model (default is 'mistral')
OLLAMA_MODEL=mistral

# Optional: Configure the embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Running the Server

```bash
uvicorn rag_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Search Remedies

`POST /search`

Search for Ayurvedic remedies and optionally generate a response using an LLM.

**Query Parameters:**
- `query` (string, required): The search query
- `k` (int, optional, default=5): Number of results to return
- `score_threshold` (float, optional, default=0.5): Minimum similarity score (0-1)
- `generate_response` (bool, optional, default=true): Whether to generate a response
- `model` (string, optional): Specific model to use (e.g., 'mistral', 'gemini')
- `temperature` (float, optional, default=0.7): Model temperature (0-1)
- `max_tokens` (int, optional, default=1000): Maximum tokens to generate

**Example Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/search?query=turmeric%20benefits&k=3&generate_response=true' \
  -H 'accept: application/json'
```

### Generate Text

`POST /generate`

Generate text using the best available model with optional context.

**Request Body:**
```json
{
  "query": "What are the benefits of turmeric?",
  "context": ["Turmeric has anti-inflammatory properties.", "It's commonly used in Ayurveda."],
  "model": "gemini",
  "temperature": 0.7,
  "max_tokens": 500
}
```

## Model Selection

The backend will automatically select the best available model:
1. Tries to use the local Ollama model if running
2. Falls back to Gemini if Ollama is not available
3. Requires at least one model to be configured

## Development

### Testing

```bash
pytest
```

### Linting

```bash
black .
flake8
```

## License

MIT
