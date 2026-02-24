# 0002 Evaluation Approach

Status: Accepted


## Decision

This project evaluates RAG chatbots by scoring captured query–examples (primary evaluation unit, [see Metrics Taxonomy](docs/methodology/metrics-taxonomy.md)) using supervised evaluator models trained on human annotations.

The following architectural constraints apply:

- **Reference-based evaluation only**
  - Evaluation requires a human-annotated dataset.
  - Automated scoring is performed by fine-tuning and applying cross-encoder transformer models for multilabel classification.
  - Out of scope: LLM-as-judge, zero-shot evaluators, and other reference-free scoring approaches.
- **Offline batch evaluation**
  - The framework evaluates captured examples, retrospectively, in batch.
  - Out of scope: Real-time chatbot integration
- **Failure-mode decomposition**
  - Evaluation is decomposed into retrieval, grounding, and generation
- **Pipeline delegation**
  - Training and inference are executed via `tlmtc` as the canonical transfer-learning pipeline.


## Rationale

- **Reference-based evaluation yields reproducible, auditable, and reliable scores** 
  - LLM-as-judge / zero-shot approaches are prompt- and model/version–sensitive, inherently non-deterministic, impose marginal token costs per example, and are difficult to compare across runs.
  - Human-annotated labels provide an explicit ground truth for auditability and for validating the evaluator as a measurement instrument.
  - Supervised evaluators amortize cost into efficient fine-tuning and enable fast, cheap batch inference for repeatable runs at scale.
  - Cross-encoders model a relational evaluator over RAG structure that learns compatibility/entailment patterns between query, context, and answer—signals intrinsic to RAG evaluation tasks and therefore more portable across datasets.
  - Multilabel classification matches the construct: within each metric family, evaluation dimensions can co-occur and be logically interdependent.
- **Offline batch evaluation supports reproducibility and keeps the system simple**
  - Human annotation is inherently asynchronous and produces labeled datasets in discrete snapshots rather than streams.
  - Batch runs enable controlled experimentation and make results comparable across runs and over time.
  - Avoids coupling evaluation to production systems and eliminates the need for real-time ingestion.
- **Failure-mode decomposition improves construct validity and actionability**
  - Separating retrieval, grounding, and generation keeps each task’s unit of annotation conceptually coherent and avoids NA-heavy schemas that dilute rater attention and agreement.
  - A single “overall quality” judgment conflates distinct error types, making scores harder to interpret and less diagnostically useful.
  - Decomposed outputs map directly to levers in a RAG system, supporting actionable debugging and regression triage.
- **Pipeline delegation enforces separation of concerns and reduces maintenance risk**
  - `tlmtc` encapsulates the transfer-learning lifecycle, allowing `chatboteval` to focus on evaluation methodology, schema contracts, and reporting.
  - Reusing a dedicated transfer-learning pipeline avoids reimplementing complex and error-prone ML infrastructure, reducing technical debt.


## Consequences

- Evaluation requires an annotation workflow and a labeled dataset snapshot; the framework cannot operate in a reference-free mode.
- The scoring backend is constrained to supervised cross-encoder multilabel classification; metric computation assumes model outputs are aligned with the annotation protocol.
- The annotation protocol must be multilabel-compatible (non–mutually-exclusive binary dimensions); continuous or ranking-style judgments are out of scope.
- `tlmtc` owns: data splitting and pre-processing, HPO, fine-tuning, inference, and model validation
