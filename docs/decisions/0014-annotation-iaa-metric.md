# 0014: IAA Metric — Krippendorff's Alpha

Status: Draft


## Decision

**Primary metric: Krippendorff's Alpha (α)** — computed per label dimension, per dataset.

**Secondary metric: Pairwise Cohen's Kappa (κ)** — used during calibration sessions only to identify which annotator pairs diverge most.

**Not used: Percent Agreement** — rejected (no chance correction).

Thresholds for MAMA cycle go/no-go decisions (Krippendorff 2004):
- α ≥ 0.8 — reliable; proceed to scale annotation
- 0.667 ≤ α < 0.8 — moderate; revise guidelines, re-run MAMA cycle
- α < 0.667 — insufficient reliability; escalate (likely schema or guideline problem)


## Rationale

**Krippendorff's alpha was chosen because it handles the specific constraints of this annotation setup:**

1. **Variable annotator counts per record.** During scale annotation (post-MAMA), not all records will be labeled by all annotators. Alpha handles missing values natively — units annotated by fewer than all annotators are included in the calculation rather than discarded.

2. **Multiple annotators.** Alpha generalises to any number of annotators. Cohen's kappa is strictly pairwise; Fleiss's kappa handles multiple annotators but requires complete, balanced designs (all annotators label all records).

3. **Binary labels.** Alpha is defined for nominal data with a binary distance metric (δ = 0 if equal, 1 if different). No adaptation required.

4. **Single formula across the annotation lifecycle.** The same metric applies during MAMA cycles (full overlap) and scale annotation (partial overlap), so thresholds are comparable across iterations.

**Cohen's kappa retained as a secondary diagnostic.** Pairwise kappa is useful during calibration to answer "which two annotators disagree most?" — a question alpha doesn't answer directly since it aggregates across all annotators. Limited to calibration sessions; not used for go/no-go decisions.


## Alternatives Considered

**Fleiss's Kappa**

Generalises Cohen's kappa to multiple annotators. Requires a complete design: every annotator must label every record. Does not handle missing data.

Rejected: not suitable for scale annotation where overlap is partial. Would require discarding all records not labeled by the full annotator set, reducing the effective sample size.

**Percent Agreement**

Proportion of annotator pairs who agree on a label. Simple to compute and explain.

Rejected: makes no correction for chance agreement. Labels with high base rates (e.g., `topically_relevant` where most chunks are relevant) will show high percent agreement by chance, inflating scores and making them incomparable across labels.

**Cohen's Kappa as primary**

Pairwise only — requires aggregating over annotator pairs when more than two annotators are present.

Rejected as primary: pairwise averaging is not equivalent to multi-annotator alpha, and the result depends on how pairs are formed. Retained as secondary for pairwise diagnostics where it is the correct tool.


## Consequences

- IAA is computed per label dimension per dataset — one alpha score per (label, task)
- Threshold evaluation determines per-task go/no-go: tasks can proceed to scale independently
- `record_uuid` enables tracking disagreement across tasks for the same input (cross-task analysis)
- Implementation: `krippendorff` Python library or equivalent

See [Quality Assurance](../design/annotation-quality-assurance.md) for MAMA cycle workflow and full metric formulas.


## References

- Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage. — threshold values and metric definition
- [Quality Assurance](../design/annotation-quality-assurance.md) — MAMA cycle workflow, formulas, thresholds
- [Annotation Protocol](../methodology/annotation-protocol.md) — labels being measured
- [Export Pipeline](../design/annotation-export-pipeline.md) — annotation export consumed by IAA calculation
