# chatboteval Documentation

## What This Is

A general-purpose, open-source Python framework for evaluating RAG (retrieval-augmented generation) chatbots. Combines a **human annotation interface** for domain experts to label query-response pairs and an **automated evaluation pipeline** using transformer-based models.

**Pilot project:** Bertelsmann Stiftung's PublikationsBot (internal chatbot for ~3,000 grey publications).

**Open-source goal:** General-purpose tool applicable to any RAG system.

## Core Components

1. **Annotation Interface** — Web-based UI where reviewers label query-response pairs (correctness, grounding, relevance, harm/bias)
2. **Evaluation Framework** — Reproducible ML pipeline for training and inference on evaluation models (DeBERTa, SBERT, cross-encoders)
3. **Query Generation** — Separate workflow for synthetic query generation and prompt variation (out of core package scope)

## Non-Goals

- Cloud-hosted deployment (GDPR/data sensitivity requires self-hosted only)
- German UI localisation (English interface, revisit if needed)
- Real-time chatbot integration (evaluates captured query-response pairs, not live traffic)
- Custom frontend from scratch (preference for turnkey/existing tools)

## Architecture

```
chatboteval/
├── src/chatboteval/          # Main Python package
│   ├── data/                 # Data loading, Argilla integration
│   ├── training/             # ML model training
│   ├── inference/            # Model scoring
│   └── cli.py                # CLI entrypoints
├── apps/annotation/          # Argilla deployment infrastructure
│   └── docker-compose.yml    # Argilla + PostgreSQL + Elasticsearch
└── docs/                     # Documentation (this directory)
```

## Getting Started

_(To be expanded with installation and quickstart guides)_

## Documentation Map

### Decisions

Key architectural and tooling decisions with rationale:

- [Decision Records Index](decisions/README.md)

### Design

Component design documents covering responsibilities, interfaces, and failure modes:

- [Design Documents Index](design/README.md)

### Reference

- [Glossary](glossary.md) — Key terms and concepts

## Tracking & Contributing

- **Issues:** Track work via [GitHub Issues](https://github.com/bertelsmannstift/chatboteval/issues)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for PR workflow, commit conventions, and code standards

## Context

**Collaboration:** Hertie School Data Science Lab × Bertelsmann Stiftung
**Timeline:** 6-month pilot (Jan–Jun 2026)
**Team:** Sascha Göbel (faculty lead), Henry Baker, Luis Fernando Ramírez Ruiz, Drew Dimmery
**Licence:** MIT
