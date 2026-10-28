
import os
from uuid import uuid4

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, ValidationError

from structured_output import classify_message
from response_service import generate_response
from database import create_database, save_record

load_dotenv()

# Use a normal OpenAI-compatible Groq client for chat responses.
# This avoids the Instructor response_model requirement.
chat_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

create_database()

# Week 3: In-memory conversation storage
chat_sessions: dict[str, list[dict[str, str]]] = {}

app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://structured-ingestion-firewall.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestionRequest(BaseModel):
    text: str = Field(min_length=5, max_length=10000)

    @field_validator("text")
    @classmethod
    def clean_text(cls, value):
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Enter at least 5 characters.")
        return value


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=5, max_length=10000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value):
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Enter at least 5 characters.")
        return value


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    session_id: str | None = None


class TokenMetadata(BaseModel):
    input_characters: int
    estimated_input_tokens: int


class IngestionResponse(BaseModel):
    intent: str
    risk_profile: str
    priority: int
    summary: str
    token_metadata: TokenMetadata


class AnalyzeResponse(BaseModel):
    intent: str
    risk_profile: str
    priority: int
    summary: str
    response_markdown: str
    token_metadata: TokenMetadata


class ChatResponse(BaseModel):
    session_id: str
    response_markdown: str


def estimate_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def save_ticket(message, ticket, token_count):
    save_record(
        message=message,
        intent=ticket.intent.value,
        risk_profile=ticket.risk_profile.value,
        priority=ticket.priority,
        summary=ticket.summary,
        input_tokens=token_count,
    )


@app.get("/")
def health_check():
    return {"status": "running"}


@app.post("/ingest", response_model=IngestionResponse)
def ingest(request: IngestionRequest):
    try:
        ticket = classify_message(request.text)
        token_count = estimate_tokens(request.text)

        save_ticket(request.text, ticket, token_count)

        return IngestionResponse(
            intent=ticket.intent.value,
            risk_profile=ticket.risk_profile.value,
            priority=ticket.priority,
            summary=ticket.summary,
            token_metadata=TokenMetadata(
                input_characters=len(request.text),
                estimated_input_tokens=token_count,
            ),
        )
    except ValidationError:
        raise HTTPException(
            status_code=422,
            detail="Generated output failed validation.",
        )
    except Exception as exc:
        print(f"Ingestion error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="AI processing failed. Check the terminal.",
        )


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        ticket = classify_message(request.message)
        answer = generate_response(request.message, ticket)
        token_count = estimate_tokens(request.message)

        save_ticket(request.message, ticket, token_count)

        return AnalyzeResponse(
            intent=ticket.intent.value,
            risk_profile=ticket.risk_profile.value,
            priority=ticket.priority,
            summary=ticket.summary,
            response_markdown=answer,
            token_metadata=TokenMetadata(
                input_characters=len(request.message),
                estimated_input_tokens=token_count,
            ),
        )
    except ValidationError:
        raise HTTPException(
            status_code=422,
            detail="Generated output failed validation.",
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"AI processing failed: {exc}",
        )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid4())

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        history = chat_sessions[session_id]

       
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and professional customer support assistant. "
                    "Use conversation history to answer follow-up questions. "
                    "Respond clearly using Markdown. "

                    "Be honest about your capabilities. You cannot access customer "
                    "accounts, payment records, or external support systems unless "
                    "an implemented tool provides that access. "

                    "Never claim you checked an account, verified a payment, "
                    "created a ticket, sent an email, or processed a refund unless "
                    "that action was actually completed and confirmed. "

                    "If a user reports being charged twice, apologize and explain "
                    "how to check whether both transactions completed or one is "
                    "still pending. If both charges completed, advise the user to "
                    "contact the service's official billing support. Do not promise "
                    "a refund. "

                    "Never ask for passwords, full card numbers, CVVs, or "
                    "one-time authentication codes. "

                    "Ask relevant follow-up questions and provide practical next "
                    "steps. Never invent account details or claim actions you "
                    "cannot perform."
                ),
            },
            *history,
            {"role": "user", "content": request.message},
        ]


        result = chat_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
        )

        answer = result.choices[0].message.content

        if not answer or not answer.strip():
            raise RuntimeError("The AI returned an empty response.")

        history.append(
            {"role": "user", "content": request.message}
        )
        history.append(
            {"role": "assistant", "content": answer.strip()}
        )

        # Limit memory to the latest 20 messages per session.
        chat_sessions[session_id] = history[-20:]

        return ChatResponse(
            session_id=session_id,
            response_markdown=answer.strip(),
        )

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Chat processing failed: {exc}",
        )
