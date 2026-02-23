# 0011: CLI Commands

Status: Draft

> Early draft — rough / unfinished ideas. @SG feel free to leave high-level comments for direction. But I'll be polishing this up Friday day as currently leans towards a research doc

## Decision

Working assumption: 
- primary pipeline commands (`generate`, `eval`, `train`) at top-level
- annotation commands grouped under `chatboteval annotation <subcommand>` namespace label 

All commands have Python API equivalents. CLI commands are thin wrappers around Python functions.

>design principle: if no arg / subcommand passed -> GUI/Wizard


## Full Command Reference

>all super tbc / thought in progress

Top level:

| Command | Description | Deps required | Status | Ref |
|---------|-------------|-----------------|--------|-----|
| `chatboteval generate` | Generate synthetic query-response pairs | TBD |  v1.0 | — |
| `chatboteval eval` | Run evaluation pipeline on annotated CSV | TBD |  v1.0 | — |
| `chatboteval train` | Fine-tune model on annotated CSV | `[finetune]` / `[finetune-peft]` |  v1.0 | — |

Annotate namespace:

| Command | Description | Deps required | Status | Ref |
|---------|-------------|-----------------|--------|-----|
| `chatboteval annotation setup` | Configure Argilla (workspaces, schemas, users) | `[annotation]` | v1.0 | [ADR-0010](0010-annotation-entrypoints.md), [ADR-0012](0012-infra-installation-setup-ux.md) |
| `chatboteval annotation import <file>` | Load data into Argilla datasets | `[annotation]` | v1.0 | [ADR-0010](0010-annotation-entrypoints.md) |
| `chatboteval annotation export <output>` | Export annotations to CSV | `[annotation]` | v1.0 | [ADR-0010](0010-annotation-entrypoints.md), [ADR-0005](0005-annotation-export-schema.md) |
| `chatboteval annotation open` | Open Argilla web UI in browser | `[annotation]` | v1.0 | [ADR-0010](0010-annotation-entrypoints.md) |


> `chatboteval annotation setup` has three modes: `--local`, `--hosted --url <url>`, `--cloud`. See [ADR-0012](0012-infra-installation-setup-ux.md).

## Command Sketches

```
chatboteval generate --data <path> [--model <model_id>] [--output <path>]
chatboteval eval     --data <csv_path> [--output <path>] [--reference <path>]
chatboteval train    --data <csv_path> [--method finetune|peft|optuna] [--output <path>]

chatboteval annotation setup [--local | --hosted --url <url> | --cloud]
chatboteval annotation import  <file>
chatboteval annotation export  <output_path>
chatboteval annotation open
```

Feature-gated extras (see [ADR-0012](0012-infra-installation-setup-ux.md)):
- `--method peft` requires `chatboteval[finetune-peft]`
- `--method optuna` requires `chatboteval[finetune-optuna]`
- `generate` optional deps TBD (local LLM vs hosted API)


## Namespace Options

Research basis: HuggingFace `hf` CLI ([docs](https://huggingface.co/docs/huggingface_hub/guides/cli)), GitHub `gh` CLI ([docs](https://cli.github.com/manual/)), MLflow CLI ([docs](https://mlflow.org/docs/latest/cli.html)), DVC ([docs](https://dvc.org/doc/command-reference)), dbt ([docs](https://docs.getdbt.com/reference/dbt-commands)), W&B `wandb` ([docs](https://docs.wandb.ai/ref/cli)).

**Pattern finding:** Flat structures (`dbt`, `dvc`, `wandb`) work well at small command counts; grouped namespaces (`hf`, `gh`, `mlflow`) dominate as surface grows. Neither pattern formally separates admin vs workflow — the distinction is conceptual, enforced by docs not structure.

---

### Option A: Fully flat

All commands at top-level — no namespaces.

```
chatboteval setup     [--local | --hosted --url <url> | --cloud]
chatboteval annotate   # opens Argilla UI (also --setup? or just have this at python code level)
chatboteval generate  --data <path> [--model <model_id>] [--output <path>]
chatboteval eval      --data <data_path> [--output <path>] [--reference <path>]
chatboteval train     --data <csv_path> [--method finetune|peft|optuna] [--output <path>]
chatboteval --help
```

**Pros:**
- Lowest friction — every command is one level deep
- Consistent depth; no mixed flat/nested surface
- dbt/dvc precedent — common for tools with a clear linear workflow
- Aligns with f2f UX principle: minimal entry points

**Cons:**
- No structural separation between annotation admin (setup/import/export) and ML pipeline commands
- Verb reuse risk if scope grows (e.g. a future `chatboteval export` for model export conflicts with annotation export)
- `--help` lists all 7+ commands with no visual grouping

---

### Option B: Annotation namespace + flat pipeline commands

Annotation admin commands under `chatboteval annotation`; pipeline commands flat at top-level.

```
chatboteval annotation setup    [--local | --hosted --url <url> | --cloud]
chatboteval annotation import   <file>
chatboteval annotation open                                       # opens Argilla UI
chatboteval annotation export   <output_path>
chatboteval generate  --data <path> [--model <model_id>] [--output <path>]
chatboteval eval      --data <csv_path> [--output <path>] [--reference <path>]
chatboteval train     --data <csv_path> [--method finetune|peft|optuna] [--output <path>]
```

`chatboteval --help` shows: `annotation`, `generate`, `eval`, `train`

**Pros:**
- Clean top-level surface for the daily-use ML pipeline commands
- Annotation admin is clearly scoped — hard to accidentally run `setup` thinking it's a pipeline step
- Namespace can grow independently (add `annotation iaa`, `annotation status` without polluting top-level)
- Precedent: MLflow (`mlflow server` vs `mlflow run`), hf (`hf auth` vs `hf download`)

**Cons:**
- Mixed depth: `annotation` is a group, `generate/eval/train` are bare verbs — visually inconsistent in `--help`
- Annotation tasks require two words even for daily operations (`chatboteval annotation open`)

---

### Summary

| | Option A — fully flat | Option B — annotation namespace |
|---|---|---|
| `--help` depth | 1 level | Mixed (1 for pipeline, 2 for annotation) |
| Precedent | dbt, dvc, wandb | mlflow, hf (partial) |
| Verb reuse risk | Higher | Lower |
| Discoverability | Single list | Grouped; annotation commands hidden one level down |
| Extensibility | Flat gets noisy after ~10 commands | Annotation group can grow without top-level pollution |


## Rationale

**Annotation as admin infrastructure:** Setup/import/export are one-time-per-iteration admin tasks. Namespacing under `chatboteval annotation` keeps the daily-use surface clean.

**Python API parity:** All commands available programmatically. From f2f: "download package → run command → output."


## Consequences

- Namespace choice determines `--help` discoverability and long-term extensibility
- v1.0 ships only `chatboteval annotation *`; ML pipeline commands reserved for v1.1+
- Missing extras produce clear install hints at runtime (not import-time)


## Open Questions

- Which namespace proposal to adopt — see Proposals section
- `generate`: local LLM (GPU dep) or hosted API? Determines optional extras.
- `eval`: optional `--reference` arg or separate subcommands for reference-based vs reference-free?
- `train`: confirm naming (`train` vs `finetune`) — f2f noted "train (TBC)"

See [Packaging & Entrypoints](../design/infra-packaging-entrypoints.md) for dependency group details.
