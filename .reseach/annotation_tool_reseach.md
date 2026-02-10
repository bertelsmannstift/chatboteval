# Annotation Tool Decision

**Status:** OPEN 
**Impact:** High — shapes monorepo architecture, deployment model, development timeline, and open-source strategy
**Last updated:** 2026-02-10


## Open Qs needing input:
1. How important is local (`pip install chatboteval`)?
2. Does BF have Elasticsearch already?

## Context

- we need a web-based annotation interface for BF experts to label RAG chatbot query-response pairs. 
- must support:
    - multi-user access, 
    - configurable annotation schemas, 
    - a retrieved documents panel for grounding verification (TODO confirm this), 
    - export to HuggingFace datasets for model training.

**Key constraints:**
- Self-hosted (GDPR, BF on-prem)
- Docker deployment OK
- Multi-user (5-10+ concurrent annotators) (TODO confirm this)
- Open-source 
- Near-term DeBERTa etc fine-tuning pipeline
- Configurable schema (evolving during pilot)
- Retrieved documents panel essential (TODO confirm this)

---

## Option A: Custom (FastAPI + HTMX)

Custom FastAPI (backend) + HTMX/Jinja2 (frontend).
Most customisable, but most work.

### Pros

1. **Pydantic schema as SSOT** — schema definitions propagate automatically through UI, validation, storage, export, and training (= introspection). No translation layer between models vs the annotation tool's models.
2. **Storage abstraction** — Native SQLite ↔ PostgreSQL switching. Local mode (single file) and hosted mode (multi-user) share same app src code.
3. **No external dependencies** — Self-contained Python package. 
    - power users could `pip install chatboteval` and run. 
    - No Elasticsearch, no separate server process.
4. **Framework integration** — Annotation, training, inference, and export can live in same codebase. Shared schema, shared models, no import/export friction, etc.
5. **Full UI control** — e.g. retrieved documents panel, keyboard shortcuts, tiered schema (if want).
6. **Open-source value** — standalone tool w/ minimal dependencies. 
7. **Long-term ownership** — (small but non-trivial; / depends how much BF / DSL want to dev this in future)
8. **Lighter deployment** — Docker image with just PostgreSQL (or SQLite for local). No Elasticsearch cluster required.

### Cons

1. **Development time** est 2/3x as much work vs out-of-the-box
    - Must build incl: auth, session management, batch assignment, progress tracking, concurrent access control, admin dashboard.
    - Every feature (RBAC, conflict resolution, activity logging) must be built and maintained by the team.
2. **Multi-user complexity** — Concurrent annotation, batch locking, real-time progress updates all need implementation (solved problems in existing platforms).
4. **No community plugins** — No ecosystem of pre-built integrations.
5. **Security surface** — Must implement auth, session management, etc from scratch.
6. **Testing burden** 

### WP breakdown
1. Schema + storage foundation
2. FastAPI backend (routes, auth, sessions)
3. HTMX frontend (annotation UI, docs panel)
4. Batch management + IAA
5. Admin dashboard

---

## Option B: Argilla

Deploy Argilla (open-source LLM annotation platform) -> build Python SDK wrapper for our integration.
Perfect fit BUT Elasticsearch dependency.

### Pros

1. **Fastest MVP** — 2multi-user annotation, batch management, progress tracking, auth = built-in.
2. **LLM/RAG focused** — Purpose-built for LLM evaluation annotation. Supports text fields, rating questions, label questions, ranking questions, etc
3. **CustomField** — HTML/CSS/JavaScript templates enable custom UI components (retrieved documents panel possible via custom HTML).
4. **HuggingFace integration** — Native push/pull to HuggingFace datasets. Direct path to DeBERTa fine-tuning.
5. **Python SDK** — Programmatic dataset creation, batch assignment, and export via `pip install argilla`.
6. **Active development** — currnertly v backed by HuggingFace ecosystem.
7. **OAuth2 built-in** — User management, workspaces, API keys etc out of the box.
8. **Battle-tested** — Production deployments at scale, edge cases already handled.

### Cons

1. **Elasticsearch dependency** — Requires Elasticsearch or OpenSearch cluster alongside PostgreSQL. 
    -  => qdds infra complexity (doable as would not really need single Docker container) + heavyweight mem footprint (~2-4 GB RAM) for otherwise q lightweight job (just disproportionate, but extenisble/scalable).
    - (= MOST MAJOR PAIN POINT)
