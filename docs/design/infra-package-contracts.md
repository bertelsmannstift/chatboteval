# Package Contracts Design

## Purpose

Scaffolds the contract layer for `chatboteval` — canonical schemas, path conventions, and config structures that all internal modules depend on. Each section describes patterns to be followed during implementation; concrete schemas are defined in tool-specific issue specs and code PRs.

Tooling choices underpinning this layer (Pydantic @ boundaries, dataclasses for runtime types, dependency dir, CSV interchange) are captured in [ADR-0005](../decisions/0005-contract-layer-tooling.md).


---

## Contract scaffold

```
src/chatboteval/
├── core/
│   ├── schemas/                   # Boundary schemas (Pydantic SSOT)
│   │   ├── __init__.py
│   │   ├── base.py                # Shared StrEnums and common types
│   │   ├── csv_io.py              # CSV serialisation helpers
│   │   └── <tool>_*.py            # e.g. querygen_input, querygen_output,
│   │                              #      querygen_plan, querygen_realize
│   ├── types/                     # Runtime types (frozen dataclasses)
│   │   └── __init__.py
│   ├── settings/
│   │   ├── settings_base.py       # ResolvableSettings base, secrets helpers
│   │   └── <tool>_settings.py
│   └── paths/                     # Workspace path resolution
│       ├── paths.py               # WorkspacePaths (shared spine)
│       └── <tool>_paths.py        # Tool-specific path bundles
├── api/
│   └── <tool>.py                  # Entrypoint: resolve(), path init
└── cli/
    └── commands/

<base_dir>/                        # defaults to cwd
  <tool>/
    runs/
      <run_id>/                    # per-run artefacts

~/.chatboteval/
  config.yaml                      # user config (optional, not auto-discovered yet)
```

Dependency direction: `core/ ← api/ ← cli/` (per [ADR-0007](../decisions/0007-packaging-invocation-surface.md)).

`core/schemas/` is dependency root — no internal imports. Tool implementations and `api/` import from it; it imports from nothing.


---

## 1. Boundary Schemas

Pydantic models in `core/schemas/` — the single source of truth for all inter-module contracts. CSV/JSON are downstream serialisations of these models, not parallel definitions.

Per-tool schemas are organised by tool prefix (e.g. `querygen_input.py`, `querygen_output.py`, `querygen_plan.py`, `querygen_realize.py`).

All schema models are frozen by default (`model_config = ConfigDict(frozen=True)`). Schema changes are breaking changes requiring version bumps.

### LLM-boundary schemas

Schemas that double as LLM structured output contracts follow additional conventions:

- All fields include `Field(description=...)` — these serve as written instructions to the model
- A thin wrapper model (e.g. `QueryBlueprintList`) provides the top-level object for structured output
- Cross-stage join keys (e.g. `candidate_id`) couple related schemas; changes to join keys are breaking changes across all schemas that share them


---

## 2. Serialisation

> On-disk formats — downstream of the Pydantic schemas above.

`core/schemas/csv_io.py` handles tabular serialisation/deserialisation. This section documents only the differences between the in-memory schema and the on-disk representation.

### Tabular data (CSV)

CSV is the interchange format for all tabular data. One format everywhere.

Conventions:

- 1 CSV per record type, flat and string-typed
- List fields serialised as JSON arrays (e.g. `context_set`)
- Enums serialised as string values
- UUIDs and datetimes serialised as strings (ISO 8601 for dates)
- Column order derived from Pydantic model field definition order (model_fields.keys())

Serialisation/deserialisation logic lives in dedicated helpers, not on the schema models themselves.

### Run metadata (JSON sidecar)

Non-tabular, run-level metadata (e.g. `run_id`, `created_at`, model info) is written as a JSON sidecar alongside the CSV (e.g. `synthetic_queries.meta.json`). This avoids repeating per-run fields as columns in every CSV row.


---

