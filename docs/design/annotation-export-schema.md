# Annotation Export Schema

> **Depends on:** [Annotation Protocol](../methodology/annotation-protocol.md) for label definitions


## Format

- Export annotations as CSV
- Flat format: one row per annotator response vector
- Three task-specific export schemas, defined by downstream pipeline requirements
- HuggingFace Datasets (Arrow/Parquet) as future extension — deferred


## Export Schemas

Each task produces a separate CSV. Columns are task-specific; shared metadata columns are common to all three.

> **Note:** Export schemas define what downstream pipelines need. They are not a mirror of what annotators see in the annotation interface (field naming and structure may differ).

> **SSOT:** [Annotation Protocol](../methodology/annotation-protocol.md) is the single source of truth for label semantics. In case of drift, the protocol takes precedence.

### Shared metadata columns (all tasks)

| Column | Type | Description |
|--------|------|-------------|
| `record_uuid` | string | Cross-dataset record identifier (see Import Pipeline design doc) |
| `annotator_id` | string | Annotator username |
| `task` | string | Task identifier: `retrieval`, `grounding`, or `generation` |
| `language` | string | Language code (e.g. `de`, `en`) |
| `created_at` | datetime | Submission timestamp |

### Task 1: Retrieval export

Unit: one row per `(query, chunk, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `input_query` | string | Original user query as sent to the retriever |
| `chunk` | string | Retriever-level text segment |
| `chunk_id` | string | ID assigned to the chunk at ingestion |
| `doc_id` | string | Document ID linking the chunk to its source document |
| `chunk_rank` | int | Rank of chunk in (post-rerank) result set |
| `topically_relevant` | bool | Chunk contains information substantively related to the query |
| `evidence_sufficient` | bool | Chunk provides sufficient evidence to support answering the query |
| `misleading` | bool | Chunk could plausibly lead to an incorrect or distorted answer |
| `notes` | string | Optional annotator notes |
| *(shared metadata)* | | |

### Task 2: Grounding export

Unit: one row per `(answer, context_set, annotator)` triple.

| Column | Type | Description |
|--------|------|-------------|
| `answer` | string | System response |
| `context_set` | string | Full retrieved context as injected in the prompt, concatenated as a single string with `[CTX_SEP]` separators |
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


## Schema Design Notes

**Flat over nested:** One row per annotator response enables direct IAA calculation without unpacking; simpler cross-dataset joins on `record_uuid`.

**Task-specific schemas:** Tasks have different annotation units (query–chunk vs answer–context vs query–answer) and disjoint label sets. Single unified schema would require many null columns.

**CSV:** Human-readable; broadest compatibility with downstream pipelines and non-Python tooling.

> **Secondary format: HuggingFace Datasets** — Argilla v2 SDK natively supports `dataset.records.to_datasets()`. Deferred feature.

> **Alternative rejected: Nested JSON (one object per record with annotation array)** — Harder to compute inter-annotator agreement; requires unpacking before analysis.

## Downstream Implications

- Downstream pipelines must map task-specific role columns to HF-style conventions: `text` / `text_pair`.
    - retrieval: `text=query`, `text_pair=chunk`
    - grounding: `text=answer`, `text_pair=context_set`
    - generation: `text=query`, `text_pair=answer`
- Cross-dataset linking uses `record_uuid`; see Import Pipeline design doc.
- IAA calculation reads flat export directly, filtering by label column within each task CSV.
- See [Annotation Protocol](../methodology/annotation-protocol.md) for label definitions.
