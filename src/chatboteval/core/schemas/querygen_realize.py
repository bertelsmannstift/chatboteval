"""Structured output contract for stage 2 query realization."""

from pydantic import BaseModel, ConfigDict, Field


class RealizedQuery(BaseModel):
    """Schema for one realized query."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(description="Return the candidate_id exactly as provided in the stage 2 input blueprint.")
    query: str = Field(description="Return the realized user query text for this candidate.")


class RealizedQueryList(BaseModel):
    """Schema for one batch of realized queries."""

    model_config = ConfigDict(extra="forbid")

    queries: list[RealizedQuery] = Field(
        description="Return a queries list containing one realized query object for each candidate in this batch."
    )
