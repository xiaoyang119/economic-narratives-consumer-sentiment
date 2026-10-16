# Economic narratives and US consumer sentiment

AI Applications in Finance final project. Frozen research cutoff: **14 October 2026, America/New_York**. All deliverables and documentation are in English.

## Start here

- `deliverables/research_report.pdf`: 12-page research report.
- `deliverables/presentation_final.pptx`: eight editable slides with presenter notes, designed for roughly 6–8 minutes.
- `deliverables/dashboard.html`: self-contained interactive dashboard. Double-click it to open in a browser; a server is not required.
- `deliverables/speaker_notes_final.md`: presenter script with timing and sources.
- `deliverables/research_report.md`: editable report text.

The full package also includes the original assignment and spreadsheet, source snapshots, provenance, analysis code, figures, metrics, annotation materials and integrity tests.

## Findings and boundaries

Across 105 final monthly outcomes, persistence RMSE is 4.75, economic-only RMSE is 14.10 and economic-plus-recent-sentiment RMSE is 5.19. The October preliminary gap is -26.55 under the economic model and -6.81 under the dynamic model. These are model-dependent forecast errors, not estimates of cognitive bias.

The final screened media pilot covers four monthly bins. The external financial-text benchmark does not validate labels in this corpus. A separate historical comparison uses the San Francisco Fed Daily News Sentiment Index: dynamic RMSE changes from 5.19 to 5.23 over the full window, with no established stable improvement. That index has no recovered historical vintages, so its comparison is retrospective, not a verified real-time media forecast test. Independent annotation by two people remains unmet. No human labels, causal effects or agreement statistics have been fabricated. See report page 11 for the requirement matrix.

## Reproduce offline

Python 3.12 or newer is recommended. In a normal environment install `requirements.txt` into a virtual environment, then run:

```text
python run_project.py --offline --report
python -m unittest discover -s tests -v
```

Within this Codex workspace, use the bundled Python executable returned by the dependency loader. Missing plotting and legacy Excel libraries are installed only under `.build/pythonlibs`, which the analysis adds to its import path. Core pandas, NumPy, PDF and Excel libraries come from the bundled runtime.

Offline reproduction uses retained data and requires no account or API key. Rebuilding analyses and the dashboard is deterministic for these files. PDF metadata and chart renderers may change output bytes without changing results.

`python run_project.py --refresh` performs public read-only downloads for the frozen cutoff. Historical search engines can return different records, so this is a new collection version. A refresh does not automatically rewrite the report or slides. Review changes before rebuilding those artifacts. Failed or mismatched economic vintages stop the analysis; the pipeline never substitutes present-day values for an old vintage.

## Project layout

```text
data/raw/                 Public economic vintages, feeds, survey tables and benchmark
data/processed/           Forecast features, coded text and survey components
data/incoming/            Optional historical media input
results/                  Predictions, evaluation, diagnostics and dashboard snapshot
figures/                  Research figures
annotations/              Blind A/B files, audit key and labeling guide
prompts/                  Clearly marked, unexecuted optional LLM extension
src/                      Collection, analysis and artifact builders
tests/                    Data, timing and deliverable integrity checks
deliverables/             User-facing outputs
```

## Forecast design

Each origin is the first day of the target month. Predictors and training labels come from the exact ALFRED vintage of the previous calendar day. GDP growth is computed from two real quarterly levels in that vintage, then held as the latest published quarterly input. PCE YoY is computed from levels 12 months apart in the same vintage. No GDP interpolation is used.

The ALFRED sentiment feed can lag Michigan's direct publication. The persistence benchmark is therefore conservative and reflects the selected distribution channel, not every observation a market participant could obtain. The final outcome series used for scoring differs from the real-time training labels. October's preliminary value is reported separately.

Uncertainty uses up to 60 previous forecast errors, a minimum of 24, and a finite-sample adjusted absolute-error quantile. Outcome values in interval calibration also respect the origin vintage. Empirical coverage and paired block-bootstrap comparisons are saved. No finite-sample coverage guarantee is claimed under time dependence or regime changes.

