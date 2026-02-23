# Packaging & Entrypoints Design

## Overview

How `chatboteval` package is structured, installed, and invoked. Covers the Python API, CLI entrypoints, optional dependency groups, and deployment modes.

See [ADR-0009: Annotation Entrypoints](../decisions/0010-annotation-entrypoints.md) for CLI scope decision and tradeoffs.

## User Workflow

```
pip install chatboteval[annotation]         # 1. install with annotation extras
make up                                     # 2. start Argilla stack (Docker Compose)
chatboteval annotation setup --local        # 3. configure workspaces, schemas, users
chatboteval annotation import <file>        # 4. load data into Argilla datasets
# annotate via Argilla web UI              # 5. label in browser
chatboteval annotation export <output_path> # 6. export annotations to CSV
```

CLI commands are thin wrappers around the Python API. All operations are also available programmatically via `chatboteval.*` functions.

## Optional Dependencies Philosophy

**Principle: no installation surprises. Users must explicitly opt in to heavy dependencies.**

The core `pip install chatboteval` installs only the minimum required to run. Feature groups are gated behind extras that users opt into deliberately:

```bash
pip install chatboteval                         # core only
pip install chatboteval[annotation]             # + Argilla SDK for annotation interface
pip install chatboteval[finetune]               # + standard fine-tuning deps
pip install chatboteval[finetune-peft]          # + PEFT (parameter-efficient fine-tuning)
etc
```
- No surprise large installs.
- No dependency conflicts for users who don't need a feature.
- Core functionality (data import, CSV export) always works without extras.

**Important:** If a feature requires an optional extra that isn't installed, the package should fail fast with a clear, actionable error message (i.e. to pip install opt deps) rather than a cryptic import error.

## Dependency Groups (planned)

| Extra | Contents | Use case |
|---|---|---|
| `annotation` | `argilla`, `datasets` | Annotation interface — import/export, Argilla SDK wrappers |
| `finetune` | `torch`, `transformers`, `pandas` | Standard supervised fine-tuning on annotated CSV |
| `finetune-peft` | `peft`, `bitsandbytes` | Parameter-efficient fine-tuning (LoRA, QLoRA) |
| `finetune-optuna` | `optuna` | Hyperparameter optimisation for fine-tuning runs |
| `dev` | `pytest`, `ruff`, `mypy` | Development tooling |
|others? | | |
|`synthetic-data-gen` | | if our generation pipeline requires running LLMs - what deps? | 

## Responsibilities

- Define `[project.optional-dependencies]` in `pyproject.toml` for each group.
- Guard optional imports with `ImportError` + helpful message at the call site (not at module import).
- CLI entrypoints registered under `[project.scripts]` in `pyproject.toml`.

## Inputs / Outputs

**Input:** User installs the package with chosen extras.

**Output:** Only the chosen feature set is available; attempting to use an uninstalled feature raises a clear error pointing to the relevant install command.

## Failure Modes / Edge Cases

- **Missing optional dep at runtime:** Raise `ImportError` with explicit install hint, not a silent no-op or cryptic traceback.
- **Version conflicts between extras:** Document known conflicts (e.g. `bitsandbytes` GPU vs CPU builds). Users installing `[finetune-peft]` on CPU-only machines should see a clear warning. Docker isolation as needed.

## References

- [Decision 0001: Argilla Annotation Platform](../decisions/0001-annotation-argilla-platform.md) — annotation-specific entrypoints and optional dependency pattern
- [Decision 0005: Annotation Export Format](../decisions/0005-annotation-export-schema.md) — CSV primary output consumed by downstream fine-tuning pipeline
- [Decision 0010: Annotation Entrypoints](../decisions/0010-annotation-entrypoints.md) — annotation CLI scope decision
- [Decision 0011: CLI Commands](../decisions/0011-infra-cli-commands.md) — full CLI reference (annotation + product commands)
- [Decision 0012: Installation & Zero-Config Setup](../decisions/0012-infra-installation-setup-ux.md) — optional extras, setup wizard UX
- `pyproject.toml` — authoritative source for defined extras
