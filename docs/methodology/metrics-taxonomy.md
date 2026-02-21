# Metrics Taxonomy

<<<<<<<< HEAD:docs/methodology/metrics-taxonomy.md
This document defines the evaluation metric taxonomy used by this framework. It specifies:
- the metric families used to decompose RAG chatbot performance
- the evaluation unit and notation,
- the required annotation labels each metric depends on
- the deterministic aggregation rules used to compute metric values
========
Status: Accepted
>>>>>>>> bf3cb6f (docs: annotation decisions 0005-0009, rename 0001-0004 to module-prefix scheme, accept 0002):docs/decisions/0002-eval-metrics-taxonomy.md


## Metric families

1) **Retrieval metrics** — search quality of the retrieved context
2) **Grounding metrics** — whether the answer is supported by retrieved evidence
3) **Generation metrics** — answer quality independent of retrieval mechanics


## Evaluation unit

The primary evaluation unit is a **query example**, consisting of:
- a query
- its retrieved top-K context set
- the generated answer.

Individual metrics may use only a subset of these fields (e.g., chunk-level labels, context-set or answer-level labels). However, metric computation follows the same aggregation principle:

1. Compute a score per query example.
2. Report the dataset score as the average across query examples, unless explicitly stated otherwise.


## Core notation

- $i = 1, ..., I$ index queries/examples
- $k = 1, ..., K$ index the rank position within the retrieved top-`K`
- $q_i$ a single query
- $a_i$ a generated answer
- $c_{ik}$ a retrieved context chunk at rank $k$
- $C_i$ the retrieved context set consisting of the top-`K` context chunks


## Taxonomy

### 1) Retrieval metrics

Definition: Evaluates the relevance and ranking quality of retrieved context with respect to the query.<br>
Computed over: queries $q_i$, $i = 1, ..., I$ and the top-_K_ retrieved chunks $c_{ik}$, $k = 1, ..., K$

- **Topical Precision@K:** 
  - Of the top-_K_ retrieved chunks, what fraction are topically relevant?
  - Connected label: `topically_relevant`, $t_{ik} \in \{0,1\}$
```math
  \text{TopicalPrecision@K}
  \,=\,
  \frac{1}{I}\sum_{i=1}^{I}\left(\frac{1}{K}\sum_{k=1}^{K} t_{ik}\right)
```
- **Sufficiency Hit@K:**
  - For what share of queries is there at least one sufficient-evidence chunk in the top-_K_?
  - Connected label: `evidence_sufficient`, $s_{ik} \in \{0,1\}$
```math
  \text{SufficiencyHit@K}
  =
  \frac{1}{I}\sum_{i=1}^{I}\left[\sum_{k=1}^{K} s_{ik} \ge 1\right]
```
- **Sufficiency Rate@K:** 
  - Of the top-_K_ retrieved chunks, what fraction are individually sufficient evidence?
  - Connected label: `evidence_sufficient`, $s_{ik} \in \{0,1\}$
```math
  \text{SufficiencyRate@K}
  =
  \frac{1}{I}\sum_{i=1}^{I}\left(\frac{1}{K}\sum_{k=1}^{K} s_{ik}\right)
```
- **Misleading Context Rate@K:** 
  - Of the top-_K_ retrieved chunks, what fraction are misleading with respect to answering the query (risk-inducing if used as evidence)?
  - Connected label: `misleading`, $m_{ik} \in \{0,1\}$
```math
  \text{MisleadingContextRate@K}
  =
  \frac{1}{I}\sum_{i=1}^{I}\left(\frac{1}{K}\sum_{k=1}^{K} m_{ik}\right)
 ```
- **Mean Reciprocal Rank@K:**
  - How high in the ranking is the first topically relevant chunk?
  - Connected label: `topically_relevant`, $t_{ik} \in \{0,1\}$
