# 0012: Installation & Zero-Config Setup

Status: Draft

> Early draft — rough / unfinished ideas. @SG feel free to leave high-level comments for direction. But I'll be polishing this up Friday day
>
> Extended research on wizard UX, progressive disclosure, library recommendations (Questionary), idempotency patterns, config location, and open questions: `.hb-scratch/research-setup-ux.md`

## Decision

**No installation surprises.** Users explicitly opt in to heavy dependencies. Base `pip install chatboteval` installs only core; all feature-gated functionality behind named extras.

Annotation setup has three modes: 
- **local** (Docker Compose on user's machine)
- **hosted** (existing remote Argilla instance)
- **cloud** [indefinitely deferred/remove?] HF Spaces — optional, paid) 


## Optional Extras

```bash
pip install chatboteval                    # core only (data loading, CSV I/O)
pip install chatboteval[annotation]        # + Argilla SDK (annotation interface)
pip install chatboteval[finetune]          # + torch, transformers (standard fine-tuning)
pip install chatboteval[finetune-peft]     # + peft, bitsandbytes (LoRA / QLoRA)
pip install chatboteval[finetune-optuna]   # + optuna (hyperparameter optimisation)
pip install chatboteval[dev]               # + pytest, ruff, mypy
```

Extras can be combined: `pip install chatboteval[annotation,finetune]`.

**Fail-fast on missing extras:** Attempting to use a feature without its extra raises a clear, actionable error — not a cryptic import traceback:

```
ArgillaNotInstalledError: Argilla is not installed.
Install with: pip install chatboteval[annotation]
```

Import guards are at the call site, not at module import (so `import chatboteval` always works).


## Annotation Setup Modes

Three modes for `chatboteval annotation setup` (or `make setup`):

| Mode | Command | What it does |
|------|---------|--------------|
| **Local** | `chatboteval annotation setup --local` | Writes `docker-compose.yml` + `.env` to `./apps/annotation/`; runs `docker compose up` |
| **Hosted** | `chatboteval annotation setup --hosted --url <url>` | Writes URL + credentials to `~/.chatboteval/config.yaml`; validates connection |
| **Cloud** | `chatboteval annotation setup --cloud` | Guides through HuggingFace Spaces setup (optional, paid) |

For v1.0 (BF pilot), only **Local** and **Hosted** modes are required. Cloud is documented for future open-source users.

**Makefile abstraction:** `make setup` chains Docker startup + SDK configuration as a convenience target (see [Deployment design doc](../design/infra-deployment.md)):

```
make up       → start Docker containers
chatboteval annotation setup → configure Argilla via SDK
make setup    → both, sequentially
```


## Rationale

**No installation surprises:** `torch`, `argilla`, and `bitsandbytes` are large, sometimes GPU-specific packages. Forcing them on users who only need CSV export or evaluation would cause dependency conflicts and long installs. Optional extras let users install exactly what they need. From the 17-02 f2f: "our package installation should be the same: optional dependencies — no huge installation surprises."

**Three setup modes:** Different deployment contexts have fundamentally different setup flows. Flags make this explicit; a single `setup` command that silently guesses the mode would be harder to debug.

**Hosted mode for BF pilot:** Annotation will run on BF infrastructure, not the developer's laptop. `--hosted` allows connecting `chatboteval` to an existing Argilla instance without running Docker locally.


## Consequences

- `pyproject.toml` is the authoritative source for defined extras
- All optional import guards must be at call site, not module level
- `~/.chatboteval/config.yaml` is the config file location for hosted/cloud modes
- Local mode requires Docker on the user's machine (documented prerequisite)
- Cloud mode (HF Spaces) is out of scope for v1.0; documented for open-source users

## References

- [ADR-0010: Annotation Entrypoints](0010-annotation-entrypoints.md) — annotation command structure
- [ADR-0011: CLI Commands](0011-infra-cli-commands.md) — full CLI reference and optional deps
- [Deployment](../design/infra-deployment.md) — Docker Compose stack and Makefile targets
- [Packaging & Entrypoints](../design/infra-packaging-entrypoints.md) — dependency groups and design doc
