# Independent annotation guide

This package contains a frozen, stratified 300-item queue. The A and B files have identical item IDs. Neither file contains model labels, publisher names, links or the other annotator's answers. Publication date and observation unit context remain visible. `audit_key.csv` is for adjudication after independent annotation, not for the first pass.

No human labels have been supplied. Automated labels must never be submitted as independent human judgments. A personal project cannot manufacture two independent annotators by running two prompts.

## Labeling procedure

1. Two different people independently label every item, each using only their own file. Enter a stable real annotator ID, preferably a pseudonym rather than a personal name.
2. Tone is negative, neutral or positive economic information for a US household or the US economy. Distinguish deterioration from the word used to describe it: falling inflation can be favorable, while falling income can be unfavorable. Use neutral for genuinely mixed or indeterminate implications and explain ambiguity in the evidence field.
3. Enter 1 or 0 for each frame. Price-level framing emphasizes how expensive something is or accumulated costs. Inflation-rate framing emphasizes the rate or direction of price changes. Household framing discusses personal finances, budgets, groceries or housing. Aggregate framing discusses national growth, employment or aggregate measures. Forecast framing discusses future conditions or uncertainty. These fields are not mutually exclusive.
4. Mark numeric_claim 1 if the title makes a numerical economic claim, otherwise 0. Numbers in dates and listicle counts do not by themselves qualify.
5. For factual_calibration use `not_assessable_from_title`, `matches_official_release`, `mismatches_official_release`, or `no_numeric_claim`. A factual label requires the exact measure, period, unit, release date and official value. The same numerical value for a different month is not a match. A forecast is not a false statement merely because it later differs from an observation. Keep ambiguous claims unassessed.
6. For political_credit_blame use `credit`, `blame`, `both`, `mention_only`, or `none`. Criticism is not automatically bias. An actor's name alone is insufficient to infer attribution.
7. Copy the shortest title excerpt needed to support the decision. Do not paste full articles or disclose usernames.

## Agreement and adjudication

Run `python src/evaluate_annotations.py` only after the independent files have at least 300 paired tone labels and two distinct annotator IDs. The script reports raw tone agreement and Cohen's kappa. A third decision process or documented consensus can adjudicate disagreements afterward. Save the agreed tone as `annotations/adjudicated.csv` with columns `item_id,tone`. Preserve both original files.

Report precision, recall and F1 for all three tone classes, both overall and by source type. Small source-specific cells need counts and caution. Frame agreement should be computed separately for each binary label, and fact-check accuracy should exclude claims that could not be assessed. The supplied evaluator automates tone agreement and classification metrics only; the other dimensions require separately documented review.

## Selection and mechanisms

The queue is stratified across source type, predicted tone and month. Its proportions do not estimate population sentiment or media supply without appropriate design weights. Compare identical releases or matched surprises across publishers before calling a tone difference selective coverage. This text annotation cannot establish a reader's confirmation bias, availability bias or anchoring.
