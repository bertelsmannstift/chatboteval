# 0005: Annotation Export Schema

Status: Accepted

> **Depends on:** [ADR-0006](0006-annotation-tasks.md) for label definitions

## Decision

- Export annotations as CSV
- Flat format: one row per annotator response vector.
- Three task-specific export schemas, defined by downstream pipeline requirements
- HuggingFace Datasets (Arrow/Parquet) as future extension, not implemented in v1.0.

## Rationale

**Flat over nested:** One row per annotator response enables direct IAA calculation without unpacking; simpler cross-dataset joins on `record_uuid`.

**Task-specific schemas:** Tasks have different annotation units (query–chunk vs answer–context vs query–answer) and disjoint label sets. Single unified schema would require many null columns.

**CSV:** Human-readable; broadest compatibility with downstream pipelines and non-Python tooling.

> **Secondary format: HuggingFace Datasets** — Argilla v2 SDK natively supports `dataset.records.to_datasets()`. Deferred feature.

## Consequences

- Downstream pipelines must map task-specific role columns to HF-style conventions: `text` / `text_pair`.
    - retrieval: `text=query`, `text_pair=chunk`
    - grounding: `text=answer`, `text_pair=context_set`
    - generation: `text=query`, `text_pair=answer`
- Cross-dataset linking uses `record_uuid`; see Import Pipeline design doc (forthcoming PR).
- IAA calculation reads flat export directly, filtering by label column within each task CSV.
- See [ADR-0006: Annotation Tasks](0006-annotation-tasks.md) for label definitions.