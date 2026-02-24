# Export Pipeline

Script to export completed annotations from Argilla to structured CSV files for downstream use.

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
        │   (grounding_junior workspace)                    (query, chunk, chunk_id,
        │                                                    chunk_rank, labels...)
        │
        ├── task2_grounding ──────────────────────────────► grounding.csv
        │   (grounding_junior workspace)                    (query, answer,
        │                                                    context_set, labels...)
        │
        └── task3_generation ─────────────────────────────► generation.csv
            (domain_experts workspace)                      (query, answer, labels...)
                    │
                    │  (optional)
                    ▼
           Merged view (join on record_uuid)
           ─ Task 1 aggregated per query before join
           ─ NULLs for missing cross-task annotations
```

**Entry point:** `chatboteval export <output_dir>` (CLI) or `chatboteval.export(...)` (Python API)

## Inputs

Three Argilla datasets, accessed via Argilla SDK. Filter: `status == "submitted"` only (exclude draft, discarded).

| Dataset | Workspace | Records |
|---------|-----------|---------|
| `task1_retrieval` | `grounding_junior` | One record per query–chunk pair |
| `task2_grounding` | `grounding_junior` | One record per query–answer pair |
| `task3_generation` | `domain_experts` | One record per query–answer pair |

## Outputs

Three task-specific CSVs, one row per annotator response vector. Format rationale: [Annotation Export Schema](annotation-export-schema.md).

Full column definitions (shared metadata + per-task schemas): [Annotation Export Schema](annotation-export-schema.md).

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

- [Annotation Export Schema](annotation-export-schema.md) — CSV/flat format rationale and column definitions
- [Annotation Protocol](../methodology/annotation-protocol.md) — Label definitions, units of annotation, and logical constraints
- [Import Pipeline](annotation-import-pipeline.md) — Upstream data flow
- [Quality Assurance](annotation-quality-assurance.md) — IAA calculation consumes export output
