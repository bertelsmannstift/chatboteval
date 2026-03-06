"""Boundary schemas for annotation export records (one per task type)."""

from datetime import datetime

from chatboteval.core.schemas.base import ContractModel, Task


class AnnotationBase(ContractModel):
    record_uuid: str
    annotator_id: str
    task: Task
    language: str | None
    inserted_at: datetime
    created_at: datetime
    record_status: str


class RetrievalAnnotation(AnnotationBase):
    input_query: str
    chunk: str
    chunk_id: str
    doc_id: str
    chunk_rank: int
    topically_relevant: bool
    evidence_sufficient: bool
    misleading: bool
    notes: str = ""


class GroundingAnnotation(AnnotationBase):
    answer: str
    context_set: str
    support_present: bool
    unsupported_claim_present: bool
    contradicted_claim_present: bool
    source_cited: bool
    fabricated_source: bool
    notes: str = ""


class GenerationAnnotation(AnnotationBase):
    query: str
    answer: str
    proper_action: bool
    response_on_topic: bool
    helpful: bool
    incomplete: bool
    unsafe_content: bool
    notes: str = ""
