# 0002: Metrics Taxonomy

Status: Draft


## Decision

We structure evaluation metrics into three families:

1) **Retrieval metrics** — search quality
2) **Grounding metrics** — evidence support / faithfulness
3) **Generation metrics** — answer quality


## Taxonomy

### 1) Retrieval metrics (depend on query, retrieved context)

Goal: *Did we retrieve documents relevant to the query?*

- **Context precision (Precision@k):** of the top-k retrieved chunks, how many are relevant?
- **MRR:** how high up in the results was the first relevant chunk?
- **NDCG:** how well does the ranking prioritize highly relevant chunks?
- **Weighted relevance mass:** what proportion of total relevance is captured within top-k?

### 2) Grounding metrics (depend on answer, retrieved context)

Goal: *Does the answer use the retrieved evidence?*

- **Faithfulness / groundedness:** are claims in the answer backed by the retrieved context?
- **Contradiction rate:** are any claims contradicted by the retrieved context?
- **Citation coverage:** does the answer correctly attribute claims to specific chunks/pages (where citations exist)?

### 3) Generation metrics (depend on query, answer)

Goal: *Is the answer good / correct / complete?*

- **Answer relevance:** does the response address the user's prompt?
- **Correctness:** are factual statements and conclusions accurate given the query/task framing?
- **Comprehensiveness:** does the answer cover all required parts of a multi-part query?


## Consequences

- We separate failure modes: retrieval vs grounding vs generation.
- Annotation rubrics should map cleanly onto these three families.
- Reporting should summarize results by family first, then by metric.
