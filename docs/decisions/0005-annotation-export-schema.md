# 0005: Annotation Export Schema

Status: Accepted

> **Depends on:** [ADR-0006](0006-annotation-tasks.md) for label definitions

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
| `language` | string | Detected language code (`de` / `en`) |
| `created_at` | datetime | Submission timestamp |

### Task 1: Retrieval export

Unit: one row per `(query, chunk, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `input_query` | string | Input query as sent to the retriever |
| `generated_search_query` | string | LLM-rewritten query actually sent to the retriever |
| `chunk` | string | Retriever-level text segment |
| `chunk_id` | string | ID assigned to the chunk at ingestion |
| `doc_id` | string | Document ID linking the chunk to its source document |
| `chunk_rank` | int | Rank of chunk in (post-rerank) result set |
| `topically_relevant` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `evidence_sufficient` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `misleading` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

### Task 2: Grounding export

Unit: one row per `(answer, context_set, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `answer` | string | System response |
| `context_set` | string | Full retrieved context as injected in the prompt, concatenated as a single string with [CTX_SEP] separators |
| `support_present` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `unsupported_claim_present` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `contradicted_claim_present` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `source_cited` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `fabricated_source` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

### Task 3: Generation export

Unit: one row per `(query, answer, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `query` | string | Input query |
| `answer` | string | System response |
| `proper_action` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `response_on_topic` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `helpful` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `incomplete` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
| `unsafe_content` | bool | *[ADR-0006](0006-annotation-tasks.md)* |
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
- Cross-dataset linking uses `record_uuid`; see [Import Pipeline](../design/annotation-import-pipeline.md).
- IAA calculation reads flat export directly, filtering by label column within each task CSV.
- See [ADR-0006: Annotation Tasks](0006-annotation-tasks.md) for label definitions.
