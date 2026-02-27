# 0005: Contract Layer Tooling

Status: Draft

## Decision

The `core/` contract layer uses following tooling choices:

**Pydantic for all contract definitions** — domain types, data schemas, and config (via Pydantic Settings). Pydantic is a core dependency.

**Rationale:** A frozen Pydantic model is a dataclass with validation built in. Marginal runtime cost is negligible, and gives free serialisation (`model_dump_json()`/`model_dump()`), schema generation, and consistent validation without maintaining 2 paradigms.

**Contract types over raw dicts** for all inter-module data exchange. Schema changes are breaking changes.

**No business logic in the contract layer** - types, schemas, and config only. `core/` is the bottom of the dependency graph w/ zero internal imports.

**Dependency direction:** `core/ ← api/ ← cli/` (per [ADR-0007](0007-packaging-invocation-surface.md)). `api/` re-exports contract types directly so users get typed interfaces without knowing internal structure.

**`StrEnum` for controlled vocabularies** — `Task` and other fixed enumerations. The vocabulary (`retrieval`/`grounding`/`generation`) is stable across all docs. (Catches typos at import time, enables ide autocomplete, centralises renaming)

**CSV for all data exchange.** ( -> the `context_set` column uses JSON-serialised array). One format everywhere; the column is machine-consumed so readability is not a concern.

**Frozen domain types** — immutability by default; prevents accidental mutation mid-pipeline.

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