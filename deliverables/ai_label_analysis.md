# Exploratory analysis using AI-classified media texts

A fixed stratified sample of 300 headlines and Reddit post titles was labeled by Claude Sonnet5.5 and DeepSeek V41-Flash (version identifiers supplied by the user). These are AI outputs, not human annotations. Actual prompts and blinding were not recorded. No model is used as ground truth, and disagreement is retained rather than resolved into manufactured consensus. All proportions below describe this unweighted sample.

## Economic tone

| Label | Claude Sonnet5.5 | DeepSeek V41-Flash |
|---|---:|---:|
| Negative | 122 (40.7%) | 177 (59.0%) |
| Neutral | 165 (55.0%) | 95 (31.7%) |
| Positive | 13 (4.3%) | 28 (9.3%) |

## Negative tone by source type

| Source type | Items | Claude Sonnet5.5 | DeepSeek V41-Flash |
|---|---:|---:|---:|
| national | 127 | 41.7% | 54.3% |
| local | 33 | 33.3% | 51.5% |
| social | 140 | 41.4% | 65.0% |

Differences are descriptive. Source type is confounded with topic, timing, sampling and wording. Small local-news cells limit comparisons. Neither negative content nor a source difference establishes bias.

## Framing

| Frame | Claude Sonnet5.5 | DeepSeek V41-Flash |
|---|---:|---:|
| Price Level | 60 (20.0%) | 53 (17.7%) |
| Inflation Rate | 151 (50.3%) | 145 (48.3%) |
| Household | 79 (26.3%) | 70 (23.3%) |
| Aggregate | 187 (62.3%) | 223 (74.3%) |
| Forecast | 58 (19.3%) | 60 (20.0%) |

Frames can co-occur. Rate-focused coverage need not imply low household pressure, because slower price growth does not mean lower price levels. Text flags do not establish a psychological mechanism.

## Monthly descriptions

| Month | Items | Claude Sonnet5.5 negative | DeepSeek V41-Flash negative |
|---|---:|---:|---:|
| 2026-07 | 35 | 48.6% | 54.3% |
| 2026-08 | 40 | 40.0% | 70.0% |
| 2026-09 | 34 | 47.1% | 55.9% |
| 2026-10 | 191 | 38.2% | 58.1% |

Only four monthly bins are available. October ends on 14 October and is sampled more heavily. These rates cannot establish a trend, election effect, media-sentiment association or predictive improvement. No regression on four bins is presented.

## Political attribution and factual calibration

| Measure | Claude Sonnet5.5 | DeepSeek V41-Flash |
|---|---:|---:|
| credit | 3 | 1 |
| blame | 25 | 6 |
| both | 2 | 1 |
| mention_only | 59 | 82 |
| none | 211 | 210 |
| Numerical claims flagged | 48 | 70 |
| Numerical claims verified against an official release | 0 | 0 |

Credit and blame refer to model-coded attribution, not political bias. A flag for a number is not a completed fact check. Neither annotation file contains a verified numerical match or mismatch, so misinformation rates remain unavailable.

## Findings supported by both label sets

- Inflation rate appears in 48.3% to 50.3% of sampled texts across the two label sets.
- Price level appears in 17.7% to 20.0% of sampled texts across the two label sets.
- Household appears in 23.3% to 26.3% of sampled texts across the two label sets.
- Aggregate appears in 62.3% to 74.3% of sampled texts across the two label sets.

Both label sets contain more negative than positive items. This supports the narrow description that negative economic implications are more common than positive ones in this selected sample under both classifiers. It does not establish disproportionate negativity relative to economic events or the broader media population.

## What changes in the project

The AI labels now support descriptive tone, framing, source, month and political-attribution tables. Economic forecast results are unchanged. Accuracy, precision, recall and F1 on this project remain unavailable without an independently established reference set. Human agreement and adjudicated truth are not claimed. The existing retrospective external news-index test remains separate from this four-month text sample.
