# Design Documents

This directory contains living, decision-aligned engineering blueprints that explain how components are structured, connected, and operationalized in code.

Design documents focus on (this is guidance, not a required section template):

- **Responsibilities and boundaries** — What the component owns, and what it explicitly does not
- **Placement in the overall architecture** — How it connects to adjacent components
- **Module / package structure** — The concrete layout and internal seams
- **Public interfaces / contracts** — User-facing APIs and boundaries: inputs/outputs, invariants, and semantics
- **Key flows / control flow** — The main execution paths and state transitions
- **Extension points** — Expected customization hooks and how to add functionality safely
- **Failure modes & operational constraints** — Edge cases, degradation behavior, and operational considerations
- **Links to relevant work** — Issues/PRs for active tracking and implementation context

## Index

- [Annotation Interface](annotation-interface.md) — Human annotation workflow and Argilla integration
- [Annotation Export Schema](annotation-export-schema.md) — CSV export format and task-specific schemas
- [Annotation UI Presentation](annotation-presentation.md) — UI presentation model, field visibility, and question wording
- [Annotation E2E Flow](annotation-e2e-flow.md) — End-to-end data flow diagram
- [Annotation Export Pipeline](annotation-export-pipeline.md) — Export architecture, merged view, constraint validation
- [Annotation Import Pipeline](annotation-import-pipeline.md) — Import pipeline, source adapter, canonical record schema
- [Annotation Workspace & Task Distribution](annotation-workspace-task-distribution.md) — Workspace structure, dataset mapping, task distribution
- [Annotation User Management](annotation-user-management.md) — Account provisioning and credential management
- [Annotation Quality Assurance](annotation-quality-assurance.md) — MAMA cycle, IAA measurement, guideline iteration
- [Synthetic Test Set](synthetic-test-set.md) — Query generation, prompt variation, and response collection
- [Packaging and Invocation Surface](packaging-invocation-surface.md) — Package structure, module boundaries, and invocation bindings
