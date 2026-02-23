# 0015: Library-First Architecture

**Status:** Draft

## Decision

`chatboteval` is a **library-first** package. All business logic lives in the Python API (`src/chatboteval/`). CLI commands are thin wrappers that parse arguments and delegate to the library. The Python API is the primary interface; the CLI is a convenience layer.

## Context

The codebase has accumulated references to CLI commands (ADR-0011), optional extras packaging (ADR-0012), and annotation entrypoints (ADR-0010) without formally stating the foundational relationship between the Python API and the CLI. Two archetypes exist in the ecosystem:

- **Library-first:** Python API is the primary interface. CLI wraps the API. Users can import and call functions directly. Examples: scikit-learn, HuggingFace `transformers`, `datasets`, `evaluate`.
- **CLI-first:** CLI is the primary interface. A Python API may be exposed as a byproduct. Examples: dbt, dvc, Alembic.

This decision records which archetype `chatboteval` follows and why.

## Rationale

**Users are ML practitioners writing Python.** The primary integration path is `import chatboteval` in a notebook or script — not a shell pipeline. CLI commands are a secondary convenience for operators running batch jobs or one-off commands (e.g., `chatboteval annotate start`).

**Library-first enables composability.** Users can embed evaluation logic in their own training loops, CI pipelines, or notebooks. A CLI-first design would require subprocess calls or re-implementing logic externally.

**Testability.** Pure Python functions are straightforward to unit-test. CLI-first code couples business logic to argument parsing, making tests heavier and slower.

**Precedent.** HuggingFace `evaluate`, `datasets`, and scikit-learn all follow this pattern: rich Python API, optional CLI or scripts as thin convenience wrappers.

## Consequences

**Structural:**
- All business logic in `src/chatboteval/` (importable modules, no side effects on import)
- CLI entry points in `src/chatboteval/cli/` — each command is ≤ ~20 lines: parse args, call library function, handle output
- `pyproject.toml` `[project.scripts]` entries map to CLI wrapper functions
- Public API designed before CLI commands (API surface drives CLI shape, not vice versa)

**Interface contract:**
- Every CLI command has a 1:1 corresponding Python function that can be called directly
- CLI-only behaviour (e.g., progress bars, coloured output) is acceptable; business logic is not
- Optional extras (`pip install chatboteval[annotation]`) gate library imports, not CLI availability

**Testing:**
- Unit tests target library functions directly
- CLI tests are integration tests that verify argument parsing and output formatting only

## Alternatives Considered

| Option | Rejected Reason |
|---|---|
| CLI-first | Primary users are Python practitioners; CLI-first couples logic to argparse, hurts composability |
| API-only (no CLI) | CLI convenience is low-cost and reduces friction for operators; not a meaningful trade-off |
| CLI-only (no Python API) | Incompatible with notebook/training loop usage patterns |

## References

- HuggingFace `evaluate` library — library-first with optional CLI scripts
- scikit-learn — no CLI; pure library
- dbt — CLI-first; Python API is secondary/internal
- ADR-0010: Annotation Entrypoints
- ADR-0011: CLI Commands
- ADR-0012: Installation & Dependencies