2. **Schema translation** — Must map Pydantic models → Argilla Questions → back to Pydantic for export. Translation layer adds complexity and potential for drift.
3. **Storage lock-in** — Argilla uses its own storage model (PostgreSQL + Elasticsearch). Cannot use SQLite for local mode. No storage abstraction.
4. **Limited UI customisation** — CustomField is powerful but constrained. Complex interactions (keyboard shortcuts across custom fields, tiered schema show/hide) may be difficult.
5. **Framework boundary** — Argilla is a separate service. chatboteval's training/inference/export pipeline talks to Argilla via SDK, not shared code. Import/export friction at the boundary.
6. **Open-source perception** — Users of chatboteval must also deploy Argilla. "Install our tool AND deploy this other platform" is a harder sell than a self-contained package.
7. **Version coupling** — Argilla SDK versions must track Argilla server versions. Breaking changes in Argilla affect chatboteval.
8. **No SQLite local mode** — Local development requires Docker (Argilla + PostgreSQL + Elasticsearch). Cannot run `chatboteval annotate` with just a SQLite file.

### WP breakdown
1.  Argilla deployment (Docker Compose)
2. Schema mapping (Pydantic → Argilla) [TODO confirm if needed]
3. CustomField for retrieved docs panel 
4. SDK wrapper + export integration 

---

## Option C: Label Studio

gen-purpose annotation platform

### Pros

1. **Mature platform** — community, docs, etc.
2. **Fexible templates** — XML-based template system supports complex annotation layouts.
3. **Broad ecosystem** — Integrations with ML platforms, pre-labelling backends.
4. **Self-hosted** — Open-source community edition available.
5. **REST API** — Comprehensive API for programmatic control.

### Cons

1. **Enterprise licensing** — Multi-user workspace features and adv permissions require LS Enterprise (paid). Community edition is essentially single-user. (= MAJOR BLOCKER)
2. **Not LLM-focused** — gen-purpose (images, audio, video, text) -> RAG-specific workflows (retrieved docs panel, grounding verification etc) need extensive custom templating.
3. **XML templates** — Configuration is XML-based, not Pythonic. Friction with Pydantic-driven approach (minor)
4. **No HuggingFace integration** — Export → transform → import workflow needed for model training. No native push to datasets.
5. **Heavy deployment** — Requires PostgreSQL + Redis + Label Studio server. Docker Compose setup is more complex than Argilla.
6. **Schema mapping** — XML template ↔ Pydantic model mapping is more complex than Argilla's Python SDK.
7. **Cost for multi-user** — Enterprise pricing starts at ~$20/user/month. For 10 annotators over 6 months = ~$1,200. Not prohibitive but adds cost.
8. **Overkill** — Much of Label Studio's power (image annotation, video segmentation, audio transcription) is irrelevant. You pay the complexity cost without using the features.

---

## Option D: Streamlit

Build an annotation interface as Streamlit app.

### Pros

1. **Fastest prototype (& iteration)** —  Python script → working web app in hours.
2. **Python-native** — Pure Python, no frontend framework to learn.
3. **Good for local mode** — `streamlit run app.py` just works for single-user local annotation.

### Cons

1. **Not an annotation platform** — build all annotation infrastructure from scratch: auth, sessions, batch management, concurrent access, progress tracking, auto-save, conflict resolution.
2. **Concurrency issues** — session state model is per-tab, not per-user. Multi-user concurrent annotation is diff/imposs.
3. **Performance ceiling** 
4. **No WebSocket support** 
5. **Session management** — sessions are ephemeral / resume capability must be built on top.
6. **Scalability** 
7. **Maintenance estimate** — building all annotation infrastructure in Streamlit would likely take longer than FastAPI + HTMX (fighting framework's assumptions).


---

## Recommendation

### For chatboteval specifically:

**1st choice: Argilla** 

Faster to setup than custom / can always migrate to custom later.
Only real blocker: Elasticsearch (as separate service)

**2nd choice: Custom (FastAPI + HTMX)** 

Can build whatever we need

The project's requirements (Pydantic SSOT, storage abstraction, framework integration, open-source self-contained package) align naturally with a custom build. The 6-8 week timeline is acceptable given the 6-month pilot.




