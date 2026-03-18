"""Boundary schemas for canonical annotation import records."""

from pydantic import BaseModel, ConfigDict, Field

from pragmata.core.types import NonEmptyStr


class Chunk(BaseModel):
    """Single retrieved chunk within a query-response pair.

    Attributes:
        chunk_id: Unique identifier for this chunk.
        doc_id: Identifier of the source document.
        chunk_rank: 1-based rank indicating retrieval position.
        text: Content of the retrieved chunk.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: NonEmptyStr
    doc_id: NonEmptyStr
    chunk_rank: int = Field(ge=1)
    text: NonEmptyStr


class QueryResponsePair(BaseModel):
    """Canonical import record pairing a query with its response and chunks.

    Each pair fans out to records in the retrieval, grounding, and generation
    annotation datasets.

    Attributes:
        query: The user query.
        answer: The system-generated response.
        chunks: Retrieved chunks used to produce the answer (min 1).
        context_set: Identifier grouping chunks into a retrieval context.
        language: Optional ISO language code (e.g. ``"de"``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    query: NonEmptyStr
    answer: NonEmptyStr
    chunks: list[Chunk] = Field(min_length=1)
    context_set: NonEmptyStr
    language: str | None = None
