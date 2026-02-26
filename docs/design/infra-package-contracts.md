# Package Contracts Design

## Purpose

Scaffolds the contract layer for `chatboteval` — a set of canonical types, schemas, path conventions, and config structures that all internal modules depend on. Each section below is a stub — the authoritative definition to be developed during implementation. Together they form the shared vocabulary and structural conventions for the whole package.

## Key decisions

- **Pydantic** for all contract definitions (domain types, data schemas, config via Pydantic Settings). Validates structure at module boundaries; Pydantic becomes a core dependency.
- **Dependency direction:** `core/ ← api/ ← cli/` (per [ADR-0007](../decisions/0007-packaging-invocation-surface.md)). Contract definitions in `core/` have zero internal imports — they are the bottom of the dependency graph.
- **All inter-module data exchange** uses contract types, not raw dicts. Schema changes are breaking changes.
- **No business logic** in the contract layer — types and schemas only.
- **Public API surface:** `api/` re-exports contract types directly. Users get typed interfaces without knowing internal structure.


---

## 1. Domain Types

Core data structures shared across all pipeline stages. Defined as Pydantic models in `src/chatboteval/core/types.py`.

>= in-memory Python objects

**Unit of annotation:**

```
QueryResponsePair
  query: str
  response: str
  context_set: list[str]       # one entry per retrieved chunk; serialised as JSON array in CSV, concatenated with [CTX_SEP] in annotation exports
  source_id: str               # opaque identifier from source system
  metadata: dict               # pass-through from source (timestamps, model id, etc.)
```

**Annotations** — task-specific types matching the [export schema](annotation-export-schema.md). Each task has a different annotation unit and label set:

```
RetrievalAnnotation                        # unit: (query, chunk)
  record_uuid: str
  input_query: str
  chunk: str
  chunk_id: str
  doc_id: str
  chunk_rank: int
  topically_relevant: bool
  evidence_sufficient: bool
  misleading: bool
  notes: str | None
  annotator_id: str
  language: str
  inserted_at: datetime
  created_at: datetime
  record_status: str
```

```
GroundingAnnotation                        # unit: (answer, context_set)
  record_uuid: str
  answer: str
  context_set: str                         # concatenated with [CTX_SEP]
  support_present: bool
  unsupported_claim_present: bool
  contradicted_claim_present: bool
  source_cited: bool
  fabricated_source: bool
  notes: str | None
  annotator_id: str
  language: str
  inserted_at: datetime
  created_at: datetime
  record_status: str
```

```
GenerationAnnotation                       # unit: (query, answer)
  record_uuid: str
  query: str
  answer: str
  proper_action: bool
  response_on_topic: bool
  helpful: bool
  incomplete: bool
  unsafe_content: bool
  notes: str | None
  annotator_id: str
  language: str
  inserted_at: datetime
  created_at: datetime
  record_status: str
```

**Per-example predictions** (from `tlmtc` inference) — multilabel classification output, one prediction per example:

> **NB:** `ExamplePrediction` is speculative / tbc, actual format depends on `tlmtc`'s output interface, which hasn't been inspected yet. Revise later.

```
ExamplePrediction                          # per-example multilabel output from tlmtc
  record_uuid: str
  task: "retrieval" | "grounding" | "generation"
  predicted_labels: dict[str, bool]        # e.g. {"topically_relevant": true, "evidence_sufficient": false}
```

**Aggregated metrics** (computed by `chatboteval`) — deterministic aggregation using formulas from the [Metrics Taxonomy](../methodology/metrics-taxonomy.md). Input labels come from (i) human annotations initially, and (ii) fine-tuned evaluator model predictions (`ExamplePrediction`) once trained. See [ADR-0002](../decisions/0002-evaluation-approach.md) for evaluation approach.

```
MetricResult                               # aggregated by chatboteval from ExamplePredictions
  metric_name: str                         # e.g. "TopicalPrecision@K", "GroundingPresenceRate"
  metric_family: "retrieval" | "grounding" | "generation"
  value: float                             # 0.0–1.0
  dataset_size: int                        # number of examples aggregated over
```

