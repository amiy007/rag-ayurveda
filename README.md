# RAG Ayurveda Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Ayurvedic home remedies, built with Python, FastAPI, and FAISS. This application allows users to query a knowledge base of Ayurvedic remedies using natural language.

## Features

- **PDF Ingestion**: Process and index Ayurvedic remedy PDFs
- **Vector Search**: Fast similarity search using FAISS
- **Local LLM Integration**: Supports Ollama for local inference
- **REST API**: FastAPI backend for easy integration
- **Modular Design**: Easy to extend with new features and models

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) (for local LLM inference)
- [Poetry](https://python-poetry.org/) (recommended) or pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rag-ayurveda-chatbot.git
   cd rag-ayurveda-chatbot/backend
   ```

2. Install dependencies:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using Poetry (recommended)
   poetry install
   ```

3. Install Ollama (for local LLM):
   ```bash
   # Follow instructions at https://ollama.ai/
   
   # Pull a model (e.g., mistral)
   ollama pull mistral
   ```

## Usage

### 1. Process the PDF

Place your Ayurvedic remedies PDF in the `backend/data` directory and run:

```bash
python -m ingest
```

This will:
- Extract text from the PDF
- Split it into chunks
- Generate embeddings
- Create a FAISS vector store

### 2. Start the API Server

```bash
uvicorn rag_api:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Query the API

Search for remedies:
```bash
curl "http://localhost:8000/search?query=remedy for indigestion&k=3"
```

Health check:
```bash
curl http://localhost:8000/health
```

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /search`: Search for remedies
  - Parameters:
    - `query`: Search query (required)
    - `k`: Number of results to return (default: 5)
    - `score_threshold`: Minimum similarity score (0-1, default: 0.5)

## Project Structure

```
backend/
├── data/                   # Store PDF files here
├── vectorstore/            # FAISS vector store
├── ingest.py               # PDF processing and embedding
├── rag_api.py              # FastAPI application
├── ollama_runner.py        # Ollama LLM integration
└── requirements.txt        # Python dependencies
```

## Development

### Environment Setup

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black .
   isort .
   ```

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. Push and create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://python.langchain.com/) for the RAG framework
- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- [Ollama](https://ollama.ai/) for local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
