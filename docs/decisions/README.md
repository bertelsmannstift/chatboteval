# Decision Records

This directory contains architectural and tooling decisions with rationale and consequences.

Each decision document follows this structure:
- **Status:** Draft / Accepted / Superseded
- **Decision:** What we chose
- **Rationale:** Why we chose it (with alternatives considered)
- **Consequences:** Implications (positive, negative, neutral)

## Index

- [0001: Annotation — Argilla Platform](0001-annotation-argilla-platform.md) — Accepted: use Argilla for human annotation interface
- [0003: Infra — Self-Hosted Deployment](0003-infra-self-hosted-only.md) — Accepted: cloud-hosted deployment out of scope
- [0004: Eval — Offline Evaluation Only](0004-eval-offline-only.md) — Accepted: no real-time chatbot integration
- [0005: Annotation Export Schema](0005-annotation-export-schema.md) — Draft: flat CSV export, one row per annotator response; three task-specific schemas
- [0007: Invocation Surface](0007-packaging-invocation-surface.md) — Accepted: two supported invocation surfaces (Python API and CLI)
- [0007: Annotation UI Presentation](0007-annotation-presentation.md) — Draft: annotator question wording, per-task UI visibility contract, and presentation design

- [0008: Annotation Authentication Interface](0008-annotation-interface-auth.md) — Accepted: Argilla built-in auth with role mapping
- [0009: Annotation Schema Configurability](0009-annotation-schema-configurability.md) — Accepted: hardcoded schemas for v1.0, configurability deferred
