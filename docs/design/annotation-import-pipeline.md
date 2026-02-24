# Import Pipeline

Data pipeline to load captured chatbot query-response data into Argilla annotation datasets. Operates against a source-agnostic canonical schema; source-specific logic lives in adapter modules which are out of scope.

## Responsibilities

**In scope:**
- Accept canonical import records
- Transform to Argilla record schema
- Load into stratified datasets by annotation task (see [Annotation Protocol](../methodology/annotation-protocol.md))
- Validate records before import
- Assign `record_uuid` metadata for cross-dataset linking

**Out of scope:**
- Data capture from chatbot
- Source-system-specific transformation (handled by source adapter)
- Annotation task and label definition ([Annotation Protocol](../methodology/annotation-protocol.md))
- Export functionality (separate export pipeline)

## Architecture

>NB: exact api/command names pending (e.g. `chatboteval import` stage tbc)

```

┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ - - - ─ ┐
  External (out of scope)
│ ┌──────────────────────────────────┐                          |
  │  Source RAG System Output        │                          
│ └──────────────┬───────────────────┘                          │
                 │ query, answer, retrieved chunks, prompt context
│                ▼                                              │
  ┌──────────────────────────────────┐
│ │  Source Adapter (system specific)│                          |
  └──────────────┬───────────────────┘                           
└ ─ ─ ─ ─ ─ ─ ─ - ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ - - - ┘
                 │ (as ChatBotEval canonical import record/schema)
                 ▼
-──────────────────────────────────-──────────────────────────────
   Import Pipeline begins:                   
-──────────────────────────────────-──────────────────────────────

┌────────────────────────────────┐
│  chatboteval import <file>     │
└────────────┬───────────────────┘
             │
             ▼
┌──────────────────────────┐
│  Transform to            │
│  Argilla Records (SDK)   │
└────────────┬─────────────┘
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
┌────────┐ ┌────────┐ ┌────────┐
│ task1  │ │ task2  │ │ task3  │
│retriev.│ │ground. │ │generat.│
└────────┘ └────────┘ └────────┘
            │ 
            │ (workspace & task distribution → annotators label via Argilla Web UI)
            ▼
```
>TODO - exact API / CLI wrapper wording below are TBC, update when decided.

**Entry point:** CLI command (e.g., `chatboteval import <file>`)

**Single direction:** File → Argilla (no sync, no bidirectional updates)

**Fan-out:** One canonical record produces records in all three datasets. Task 1 produces K records per input (one per chunk); Tasks 2 and 3 produce one record each.

## Source Adapter & Canonical Schema

The import pipeline operates exclusively against a canonical import schema. Source-system-specific logic lives in external adapter modules - one adapter per source system (out of scope). The adapter transforms the source system's output into our canonical records; the pipeline never touches source-system internals. Adding a new source system requires only a new adapter.

### Canonical record

>TODO: a separate PR will add an independent `schema/` layer (add ref when done), this pydantic model will be the SSOT.

One record per RAG query-response cycle:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Original user query |
| `answer` | string | yes | Generated answer |
| `chunks` | list[Chunk] | yes | Retriever-level segments used for retrieval metrics |
| `context_set` | string | yes | Prompt-inserted context string, as the model saw it; documents separated by `[CTX_SEP]` |
| `language` | string | no | Detected language code |

**Chunk schema:**

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | string | Stable unique identifier for this chunk |
| `doc_id` | string | Source document/publication identifier |
| `chunk_rank` | int | Position in the flat post-rerank chunk list |
| `text` | string | Chunk text content |

### chunk_rank

Retrieval metrics (MRR@K, NDCG@K) require a flat, ordered list of K chunks. When a reranker scores at document level (not chunk level), chunk rank is derived as:

1. Sort documents by reranker score (descending)
2. For each document in rank order, enumerate its selected chunks in document order
3. `chunk_rank` = 1-indexed position in the resulting flat list

This treats all chunks from a higher-ranked document as more relevant than chunks from a lower-ranked document (=consistent with the reranker's signal). 

>If the source system provides per-chunk scores directly, `chunk_rank` can be derived from those instead.

## Outputs

Three Argilla datasets, each receiving records from every import:

### `task1_retrieval` — one record per chunk

**Fields (shown to annotators):**
- `query` ← canonical `query`
- `chunk` ← canonical `chunks[k].text`
- `answer` ← canonical `answer` (supporting context — positioned last per [Annotation UI Presentation](annotation-presentation.md))

**Metadata (stored, not shown):**
- `record_uuid` — assigned at import; links same query across all three datasets
- `chunk_id` ← canonical `chunks[k].chunk_id`
- `doc_id` ← canonical `chunks[k].doc_id`
- `chunk_rank` ← canonical `chunks[k].chunk_rank`
- `language` ← canonical `language`

**Questions:** `topically_relevant`, `evidence_sufficient`, `misleading`, `notes`

---

### `task2_grounding` — one record per query-answer pair

**Fields (shown to annotators):**
- `query` ← canonical `query`
- `answer` ← canonical `answer`
- `context_set` ← canonical `context_set`

**Metadata (stored, not shown):**
- `record_uuid`
- `language` ← canonical `language`

**Questions:** `support_present`, `unsupported_claim_present`, `contradicted_claim_present`, `source_cited`, `fabricated_source`, `notes`

---

### `task3_generation` — one record per query-answer pair

**Fields (shown to annotators):**
- `query` ← canonical `query`
- `answer` ← canonical `answer`

**Metadata (stored, not shown):**
- `record_uuid`
- `language` ← canonical `language`

**Questions:** `proper_action`, `response_on_topic`, `helpful`, `incomplete`, `unsafe_content`, `notes`

## Failure Modes

**Invalid/incomplete canonical record:**
- Validate required fields (`query`, `answer`, `chunks`, `context_set`) before processing
- Skip malformed records with error log; report summary at completion

**Missing chunks:**
- Import record anyway; log warning
- Annotators can flag retrieval failure via label questions

**Duplicate imports:**
- Check `record_uuid` / `query` against existing records
- Skip duplicates with warning logged

**Schema mismatch:**
- Validate field names match configured Argilla dataset schema on startup
- Fail early with expected vs. actual schema diff

## References

- [Export Pipeline](annotation-export-pipeline.md) — export schema and cross-dataset linking via `record_uuid`
- [Annotation Protocol](../methodology/annotation-protocol.md) — label definitions and annotation units
- [Annotation Interface](annotation-interface.md) — visibility contract and question wording
