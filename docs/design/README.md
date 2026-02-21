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
- [Synthetic Test Set](synthetic-test-set.md) — Query generation, prompt variation, and response collection
- [Reference-Based Evaluation](eval-reference-based.md) — Supervised evaluation using human-annotated ground truth
- [Reference-Free Evaluation](eval-reference-free.md) — LLM-as-judge and heuristic evaluation without ground truth
- [Packaging & Entrypoints](packaging-entrypoints.md) — Package structure, CLI, Python API, and deployment modes
