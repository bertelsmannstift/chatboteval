# Deployment

Docker Compose stack for the Argilla annotation platform, covering local development and production on-premises deployment.

## Responsibilities

**In scope:**
- Define the containerised service stack (Argilla + backing services)
- Provide local and production deployment modes
- Document resource requirements and configuration

**Out of scope:**
- Argilla SDK setup (workspaces, schemas, users) — see [Annotation Interface](annotation-interface.md)
- Cloud-hosted deployment — see [ADR-0003](../decisions/0003-infra-self-hosted-only.md)

## Stack

| Service | Role |
|---------|------|
| **Argilla Server** | Annotation web UI + API |
| **PostgreSQL** | User accounts, dataset metadata, annotation storage |
| **Elasticsearch** | Record search and indexing |
| **Redis** | Background task queue |

All services run as Docker containers orchestrated by Docker Compose.

## Deployment Modes

### Local Development

`docker compose up` using the Argilla quickstart or full stack definition. For development, testing, and MAMA cycle iteration.

- Ephemeral by default (data persists only with named volumes)
- Accessible at `localhost`

### Production (On-Premises)

Full Docker Compose stack deployed by IT. Env-based configuration, persistent volumes, internal network access.

- Persistent named volumes for PostgreSQL and Elasticsearch data
- Environment variables for credentials, API URL, resource limits
- Internal URL accessible to annotators on the organisation's network
- No external/internet access required

## Setup Orchestration

Layered approach separating infrastructure from application setup:

```
make up          → starts Docker containers, waits for health checks
chatboteval setup → configures Argilla via SDK (workspaces, schemas, users)
make setup       → chains both: infrastructure + SDK configuration
```

**Rationale:** Docker orchestration is infrastructure concern; Argilla SDK configuration is application logic. Clean separation — standard pattern in Python ML tooling.

Additional Makefile targets: `make down`, `make logs`, `make clean` (remove volumes).

## Resource Requirements

Estimated for annotation workloads (not training/inference):

| Resource | Minimum | Notes |
|----------|---------|-------|
| RAM | ~2 GB | Elasticsearch is the main consumer (JVM heap) |
| Disk | ~10 GB | PostgreSQL + Elasticsearch indices; grows with dataset size |
| CPU | 2 cores | Sufficient for concurrent annotation by <20 users |

Production deployments should monitor Elasticsearch heap usage and adjust `ES_JAVA_OPTS` as dataset size grows.

## Failure Modes

**Elasticsearch memory limits:**
- Elasticsearch requires sufficient JVM heap; defaults may be too low
- Symptom: OOM kills, search timeouts
- Mitigation: set `ES_JAVA_OPTS=-Xms512m -Xmx512m` (minimum) in Compose environment

**PostgreSQL connection refused:**
- Argilla server starts before PostgreSQL is ready
- Mitigation: health checks with `depends_on` conditions in Compose file

**Container health timeouts:**
- Elasticsearch can take 30-60s to become healthy on first start
- Mitigation: configure appropriate health check intervals and start periods

**Data loss on `docker compose down -v`:**
- Removing volumes destroys all annotation data
- Mitigation: document volume management; use `down` (without `-v`) by default

## References

- [Decision 0001: Argilla Annotation Platform](../decisions/0001-annotation-argilla-platform.md) — infrastructure trade-offs
- [Decision 0003: Self-Hosted Only](../decisions/0003-infra-self-hosted-only.md) — self-hosted deployment rationale
- [Decision 0008: Authentication Model](../decisions/0008-authentication-model.md) — auth credentials and API key passed via environment variables at deployment
- [Annotation Interface](annotation-interface.md) — SDK setup that runs after deployment
- Argilla deployment docs: https://docs.argilla.io/latest/