**Trained model artifact reference:**

```
ModelArtifact
  path: Path                   # local path to artifact directory
  task: "retrieval" | "grounding" | "generation"
  schema_version: str          # contract version this model was trained against
  training_metadata: dict      # dataset size, metrics at training time, etc.
```

### Design decisions

**1. Base class for annotation types** → `AnnotationBase` with shared metadata fields; task types inherit and add task-specific labels. 7 shared fields across 3 types is enough duplication to warrant one level of inheritance. Shared validation lives in one place.

```python
class AnnotationBase(BaseModel, frozen=True):
    record_uuid: str
    annotator_id: str
    language: str
    inserted_at: datetime            # when record was loaded into Argilla (batch provenance)
    created_at: datetime             # response submission timestamp
    record_status: str               # Argilla record status: pending | completed
    notes: str | None

class RetrievalAnnotation(AnnotationBase):
    input_query: str
    chunk: str
    chunk_id: str
    doc_id: str
    chunk_rank: int
    topically_relevant: bool
    evidence_sufficient: bool
    misleading: bool
```

**2. Frozen domain types** → all domain types use `frozen=True`. These are data records -> all fields known at construction time (from CSV rows or Argilla exports). Frozen types are safer (no accidental mutation mid-pipeline), hashable (usable in sets/dicts for deduplication), and enforce data integrity.

**3. StrEnums for controlled vocabularies** → `task`, `metric_family`, and `metric_name` defined as `StrEnum`s in `core/types.py`. The vocabulary (`retrieval`/`grounding`/`generation`) is stable across all docs. Catches typos at import time, enables IDE autocomplete, and centralises renaming.

```python
class Task(StrEnum):
    RETRIEVAL = "retrieval"
    GROUNDING = "grounding"
    GENERATION = "generation"
```


---

## 2. Data Schemas

>= on-disk serialisation (flat) formats for data exchanged between pipeline stages; what file reader/writers expects; string types

CSV for all interchange. The domain types in Section 1 are SSOT for field names and semantics —> each CSV schema is a flat serialisation of the corresponding Pydantic model.

This section documents only the file-level structure and serialisation rules that differ from the in-memory representation.

### RAG input format — input to `generate` and `annotation import`

Flat serialisation of `QueryResponsePair`, plus an `id` and `source` column:

| Column | Type | Notes |
|---|---|---|
| `id` | str | Unique identifier for the QR pair (not on the domain type) |
| `query` | str | |
| `response` | str | |
| `context_set` | str (JSON array) | `list[str]` serialised as JSON array |
| `source` | str | `source_id` on the domain type |

### Annotation export format

Three task-specific CSVs, one per task. Each CSV contains the flat serialisation of the corresponding annotation type (`RetrievalAnnotation`, `GroundingAnnotation`, `GenerationAnnotation`) — all fields from `AnnotationBase` plus task-specific fields. See [Annotation Export Schema](annotation-export-schema.md) for full column definitions.

Serialisation differences from the domain types:

| Domain type field | CSV column | Difference |
|---|---|---|
| `Task` enum | `task` (str) | Enum serialised as string value |
| `context_set: list[str]` | `context_set` (str) | Chunks concatenated with `[CTX_SEP]` separator |
| `datetime` fields | str | ISO 8601 formatted |

File naming: `retrieval.csv`, `grounding.csv`, `generation.csv`.

### Per-example predictions

Flat serialisation of `ExamplePrediction`. One row per example per task. `predicted_labels: dict[str, bool]` is unpacked into one boolean column per label (task-specific column names).

> Schema is speculative — depends on `tlmtc` output format.

### Aggregated metrics

Flat serialisation of `MetricResult`. One row per metric. All fields map 1:1, no serialisation differences.

> CSV for all data exchange, including RAG input(?). The `context_set` column contains a JSON-serialised array (`["chunk1", "chunk2"]`). This keeps one format everywhere; the column is machine-consumed so readability is not a concern.

> No per-file schema versioning. Schema version is implicit from the package version (if contract types change -> package version bumps). The only place an explicit version check matters is model–dataset compatibility, which `ModelArtifact.schema_version` already handles. Pydantic validation at load time is the version mismatch signal for CSV files.


