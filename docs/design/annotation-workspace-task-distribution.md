# Workspace & Task Distribution

Configuration of Argilla workspaces and annotation task assignment for stratified annotation.

## Responsibilities

**In scope:**
- Define workspace structure (which datasets belong to which workspace)
- Assign annotators to workspaces so each group sees only their schema
- Configure `TaskDistribution` to control record assignment and overlap for IAA

**Out of scope:**
- User account creation (see [User Management](annotation-user-management.md))
- Annotation task and label definition (see [Annotation Protocol](../methodology/annotation-protocol.md))

## Workspace Structure

```
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│  retrieval_grounding workspace      │   │  generation workspace        │
├──────────────────────────────────┤   ├──────────────────────────────────┤
│  task1_retrieval                 │   │  task3_generation                │
│  task2_grounding                 │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘
         ↑                                          ↑
  Junior annotators                       Domain expert annotators
  (retrieval + grounding)                   (generation quality)
```

Workspace names describe the tasks they contain, not the annotator roles assigned to them. Names and dataset-to-workspace mapping are deployment configuration — the architecture requires only that each dataset belongs to exactly one workspace.

Two workspaces map to the two annotator groups:

| Workspace | Assigned annotators | Tasks |
|---|---|---|
| `generation` | Domain expert annotators | Task 3: `proper_action`, `response_on_topic`, `helpful`, `incomplete`, `unsafe_content` |
| `retrieval_grounding` | Junior annotators | Task 1: `topically_relevant`, `evidence_sufficient`, `misleading`; Task 2: `support_present`, `unsupported_claim_present`, `contradicted_claim_present`, `source_cited`, `fabricated_source` |

Three Argilla datasets are required — Tasks 1 and 2 cannot share a dataset because their field structures are incompatible (per-chunk vs. per-answer-context unit):

| Dataset | Workspace | Task | Fields shown to annotator |
|---|---|---|---|
| `task1_retrieval` | `retrieval_grounding` | Task 1: Retrieval | `query`, `chunk` (primary); `answer` (supporting) |
| `task2_grounding` | `retrieval_grounding` | Task 2: Grounding | `answer`, `context_set` (primary); `query` (supporting) |
| `task3_generation` | `generation` | Task 3: Generation | `query`, `answer` (primary); `retrieved_passages` (supporting) |

Each annotator is assigned to exactly one workspace. Argilla's workspace isolation ensures annotators only see records and questions for their assigned tasks.

## Dataset Implementation

Each dataset is configured via an Argilla `Settings` object defining fields, questions, and metadata. Schemas are hardcoded for v1.0 — see [ADR-0009](../decisions/0009-annotation-schema-configurability.md).

Field order follows the visibility contract (primary content first, supporting context last) — see [Annotation UI Presentation](annotation-presentation.md). Full question wording (EN/DE) and field definitions: [Annotation Interface](annotation-interface.md). Full `rg.Settings` schemas with German question titles: see corresponding GitHub Issue.

### Logical constraint enforcement

The [Annotation Protocol](../methodology/annotation-protocol.md) defines consistency constraints between labels (e.g., `evidence_sufficient = 1 ⇒ topically_relevant = 1`). Argilla v2 does not support conditional question disabling in the standard UI. Enforcement strategy:

- **Guidelines**: constraint rules documented in the annotator-facing guidelines shown at the top of each dataset
- **Post-submission validation**: export pipeline rejects or flags constraint violations before metric computation (see [Export Pipeline](annotation-export-pipeline.md))

## Task Distribution

Argilla's `TaskDistribution` controls how many annotators are assigned per record and when a record is considered complete.

**Key parameters:**

- `min_submitted` — minimum number of submitted annotations before a record is marked complete and removed from the queue. Set to match desired annotator overlap.
- For IAA measurement: overlap should cover all annotators for the MAMA cycle dataset, then drop to a configurable overlap ratio for scale (e.g., 20% of records annotated by 2+ annotators).

**MAMA cycle (first iteration):**
- Full overlap: all annotators assigned to all records (`min_submitted` = number of annotators)
- Enables IAA measurement across all dimensions

**Scale configuration (post-MAMA):**
- `min_submitted = 1` for throughput; selective overlap assignment for ongoing IAA sampling
- Overlap ratio TBD based on MAMA iteration learnings

## Failure Modes

**Annotator assigned to wrong workspace:**
- Annotator sees wrong schema questions
- Mitigation: validate workspace assignments after setup; spot-check in Argilla UI

**`min_submitted` misconfigured:**
- Too low: records complete before sufficient overlap for IAA
- Too high: records never complete if fewer annotators than threshold
- Mitigation: verify `min_submitted` ≤ number of annotators in workspace before starting iteration

**Uneven task assignment:**
- Argilla assigns tasks to annotators in round-robin order; may not be perfectly balanced across annotators
- Mitigation: monitor completion rates per annotator in Argilla admin view

## References

- [User Management](annotation-user-management.md) — Account creation and workspace assignment
- Quality Assurance (forthcoming) — MAMA cycle overlap configuration and IAA measurement
- [Export Pipeline](annotation-export-pipeline.md) — post-submission constraint validation
- [Annotation Protocol](../methodology/annotation-protocol.md) — Label definitions and logical constraints
- [Annotation UI Presentation](annotation-presentation.md) — Joint labelling and visibility contract rationale
- [Decision 0008: Authentication](../decisions/0008-annotation-interface-auth.md) — Role-based access control
- [Decision 0009: Schema Configurability](../decisions/0009-annotation-schema-configurability.md) — Hardcoded schema rationale
- [Decision 0010: Multi-Dataset Architecture](../decisions/0010-annotation-multi-dataset-architecture.md) — rationale for three datasets vs. unified schema
- Argilla TaskDistribution docs: https://docs.argilla.io/latest/
