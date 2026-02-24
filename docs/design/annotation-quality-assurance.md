# Quality Assurance

Annotation quality measurement and guideline iteration via MAMA (Model-Annotate-Measure-Adjust) cycles.

## Responsibilities

**In scope:**
- Measure inter-annotator agreement (IAA) per annotation dimension
- Drive guideline iteration until convergence
- Identify systematic annotator disagreement
- Determine go/no-go decision for scaling annotation

**Out of scope:**
- Annotation task and label definition (see [Annotation Protocol](../methodology/annotation-protocol.md))
- Task distribution mechanics (see [Workspace & Task Distribution](annotation-workspace-task-distribution.md))
- Export format (see [Annotation Export Schema](annotation-export-schema.md))

## MAMA Cycle Workflow

```
1. Load MAMA batch (full overlap)
         │
         ▼
2. All annotators label independently
         │
         ▼
3. Export + calculate IAA per dimension
         │
    ┌────┴────────────────────┐
    ▼                         ▼
α ≥ 0.8                 α < 0.8
Proceed to              ┌────┴────┐
scale annotation        ▼         ▼
                   0.667–0.8   < 0.667
                   Review &    Escalate:
                   revise      schema/guideline
                   guidelines  problem
                        │
                        ▼
                   New MAMA cycle
```

### Steps

1. **Load batch:** Import a MAMA batch with `TaskDistribution.min_submitted` = annotator count (full overlap). All annotators see and label the same records.
2. **Annotate independently:** Annotators label without seeing others' responses. Standard Argilla workflow.
3. **Calculate IAA:** Export submitted annotations, compute Krippendorff's Alpha per dimension within each schema.
4. **Evaluate thresholds:**
   - **α ≥ 0.8** — Good agreement. Proceed to scale annotation (reduce overlap, increase throughput).
   - **0.667 ≤ α < 0.8** — Moderate agreement. Review disagreement cases, revise guidelines, run another MAMA cycle.
   - **α < 0.667** — Poor agreement. Escalate — likely a fundamental schema or guideline problem.
5. **Iterate** until convergence or decision to revise schema.

### IAA Metric

**Primary: Krippendorff's Alpha (α)**

Handles binary data, multiple annotators, and missing values (units labeled by fewer than all annotators). Computed per label independently within each task — e.g., one α for `topically_relevant`, a separate α for `evidence_sufficient`, etc.

**Notation:**
- $U$ — set of annotated units
- $m_u$ — number of annotators who labeled unit $u$
- $k_{ua} \in \{0,1\}$ — label assigned to unit $u$ by annotator $a$
- $n_c = \sum_u \sum_a \mathbf{1}[k_{ua} = c]$ — total count of label value $c$
- $\bar{n} = \sum_u m_u$ — total label count across all units and annotators

```math
\alpha = 1 - \frac{D_o}{D_e}
```

**Observed disagreement** — weighted fraction of annotator-pair disagreements within units:

```math
D_o
= \frac{1}{\bar{n}}
  \sum_{u \in U}
  \frac{1}{m_u - 1}
  \sum_{a \neq a'}
  \delta^2(k_{ua},\, k_{ua'})
```

**Expected disagreement** — disagreement expected by chance given the marginal label distribution:

```math
D_e
= \frac{1}{\bar{n}(\bar{n}-1)}
  \sum_{c \neq k}
  n_c \cdot n_k \cdot \delta^2(c, k)
```

**Distance metric** (nominal/binary):

```math
\delta^2(c, k) =
\begin{cases}
0 & c = k \\
1 & c \neq k
\end{cases}
```

For binary labels, $D_e$ simplifies to $\dfrac{2\, n_0\, n_1}{\bar{n}(\bar{n}-1)}$.

**Interpretation:** $\alpha = 1$ is perfect agreement; $\alpha = 0$ is chance-level agreement; $\alpha < 0$ is systematic disagreement below chance.

---

**Secondary: Pairwise Cohen's Kappa (κ)**

Useful during calibration sessions to identify which annotator pairs diverge most. Limited to two annotators — not suitable as the primary multi-annotator metric, and sensitive to label prevalence skew.

```math
\kappa = \frac{p_o - p_e}{1 - p_e}
```

where $p_o$ = observed proportion of agreement, and $p_e = p_0^2 + p_1^2$ is the expected agreement under marginal independence ($p_c$ = marginal proportion of label $c$).

---

**Not used: Percent Agreement**

Simple to compute but makes no correction for chance agreement, making scores incomparable across labels with different base rates.

---

**Thresholds** (Krippendorff 2004):
- $\alpha \geq 0.8$ — reliable for drawing conclusions
- $0.667 \leq \alpha < 0.8$ — acceptable for exploratory work; warrants guideline revision
- $\alpha < 0.667$ — insufficient reliability; escalate

## Inputs / Outputs

**Inputs:**
- Submitted annotations from both datasets (domain expert + grounding/retrieval)
- MAMA batch metadata (which records are in the overlap set)
- Current annotation guidelines

**Outputs:**
- IAA scores per dimension per schema
- Disagreement analysis (which records, which annotators)
- Revised guidelines (if iteration needed)
- Go/no-go decision for scaling

## Failure Modes

**IAA below minimum threshold:**
- Revise guidelines with concrete examples from disagreement cases
- Run new MAMA cycle with revised guidelines
- If persistent: consider simplifying schema dimensions

**Systematic single-annotator disagreement:**
- One annotator consistently diverges from group consensus
- Individual calibration session needed (walk through examples)
- If unresolvable: reassign annotator or exclude from IAA calculation

**Insufficient overlapping annotations:**
- MAMA batch requires full overlap — if annotators don't complete all records, IAA is unreliable
- Mitigation: monitor completion rates before running IAA calculation
- Adjust `TaskDistribution` or batch size if needed (see [Workspace & Task Distribution](annotation-workspace-task-distribution.md))

**Threshold ambiguity between tasks:**
- Tasks may converge at different rates — Task 3 (5 generation labels, expert annotators) may behave differently from Tasks 1 and 2 (8 retrieval/grounding labels, junior annotators)
- Evaluate each task independently — one can proceed to scale while another iterates

## References

- [Annotation Protocol](../methodology/annotation-protocol.md) — labels being measured per task
- [Annotation UI Presentation](annotation-presentation.md) — question wording and UI visibility contract
- [Decision 0014: IAA Metric](../decisions/0014-annotation-iaa-metric.md) — metric choice rationale and alternatives considered
- [Workspace & Task Distribution](annotation-workspace-task-distribution.md) — TaskDistribution overlap configuration
- [Export Pipeline](annotation-export-pipeline.md) — annotation export consumed by IAA calculation
