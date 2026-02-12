# Glossary

## General Terms

**RAG (Retrieval-Augmented Generation)** — Pattern where LLMs retrieve relevant documents before generating responses, grounding answers in evidence.

**Query-response pair** — Single evaluation unit: user query + chatbot response + optional retrieved documents + metadata.

**Ground truth** — Human-labelled annotations used as training targets for evaluation models.

**Inter-annotator agreement (IAA)** — Measure of consistency between independent annotators (e.g., Cohen's kappa, Krippendorff's alpha).

## Evaluation Dimensions

**Correctness** — Are factual statements and conclusions accurate given the query/task framing?

**Grounding / Faithfulness** — Are claims in the answer backed by the retrieved context? Is anything contradicted?

**Relevance** — Does the response address the user's prompt?

**Harm / Bias** — Does the response contain harmful content, biased language, or inappropriate recommendations?

## Architecture Components

**Annotation interface** — Web-based UI where domain experts label query-response pairs (powered by Argilla).

**Evaluation framework** — ML pipeline for training and inference on evaluation models (DeBERTa, SBERT, cross-encoders).

**Batch** — Collection of query-response pairs assigned to annotators as a single unit of work.

**Task distribution** — Automatic allocation of annotation tasks to reviewers, removing completed items from queues.

## Models & Methods

**DeBERTa** — Transformer model used for multi-label classification (correctness, grounding, relevance, harm).

**SBERT (Sentence-BERT)** — Sentence embedding model used for semantic similarity scoring.

**Cross-encoder** — Pairwise scoring model that evaluates query-response relevance by encoding both together.

**Multi-label classification** — Prediction task where each instance can have multiple independent labels (vs multi-class: one label only).

## Project-Specific

**PublikationsBot** — Bertelsmann Stiftung's internal RAG chatbot for searching ~3,000 grey publications (pilot application).

**BF** — Bertelsmann Foundation (project collaborator and pilot deployment site).

**Hertie** — Hertie School Data Science Lab (project lead, development and methodology).
