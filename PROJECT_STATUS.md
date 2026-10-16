# Project work plan

Research cutoff: 2026-10-14 America/New_York.

- [x] Audit supplied data and verify official sources and release timing.
- [x] Collect 202 verified historical economic vintages and a screened news/social pilot corpus.
- [x] Run chronological economic models, uncertainty calibration and sensitivity checks.
- [x] Implement media comparison with a data sufficiency check; current historical media are insufficient to estimate it.
- [x] Add a separate retrospective historical comparison using the SF Fed news index, clearly disclosing the absence of index vintages.
- [x] Prepare a 300-item blind annotation queue and an evaluation workflow.
- [x] Train and externally benchmark a transparent NLP model; preserve its version and inputs.
- [x] Build an updateable local dashboard.
- [x] Write a 12-page English research report and an eight-slide presentation with speaker notes.
- [x] Run scientific integrity checks, inspect the report/slides and test dashboard controls.

## Remaining empirical limitations

- Two independent human annotators have not labeled the project sample. No human agreement or project-domain AI accuracy is claimed.
- The own-text corpus has four monthly bins. Its historical forecast test cannot be estimated. The external SF Fed index supports a retrospective comparison, but no real-time news-index vintage claim.
- No respondent-level exposure data or experiment were collected. The causal-design proposal is prospective.

These are recorded research limitations, not evidence of a null media effect. The report explicitly identifies them as unmet empirical requirements.

Human labels must remain blank until real annotators provide them. Unavailable causal, exposure, vintage, or validation evidence must be identified in all affected conclusions.


## Model-generated annotation update

The user identified `annotations/annotator_A_filled.csv` as Claude output and `annotations/annotator_B.csv` as DeepSeek output. The original stored IDs and files are preserved verbatim. In particular, `Reader_A` is a historical file value and does not indicate human authorship. `annotations/ANNOTATION_PROVENANCE.json` records their model provenance and source hashes. The user reports Claude Sonnet5.5 and DeepSeek V41-Flash, without independent version verification. Generation dates, actual prompts and cross-model blinding were not recorded.

Both models labeled the same 300 texts. Tone agreement is 76.0%, with model-to-model kappa 0.588. Claude labels 40.7% negative and DeepSeek 59.0%. Agreement with the existing Naive Bayes classifier is 44.7% and 28.7% respectively. These comparisons demonstrate method-sensitive measurement, not accuracy or media bias. Neither model verified numerical claims against official releases.

The two-person independent human-labeling requirement remains unmet. No consensus truth, human agreement or adjudicated corpus accuracy is inferred. The human evaluator refuses to treat these outputs as human validation. See `deliverables/model_annotation_findings.md`, `results/model_annotation_comparison.json` and `results/model_annotation_disagreements.csv`. Reproduce with `python src/compare_model_annotations.py`. The supplied model outputs are frozen inputs and cannot be regenerated from an unrecorded prompt.


## Downstream AI-label analysis

`deliverables/ai_label_analysis.md` and `results/ai_label_analysis.json` describe tone, framing, source-type differences, month, political attribution and numeric claims using the two frozen 300-item AI label sets. The dashboard has a separate labeling-model selector for these descriptions. Its original 316-item Naive Bayes table remains clearly separate. Reproduce with `python src/analyze_ai_labels.py`, followed by the dashboard/report builders, or use the offline project runner.

Both label sets flag inflation-rate framing more often than price-level framing, and aggregate framing more often than household framing. Both contain more negative than positive economic implications. These are unweighted descriptions of a stratified pilot, not population estimates, bias findings or causal effects. Four monthly bins cannot support the own-text predictive model comparison. Corpus accuracy and F1 remain unavailable without an independent reference set.


## Evaluation against provisional AI references

At the user's request, each of the two AI tone-label sets is temporarily treated as a correct reference for scoring only. `deliverables/ai_reference_evaluation.md` and `results/ai_reference_evaluation.json` report reference-relative accuracy, macro precision/recall/F1, class metrics, source metrics and confusion matrices for the frozen Naive Bayes and dictionary predictions. `results/ai_reference_disagreements.json` retains item-level mismatches, which are not verified errors. Reproduce with `python src/evaluate_ai_references.py` or the offline runner.

Under the Claude reference, Naive Bayes/dictionary accuracy is 44.7%/50.0% and macro F1 is 0.297/0.385. Under DeepSeek, accuracy is 28.7%/49.7% and macro F1 is 0.235/0.395. The dictionary scores higher under both references, reversing the external-benchmark ranking. This is conditional evidence of a domain-transfer or label-definition problem. The unweighted stratified pilot scores do not establish population accuracy. Independent human validation remains unmet; its metrics stay unavailable. No retraining or independent holdout evaluation of a tuned model is claimed.
