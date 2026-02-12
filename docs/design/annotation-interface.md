# Annotation Interface

Web-based annotation interface where domain experts label RAG chatbot query-response pairs across multiple evaluation dimensions. Powered by Argilla (see [Decision 0001](../decisions/0001-argilla-annotation-platform.md)).

## Responsibilities

**In scope:**
- Present query-response pairs with retrieved context to annotators
- Collect binary labels per dimension (correctness, grounding, relevance, harm/bias - extensible)
- Support concurrent multi-user annotation with task distribution
- Export annotations to CSV/Parquet for evaluation framework

**Out of scope:**
- Query/response generation (a separate workflow)
- Model evaluation (a separate workflow)
- Downstream evaluation-model training (a separate workflow)
- Real-time chatbot integration

## Architecture

```
Entry Points:
┌─────────────────────────────────────────────────┐
│ 1. Browser → Argilla Web UI (annotation)       │
│ 2. Python API → chatboteval → Argilla SDK      │
│    (data import/export)                         │
│ 3. CLI → chatboteval → Argilla SDK             │
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
- **Hosted:** `chatboteval annotation setup --hosted --url <argilla_api_url>` → writes config to `~/.chatboteval/config.yaml` (Bertelsmann deploys on-prem, no licensing cost)
- **Cloud:** `chatboteval annotation setup --cloud` → paid option **(out of scope)**

**Package structure:**
- `/apps/annotation/` — Docker Compose configs for Argilla stack
- `src/chatboteval/data/argilla_client.py` — SDK wrappers for import/export/fetch

**Usage:** Annotation happens in browser via Argilla web UI. Python API and CLI are for data import/export and management.

## Inputs / Outputs

**Input:** Query-response pairs (CSV/JSON) with optional retrieved context (RAG chunks/source documents) and metadata.

**Annotation schema:** Single-select `LabelQuestion` per dimension (binary yes/no):
- Correctness: yes/no
- Grounding: yes/no
- Relevance: yes/no
- Harm detected: yes/no
- (Additional dimensions TBD based on pilot findings)

**Output:** CSV/Parquet with columns: `query`, `response`, `retrieved_docs`, `correctness`, `grounding`, `relevance`, `harm`, `annotator_id`, `submitted_at`

**Data flow:** Annotations stored in Argilla (PostgreSQL backend) → chatboteval exports to CSV/Parquet via Argilla SDK → evaluation framework reads CSV.

## Failure Modes

**Concurrent assignment** — Argilla's `TaskDistribution` API ensures exclusive task allocation; completed records removed from all queues.

**Incomplete annotations** — Argilla tracks draft vs submitted status. Export only fetches submitted records.

**Inter-annotator disagreement** — Overlap assignment (e.g., 20% annotated by 2+ reviewers). IAA metrics (Krippendorff's alpha) can be integrated later (low priority).

**Export schema mismatch** — Validation step checks column presence and types before write.

## References

- [Decision 0001: Argilla Annotation Platform](../decisions/0001-argilla-annotation-platform.md)
- Argilla docs: https://docs.argilla.io/latest/
