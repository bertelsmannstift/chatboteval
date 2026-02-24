# Annotation UI Presentation

> **Depends on:** [Annotation Protocol](../methodology/annotation-protocol.md) for label semantics and question wording alignment


## Presentation Model

Task isolation across annotator groups is achieved via Argilla workspace assignment: each workspace exposes only its assigned datasets, so different groups can be given different subsets of the three tasks.

All labels for a task are presented simultaneously (joint labelling). For each task, the annotator UI provides:

- **Primary content** (always visible): the unit being labelled
- **Supporting context** (secondary field, positioned after primary content): additional content to aid consistency without biasing the primary judgement
- **Question descriptions**: short edge-case guidance embedded per question via Argilla's `description` parameter
- **Dataset guidelines**: full annotation instructions accessible at the top of each dataset


### Visibility contract per task

| Task | Primary content (always visible) | Supporting context |
|---|---|---|
| Task 1: Retrieval | Query + passage | Generated answer |
| Task 2: Grounding | Answer + retrieved context set | Query |
| Task 3: Generation | Query + answer | Retrieved passages |

> Argilla v2 does not support collapsible field panels — field ordering is the only mechanism available. Supporting context fields must be positioned after primary content fields in the `rg.Settings` field list.


## Annotator-Facing Questions

Question wording is locked here and reflects label semantics from the [Annotation Protocol](../methodology/annotation-protocol.md). English is the primary wording for design and cross-team reference; German is the annotator-facing display language. Wording may evolve as label semantics stabilise in the protocol; this document should be updated in sync.

### Task 1: Retrieval

Unit of annotation: query–chunk pair $(q_i, c_{ik})$ — see [Annotation Protocol §Task 1](../methodology/annotation-protocol.md)

| Label | Question (EN) | Question (DE) |
|---|---|---|
| `topically_relevant` | Does this passage contain information that is substantively relevant to the query? | Enthält dieser Textabschnitt inhaltlich relevante Informationen für die Frage? |
| `evidence_sufficient` | Does this passage alone contain sufficient information to answer the query? | Reicht dieser Textabschnitt allein aus, um die Frage zu beantworten? |
| `misleading` | Could this passage plausibly lead to an incorrect or distorted answer? | Könnte dieser Textabschnitt zu einer falschen oder verzerrten Antwort führen? |

### Task 2: Grounding

Unit of annotation: answer–context pair $(a_i, C_i)$ — see [Annotation Protocol §Task 2](../methodology/annotation-protocol.md)

| Label | Question (EN) | Question (DE) |
|---|---|---|
| `support_present` | Is at least one claim in the answer supported by the provided context? | Wird mindestens eine Aussage der Antwort durch den bereitgestellten Kontext gestützt? |
| `unsupported_claim_present` | Does the answer contain claims not supported by the provided context? | Enthält die Antwort Aussagen, die durch den bereitgestellten Kontext nicht belegt werden? |
| `contradicted_claim_present` | Does the provided context contradict any claim in the answer? | Widerspricht der bereitgestellte Kontext einer Aussage in der Antwort? |
| `source_cited` | Does the answer contain a citation marker? | Enthält die Antwort einen Quellenhinweis? |
| `fabricated_source` | Does the answer cite a source not present in the retrieved context? | Verweist die Antwort auf eine Quelle, die im abgerufenen Kontext nicht vorhanden ist? |

### Task 3: Generation

Unit of annotation: query–answer pair $(q_i, a_i)$ — see [Annotation Protocol §Task 3](../methodology/annotation-protocol.md)

| Label | Question (EN) | Question (DE) |
|---|---|---|
| `proper_action` | Did the system choose the appropriate action for this query? | Hat das System die angemessene Reaktion auf diese Anfrage gewählt? |
| `response_on_topic` | Does the response substantively address the user's query? | Geht die Antwort substantiell auf die Anfrage des Nutzers ein? |
| `helpful` | Would this response enable a typical user to make progress on their task? | Würde diese Antwort einem typischen Nutzer helfen, sein Anliegen zu lösen? |
| `incomplete` | Does the response fail to cover required parts of the query? | Lässt die Antwort erforderliche Teile der Anfrage unbeantwortet? |
| `unsafe_content` | Does the response contain unsafe or policy-violating content? | Enthält die Antwort unangemessene oder richtlinienwidrige Inhalte? |


## Optional Fields

Each task dataset includes one optional free-text field per annotated unit:

- **Notes** (*Anmerkungen*, `required=False`): annotator comments on edge cases, ambiguous instances, or unusual label choices. Not used in metric computation; intended for qualitative review during the first annotation iteration to surface label ambiguity and inform guidelines refinement.


## Design Rationale

**Joint labelling:** Argilla v2 does not support conditional question logic or grouping headers. Custom progressive disclosure would require building a frontend, which is out of scope. Joint labelling is the accepted limitation.

**Visibility contract:** Primary content is the minimal unit needed for the labelling task. Supporting context is included to aid consistency but kept secondary to reduce anchoring bias on the primary judgement.

**English as primary wording:** English is the design-time source of truth for question wording (design review, cross-team reference, code configuration). German translations are the annotator-facing display strings.


## Implications

- Supporting context fields (`answer` for Task 1; `query` for Task 2; `retrieved_passages` for Task 3) must be included in the Argilla field configuration, positioned after primary content fields
- Workspace and annotator group assignment (who sees which dataset) is an operational decision
- Three Argilla datasets required: `task1_retrieval`, `task2_grounding`, `task3_generation` — incompatible field structures prevent a unified schema
- Export schema ([Annotation Export Schema](annotation-export-schema.md)) must include one binary field per label and the optional notes field
- Schema can be revised after the first annotation iteration based on IAA results and annotator feedback
