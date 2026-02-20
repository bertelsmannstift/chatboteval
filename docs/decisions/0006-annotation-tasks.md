# 0006: Annotation tasks

Status: Draft


## Decision

We define three distinct annotation tasks, corresponding to the three metric families defined in the metrics taxonomy:
1. Retrieval
2. Grounding
3. Generation

Each task:
- consists of binary questions
- uses multilabel (non–one-hot) annotations subject to logical consistency constraints
- requires all fields to be completed (no missing values)
- produces a multilabel vector per annotated unit


## Task 1: Retrieval annotation

### Unit of annotation

- For each query $𝑞_i$, we consider a ranked list of retrieved chunks: ($𝑞_i$, $c_{i1}$), ($𝑞_i$, $c_{i2}$), $...$, ($𝑞_i$, $c_{ik}$)
- Retrieval annotation is performed per query-chunk pair ($𝑞_i$, $c_{ik}$)

### Labels

For each pair ($𝑞_i$, $c_{ik}$), annotators must assign:
- `topically_relevant` $∈ {0,1}$
- `evidence_sufficient` $∈ {0,1}$
- `misleading` $∈ {0,1}$

### Label semantics

- `topically_relevant`: The retrieved chunk contains information that is substantively related to the query.
- `evidence_sufficient`: The chunk provides sufficient evidence to support answering the query, even if additional chunks could also be relevant.
- `misleading`: The retrieved chunk contains information that could plausibly lead to an incorrect or distorted answer if used.

### Logical constraints

The following consistency constraints apply:
1. `evidence_sufficient` implies `topically_relevant`, i.e., `evidence_sufficient` $=1⇒$ `topically_relevant` $=1$
2. `evidence_sufficient` and `misleading` cannot co-occur, i.e., `evidence_sufficient` $=1⇒$ `misleading` $=0$


## Task 2: Grounding annotation

### Unit of annotation

- For each answer $a_i$, we consider the full retrieved context set $C_i$ shown to the model
- Grounding annotation is performed per answer-context pair ($a_i$, $C_i$)

### Labels

For each pair ($a_i$, $C_{i}$), annotators must assign:
- `support_present` $∈ {0,1}$
- `unsupported_claim_present` $∈ {0,1}$
- `contradicted_claim_present` $∈ {0,1}$
- `source_cited` $∈ {0,1}$
- `fabricated_source` $∈ {0,1}$

### Label semantics

- `support_present`: At least one substantive claim in the answer is supported by evidence contained in the provided context set $C_{i}$.
- `unsupported_claim_present`: The answer contains at least one substantive claim that is not supported by the provided context set $C_{i}$ (i.e., the context does not provide evidence for it).
- `contradicted_claim_present`: The provided context set $C_{i}$ contains information that contradicts at least one substantive claim in the answer.
- `source_cited`: The answer contains at least one citation marker (in the system’s expected citation format).
- `fabricated_source`: The answer cites at least one source that cannot be matched to the retrieved context set $C_{i}$ shown (or is otherwise clearly invented).

### Logical constraints

The following consistency constraints apply:
1. `contradicted_claim_present` implies `unsupported_claim_present`, i.e., `contradicted_claim_present` $=1⇒$ `unsupported_claim_present` $=1$
2. `fabricated_source` implies `source_cited`, i.e., `fabricated_source` $=1⇒$ `source_cited` $=1$


## Task 3: Generation annotation

### Unit of annotation

- For each query $𝑞_i$, we consider the model’s generated answer $a_i$
- Generation annotation is performed per query–answer pair ($q_i$, $a_i$)

### Labels

For each pair ($q_i$, $a_i$), annotators must assign:
- `proper_action` $∈ {0,1}$
- `response_on_topic` $∈ {0,1}$
- `helpful` $∈ {0,1}$
- `incomplete` $∈ {0,1}$
- `unsafe_content` $∈ {0,1}$

### Label semantics

- `proper_action`: The response selects the appropriate response type (e.g., answer, refusal, clarification request) given the query and system constraints.
- `response_on_topic`: The response substantively addresses the user’s request.
- `helpful`: The response would enable a typical user to make progress on the task.
- `incomplete`: The response fails to cover one or more required parts of the query or task framing.
- `unsafe_content`: The response contains content that violates safety or policy constraints.


## Rationale

- **Three distinct annotation tasks**: Separating retrieval, grounding, and generation keeps each task’s unit of annotation conceptually coherent and avoids NA-heavy schemas that dilute rater attention and agreement.
- **Binary labels**: Yes/no judgments minimize cognitive load and ambiguity, improving consistency and making downstream aggregation into metrics straightforward. Directly supports multilabel classification.
- **No missing values**: Requiring complete fields prevents ambiguous denominators and silent missingness bias, ensuring metrics are well-defined across all annotated units.
- **Answer-level grounding labels**: Answer-level presence flags capture the dominant grounding failure modes with far lower burden than claim-level decomposition, improving reliability and scalability.


## Consequences

- **Annotation interface structure**: The UI must implement three dedicated views aligned to the three units of annotation rather than one generic sheet.
- **Constraint enforcement**: The UI should prevent invalid label combinations at entry time (disable/auto-resolve) so annotators cannot produce logically inconsistent rows.
- **Strict schema validation**: The data pipeline must reject or normalize missing/invalid values and constraint violations to keep metric computation deterministic and auditable.
