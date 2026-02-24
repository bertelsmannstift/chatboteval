# 0013: Multi-Dataset Architecture

Status: Draft


## Decision

Three separate Argilla datasets — one per annotation task:

| Dataset | Task | Record unit |
|---------|------|-------------|
| `task1_retrieval` | Retrieval quality | One record per (query, chunk) |
| `task2_grounding` | Grounding quality | One record per (query, response) |
| `task3_generation` | Generation quality | One record per (query, response) |

All three datasets are assigned to workspaces (see [Workspace & Task Distribution](../design/annotation-workspace-task-distribution.md)). Records from the same input are linked across datasets via `record_uuid` metadata.


## Rationale

**Task 1 and Task 2 have incompatible record multiplicities.** Task 1 produces K records per input (one per retrieved chunk); Task 2 produces one record per input. This difference in cardinality is the fundamental constraint that prevents sharing a dataset:

- A unified schema would require either embedding K chunks as separate fields (bounded, inflexible) or repeating the (query, response) pair K times (creates duplicate annotation burden for grounding labels).
- Argilla datasets enforce a single fixed schema — all records must have the same fields. A Task 1 record has a `chunk` field; a Task 2 record has a `context` field. These cannot coexist cleanly in one schema.

**Task 3 is separated from Task 2 to enforce annotator stratification.** Tasks 1 and 2 go to junior annotators (`grounding_junior` workspace); Task 3 goes to domain experts (`domain_experts` workspace). Keeping them in separate datasets means workspace assignment naturally controls access — annotators in `grounding_junior` never see Task 3 records, and vice versa.

**Three datasets is the minimum needed — no more.** Tasks 2 and 3 share the same record structure (`query` + `response`) and could theoretically share a schema, but their questions differ entirely and they go to different annotator groups. Separate datasets keeps schema, workspace, and task cleanly aligned.


## Alternatives Considered

**Unified schema with optional/conditional fields**

One dataset with all fields (`query`, `chunk`, `response`, `context`) and questions for all tasks. Annotators see all fields regardless of their task.

Rejected:
- Argilla v2 has no conditional question display — annotators would see irrelevant fields
- K chunk-level records would exist alongside response-level records in the same dataset, confusing annotators
- IAA computation becomes harder when record structure is heterogeneous

**Two datasets: one per annotator group**

`grounding_junior` dataset for Tasks 1+2 combined; `domain_experts` for Task 3.

Rejected:
- Task 1 produces K records per input; Task 2 produces 1. If loaded into the same dataset, the schema must accommodate both structures, reintroducing the multiplicity problem.
- Annotation UX is worse: annotators see questions for both Task 1 and Task 2 on every record, but most records are relevant only to one.

**Dynamic dataset routing at import time only**

Create a single logical dataset per annotator group and route records at import, without encoding task separation in schema.

Rejected: same problem — Argilla schemas are static. You cannot route Task 1 and Task 2 records into the same dataset without schema conflicts.


## Consequences

- Import pipeline must route each input into multiple datasets: K task1 records + 1 task2 record + 1 task3 record per input
- Export pipeline produces three separate CSVs; merged view is post-hoc (joined on `record_uuid`)
- `record_uuid` is a required metadata field on all three datasets — it is the only cross-dataset link
- IAA is computed per-dataset, not cross-dataset (each task converges independently)


## References

- [Workspace & Task Distribution](../design/annotation-workspace-task-distribution.md) — workspace assignment and dataset schemas
- [Import Pipeline](../design/annotation-import-pipeline.md) — routing logic
- [Export Pipeline](../design/annotation-export-pipeline.md) — per-dataset CSV export and merged view
- [Annotation Export Schema](../design/annotation-export-schema.md) — export schema per task
- [Annotation Protocol](../methodology/annotation-protocol.md) — task definitions and record units
- [Annotation UI Presentation](../design/annotation-presentation.md) — question wording and UI visibility contract