---

## 3. File Path Conventions

Canonical locations for data artefacts produced and consumed by the pipeline (not source code layout, see [ADR-0007](../decisions/0007-packaging-invocation-surface.md) for package structure).

```
<project_root>/
  data/                 # datasets (versionable, shareable)
    input/              # raw RAG output to annotate or evaluate
    generated/          # synthetic test set from `chatboteval generate`
    annotated/          # annotation exports from `chatboteval annotation export`
  models/               # trained model artifacts managed by chatboteval
    auto_labeller/      # multilabel text classifier (one subdir per run)
                        # extensible
  outputs/              # computed results (reproducible from data + model)
    eval/               # evaluation results from `chatboteval eval`

~/.chatboteval/
  config.yaml           # user config (Argilla credentials, model paths, output dirs)

./apps/
  annotation/
    docker-compose.yml  # Argilla stack (local mode only)
    .env
```

These paths are exposed as module-level `Path` constants in `src/chatboteval/core/paths.py` — one constant per directory above (e.g. `DATA_INPUT`, `DATA_ANNOTATED`, `MODELS_AUTO_LABELLER`, `OUTPUTS_EVAL`). All path resolution relative to project root happens in this module; consuming code imports the constants rather than constructing paths.

> Directory structure is fixed by convention (no configuration).Only override is output.base_dir in config, which can change where outputs are written.

---

## 4. Core Config Schema

Structure of `~/.chatboteval/config.yaml`, parsed at startup by `src/chatboteval/core/settings.py` using Pydantic Settings.

```yaml
argilla:
  mode: local              # local | hosted
  url: http://localhost:6900
  api_key: owner.apikey

tlmtc:
  model_dir: ./models/auto_labeller   # path to trained evaluator artifacts

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

> Global config only at `~/.chatboteval/config.yaml` for v1.0. Follows the dbt/AWS CLI pattern, appropriate for tool with credentials.

> **NB:** Task-specific configuration (active tasks, stratification rules, distribution overlap targets) is not runtime config, instead it's applied at dataset creation time during `chatboteval annotation import`. 
> - `Task` enum defines the fixed set of tasks (see above)
> - Argilla dataset settings (workspace assignment, `TaskDistribution` overlap) are configured via the import pipeline when datasets are created(see [Workspace & Task Distribution](annotation-workspace-task-distribution.md) and [Import Pipeline](annotation-import-pipeline.md))
>   1. Create Argilla datasets once (oon first import)
>   2. Task distribution, workspace assignment, overlap targets are baked into the datasets at creation
>   3. Subsequent imports add records to existing datasets (no reconfiguration)
> Only alternative would be to move these dataset configs to `chatboteval init` -> `~/.chatboteval/config.yaml` - over engineering?


---

## 5. Model Spec (Eval Artifact)

Canonical on-disk structure of a trained auto-labeller, produced by `tlmtc` and consumed by `chatboteval eval`.

```
models/auto_labeller/<run-id>/          # run-id = ISO timestamp, e.g. 2025-03-15T14-30-00
  model/                  # HuggingFace-compatible model weights and tokeniser
  metadata.json           # Pydantic-serialised ModelArtifact (see Section 1)
  schema.json             # input column contract this model expects
```

The `metadata.json` must be sufficient to determine whether a model artifact is compatible with a given dataset (schema version match) without loading the model weights.

> **run-id:** ISO timestamp (`YYYY-MM-DDTHH-MM-SS`). Sortable, human-readable.
>
> **Metadata format:** `metadata.json` is a direct Pydantic serialisation of `ModelArtifact` — written with `model_dump_json()`, read with `model_validate_json()`. Consistent with the rest of the contract layer (Pydantic as SSOT).
>
> **Schema version mismatch:** At eval time, compare `ModelArtifact.schema_version` against current package version. Mismatch -> fail with clear error. No migration, no backwards compatibility (need to retrain). 

---

## References

- [ADR-0007: Packaging and Invocation Surface](../decisions/0007-packaging-invocation-surface.md) — module dependency direction
