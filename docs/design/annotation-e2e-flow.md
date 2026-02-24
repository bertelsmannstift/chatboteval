# Annotation — End-to-End Flow (v1.0)

End-to-end data flow for the annotation pipeline, from source system output through to quality-assured annotation exports.

```
┌──────────────────────────────────┐
│  Source RAG System               │  
│  (any chatbot with adapter)      │
└──────────────┬───────────────────┘
               │ query, answer, retrieved chunks, prompt context
               ▼
┌──────────────────────────────────┐
│  Source Adapter                  │  system-specific
│  chatboteval.adapters.<system>   │
└──────────────┬───────────────────┘
               │ canonical import records
               ▼
┌──────────────────────────────────┐
│  Import Pipeline                 │  → annotation-import-pipeline.md
│  chatboteval import <file>       │
└────┬─────────────┬───────────────┘
     │             │              │
     ▼             ▼              ▼
task1_retrieval  task2_grounding  task3_generation   ← Argilla datasets
     │             │              │
     └─────────────┴──────────────┘
                   │ annotators label via Argilla Web UI
                   │ (workspace & task distribution → annotation-workspace-task-distribution.md)
                   ▼
┌──────────────────────────────────┐
│  Export Pipeline                 │  → annotation-export-pipeline.md
│  chatboteval export <output_dir> │
└────┬─────────────┬───────────────┘
     │             │              │
     ▼             ▼              ▼
retrieval.csv  grounding.csv  generation.csv
     │             │              │
     └─────────────┴──────────────┘
                   │ (optional) join on record_uuid → merged.csv
                   ▼
┌──────────────────────────────────┐
│  Quality Assurance               │  → annotation-quality-assurance.md
│  IAA: Krippendorff's α per label │
└──────────────────────────────────┘
```

**Infrastructure:** Argilla runs in Docker Compose. Users provisioned via [User Management](annotation-user-management.md). Annotation tasks and labels defined in [Annotation Protocol](../methodology/annotation-protocol.md).
