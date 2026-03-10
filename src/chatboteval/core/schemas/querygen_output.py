"""Output contract for synthetic query generation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt, field_validator


class SyntheticQueryRow(BaseModel):
    """Schema for one synthetic query CSV row."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    query: str
    domain: str | None = None
    role: str | None = None
    language: str | None = None
    topic: str | None = None
    intent: str | None = None
    task: str | None = None
    difficulty: str | None = None
    format: str | None = None

    @field_validator("query_id", "query")
    @classmethod
    def required_strings_non_empty(cls, v: str) -> str:
        """Reject blank required string fields."""
        v = v.strip()
        if not v:
            raise ValueError("value must be a non-empty string")
        return v

    @field_validator(
        "domain",
        "role",
        "language",
        "topic",
        "intent",
        "task",
        "difficulty",
        "format",
    )
    @classmethod
    def optional_strings_non_empty_if_present(cls, v: str | None) -> str | None:
        """Reject blank optional string fields when provided."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("optional metadata values must be non-empty strings")
        return v


class SyntheticQueriesMeta(BaseModel):
    """Schema for synthetic query dataset-level metadata."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: datetime
    n_queries: PositiveInt
    model_provider: str
    model: str

    @field_validator("run_id", "model_provider", "model")
    @classmethod
    def metadata_strings_non_empty(cls, v: str) -> str:
        """Reject blank metadata string fields."""
        v = v.strip()
        if not v:
            raise ValueError("value must be a non-empty string")
        return v