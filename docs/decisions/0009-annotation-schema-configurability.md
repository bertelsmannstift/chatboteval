# 0009: Annotation Schema Configurability

Status: Accepted

## Decision

Annotation schemas are hardcoded for v1.0 and are not user-configurable in v1.x. Schemas are defined as Argilla `Settings` objects in a dedicated Python module, separated from setup orchestration logic. No config-file-driven schema editor.

Any future schema change is a breaking design decision requiring a new ADR and new major version, not a config layer.


## Rationale

**Argilla is code-first by design:** `Settings` objects are Python — that is the intended SDK interface. There is no built-in schema editor. Building abstraction on top of this means re-implementing what the SDK exposes cleanly, in a different format. Configurability adds complexity with no benefit.

**Schemas implement the label set assumed by the metrics taxonomy and annotation-task decisions:** making schemas user-configurable would undermine the interpretability and comparability of results across annotators and datasets (see [ADR-0002: Metrics Taxonomy](0002-eval-metrics-taxonomy.md), [ADR-0006: Annotation Tasks](0006-annotation-tasks.md)).


>## Alternatives considered
>
>**YAML/TOML config layer:** Define schemas in config files, parsed into `Settings` objects at setup time. Rejected because:
>- Requires building a config schema (schema for the schema), parser, validator, and error handling
>- Re-implements Argilla's Python SDK in a different format; leaky abstraction adds maintenance burden as Argilla's API evolves
>
>**Argilla admin UI schema editor:** Does not exist in Argilla v2. Schemas must be defined via SDK. Not a viable path without building a custom frontend (out of scope — see [ADR-0001](0001-annotation-argilla-platform.md)).
>
>**Dedicated schema module (fork-and-modify path):** Schema definitions live in a dedicated Python module (e.g. `schemas.py`), clearly separated from setup orchestration. Downstream users fork and edit the Python directly. Zero overhead, fully Pythonic, aligns with how Argilla is designed to be used. This remains the recommended extension path if schema changes are ever warranted.


## Consequences

- Changing annotation dimensions requires modifying setup code and re-creating Argilla datasets
- Schema definitions should live in a dedicated module, not inline with orchestration logic, to make the fork-and-modify path obvious
- Any schema change requires updating/reviewing the annotation-related ADRs first (metrics taxonomy + annotation tasks + presentation), then updating the code implementation
- See [ADR-0006: Annotation Tasks](0006-annotation-tasks.md) and [ADR-0007: Annotation UI Presentation](0007-annotation-presentation.md) for current schema definitions
