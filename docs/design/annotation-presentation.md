# Annotation UI Presentation

> **Depends on:** [ADR-0006](../decisions/0006-annotation-tasks.md) for label semantics and question wording alignment

## Presentation Model

Task isolation across annotator groups is achieved via Argilla workspace assignment: each workspace exposes only its assigned datasets, so different groups can be given different subsets of the three tasks.

All labels for a task are presented simultaneously (joint labelling). For each task, the annotator UI provides:

- **Primary content** (always visible): the unit being labelled
- **Supporting context** (secondary field, positioned after primary content): additional content to aid consistency without biasing the primary judgement
- **Question descriptions**: short edge-case guidance embedded per question via Argilla's `description` parameter
- **Dataset guidelines**: full annotation instructions accessible at the top of each dataset

Full visibility contract, annotator-facing question wording (EN/DE), and optional fields specification: [Annotation Interface](annotation-interface.md).

## Design Rationale

**Joint labelling:** Argilla v2 does not support conditional question logic or grouping headers. Custom progressive disclosure would require building a frontend, which is out of scope. Joint labelling is the accepted limitation.

**Visibility contract:** Primary content is the minimal unit needed for the labelling task. Supporting context is included to aid consistency but kept secondary to reduce anchoring bias on the primary judgement.

**English as default display language:** English is both the design-time source of truth and the default annotator-facing display language. German translations are available as an optional display language.

## Implications

- Supporting context fields (`answer` for Task 1; `query` for Task 2; `retrieved_passages` for Task 3) must be included in the Argilla field configuration, positioned after primary content fields
- Workspace and annotator group assignment (who sees which dataset) is an operational decision
- Three Argilla datasets required: `task1_retrieval`, `task2_grounding`, `task3_generation` — incompatible field structures prevent a unified schema
- Export schema ([Annotation Export Schema](annotation-export-schema.md)) must include one binary field per label and the optional notes field
- Schema can be revised after the first annotation iteration based on IAA results and annotator feedback
