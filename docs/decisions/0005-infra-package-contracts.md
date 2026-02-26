# 0005: Package Contract Layer

Status: Draft


## Decision

`chatboteval` defines a shared contract layer inside `core/` — a set of canonical types, schemas, path conventions, and config structures that all internal modules depend on. This layer has no internal package dependencies and is the stable foundation that `api/` and `cli/` build on.

The contract layer covers:

1. **Domain types** — shared data structures (QueryResponsePair, Annotation, EvalResult, ModelArtifact)
2. **Data schemas** — input/output column contracts (annotation CSV, RAG input format)
3. **File path conventions** — canonical locations for data, models, and outputs
4. **Core config schema** — structure of `~/.chatboteval/config.yaml` and project-level config
5. **Model spec** — canonical structure of a trained auto-labeller artifact on disk

All contracts are defined using **Pydantic** models. Config uses Pydantic Settings. No business logic lives in the contract layer — types and schemas only.


## Rationale

**Prevents inter-module drift:** Without a shared type vocabulary, `core/annotation`, `core/eval`, and `core/train` each define their own representations of the same concepts (annotation, label, result). Contracts make the shared language explicit.

**Enables type-safe data flow:** Pydantic models enforce structure at module boundaries. Data that passes between pipeline stages is validated, not assumed.

**Stable public API foundation:** The public API (`api/`) can re-export contract types directly. Users get typed interfaces without knowing internal structure.

**Dependency direction:** `core/ ← api/ ← cli/`. The contract definitions within `core/` have zero internal imports.


## Consequences

- Contract definitions live in `src/chatboteval/core/` (`types.py`, `paths.py`, `settings.py`, `schema/`) as the bottom of the dependency graph
- All inter-module data exchange uses contract types, not raw dicts
- Schema changes to contracts are breaking changes — require explicit versioning consideration
- Pydantic becomes a core dependency (not optional)


## References

- [ADR-0007: Packaging and Invocation Surface](0007-packaging-invocation-surface.md) — dependency direction (`cli → api → core`)
- [Package Contracts Design](../design/infra-package-contracts.md) — detailed scaffold for each contract area
