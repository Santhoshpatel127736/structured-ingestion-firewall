# Enterprise Structured Ingestion Firewall

An LLM-powered API that processes customer messages, classifies their intent, validates structured outputs, estimates input tokens, and stores the results in a SQLite database.

## Features

- **LLM-powered classification:** Uses Groq to classify customer messages.
- **Structured outputs:** Uses Instructor and Pydantic to validate the LLM response.
- **Input validation:** Rejects messages that are too short or exceed the allowed length.
- **Token estimation:** Uses `tiktoken` to estimate input token usage.
- **Database storage:** Saves processed messages and classification results in SQLite.
- **REST API:** Built with FastAPI.
- **Automated testing:** Includes tests for API validation, successful ingestion, and simulated LLM failures.

## Technology Stack

- Python
- FastAPI
- Groq API
- Instructor
- Pydantic
- SQLite
- tiktoken
- pytest

## How It Works

1. A client submits a customer message to the `/ingest` endpoint.
2. FastAPI validates the input.
3. The Groq LLM classifies the message into an intent and risk profile.
4. Pydantic validates the structured response.
5. The application estimates the input token count.
6. The result is saved in the SQLite database.
7. The API returns the classification, summary, priority, and token metadata.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Santhoshpatel127736/structured-ingestion-firewall.git
cd structured-ingestion-firewall
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key. Never commit or share your `.env` file.

### 5. Start the API

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/ingest` | Validate, classify, and store a customer message |

Example request body:

```json
{
  "text": "I was charged twice for my order and need a refund."
}
```

The response includes the predicted intent, risk profile, priority, summary, and estimated input tokens.

## Run Tests

```bash
python -m pytest -v
```

## Security

- Store your Groq API key in `.env`.
- Never commit API keys or other secrets.
- Keep `.env`, `.venv/`, and `ingestion.db` out of Git.

## Project Status

Week 1 implementation: API, structured classification, token estimation, SQLite persistence, and automated tests.

Built as a learning project exploring reliable LLM-powered data ingestion and validation.