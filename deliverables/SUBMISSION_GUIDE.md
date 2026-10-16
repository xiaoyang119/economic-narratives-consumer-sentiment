# Final submission and presentation guide

Research cutoff: 14 October 2026. Final submission version prepared on 16 October 2026.

## Submit these files

1. `research_report.pdf`: the 12-page main report.
2. `presentation_final.pptx`: the final eight-slide presentation, including the provisional AI-reference evaluation.
3. `dashboard.html`: the self-contained monitoring dashboard. Download and open it in a browser; GitHub displays its source rather than running the dashboard.
4. `project_package.zip`: the reproducible package containing data, provenance, code, prompts, the labeling guide, annotations, results and deliverables. Read `README.md` after extraction.

If the course platform provides one upload slot, submit the complete ZIP. If it provides separate slots, upload the report, final deck and dashboard separately as well. The GitHub link is supplementary unless the instructor explicitly accepts it as the analytical package. The repository is private, so its URL alone does not give the instructor access. A GitHub repository or video recording is not an explicit requirement in the provided assignment.

The final speaker script is `speaker_notes_final.md`. Use it to rehearse. The original `presentation.pptx` and `speaker_notes.md` remain in the package as earlier versions; use the files with `_final` for presentation. The three AI-analysis Markdown files are supplementary results already included in the package and do not need separate submission unless requested.

## Presentation plan: approximately 7 minutes 40 seconds

| Slide | Time | Main point |
|---|---:|---|
| 1. Research question | 45 seconds | Can economic narratives explain weak consumer sentiment? Consider household pressure, framing and measurement/model limitations. |
| 2. Economic measurement and timing | 55 seconds | Reconcile the supplied spreadsheet with official data and exclude information unavailable at the cutoff. |
| 3. Forecast design | 55 seconds | Use dated economic vintages and chronological evaluation, with GDP remaining quarterly. |
| 4. Forecast performance | 60 seconds | Persistence RMSE 4.75 outperforms economic-only RMSE 14.10. |
| 5. October gap | 60 seconds | The gap changes from -26.55 to -6.81 with recent sentiment included. Both observations lie inside their respective intervals. |
| 6. Media and AI-reference evaluation | 70 seconds | 316 texts; 300 with AI labels. Dictionary macro F1 exceeds Naive Bayes under both provisional AI references. Explain the reference assumption. |
| 7. Historical media test | 60 seconds | News-index augmentation does not show a stable full-window dynamic forecast gain. The index comparison is retrospective. |
| 8. Financial implication and dashboard | 55 seconds | Benchmark sentiment-gap signals and show uncertainty before using them in forecasting or risk monitoring. |

The planned slide time totals 7 minutes 40 seconds. If demonstrating the dashboard live, replace about 20 seconds of the final-slide explanation with the demo rather than adding time. Switch the economic model to show how the gap changes, then show the AI-reference selector. Keep the local HTML open beforehand and prepare a screenshot as a fallback.

## Before submission

- Add the actual presenter name(s), course section and any required student identifier using the instructor's requested format. Do not invent collaborators.
- Open the final PPTX in PowerPoint and rehearse once with a timer. The deck was generated and checked programmatically; no live PowerPoint inspection is claimed.
- Confirm the report has 12 pages and that the HTML opens after download.
- Keep the research cutoff at 14 October. Do not present later releases as observed data.
- Reproduce with `python run_project.py --offline --report` and `python -m unittest discover -s tests -v` if checking the analytical package.

## Method disclosure and likely questions

The user reviewed the model judgments and reported that they resembled their own likely decisions. This is an informal plausibility check, not a separately recorded blind annotation of all 300 items. A is Claude Sonnet5.5 and B is DeepSeek V41-Flash, with version names reported by the user. Treating each as a provisional reference enables conditional accuracy/F1 scoring. The assignment's requirement for two independent human annotators remains unmet; selecting a final project version does not change that status.

If asked why the dictionary wins here but loses on Financial PhraseBank, explain that company-finance sentences and household/macro headlines have different label meanings and language. These results are conditional on the AI references and cannot identify which labels are truly correct.

If asked whether media caused low sentiment, say that the project estimates descriptive patterns and associations, while the experimental design is a proposal. Neither the short text pilot nor the retrospective index test identifies a causal national effect.

The assignment does not specify whether the overall project can be submitted in pairs or how many people must speak. Follow any separate classroom or course-platform instructions. If collaboration is permitted, two presenters can divide slides 1-5 and 6-8 while keeping the total presentation within 6-8 minutes.
