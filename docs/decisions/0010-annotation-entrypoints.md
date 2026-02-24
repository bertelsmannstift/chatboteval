# 0010: Annotation Entrypoint Design

Status: Under Discussion

> Early draft — rough / unfinished ideas. @SG feel free to leave high-level comments for direction. But I'll be polishing this up Friday day

## Decision

TBD — presenting options for discussion.

Three *annotation* entrypoint types are planned: direct URL, Python API, and CLI. All open the Argilla web UI. The open question is CLI scope (how many commands).

Annotation commands live under `chatboteval annotation <subcommand>` — keeping top-level clean for product commands (`generate`, `eval`, `train`).


## Options

### Option A: Minimal

One command: `chatboteval annotation annotate <data>` — starts Argilla stack (if not running), imports data, opens web UI.

Import/export handled via Python API or Makefile scripts only.

**Pros:**
- Lowest cognitive load; minimal CLI surface to maintain
- "install package → run command → web app opens"
- Aligns with f2f UX principle: "minimal entry points → GUIs open to offer users options; simple entry point + in-app guidance"

**Cons:**
- No CLI automation for import/export; admin tasks require Python knowledge
- Conflates setup, import, and annotation into one command (harder to debug)
- Less composable for scripting

> Consider `chatboteval annotation init` → opens a GUI/wizard that helps fill out `~/.chatboteval/config.yaml`

### Option B: Core Workflow Commands

Separate commands for each workflow step:

```
chatboteval annotation setup    # configure Argilla (workspaces, schemas, users)
chatboteval annotation import   # load data into Argilla datasets
chatboteval annotation export   # export annotations to CSV
chatboteval annotation open     # open Argilla web UI in browser
```

Each command does one thing. Composable and scriptable.

**Pros:**
- Clear separation of concerns (debug individual steps)
- Scriptable (CI, Makefile targets, automation)

**Cons:**
- More surface area to maintain
- Users must learn multiple commands (mitigated by `--help`)

### Option C: Rich CLI

All of Option B plus additional admin/analysis commands:

```
chatboteval annotation iaa       # compute inter-annotator agreement
chatboteval annotation status    # show dataset completion progress
chatboteval annotation users     # manage user accounts
```

**Pros:** Full admin and QA coverage from CLI; no need to drop into Python for any workflow.

**Cons:** High maintenance; overengineered for v1.0 — add later if demanded.


## Annotation Entrypoints

Regardless of CLI scope, annotation is accessed via three entry points (all open Argilla web UI):

| Entrypoint | Use case |
|------------|----------|
| **URL** | Direct browser access to Argilla instance |
| **Python API** | `chatboteval.annotation.open()` — programmatic access |
| **CLI** | `chatboteval annotation open` — convenience wrapper |

Annotation itself happens entirely in the Argilla web UI. CLI and Python API are for data management only.


## Implementation Notes

- **CLI framework:** Typer
- **Python API:** CLI commands are thin wrappers around Python functions; public API exists regardless of CLI scope
- **Registration:** `[project.scripts]` in `pyproject.toml`

See [Packaging and Invocation Surface](../design/packaging-invocation-surface.md) for dependency group details.


## Consequences

- CLI scope determines maintenance surface and user onboarding complexity
- Python API is the primary programmatic interface regardless of CLI choice
- Option B is the natural middle ground; Option A aligns better with the f2f UX principle; Option C is deferred
