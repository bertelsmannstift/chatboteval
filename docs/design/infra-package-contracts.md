# Package Contracts Design

## Purpose

Scaffolds the contract layer for `chatboteval` — canonical types, schemas, path conventions, and config structures that all internal modules depend on. Each section is a stub to be developed during implementation. Together they form the shared vocabulary and structural conventions for the whole package.

Architectural choices underpinning this layer (Pydantic everywhere, dependency direction, contract types over raw dicts, frozen models, CSV interchange) are captured in [ADR-0005](../decisions/0005-contract-layer-tooling.md).


---

## 1. Domain Types

Core data structures shared across pipeline stages. Defined as frozen Pydantic models in `src/chatboteval/core/types.py`.

> In-memory Python objects — not on-disk formats (see Section 2 for serialisation).

**Controlled vocabulary:**

```python
class Task(StrEnum):
    RETRIEVAL = "retrieval"
    GROUNDING = "grounding"
    GENERATION = "generation"
```

**Unit of annotation:**

```
QueryResponsePair
  query: str
  response: str
  context_set: list[str]       # one entry per retrieved chunk
  source_id: str               # opaque identifier from source system
  metadata: dict               # pass-through from source (timestamps, model id, etc.)
```

**Annotation base:**

```python
class AnnotationBase(BaseModel, frozen=True):
    record_uuid: UUID
    annotator_id: str
    language: str
    inserted_at: datetime            # when record was loaded into Argilla (batch provenance)
    created_at: datetime             # response submission timestamp
    record_status: str               # Argilla record status: pending | completed
    notes: str | None
```

**Task-specific annotation types** — inherit from `AnnotationBase`, add task-specific labels. Match the [export schema](annotation-export-schema.md).

```
RetrievalAnnotation(AnnotationBase)        # unit: (query, chunk)
  input_query: str
  chunk: str
  chunk_id: str
  doc_id: str
  chunk_rank: int
  topically_relevant: bool
  evidence_sufficient: bool
  misleading: bool
```

```
GroundingAnnotation(AnnotationBase)        # unit: (answer, context_set)
  answer: str
  context_set: str                         # concatenated with [CTX_SEP]
  support_present: bool
  unsupported_claim_present: bool
  contradicted_claim_present: bool
  source_cited: bool
  fabricated_source: bool
```

```
GenerationAnnotation(AnnotationBase)       # unit: (query, answer)
  query: str
  answer: str
  proper_action: bool
  response_on_topic: bool
  helpful: bool
  incomplete: bool
  unsafe_content: bool
```


---

## 2. Data Schemas

> On-disk serialisation formats — what file readers/writers expect. String types, flat structure.

CSV for all interchange. The domain types in Section 1 are the source of truth for field names and semantics — each CSV schema is a flat serialisation of the corresponding Pydantic model. This section documents only the file-level structure and serialisation rules that differ from the in-memory representation.

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

Three task-specific CSVs, one per task. Each CSV contains the flat serialisation of the corresponding annotation type — all fields from `AnnotationBase` plus task-specific fields. See [Annotation Export Schema](annotation-export-schema.md) for full column definitions.

Serialisation differences from the domain types:

| Domain type field | CSV column | Difference |
|---|---|---|
| `Task` enum | `task` (str) | Enum serialised as string value |
| `UUID` | `record_uuid` (str) | UUID serialised as string |
| `context_set: list[str]` | `context_set` (str) | Chunks concatenated with `[CTX_SEP]` separator |
| `datetime` fields | str | ISO 8601 formatted |

File naming: `retrieval.csv`, `grounding.csv`, `generation.csv`.

Serialisation logic lives in `src/chatboteval/core/schema/` — separate from the domain types in `core/types.py`.


---

## 3. File Path Conventions

Canonical locations for data artefacts produced and consumed by the pipeline (not source code layout — see [ADR-0007](../decisions/0007-packaging-invocation-surface.md) for package structure).

```
<project_root>/
  data/                 # datasets (versionable, shareable)
    input/              # raw RAG output to annotate
    generated/          # synthetic test set from `chatboteval generate`
    annotated/          # annotation exports from `chatboteval annotation export`
  outputs/              # computed results (reproducible from data)

~/.chatboteval/
  config.yaml           # user config (optional — see Section 4)

./apps/
  annotation/
    docker-compose.yml  # Argilla stack (local mode only)
    .env
```

Paths are exposed via a `PathResolver` dataclass in `src/chatboteval/core/paths.py`:

```python
@dataclass
class PathResolver:
    base_dir: Path = Path(".")

    @property
    def data_input(self) -> Path:
        return self.base_dir / "data" / "input"

    @property
    def data_generated(self) -> Path:
        return self.base_dir / "data" / "generated"

    @property
    def data_annotated(self) -> Path:
        return self.base_dir / "data" / "annotated"

    @property
    def outputs(self) -> Path:
        return self.base_dir / "outputs"
```

The resolver takes `base_dir` (project root by default) and exposes resolved paths. Consuming code imports the resolver rather than constructing paths — single resolution point, easy to override in tests or via config.

> Directory structure is fixed by convention (no configuration). Only override is `base_dir` itself, which shifts the entire tree.


---

## 4. Core Config Schema

Structure of `~/.chatboteval/config.yaml`, parsed at startup by `src/chatboteval/core/settings.py` using Pydantic Settings.

**The config file is optional.** Built-in defaults mean the tool works with zero config — the file is only needed when overriding defaults (e.g. Argilla credentials, custom output paths).

```yaml
argilla:
  mode: local              # local | hosted
  url: http://localhost:6900
  api_key: owner.apikey

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

Defaults belong on the settings model fields — Pydantic Settings handles the precedence chain natively. If no config file exists and no env vars are set, the built-in defaults apply.

> Global config only at `~/.chatboteval/config.yaml` for v1.0. Follows the dbt/AWS CLI pattern, appropriate for a tool with credentials.

> **Task-specific configuration** (active tasks, stratification rules, distribution overlap targets) is not runtime config — it's applied at dataset creation time during `chatboteval annotation import`.
> - `Task` enum defines the fixed set of tasks
> - Argilla dataset settings (workspace assignment, `TaskDistribution` overlap) are configured via the import pipeline when datasets are created (see [Workspace & Task Distribution](annotation-workspace-task-distribution.md) and [Import Pipeline](annotation-import-pipeline.md))


---

## References

- [ADR-0005: Contract Layer Tooling](../decisions/0005-contract-layer-tooling.md) — tooling choices underpinning this layer
- [ADR-0007: Packaging and Invocation Surface](../decisions/0007-packaging-invocation-surface.md) — module dependency direction
- [Annotation Export Schema](annotation-export-schema.md) — full column definitions for export CSVs