## 3. Runtime Types

Frozen dataclasses for internal ergonomic types that don't need Pydantic validation. These are not contracts — they're implementation conveniences free to evolve without triggering breaking-change discipline.

General-purpose runtime types live in `core/types/`. Domain-specific frozen dataclasses (e.g. path bundles) live alongside their domain module (e.g. `core/paths/`).

Examples: run result objects (run_id, output paths, record counts), path bundles. These may reference schema models but don't duplicate field definitions.


---

## 4. File Path Conventions

Canonical locations for data artefacts produced and consumed by the pipeline (not source code layout — see [ADR-0007](../decisions/0007-packaging-invocation-surface.md) for package structure).

```
<base_dir>/                       # defaults to cwd; overridable
  <tool>/
    runs/
      <run_id>/                   # per-run artefacts (CSV + JSON sidecar)

~/.chatboteval/
  config.yaml                     # user config (optional — see Section 5)
```

A `WorkspacePaths` frozen dataclass in `core/paths/paths.py` exposes the shared workspace spine. Initialised once at the API/CLI entrypoint and threaded down — consuming code uses the resolver rather than constructing paths directly (single resolution point, easy to override in tests).

Key API:

- `WorkspacePaths.from_base_dir(path)` — normalises and resolves the workspace root
- `tool_root(tool)` — returns `base_dir / tool`
- `run_root(tool, run_id)` — returns `base_dir / tool / runs / run_id`
- `under_base(path)` — resolves a path relative to `base_dir`
- `coerce_path(str | Path)` — standalone helper for input normalisation

Tool-specific path bundles (e.g. `QueryGenRunPaths` in `core/paths/querygen_paths.py`) are optional frozen dataclasses that pre-resolve all artefact paths for a run. A `resolve_<tool>_paths()` function constructs the bundle from `WorkspacePaths`. Tools with simple output structures can use `WorkspacePaths` directly.


---

## 5. Config & Settings

### Global config

Optional user config at `~/.chatboteval/config.yaml`. Built-in defaults mean the tool works with zero config — the file is only needed when overriding defaults (e.g. custom output paths).

Config file auto-discovery is deferred — callers must pass the config path explicitly for now.

Full precedence chain (highest to lowest):

```
CLI flags / API call overrides          ← one-off overrides
        ↓
Environment variables
        ↓
Config file (passed explicitly)
        ↓
Built-in defaults
```

### Secrets

Secrets (API keys, credentials) are resolved separately from settings — they do not appear in config files or settings models. `core/settings/settings_base.py` provides a `resolve_provider_api_key()` helper that reads API keys from well-known environment variables (e.g. `MISTRAL_API_KEY`, `OPENAI_API_KEY`). A `MissingSecretError` is raised when the required key is not set.

### Tool-specific settings

Each tool has a settings module in `core/settings/` containing:

- **Semantically scoped settings classes** for logical groupings (e.g. `LlmSettings` for model config)
- **A `RunSettings` class** that bundles the above plus run-level fields and inherits from `ResolvableSettings`

`ResolvableSettings` in `core/settings/settings_base.py` is a Pydantic `BaseModel` (not `BaseSettings`) providing a `resolve()` classmethod that handles the precedence merge. Merge uses an `UNSET` sentinel to distinguish "not provided" from explicit values, with `deep_merge()` for recursive dict merging and `prune_unset()` to strip sentinel values. Each tool's `RunSettings` inherits this — no reimplementation per tool.

The API entrypoint (`api/<tool>.py`) calls `RunSettings.resolve()` with caller-supplied overrides and config, then passes the resolved settings to the implementation layer.


---

## References

- [ADR-0005: Contract Layer Tooling](../decisions/0005-contract-layer-tooling.md) — tooling choices underpinning this layer
- [ADR-0007: Packaging and Invocation Surface](../decisions/0007-packaging-invocation-surface.md) — module dependency direction
