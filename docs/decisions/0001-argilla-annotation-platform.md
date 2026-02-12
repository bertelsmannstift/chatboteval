# 0001 Argilla Annotation Platform

Status: Accepted


## Decision

Use **Argilla v2.8.0** as the annotation platform for human labelling of RAG chatbot query-response pairs.


## Context

Need an annotation platform for 5-10 domain experts to label chatbot responses across multiple dimensions (correctness, grounding, relevance, harm/bias, etc). Must be self-hosted (GDPR), support task assignment and structured export, and deploy within the pilot timeline.

**Alternatives considered:**

- **Label Studio** — Roles, task assignment, and IAA metrics locked behind Enterprise paywall.
- **Doccano** — Similar gaps (no task assignment, no IAA, broken approval workflow).
- **Streamlit/Gradio** — Concurrency bugs with 3+ users; would require building annotation infrastructure from scratch.
- **Custom build (FastAPI + React)** — 2-4 weeks development, maintenance burden, defeats "turnkey over custom" principle.

**Why Argilla:**

1. Only free tool with proper task distribution (`TaskDistribution` API)
2. Python-native SDK designed for ML workflows
3. Active development (HuggingFace acquisition, March 2025)
4. Role-based access (Owner/Admin/Annotator) in free tier
5. Built-in IAA metrics (Krippendorff's alpha)

**Trade-offs accepted:**

- Infrastructure weight — requires Elasticsearch + PostgreSQL + Redis (mitigated by Docker Compose)
- RAG UI needs CustomField HTML/CSS template (~0.5-1 day work)
- Review workflow is programmatic via SDK (no click-through UI)


## Consequences

- Fast deployment (cf custom build).
- Turnkey features: user management, task distribution, IAA.
- Python-native integration fits package architecture.
- No feature paywall risk (unlike Label Studio Enterprise).
- Infrastructure heavier than alternatives (Elasticsearch + PostgreSQL + Redis).
- See [Annotation Interface design doc](../design/annotation-interface.md) for implementation details.
