# Claude and DeepSeek annotation comparison

These are model-generated labels, not two independent human annotations. The user identified A as Claude Sonnet5.5 and B as DeepSeek V41-Flash. These version identifiers are user-reported and were not independently verified. Original files and stored IDs are preserved. Actual prompts, generation dates and cross-model blinding were not recorded. The optional prompt in this project is not evidence of the prompt used.

## Paired results

Both models labeled the same 300 texts. Tone agreement is 76.0%, with model-to-model Cohen kappa 0.588. There are 72 tone disagreements. This measures consistency, not correctness.

| Tone | Claude | DeepSeek |
|---|---:|---:|
| Negative | 122 | 177 |
| Neutral | 165 | 95 |
| Positive | 13 | 28 |

## Preliminary conclusions

1. Tone estimates are sensitive to the labeling model. Claude calls 122/300 (40.7%) negative; DeepSeek calls 177/300 (59.0%) negative, an 18.3 percentage-point difference. These are unweighted proportions in a stratified pilot, not population negativity rates.
2. The main boundary is neutral versus directional tone. Of Claude's 165 neutral labels, DeepSeek calls 56 negative and 15 positive. Only one remaining tone disagreement occurs outside that group. This is consistent with different treatment of mixed or ambiguous implications, but actual prompts and blinding were not recorded, so the cause cannot be identified.
3. Agreement differs by dimension. Price-level framing agrees on 287/300 items (95.7%), while aggregate framing agrees on 254/300 (84.7%). Only 133/300 items agree on every coded dimension. High agreement does not rule out shared errors.
4. Numerical-claim detection also varies: Claude flags 48 items and DeepSeek 70. Neither supplies a matches/mismatches-official-release label. These annotations do not establish factual accuracy or misinformation rates.
5. The existing classifier and both models are compared on the same 300 items below. No model is treated as ground truth. Corpus accuracy, human agreement and adjudicated F1 remain unavailable.

| Comparison | Tone agreement | Model-to-model kappa |
|---|---:|---:|
| Claude vs Naive Bayes | 44.7% | 0.056 |
| DeepSeek vs Naive Bayes | 28.7% | -0.012 |

| Dimension | Agreement | Kappa |
|---|---:|---:|
| tone | 76.0% | 0.588 |
| price_level_frame | 95.7% | 0.858 |
| inflation_rate_frame | 93.3% | 0.867 |
| household_frame | 89.0% | 0.706 |
| aggregate_frame | 84.7% | 0.651 |
| forecast_frame | 89.3% | 0.662 |
| numeric_claim | 91.3% | 0.728 |
| factual_calibration | 91.3% | 0.728 |
| political_credit_blame | 87.0% | 0.713 |

| Source type | Items | Tone agreement | Kappa |
|---|---:|---:|---:|
| local | 33 | 78.8% | 0.619 |
| national | 127 | 80.3% | 0.663 |
| social | 140 | 71.4% | 0.509 |

## Implication for the research question

The model comparison strengthens the evidence of measurement uncertainty. It does not establish that media is biased, that consumers saw these texts, or that coverage caused low consumer sentiment. Economic forecasts and the separate retrospective news-index comparison are unchanged. Future independent human review should prioritize the 72 tone disagreements and numerical-claim boundary cases, while using a separately documented representative evaluation design for accuracy estimation.

No consensus or adjudicated truth has been manufactured. The required two-person independent human labeling remains incomplete.
