# Classifier evaluation against provisional AI reference labels

For this exploratory evaluation, each user-supplied AI label set is temporarily treated as the correct reference, separately. A is Claude Sonnet5.5 and B is DeepSeek V41-Flash (user-reported identifiers). Results measure performance relative to that reference, not independently verified accuracy. No human validation or adjudicated truth is claimed. The same frozen 300-item sample and original classifier predictions are used for every comparison; neither classifier is retrained.

## Overall results

| AI reference | Classifier | Items | Reference accuracy | Macro precision | Macro recall | Macro F1 |
|---|---|---:|---:|---:|---:|---:|
| Claude Sonnet5.5 | Naive Bayes | 300 | 44.7% | 0.356 | 0.329 | 0.297 |
| Claude Sonnet5.5 | Dictionary | 300 | 50.0% | 0.389 | 0.399 | 0.385 |
| DeepSeek V41-Flash | Naive Bayes | 300 | 28.7% | 0.300 | 0.316 | 0.235 |
| DeepSeek V41-Flash | Dictionary | 300 | 49.7% | 0.398 | 0.402 | 0.395 |

## Reference: Claude Sonnet5.5

### Class-level scores

| Classifier | Reference class | Support | Predicted items | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| Naive Bayes | negative | 122 | 34 | 0.441 | 0.123 | 0.192 |
| Naive Bayes | neutral | 165 | 195 | 0.600 | 0.709 | 0.650 |
| Naive Bayes | positive | 13 | 71 | 0.028 | 0.154 | 0.048 |
| Dictionary | negative | 122 | 145 | 0.469 | 0.557 | 0.509 |
| Dictionary | neutral | 165 | 128 | 0.625 | 0.485 | 0.546 |
| Dictionary | positive | 13 | 27 | 0.074 | 0.154 | 0.100 |

### Source-specific scores

| Classifier | Source type | Items | Reference accuracy | Macro F1 |
|---|---|---:|---:|---:|
| Naive Bayes | local | 33 | 57.6% | 0.342 |
| Naive Bayes | national | 127 | 37.0% | 0.255 |
| Naive Bayes | social | 140 | 48.6% | 0.322 |
| Dictionary | local | 33 | 81.8% | 0.536 |
| Dictionary | national | 127 | 42.5% | 0.335 |
| Dictionary | social | 140 | 49.3% | 0.397 |

### Naive Bayes: confusion matrix

Rows are reference labels; columns are classifier predictions.

| Reference / predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| negative | 15 | 74 | 33 |
| neutral | 12 | 117 | 36 |
| positive | 7 | 4 | 2 |

### Dictionary: confusion matrix

Rows are reference labels; columns are classifier predictions.

| Reference / predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| negative | 68 | 46 | 8 |
| neutral | 68 | 80 | 17 |
| positive | 9 | 2 | 2 |

## Reference: DeepSeek V41-Flash

### Class-level scores

| Classifier | Reference class | Support | Predicted items | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| Naive Bayes | negative | 177 | 34 | 0.500 | 0.096 | 0.161 |
| Naive Bayes | neutral | 95 | 195 | 0.328 | 0.674 | 0.441 |
| Naive Bayes | positive | 28 | 71 | 0.070 | 0.179 | 0.101 |
| Dictionary | negative | 177 | 145 | 0.655 | 0.537 | 0.590 |
| Dictionary | neutral | 95 | 128 | 0.391 | 0.526 | 0.448 |
| Dictionary | positive | 28 | 27 | 0.148 | 0.143 | 0.145 |

### Source-specific scores

| Classifier | Source type | Items | Reference accuracy | Macro F1 |
|---|---|---:|---:|---:|
| Naive Bayes | local | 33 | 39.4% | 0.255 |
| Naive Bayes | national | 127 | 26.0% | 0.222 |
| Naive Bayes | social | 140 | 28.6% | 0.234 |
| Dictionary | local | 33 | 60.6% | 0.414 |
| Dictionary | national | 127 | 40.9% | 0.338 |
| Dictionary | social | 140 | 55.0% | 0.429 |

### Naive Bayes: confusion matrix

Rows are reference labels; columns are classifier predictions.

| Reference / predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| negative | 17 | 117 | 43 |
| neutral | 8 | 64 | 23 |
| positive | 9 | 14 | 5 |

### Dictionary: confusion matrix

Rows are reference labels; columns are classifier predictions.

| Reference / predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| negative | 95 | 69 | 13 |
| neutral | 35 | 50 | 10 |
| positive | 15 | 9 | 4 |

## Findings conditional on the AI references

- Using Claude Sonnet5.5 as the provisional reference, dictionary macro F1 is 0.385 versus 0.297 for Naive Bayes. Negative-class recall is 55.7% versus 12.3%.
- Using DeepSeek V41-Flash as the provisional reference, dictionary macro F1 is 0.395 versus 0.235 for Naive Bayes. Negative-class recall is 53.7% versus 9.6%.

Under both references, the dictionary scores higher overall and within each source type. This reverses the external Financial PhraseBank ranking and suggests a domain-transfer or label-definition problem in the original classifier, conditional on reference quality. Neither classifier has strong three-class macro F1 on this pilot under either AI reference. These results do not justify treating either as a validated media-bias measure.

## Interpretation and limits

The metrics depend on the chosen AI reference. A low score identifies a mismatch with that reference and can arise from classifier domain transfer, differences in tone definitions, or reference-label errors. Model-generated labels are not a substitute for an independently established standard. The stratified sample was selected partly using the existing classifier outputs, so these unweighted scores are sample-specific and should not be generalized to the full media population.

Macro scores average the three fixed classes equally. Undefined class scores are set to zero; small source/class cells require caution. The positive reference class is small, particularly under Claude. No model was tuned on these labels, and no independent holdout evaluation of a newly tuned model is implied.

Political attribution and framing descriptions remain exploratory. Factual accuracy is not estimated: neither AI reference supplies verified official numerical matches or mismatches. Economic forecasts and causal conclusions remain unchanged. The item-level disagreement inventory is saved separately for future review.
