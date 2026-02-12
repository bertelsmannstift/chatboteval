# Annotation Interface

Web-based annotation interface where domain experts label RAG chatbot query-response pairs across multiple evaluation dimensions. Powered by Argilla v2.8.0 (see [Decision 0001](../decisions/0001-argilla-annotation-platform.md)).

## Responsibilities

**In scope:**
- Present query-response pairs with retrieved context to annotators
- Collect ratings per dimension (correctness, grounding, relevance, harm/bias)
- Distribute tasks across 5-10 concurrent reviewers
- Export annotations to CSV/Parquet for evaluation framework

**Out of scope:**
- Query/response generation (separate workflow)
- Model training (evaluation framework)
- Real-time chatbot integration

## Architecture

```
Annotator (Browser)
    │ HTTPS
    ▼
Argilla Web UI (Docker)
    │ SDK / API
    ▼
chatboteval package (Python)
    │
    ├── PostgreSQL (metadata, annotations)
    └── Elasticsearch (search index)
```

**Deployment:** Three modes — local (Docker), hosted (BF on-prem), cloud (HuggingFace Spaces). All annotation happens in browser via Argilla web UI.

## Inputs / Outputs

**Input:** Query-response pairs (CSV/JSON) with optional retrieved context and metadata.

**Annotation schema:** Single-select `LabelQuestion` per dimension (not multi-select):
- Correctness: correct / partial / incorrect
- Grounding: grounded / partial / not_grounded
- Relevance: relevant / partial / not_relevant
- Harm: none / minor / major

**Output:** CSV/Parquet with columns: query, response, retrieved_docs, correctness, grounding, relevance, harm, annotator_id, submitted_at.

**Data flow:** Argilla → PostgreSQL → export CSV/Parquet → evaluation framework.

## Failure Modes

**Concurrent assignment** — Argilla's `TaskDistribution` API ensures exclusive task allocation; completed records removed from all queues.

**Incomplete annotations** — Argilla tracks draft vs submitted status. Export only fetches submitted records.

**Inter-annotator disagreement** — Overlap assignment (e.g., 20% annotated by 2+ reviewers). IAA metrics (Krippendorff's alpha) calculated post-hoc.

**Export schema mismatch** — Validation step checks column presence and types before write.

## References

- [Decision 0001: Argilla Annotation Platform](../decisions/0001-argilla-annotation-platform.md)
- Argilla docs: https://docs.argilla.io/latest/
