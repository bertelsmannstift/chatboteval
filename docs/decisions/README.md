# Decision Records

This directory contains architectural and tooling decisions with rationale and consequences.

Each decision document follows this structure:
- **Status:** Draft / Accepted / Superseded
- **Decision:** What we chose
- **Rationale:** Why we chose it (with alternatives considered)
- **Consequences:** Implications (positive, negative, neutral)

## Filename Prefixes

Filenames are prefixed by pipeline module:

| Prefix | Module | Covers |
|--------|--------|--------|
| `annotation-` | Annotation interface | Argilla platform, tasks, schema, UX, auth, IAA, import/export, user mgmt, workspace, source adapters |
| `eval-` | Evaluation pipeline | Metrics taxonomy, evaluation mode constraints, synthetic test sets |
| `infra-` | Infrastructure | Library architecture, CLI design, installation/setup UX, deployment, packaging |

## Index

- [0001: Annotation — Argilla Platform](0001-annotation-argilla-platform.md) — Accepted: use Argilla for human annotation interface
- [0002: Eval — Metrics Taxonomy](0002-eval-metrics-taxonomy.md) — Draft: structure evaluation metrics into retrieval/grounding/generation families
- [0003: Infra — Self-Hosted Deployment](0003-infra-self-hosted-only.md) — Accepted: cloud-hosted deployment out of scope
- [0004: Eval — Offline Evaluation Only](0004-eval-offline-only.md) — Accepted: no real-time chatbot integration
- [0005: Annotation Export Schema](0005-annotation-export-schema.md) — Draft: flat CSV export, one row per annotator response; three task-specific schemas
- [0006: Annotation Tasks](0006-annotation-tasks.md) — Draft: three annotation tasks (retrieval/grounding/generation) with binary labels, logical constraints, and formal units of annotation
- [0007: Annotation UI Presentation](0007-annotation-presentation.md) — Draft: annotator question wording, per-task UI visibility contract, and presentation design
- [0008: Annotation Authentication Interface](0008-annotation-interface-auth.md) — Accepted: Argilla built-in auth with role mapping
- [0009: Annotation Schema Configurability](0009-annotation-schema-configurability.md) — Accepted: hardcoded schemas for v1.0, configurability deferred
- [0010: Annotation Entrypoints](0010-annotation-entrypoints.md) — Under Discussion: annotation CLI scope (URL / Python API / CLI options)
- [0011: Infra — CLI Commands](0011-infra-cli-commands.md) — Draft: full CLI reference (annotation + product commands); generate / eval / train structure (v1.1+ scope)
- [0012: Infra — Installation & Zero-Config Setup](0012-infra-installation-setup-ux.md) — Draft: optional extras, no-surprise install philosophy, setup wizard UX
- [0013: Annotation Multi-Dataset Architecture](0013-annotation-multi-dataset-architecture.md) — Draft: three separate datasets per task; rationale for why a unified schema is not viable
- [0014: Annotation IAA Metric](0014-annotation-iaa-metric.md) — Draft: Krippendorff's Alpha as primary IAA metric; Cohen's Kappa secondary for pairwise calibration
- [0015: Infra — Library-First Architecture](0015-infra-library-first-architecture.md) — Draft: Python API is primary interface; CLI commands are thin wrappers that delegate to the library
- [0016: Annotation Source Adapter](0016-annotation-source-adapter.md) — Draft: canonical import schema with source-specific adapter modules; PB adapter mapping
