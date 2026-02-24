# Export Pipeline

Data pipeline to export completed annotations from Argilla recoords to structured CSV files for downstream use.

## Responsibilities

**In scope:**
- Fetch submitted annotations from all three Argilla datasets
- Output one flat CSV per task (primary export)
- Produce an optional merged view joining all tasks on `record_uuid`
- Validate export schema before write
- Post-submission constraint validation (flag logical violations before metric computation)

**Out of scope:**
- Data import (see [Import Pipeline](annotation-import-pipeline.md))
- IAA calculation (consumes export output; separate concern)
- Annotation quality filtering (export all submitted records; filtering is downstream)

## Architecture

```
Argilla PostgreSQL
        │
        ├── task1_retrieval ──────────────────────────────► retrieval.csv
        │   (retrieval_grounding workspace)                    (query, chunk, chunk_id,
        │                                                    chunk_rank, labels...)
        │
        ├── task2_grounding ──────────────────────────────► grounding.csv
        │   (retrieval_grounding workspace)                    (query, answer,
        │                                                    context_set, labels...)
        │
        └── task3_generation ─────────────────────────────► generation.csv
            (generation workspace)                      (query, answer, labels...)
                    │
                    │  
                    ▼
           Merged view (join on record_uuid)
           ─ Task 1 aggregated per query before join
           ─ NULLs for missing cross-task annotations
```
>tbc on api / cli wrapper wording:

**Entry point:** `chatboteval export <output_dir>` (CLI) or `chatboteval.export(...)` (Python API)

## Inputs

Three Argilla datasets, accessed via Argilla SDK. Filter: `status == "submitted"` only (exclude draft, discarded). 

> NB: Workspace names are deployment configuration, not fixed architecture; current defaults  reflect one possible annotator stratification (see [Workspace & Task Distribution](annotation-workspace-task-distribution.md)).

| Dataset | Workspace | Records |
|---------|-----------|---------|
| `task1_retrieval` | `retrieval_grounding` | One record per query–chunk pair |
| `task2_grounding` | `retrieval_grounding` | One record per query–answer pair |
| `task3_generation` | `generation` | One record per query–answer pair |

## Export Format & Schema

>NB: seperate PR will add separate `schema/` layer (add ref when done), this pydantic model be the SSOT.

> **Depends on:** [Annotation Protocol](../methodology/annotation-protocol.md) for label definitions

Export as CSV — flat format, one row per annotator response vector. Three task-specific CSVs with disjoint label columns and shared metadata.

> Export schemas define what downstream pipelines need. They are not a mirror of what annotators see in the annotation interface (field naming and structure may differ).

### Shared metadata columns (all tasks)

| Column | Type | Description |
|--------|------|-------------|
| `record_uuid` | string | Cross-dataset record identifier (see [Import Pipeline](annotation-import-pipeline.md)) |
| `annotator_id` | string | Annotator username |
| `task` | string | Task identifier: `retrieval`, `grounding`, or `generation` |
| `language` | string | Language code (e.g. `de`, `en`) |
| `created_at` | datetime | Submission timestamp |

### Task 1: Retrieval — `retrieval.csv`

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

### Task 2: Grounding — `grounding.csv`

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

### Task 3: Generation — `generation.csv`

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

### Merged view (optional)

Joins all three task CSVs on `record_uuid`. Task 1 requires an aggregation step first — multiple rows per query (one per chunk) must be reduced to a per-query summary before joining.

```
record_uuid │ query │ answer │ context_set
│ [task1 aggregated] topically_relevant_any │ evidence_sufficient_any │ misleading_any
│ [task2] support_present │ unsupported_claim_present │ contradicted_claim_present
│          source_cited │ fabricated_source
│ [task3] proper_action │ response_on_topic │ helpful │ incomplete │ unsafe_content
│ [meta] annotator_id_t1 │ annotator_id_t2 │ annotator_id_t3 │ ...
```

NULLs for any task where no submitted annotation exists for the record.

## Constraint Validation

The [Annotation Protocol](../methodology/annotation-protocol.md) defines logical consistency constraints between labels (e.g. `evidence_sufficient = 1 ⇒ topically_relevant = 1`). The export pipeline validates these before metric computation and flags or rejects violating rows. See [Annotation Protocol](../methodology/annotation-protocol.md) for the full constraint list.

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
- Cross-dataset linking uses `record_uuid`; see [Import Pipeline](annotation-import-pipeline.md).
- IAA calculation reads flat export directly, filtering by label column within each task CSV.
- See [Annotation Protocol](../methodology/annotation-protocol.md) for label definitions.

## Failure Modes

**Missing `record_uuid`:**
- Records without `record_uuid` cannot be joined across datasets
- Log warning; include in flat export, exclude from merged view

**Partial annotations:**
- A record may have annotations in some tasks but not others
- Include in flat export; include in merged view with NULLs for missing tasks

**Schema mismatch:**
- Validate expected column names and types before write
- Fail with diff of expected vs actual schema

**Argilla connection failure:**
- Fail with clear error including API URL
- No partial output written (atomic: write only on success)

## References

- [Annotation Protocol](../methodology/annotation-protocol.md) — Label definitions, units of annotation, and logical constraints
- [Import Pipeline](annotation-import-pipeline.md) — Upstream data flow
- Quality Assurance (forthcoming) — IAA calculation consumes export output