```math
  k_i^* = \min \{ k \in \{1,\dots,K\} : t_{ik} = 1 \}
```
```math
  RR@K(i)
  =
  \begin{cases}
  \dfrac{1}{k_i^*}
  & \text{if } k_i^* \text{ exists} \\
  0
  & \text{otherwise}
  \end{cases}
```
```math
  \text{MRR@K}
  =
  \frac{1}{I}\sum_{i=1}^{I} RR@K(i)
```
- **Normalized Discounted Cumulative Gain@K:** 
  - How well does the ranking prioritize highly relevant chunks?
  - Connected labels: grades derived from `topically_relevant` and `evidence_sufficient`
```math
  w_{ik}
  =
  \begin{cases}
  2 & \text{if } s_{ik}=1\\
  1 & \text{if } t_{ik}=1 \text{ and } s_{ik}=0\\
  0 & \text{otherwise}
  \end{cases}
```
```math
  DCG@K(i)
  =
  \sum_{k=1}^{K}
  \frac{2^{w_{ik}}-1}{\log_2(k+1)}
```
```math
  NDCG@K
  =
  \frac{1}{I}
  \sum_{i=1}^{I}
  \frac{DCG@K(i)}{IDCG@K(i)}
```

### 2) Grounding metrics

Definition: Evaluates whether the generated answer is supported, contradicted, or fabricated relative to the retrieved context set.<br>
Computed over: answer $a_i$ and retrieved context set $C_i$

- **Grounding Presence Rate:**
  - Share of answers for which at least one substantive claim is supported by the provided context.
  - Connected label: `support_present`, $g_i \in \{0,1\}$
```math
  \text{GroundingPresenceRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} g_i
```
- **Unsupported Claim Rate:**
  - Share of answers containing at least one unsupported (hallucinated) substantive claim.
  - Connected label: `unsupported_claim_present`, $v_i \in \{0,1\}$
```math
  \text{UnsupportedClaimRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} v_i
```
- **Contradiction Rate:**
  - Share of answers containing at least one claim contradicted by the provided context.
  - Connected label: `contradicted_claim_present`, $x_i \in \{0,1\}$
```math
  \text{ContradictionRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} x_i
```
- **Citation Presence Rate:**
  - Share of answers that contain any citation marker.
  - Connected label: `source_cited`, $z_i \in \{0,1\}$
```math
  \text{CitationPresenceRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} z_i
```
- **Conditional Fabrication Rate:**
  - Among answers that cite something, how often is at least one citation fabricated?
  - Connected labels: `source_cited`, $z_i \in \{0,1\}$; `fabricated_source`, $f_i \in \{0,1\}$
  - This metric is computed conditionally over the subset of examples where $z_i=1$.
```math
  \text{ConditionalFabricationRate}
  =
  \frac{\sum_{i=1}^{I} z_i f_i}{\sum_{i=1}^{I} z_i}
```

### 3) Generation metrics

Definition: Evaluates the appropriateness, usefulness, and safety of the generated answer with respect to the user’s request and system constraints.<br>
Computed over: query $q_i$ and answer $a_i$

- **Proper Action Rate:**
  - Share of answers where the model chose the appropriate action (e.g., answer / clarify / refuse) given the query and system constraints.
  - Connected label: `proper_action`, $d_i \in \{0,1\}$
```math
  \text{ProperActionRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} d_i
```
- **On-Topic Rate:**
  - Share of answers that substantively address the user’s request.
  - Connected label: `response_on_topic`, $o_i \in \{0,1\}$
```math
  \text{OnTopicRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} o_i
```
- **Helpfulness Rate:**
  - Share of answers that would enable a typical user to make progress on the task.
  - Connected label: `helpful`, $h_i \in \{0,1\}$
```math
  \text{HelpfulnessRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} h_i
```
- **Incompleteness Rate:**
  - Share of answers that fail to cover one or more required parts of the query or task framing.
  - Connected label: `incomplete`, $n_i \in \{0,1\}$
```math
  \text{IncompletenessRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} n_i
```
- **Unsafe Content Rate:**
  - Share of answers that contain content violating safety or policy constraints.
  - Connected label: `unsafe_content`, $r_i \in \{0,1\}$
```math
  \text{UnsafeContentRate}
  =
  \frac{1}{I}\sum_{i=1}^{I} r_i
```
