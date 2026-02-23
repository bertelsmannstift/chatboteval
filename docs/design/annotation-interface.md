# Annotation Interface

Web-based annotation interface for labelling RAG chatbot outputs across three annotation tasks, assigned to two annotator groups by expertise. Powered by Argilla.

## Responsibilities

**In scope:**
- Present query-response pairs with retrieved context to annotators
- Collect binary labels per annotation task (see [ADR-0006](../decisions/0006-annotation-tasks.md) for label definitions)
- Support concurrent multi-user annotation with task distribution
- Export annotations to CSV/Parquet for evaluation framework


## Architecture

```
Entry Points:
┌─────────────────────────────────────────────────┐
│ 1. Browser → Argilla Web UI (annotation)        │
│ 2. Python API → chatboteval → Argilla SDK       │
│    (data import/export)                         │
│ 3. CLI → chatboteval → Argilla SDK              │
│    (data import/export)                         │
└─────────────────────────────────────────────────┘
                     ▼
         ┌───────────────────────┐
         │ Argilla Stack         │
         │ (Docker Compose)      │
         ├───────────────────────┤
         │ • Argilla Server      │
         │ • PostgreSQL          │
         │ • Elasticsearch       │
         └───────────────────────┘
```

**Installation:** `uv pip install -e ".[annotation]"` (optional extra)

**Setup modes:** 
>*(NB exact commands TBC)*
- **Local:** `chatboteval annotation setup --local` → writes Docker Compose config, runs on localhost
- **Hosted:** `chatboteval annotation setup --hosted --url <argilla_api_url>` → writes config to `~/.chatboteval/config.yaml` (deploys on-prem, no licensing cost)
- **Cloud:** `chatboteval annotation setup --cloud` → paid option **(out of scope)**

**Package structure:**
- `/apps/annotation/` — Docker Compose configs for Argilla stack
- `src/chatboteval/argilla_client.py` — SDK wrappers for import/export/fetch

**Usage:** Annotation happens in browser via Argilla web UI. Python API and CLI are for data import/export and management.

## Inputs / Outputs

**Input:** Query-response pairs (CSV/JSON) with optional retrieved context (RAG chunks/source documents) and metadata.

**Annotation tasks:**

Three tasks with distinct units of annotation, assigned across two annotator groups:

| Task | Unit | Labels | Annotator group |
|---|---|---|---|
| Task 1: Retrieval | (query, chunk) pair | `topically_relevant`, `evidence_sufficient`, `misleading` | Junior |
| Task 2: Grounding | (answer, context set) pair | `support_present`, `unsupported_claim_present`, `contradicted_claim_present`, `source_cited`, `fabricated_source` | Junior |
| Task 3: Generation | (query, answer) pair | `proper_action`, `response_on_topic`, `helpful`, `incomplete`, `unsafe_content` | Domain experts |

All labels binary, all required. Questions presented simultaneously within each task. Fields ordered per visibility contract (primary content first, supporting context appended) — see [ADR-0007](../decisions/0007-annotation-presentation.md).

> **Collapsible supporting context:** Argilla v2 does not support collapsible field panels natively, instead we will add `rg.CustomField` with `advanced_mode=True` to render collapsible supporting context inside an HTML `<details>`/`<summary>` element.

> Three separate datasets are used (one per task) — Task 1's per-chunk granularity is incompatible with Tasks 2 and 3's per-query-answer units. See [ADR-0013](../decisions/0013-annotation-multi-dataset-architecture.md).

See [ADR-0006](../decisions/0006-annotation-tasks.md) for label definitions and logical constraints.

**Output:**

Dual export format:
- **Primary:** CSV — direct input to downstream fine-tuning pipeline
- **Secondary:** HuggingFace Datasets (Arrow/Parquet) via Argilla SDK `to_datasets()`

Flat schema structure (one row per annotator response):
```
record_id | record_uuid | annotator_id | schema_type | question_name | value | status | submitted_at
```

Merged export schema (cross-dataset aggregated view) combines domain expert and junior annotations for the same record via `record_uuid` metadata linking. Supports correlation analysis across dimensions.

See [ADR-0005: Annotation Export Schema](../decisions/0005-annotation-export-schema.md) for detailed export schema and implementation guidance.

**Data flow:** Annotations stored in Argilla (PostgreSQL backend) → chatboteval exports to CSV (primary) / HuggingFace Datasets (secondary) via Argilla SDK → downstream fine-tuning pipeline reads CSV.

## Failure Modes

**Concurrent assignment** — Argilla's `TaskDistribution` API ensures exclusive task allocation; completed records removed from all queues.

**Incomplete annotations** — Argilla tracks draft vs submitted status. Export only fetches submitted records.

**Inter-annotator disagreement** — Overlap assignment (e.g., 20% annotated by 2+ reviewers). IAA metrics (Krippendorff's alpha) can be integrated later (low priority).

**Export schema mismatch** — Validation step checks column presence and types before write.

## References

- [Decision 0001: Argilla Annotation Platform](../decisions/0001-annotation-argilla-platform.md)
- [Decision 0005: Annotation Export Schema](../decisions/0005-annotation-export-schema.md)
- [Decision 0006: Annotation Tasks](../decisions/0006-annotation-tasks.md)
- [Decision 0007: Annotation UI Presentation](../decisions/0007-annotation-presentation.md)
- [Decision 0008: Authentication Model](../decisions/0008-authentication-model.md)
- [Deployment](infra-deployment.md) — Docker Compose stack and infrastructure setup
- Argilla docs: https://docs.argilla.io/latest/
