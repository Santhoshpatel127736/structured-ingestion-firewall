from structured_output import client, SupportTicket


def generate_response(message: str, ticket: SupportTicket) -> str:
    result = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        response_model=str,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful customer support assistant. "
                    "Write a clear, polite response in Markdown. "
                    "Do not invent facts or claim a refund was processed. "
                    "Explain reasonable next steps."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Customer message: {message}\n"
                    f"Classification: {ticket.model_dump_json()}\n"
                    "Write a helpful reply to the customer."
                ),
            },
        ],
    )

    if not result or not result.strip():
        raise RuntimeError("The AI returned an empty response.")

    return result.strip()