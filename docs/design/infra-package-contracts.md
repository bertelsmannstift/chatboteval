# Package Contracts Design

## Purpose

Scaffolds the contract layer defined in [ADR-0014](../decisions/0014-infra-package-contracts.md). Each section below is a stub — the authoritative definition to be developed during implementation. Together they form the shared vocabulary and structural conventions for the whole package.


---

## 1. Domain Types

Core data structures shared across all pipeline stages. Defined as Pydantic models in `src/chatboteval/core/types.py`.

**Unit of annotation:**

```
QueryResponsePair
  query: str
  response: str
  context_set: list[str]       # retrieved chunks used to generate response
  source_id: str               # opaque identifier from source system
  metadata: dict               # pass-through from source (timestamps, model id, etc.)
```

**Annotation:**

```
Annotation
  pair_id: str
  task_type: "retrieval" | "grounding" | "relevance"
  label: bool                  # binary: acceptable / not acceptable
  annotator_id: str
  timestamp: datetime
```

**Evaluation output:**

```
EvalResult
  pair_id: str
  metric_family: "retrieval" | "grounding" | "relevance"
  score: float                 # 0.0–1.0
  method: "reference_based" | "reference_free" | "model_based"
  metadata: dict               # model id, prompt version, etc.
```

**Trained model artifact reference:**

```
ModelArtifact
  path: Path                   # local path to artifact directory
  task_type: str
  schema_version: str          # contract version this model was trained against
  training_metadata: dict      # dataset size, metrics at training time, etc.
```

> **To design:** AnnotatedPair (pair + its annotations), BatchEvalReport (aggregated EvalResults for a batch). Decide whether domain types are immutable (frozen Pydantic) or mutable.


---

## 2. Data Schemas

Column-level contracts for CSV/JSONL data exchanged between pipeline stages. Defined as Pydantic models in `src/chatboteval/core/schema/` (validation at system boundaries).

**RAG input format** — input to `generate` and `annotation import`:

| Column | Type | Description |
|---|---|---|
| `id` | str | Unique identifier for the QR pair |
| `query` | str | User query |
| `response` | str | RAG system response |
| `context` | str (JSON array) | Retrieved context chunks, serialised |
| `source` | str | Source system identifier |

**Annotation export format** — output of `annotation export`, input to `train` and `eval`:

| Column | Type | Description |
|---|---|---|
| `id` | str | QR pair identifier |
| `task_type` | str | `retrieval` / `grounding` / `relevance` |
| `label` | bool | Binary annotation |
| `annotator_id` | str | Argilla user identifier |
| `annotated_at` | datetime | Timestamp |

**Evaluation output format** — output of `eval`:

| Column | Type | Description |
|---|---|---|
| `id` | str | QR pair identifier |
| `metric_family` | str | Metric family |
| `score` | float | 0.0–1.0 |
| `method` | str | Evaluation method used |

> **To design:** JSONL vs CSV for RAG input (CSV preferred per ADR-0005, but JSONL may be more natural for context arrays). Schema versioning strategy — embed `schema_version` column or use file-level metadata?


---

## 3. File Path Conventions

Canonical locations for all data artefacts. Defined as constants or a `Paths` config object in `src/chatboteval/core/paths.py`.

```
<project_root>/
  data/
    input/              # raw RAG output to annotate or evaluate
    generated/          # synthetic test set from `chatboteval generate`
    annotated/          # annotation exports from `chatboteval annotation export`
  models/
    auto_labeller/      # trained auto-labeller artifacts (one subdir per run)
  outputs/
    eval/               # evaluation results from `chatboteval eval`

~/.chatboteval/
  config.yaml           # project config (Argilla URL, model paths, output dirs)

./apps/
  annotation/
    docker-compose.yml  # Argilla stack (local mode only)
    .env
```

> **To design:** Should paths be hardcoded conventions or configurable per-project? If configurable, where does the path config live (project config vs env vars vs `chatboteval.toml`)? How are multiple concurrent runs identified (timestamped subdirs, run IDs)?


---

## 4. Core Config Schema

Structure of `~/.chatboteval/config.yaml`, parsed at startup by `src/chatboteval/core/settings.py` using Pydantic Settings.

```yaml
argilla:
  mode: local              # local | hosted
  url: http://localhost:6900
  api_key: owner.apikey

model:
  deployment: mistral      # model used for reference-free eval (LLM-as-judge)
  # local_path: ...        # if using a locally-hosted model

output:
  base_dir: ./outputs      # override default output path
```

Precedence chain (highest to lowest):
```
CLI flags
CHATBOTEVAL_* env vars
~/.chatboteval/config.yaml
built-in defaults
```

> **To design:** Project-level config vs global user config — should there be a `chatboteval.toml` in the project root (like `pyproject.toml`) separate from the user's `~/.chatboteval/config.yaml`? Task-specific config (annotation task types, stratification rules) — part of core config or separate?


---

## 5. Model Spec (Eval Artifact)

Canonical on-disk structure of a trained auto-labeller, produced by `chatboteval train` and consumed by `chatboteval eval --model`.

```
models/auto_labeller/<run-id>/
  model/                  # HuggingFace-compatible model weights and tokeniser
  metadata.json           # schema_version, task_type, training dataset hash,
                          # eval metrics at training time, training timestamp
  schema.json             # input column contract this model expects
```

The `metadata.json` must be sufficient to determine whether a model artifact is compatible with a given dataset (schema version match) without loading the model weights.

> **To design:** Run ID format (timestamp vs UUID vs semantic label). Whether `metadata.json` is a Pydantic-serialised `ModelArtifact` or a looser JSON envelope. Versioning strategy if the contract schema changes after a model is trained.


---

## References

- [ADR-0014: Package Contract Layer](../decisions/0014-infra-package-contracts.md) — rationale and dependency rules
- [ADR-0005: Storage Format](../decisions/0005-storage-format.md) — annotation CSV as primary exchange format
- [ADR-0007: Packaging and Invocation Surface](../decisions/0007-packaging-invocation-surface.md) — module dependency direction
