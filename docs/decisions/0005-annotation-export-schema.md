# 0005: Annotation Export Schema

Status: Accepted

## Decision

- Export annotations as CSV
- Flat format: one row per annotator response vector. 
- Three task-specific export schemas, defined by downstream pipeline requirements 
- HuggingFace Datasets (Arrow/Parquet) as future extension, not implemented in v1.0.

## Export Schemas

Each task produces a separate CSV. Columns are task-specific; shared metadata columns are common to all three.

> **Note:** Export schemas define what downstream pipelines need. They are not a mirror of what annotators see in the annotation interface (field naming and structure may differ).

### Shared metadata columns (all tasks)

| Column | Type | Description |
|--------|------|-------------|
| `record_uuid` | string | Cross-dataset record identifier (see [Import Pipeline](../design/annotation-import-pipeline.md)) |
| `annotator_id` | string | Annotator username |
| `task` | string | Task identifier: `retrieval`, `grounding`, or `generation` |
| `language` | string | Detected language code (`de` / `en`). Optional, provided by `Publikationsbot` |
| `created_at` | datetime | Submission timestamp |

### Task 1: Retrieval export

Unit: one row per `(query, chunk, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `input_query` | string | Original user query |
| `generated_search_query` | string | LLM-rewritten query actually sent to the retriever |
| `chunk` | string | Individual retriever-level text segment (`pub_chunks` entry, pre-publication-grouping) |
| `chunk_id` | string | PGVector UUID assigned to the chunk at ingestion (`doc.id` on retrieved LangChain Document) - stable, native, not pipeline-generated |
| `doc_id` | string | Publication catalogue number (`mediennr`) linking the chunk to its source publication (`doc.metadata["doc_id"]`) |
| `chunk_rank` | int | Rank of chunk in post-rerank result set - enables retrieval metric computation (MRR@K, NDCG@K) and validation of retriever ranking against human relevance judgements |
| `can_answer` | bool | Reranker's own judgement of answerability — useful for comparing against annotator labels |
| `topically_relevant` | bool | Chunk contains information substantively related to the query |
| `evidence_sufficient` | bool | Chunk provides sufficient evidence to support answering the query |
| `misleading` | bool | Chunk could plausibly lead to an incorrect or distorted answer |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

### Task 2: Grounding export

Unit: one row per `(query, answer, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `query` | string | Input query |
| `answer` | string | System response |
| `context_set` | string | Retrieved context as seen by the model: `retrieved_docs` entries (pub_chunks grouped by publication) concatenated as a single string with `[SEP]` separators |
| `support_present` | bool | At least one answer claim is supported by evidence in the context set |
| `unsupported_claim_present` | bool | Answer contains at least one claim not supported by the context set |
| `contradicted_claim_present` | bool | Context set contains information that contradicts at least one answer claim |
| `source_cited` | bool | Answer contains at least one citation marker in the expected format |
| `fabricated_source` | bool | Answer cites at least one source not present in the retrieved context set |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

### Task 3: Generation export

Unit: one row per `(query, answer, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `query` | string | Input query |
| `answer` | string | System response |
| `proper_action` | bool | Response selects the appropriate type (answer, refusal, clarification) given the query |
| `response_on_topic` | bool | Response substantively addresses the user's request |
| `helpful` | bool | Response would enable a typical user to make progress on their task |
| `incomplete` | bool | Response fails to cover one or more required parts of the query |
| `unsafe_content` | bool | Response contains content violating safety or policy constraints |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

## Rationale

**Flat over nested:** One row per annotator response enables direct IAA calculation without unpacking; simpler cross-dataset joins on `record_uuid`.

**Task-specific schemas:** Tasks have different annotation units (query–chunk vs answer-context vs query-answer) and disjoint label sets. (Single unified schema would require many null columns; separate CSVs cleaner + safer for downstream metric computation)

**CSV:** Human-readable; broadest compatibility with downstream pipelines and non-Python tooling.

>**Secondary format: HuggingFace Datasets**
>- Argilla v2 SDK natively supports `dataset.records.to_datasets()` — zero custom serialisation required.
>- Interoperable: loads as pandas DataFrame, supports Parquet serialisation.
>- Deferred feature.

> **Alternative rejected: Nested JSON (one object per record with annotation array)**
> Harder to compute inter-annotator agreement; requires unpacking before analysis.


## Consequences

- Downstream pipelines must map task-specific role columns to HF-style conventions: `text` / `text_pair`. 
    - retrieval: `text=query`, `text_pair=chunk`
    - grounding: `text=answer`, `text_pair=context_set`
    -  generation: `text=query`, `text_pair=answer`
- Task 1 (Retrieval) requires an aggregation step before metric computation: multiple rows per query (one per chunk) must be grouped before computing per-query retrieval metrics.
- Cross-dataset linking uses `record_uuid`; see [Import Pipeline](../design/annotation-import-pipeline.md).
- IAA calculation reads flat export directly, filtering by label column within each task CSV.
- HuggingFace Datasets extension (v1.x+): Argilla SDK supports `dataset.records.to_datasets()`.
- See [ADR-0006: Annotation Tasks](0006-annotation-tasks.md) and [ADR-0007: Annotation UI Presentation](0007-annotation-presentation.md) for label definitions.
