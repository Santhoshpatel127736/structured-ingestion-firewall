
import tiktoken

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator

from structured_output import classify_message
from database import create_database, save_record


# Create the database and its tables
create_database()


app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    version="1.0.0",
)


class IngestionRequest(BaseModel):
    text: str = Field(min_length=5, max_length=10000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 5:
            raise ValueError("Please enter at least 5 characters.")

        return value


class TokenMetadata(BaseModel):
    input_characters: int
    estimated_input_tokens: int = Field(ge=0)


class IngestionResponse(BaseModel):
    intent: str
    risk_profile: str
    priority: int = Field(ge=1, le=5)
    summary: str
    token_metadata: TokenMetadata


def estimate_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


@app.get("/")
def health_check():
    return {"status": "running"}


@app.post("/ingest", response_model=IngestionResponse)
def ingest(request: IngestionRequest):
    try:
        # Classify the user's message using the LLM
        ticket = classify_message(request.text)

        # Estimate the number of input tokens
        token_count = estimate_tokens(request.text)

        # Save the result to the database
        save_record(
            message=request.text,
            intent=ticket.intent.value,
            risk_profile=ticket.risk_profile.value,
            priority=ticket.priority,
            summary=ticket.summary,
            input_tokens=token_count,
        )

        # Return the structured response
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

    except Exception:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="LLM processing failed. Please retry later.",
        )
