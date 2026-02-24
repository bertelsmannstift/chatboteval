# 0010: Annotation Entrypoints

Status: Draft


## Decision

Annotation is accessed via three entrypoints — all ultimately open the Argilla web UI:

| Entrypoint | Usage |
|---|---|
| **URL** | Direct browser access to the Argilla instance |
| **Python API** | `chatboteval.annotation.open()` — programmatic access |
| **CLI** | `chatboteval annotation open` — convenience wrapper |

Annotation itself happens entirely in the Argilla web UI. The CLI and Python API handle data management only (import, export).

The annotation CLI surface uses **Option B: core workflow commands** — one command per workflow step, composable and scriptable:

```
chatboteval annotation import <file>
chatboteval annotation export <output_path>
chatboteval annotation open
```

Project and Argilla initialisation is handled by the top-level `chatboteval init` command (ADR forthcoming), which covers full project setup, not annotation alone.


## Rationale

**Core workflow commands over minimal:** Import and export are distinct steps that can fail independently and run in separate contexts. A single `annotate <data>` command conflates setup, data loading, and UI launch — harder to debug and harder to automate.

**CLI delegates to Python API:** All CLI commands are thin wrappers. The Python API is the primary interface; CLI is a convenience layer for operators and scripts.

**`init` at top level:** Argilla connection setup is one part of broader project initialisation (models, paths, output structure). Scoping it to `chatboteval annotation setup` would misrepresent it as annotation-only config.

**Rich commands deferred:** `annotation iaa`, `annotation status`, `annotation users` are out of scope for v1.0 — add if demanded.


## Consequences

- `chatboteval annotation` namespace contains: `import`, `export`, `open`
- Every CLI command has a corresponding Python API function
- `chatboteval init` handles full project setup including Argilla connection


## References

- [ADR-0007: Packaging and Invocation Surface](0007-packaging-invocation-surface.md) — library-first architecture and single entry point
- ADR-0011: CLI Commands (forthcoming) — full CLI surface and namespace decision
