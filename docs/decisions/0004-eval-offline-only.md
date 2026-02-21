# 0004 Offline Evaluation Only

Status: Accepted


## Decision

Real-time chatbot integration is out of scope. The framework evaluates captured query-response pairs, not live traffic.


## Rationale

- Evaluation requires human annotation, which is inherently asynchronous
- Batch processing enables reproducibility and controlled experimentation
- Simplifies architecture by avoiding real-time streaming infrastructure
- Users can evaluate production systems by exporting query logs periodically


## Consequences

- Evaluation results are retrospective, not real-time
- Users must implement their own data collection from production systems
- Architectural simplicity enables faster development and maintenance
