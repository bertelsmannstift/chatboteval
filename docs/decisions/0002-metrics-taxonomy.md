# 0002: Metrics Taxonomy

Status: Draft


## Decision

We structure evaluation metrics into three families:

1) **Retrieval metrics** — search quality
2) **Grounding metrics** — evidence support
3) **Generation metrics** — answer quality


## Taxonomy

### 1) Retrieval metrics

Goal: Did we retrieve documents relevant to the query?<br>
Defined over: queries $q_i$, $i = 1, ..., I$ (where $I$ is the total number of queries), and the top-_K_ retrieved chunks $c_{ik}$, $k = 1, ..., K$

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

Goal: Does the answer use the retrieved evidence?<br>
Defined over: answer $a_i$ and retrieved context set $C_i$

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
```math
  \text{ConditionalFabricationRate}
  =
  \frac{\sum_{i=1}^{I} z_i f_i}{\sum_{i=1}^{I} z_i}
```

### 3) Generation metrics

Goal: Is the response appropriate and useful for the user?<br>
Defined over: query $q_i$ and answer $a_i$

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


## Rationale

- **Three-family decomposition**: Separates failure modes, keeps metrics interpretable and matches common RAG evaluation decompositions. 
- **Label-first metric design**: Metrics are defined as simple aggregations of explicitly annotated binary labels. This keeps estimands transparent and makes metric values auditable.
- **No recall-style retrieval metrics**: Typically, we do not have an enumerated set of all relevant chunks in the corpus, so recall@k is not estimable without unrealistic annotation assumptions.
- **No explicit correctness metric**: For many chatbot queries there is no single unambiguous “correct” response, and correctness often requires deep domain expertise.
- **Ordinal graded relevance for NDCG**: Evidence-sufficient chunks are treated as strictly more relevant than merely topically relevant chunks. The gain levels (2,1,0) encode this ordering without implying cardinal utility differences.

## Consequences

- Reporting should summarize results by family first, then drill down by metric.
- Each metric is computable as a deterministic aggregation of one or more labels.
- Metric computation is pure post-processing: Once labels are produced, metrics are computed without additional model calls or heuristic scoring.
