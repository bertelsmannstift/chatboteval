# Design Documents

This directory contains living component design documents covering responsibilities, interfaces, and failure modes.

Each design document focuses on:
- **Responsibilities and boundaries** — What this component does and doesn't do
- **Inputs/outputs (contracts)** — Data interfaces and APIs
- **Failure modes / edge cases** — How things can/might break and how we handle it
- **Links to relevant issues** — Active work and tracking

## Index

- [Annotation Interface](annotation-interface.md) — Human annotation workflow and Argilla integration
- [Synthetic Test Set](synthetic-test-set.md) — Query generation, prompt variation, and response collection
- [Reference-Based Evaluation](eval-reference-based.md) — Supervised evaluation using human-annotated ground truth
- [Reference-Free Evaluation](eval-reference-free.md) — LLM-as-judge and heuristic evaluation without ground truth
