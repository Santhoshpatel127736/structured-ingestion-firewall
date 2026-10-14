
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    ValidationError,
)
import re


class UserProfile(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    age: int = Field(ge=18, le=100)
    email: EmailStr
    pan: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")

        return value


# Test 1: Valid data
valid_data = {
    "name": "Santhosh",
    "age": 21,
    "email": "santhosh@example.com",
    "pan": "ABCDE1234F",
}

try:
    user = UserProfile(**valid_data)
    print("VALID PROFILE")
    print(user.model_dump_json(indent=2))

except ValidationError as error:
    print(error)


# Test 2: Invalid data
invalid_data = {
    "name": "S",
    "age": 15,
    "email": "wrong-email",
    "pan": "123INVALID",
}

try:
    user = UserProfile(**invalid_data)
    print(user.model_dump_json(indent=2))

except ValidationError as error:
    print("\nINVALID PROFILE REJECTED")
    print(error)