## NLP and annotations

The implemented model is multinomial Naive Bayes with Laplace smoothing, trained only on the 80% training partition of the exact-deduplicated unanimous Financial PhraseBank subset. Macro F1 on the external 443-sentence test partition is 0.796, versus 0.543 for the word dictionary. Company financial language differs from US household economic language.

Framing and salience use inspectable lexical rules. Political actor mentions are flags for attribution review, not completed credit/blame labels. Factual calibration abstains unless the claim has an unambiguous measure and period matching a documented released benchmark. The model probability is not calibrated confidence.

Read `annotations/LABELING_GUIDE.md` before entering human labels. Existing nonblank annotation files are preserved across reruns. Run `python src/evaluate_annotations.py` after actual independent annotation. It refuses incomplete evidence instead of inventing agreement or corpus accuracy. The included LLM prompt is an optional future extension and was not executed.

## Extending the media comparison

`src/news_index_comparison.py` implements the separate historical SF Fed index test. It averages month t-2 and fits the economic, economic-plus-news and news-plus-controls models on chronological windows, with and without recent sentiment. The provider's historical index can reflect revisions and retrospective construction. The two-month calendar lag does not eliminate that limitation. Do not merge its accuracy scores with the verified real-time economic tests without retaining this distinction. The 2021-onward window is a sensitivity check, not a prespecified independent discovery sample.

Supply `data/incoming/historical_media.csv` with columns `published_date,text,source,source_kind`. Source kind must be national, local or social. Document the sampling method, legal access, duplicates and missingness. Only news enters the primary comparison; social titles remain a separate measurement unit.

Run `python src/media_comparison.py`. It requires at least 48 usable monthly news bins with at least 10 items per month, reserving a minimum 36 training months and 12 common holdout months. It compares economic-plus-recent-sentiment, that model plus lagged media tone/framing, and the media model plus household controls. It uses origin-vintage training outcomes and saves paired block-bootstrap comparisons. With the delivered pilot it correctly reports `not_estimable` and retains missing months as missing.

The 48-month rule is a conservative implementation choice, not a statement that this sample size guarantees power or resolves dependence. Additional text measures and sources require prespecified sensitivity checks and human validation.

## Updating the monitor

The dashboard can load `results/dashboard_snapshot.json` from a later analysis version, or be rebuilt with `python src/build_dashboard.py` after input changes. Its model, source, month and text filters update the displayed records. Forecast data can be downloaded as CSV.

For a future research cutoff, copy the project to a new dated research version, advance the cutoff and origin range in the collectors, verify new official release statuses and extend the sentiment target supplements. Update the final-scored month and preliminary monitoring month in the analysis, then rerun and inspect the artifacts. This frozen project does not silently advance its dates. The report lists the 23 October sentiment and 29 October GDP/PCE releases as prospective updates, not observed outcomes.

## PowerPoint reproduction

`src/build_presentation.mjs` uses the Codex-bundled `@oai/artifact-tool`, with native editable charts and embedded chart workbooks. It requires the bundled Node executable, an accessible `node_modules` link and the skill finalizer paths described in that builder. The finalized PPTX is included so viewing or editing it does not require this library. The finalizer will not overwrite an existing deliverable; choose a new filename when rebuilding.

## Sources and licensing

The PDF gives primary-source references. `data/raw/manifest.json`, `vintage_manifest.json`, `corpus_manifest.json`, `extra_feed_manifest.json` and `results/source_inventory.json` document retained files. Each source retains ownership of its material. The project analyzes headline/post-title metadata for personal academic research and is not a commercial or public redistribution service. Reddit usernames are removed from retained feeds. Source URLs can still identify public posts, so avoid publishing the raw archive indiscriminately.

Financial PhraseBank is licensed CC BY-NC-SA 3.0. The license and attribution are preserved in the original downloaded ZIP and in `data/PHRASEBANK_LICENSE.txt`. Other source terms continue to apply. No human participants were recruited or contacted.


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
