# 0005: Contract Layer Tooling

Status: Draft

## Decision

The `core/` contract layer uses the following tooling choices:

**Pydantic for all contract definitions** — domain types, data schemas, and config (via Pydantic Settings). Pydantic is a core dependency.

**Rationale:** A frozen Pydantic model is a dataclass with validation built in — same `frozen=True`, same slot-like behaviour, same typing. The marginal runtime cost is negligible, and you get free serialisation (`model_dump_json()`/`model_dump()`), schema generation, and consistent validation without maintaining two paradigms. Using dataclasses for some things and Pydantic for others means everyone has to remember which is which and you lose the uniform serialisation interface. For a project this size, one tool everywhere is simpler than a conceptual split with no clear payoff.

**Contract types over raw dicts** for all inter-module data exchange. Schema changes are breaking changes.

**No business logic in the contract layer** — types, schemas, and config only. `core/` is the bottom of the dependency graph with zero internal imports.

**Dependency direction:** `core/ ← api/ ← cli/` (per [ADR-0007](0007-packaging-invocation-surface.md)). `api/` re-exports contract types directly so users get typed interfaces without knowing internal structure.

**`StrEnum` for controlled vocabularies** — `Task` and other fixed enumerations. The vocabulary (`retrieval`/`grounding`/`generation`) is stable across all docs. Catches typos at import time, enables IDE autocomplete, centralises renaming.

**CSV for all data exchange.** The `context_set` column uses a JSON-serialised array. One format everywhere; the column is machine-consumed so readability is not a concern.

**`UUID` for record identifiers** — `record_uuid` fields are typed as `UUID`, not `str`. These are Argilla record UUIDs and should carry the correct type.

**Frozen domain types** — all domain types use `frozen=True`. These are data records with all fields known at construction time. Frozen types prevent accidental mutation mid-pipeline, are hashable (usable in sets/dicts for deduplication), and enforce data integrity.

**Annotation type inheritance** — `AnnotationBase` with shared metadata fields; task-specific types inherit and add labels. 7 shared fields across 3 types is enough duplication to warrant one level of inheritance.

**No per-file schema versioning.** Schema version is implicit from the package version (contract type changes → package version bump). Pydantic validation at load time is the version mismatch signal for CSV files.


> ## Alternatives considered
>
> **Dataclasses for internal types, Pydantic at I/O boundaries:** Would reduce the Pydantic surface area. Rejected — adds a conceptual split (which types are which?) without meaningful performance or complexity benefit. Frozen Pydantic models and frozen dataclasses have near-identical ergonomics.
>
> **TOML/JSON for config:** Rejected — Pydantic Settings handles YAML, env vars, and CLI flags with a single model definition. TOML/JSON would require a separate parser and lose the unified precedence chain.


## Consequences

- Pydantic becomes a core dependency (already required for Argilla integration)
- All contributors work with one modelling paradigm — lower cognitive overhead
- Schema changes in `core/` are breaking changes requiring version bumps
- `core/` must remain free of business logic to preserve its role as dependency root