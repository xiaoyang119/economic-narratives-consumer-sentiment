"""Compare user-supplied Claude and DeepSeek labels without assuming ground truth."""
from pathlib import Path
import json
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['negative', 'neutral', 'positive']
FIELDS = ['tone', 'price_level_frame', 'inflation_rate_frame', 'household_frame',
          'aggregate_frame', 'forecast_frame', 'numeric_claim',
          'factual_calibration', 'political_credit_blame']


def agreement(a, b):
    observed = float(a.eq(b).mean())
    pa, pb = a.value_counts(normalize=True), b.value_counts(normalize=True)
    expected = sum(float(pa.get(k, 0) * pb.get(k, 0)) for k in set(a) | set(b))
    return {'n': len(a), 'agreement': observed,
            'cohen_kappa': (observed - expected) / (1 - expected) if expected < 1 else None}


def compare():
    paths = {'Claude': ROOT/'annotations/annotator_A_filled.csv',
             'DeepSeek': ROOT/'annotations/annotator_B.csv'}
    frames = {k: pd.read_csv(p, dtype=str).fillna('') for k, p in paths.items()}
    provenance = {'status': 'model_generated_not_independent_human_annotations',
                  'basis': 'User explicitly identified A as Claude and B as DeepSeek.',
                  'independent_human_annotation_completed': False,
                  'human_paired_n': 0, 'models': {}}
    allowed = {'tone': set(LABELS), 'factual_calibration': {
        'no_numeric_claim', 'not_assessable_from_title', 'matches_official_release',
        'mismatches_official_release'}, 'political_credit_blame': {
        'none', 'mention_only', 'credit', 'blame', 'both'}}
    for name, frame in frames.items():
        if frame.item_id.duplicated().any() or len(frame) != 300:
            raise ValueError(f'{name}: expected 300 unique item IDs')
        for field in FIELDS:
            if not set(frame[field]).issubset(allowed.get(field, {'0', '1'})):
                raise ValueError(f'{name}: invalid or missing {field}')
        provenance['models'][name] = {
            'file': paths[name].relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(paths[name].read_bytes()).hexdigest(),
            'stored_annotator_ids': sorted(set(frame.annotator_id)),
            'exact_model_version': {'Claude': 'Sonnet5.5', 'DeepSeek': 'V41-Flash'}[name],
            'version_source': 'User-reported identifier, not independently verified',
            'generation_date': None,
            'actual_prompt': None, 'cross_model_blinding': 'not documented',
            'note': 'Stored IDs are preserved verbatim. Reader_A does not establish human authorship.'}
    a, b = frames['Claude'], frames['DeepSeek']
    if set(a.item_id) != set(b.item_id):
        raise ValueError('Unpaired IDs')
    joined = a.merge(b, on='item_id', suffixes=('_Claude', '_DeepSeek'), validate='one_to_one')
    if not joined.text_Claude.eq(joined.text_DeepSeek).all():
        raise ValueError('Texts differ')
    result = {'status': 'exploratory_model_comparison', 'ground_truth_available': False,
              'human_validation_completed': False, 'paired_n': len(joined),
              'model_versions': {'Claude': 'Sonnet5.5', 'DeepSeek': 'V41-Flash'},
              'version_source': 'User-reported identifiers, not independently verified',
              'actual_prompts': 'not recorded',
              'tone': agreement(joined.tone_Claude, joined.tone_DeepSeek),
              'distributions': {n: f.tone.value_counts().reindex(LABELS, fill_value=0).to_dict()
                                for n, f in frames.items()},
              'dimensions': {c: agreement(joined[c+'_Claude'], joined[c+'_DeepSeek']) for c in FIELDS},
              'by_source_kind': {k: agreement(g.tone_Claude, g.tone_DeepSeek)
                                 for k, g in joined.groupby('source_kind_Claude')},
              'tone_cross_table': pd.crosstab(joined.tone_Claude, joined.tone_DeepSeek)
                                 .reindex(index=LABELS, columns=LABELS, fill_value=0).to_dict(orient='index')}
    coded = pd.read_csv(ROOT/'data/processed/corpus_coded.csv', dtype=str).fillna('')
    result['agreement_with_existing_classifier'] = {}
    for name, frame in frames.items():
        pair = frame[['item_id', 'tone']].merge(coded[['item_id', 'tone']], on='item_id',
                  suffixes=('_model', '_NB'), validate='one_to_one')
        if len(pair) != 300:
            raise ValueError('Classifier comparison must use the same 300 items')
        result['agreement_with_existing_classifier'][name] = agreement(pair.tone_model, pair.tone_NB)
    different = pd.concat([joined[c+'_Claude'].ne(joined[c+'_DeepSeek']) for c in FIELDS], axis=1)
    result['all_dimensions_agree_n'] = int((~different.any(axis=1)).sum())
    result['any_dimension_disagreement_n'] = int(different.any(axis=1).sum())
    result['numeric_claim_n'] = {n: int(f.numeric_claim.eq('1').sum()) for n, f in frames.items()}
    result['verified_fact_labels_n'] = {n: int(f.factual_calibration.isin(
        ['matches_official_release', 'mismatches_official_release']).sum()) for n, f in frames.items()}
    details = joined[['item_id', 'text_Claude', 'source_kind_Claude']].copy()
    details.columns = ['item_id', 'text', 'source_kind']
    details['disputed_dimensions'] = [','.join(c for c in FIELDS if row[c+'_Claude'] != row[c+'_DeepSeek'])
                                     for _, row in joined.iterrows()]
    for c in FIELDS:
        details[c+'_Claude'] = joined[c+'_Claude']
        details[c+'_DeepSeek'] = joined[c+'_DeepSeek']
    details[details.disputed_dimensions.ne('')].to_csv(ROOT/'results/model_annotation_disagreements.csv', index=False)
    (ROOT/'annotations/ANNOTATION_PROVENANCE.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    (ROOT/'results/model_annotation_comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    lines = ['# Claude and DeepSeek annotation comparison', '',
        'These are model-generated labels, not two independent human annotations. The user identified A as Claude Sonnet5.5 and B as DeepSeek V41-Flash. These version identifiers are user-reported and were not independently verified. Original files and stored IDs are preserved. Actual prompts, generation dates and cross-model blinding were not recorded. The optional prompt in this project is not evidence of the prompt used.', '',
        '## Paired results', '',
        f'Both models labeled the same {len(joined)} texts. Tone agreement is {result["tone"]["agreement"]:.1%}, with model-to-model Cohen kappa {result["tone"]["cohen_kappa"]:.3f}. There are 72 tone disagreements. This measures consistency, not correctness.', '',
        '| Tone | Claude | DeepSeek |', '|---|---:|---:|']
    lines += [f'| {c.title()} | {result["distributions"]["Claude"][c]} | {result["distributions"]["DeepSeek"][c]} |' for c in LABELS]
    lines += ['', '## Preliminary conclusions', '',
        '1. Tone estimates are sensitive to the labeling model. Claude calls 122/300 (40.7%) negative; DeepSeek calls 177/300 (59.0%) negative, an 18.3 percentage-point difference. These are unweighted proportions in a stratified pilot, not population negativity rates.',
        '2. The main boundary is neutral versus directional tone. Of Claude\'s 165 neutral labels, DeepSeek calls 56 negative and 15 positive. Only one remaining tone disagreement occurs outside that group. This is consistent with different treatment of mixed or ambiguous implications, but actual prompts and blinding were not recorded, so the cause cannot be identified.',
        f'3. Agreement differs by dimension. Price-level framing agrees on 287/300 items (95.7%), while aggregate framing agrees on 254/300 (84.7%). Only {result["all_dimensions_agree_n"]}/300 items agree on every coded dimension. High agreement does not rule out shared errors.',
        '4. Numerical-claim detection also varies: Claude flags 48 items and DeepSeek 70. Neither supplies a matches/mismatches-official-release label. These annotations do not establish factual accuracy or misinformation rates.',
        '5. The existing classifier and both models are compared on the same 300 items below. No model is treated as ground truth. Corpus accuracy, human agreement and adjudicated F1 remain unavailable.', '',
        '| Comparison | Tone agreement | Model-to-model kappa |', '|---|---:|---:|']
    lines += [f'| {n} vs Naive Bayes | {v["agreement"]:.1%} | {v["cohen_kappa"]:.3f} |'
              for n,v in result['agreement_with_existing_classifier'].items()]
    lines += ['', '| Dimension | Agreement | Kappa |', '|---|---:|---:|']
    lines += [f'| {c} | {v["agreement"]:.1%} | {v["cohen_kappa"]:.3f} |' for c,v in result['dimensions'].items()]
    lines += ['', '| Source type | Items | Tone agreement | Kappa |', '|---|---:|---:|---:|']
    lines += [f'| {k} | {v["n"]} | {v["agreement"]:.1%} | {v["cohen_kappa"]:.3f} |' for k,v in result['by_source_kind'].items()]
    lines += ['', '## Implication for the research question', '',
        'The model comparison strengthens the evidence of measurement uncertainty. It does not establish that media is biased, that consumers saw these texts, or that coverage caused low consumer sentiment. Economic forecasts and the separate retrospective news-index comparison are unchanged. Future independent human review should prioritize the 72 tone disagreements and numerical-claim boundary cases, while using a separately documented representative evaluation design for accuracy estimation.', '',
        'No consensus or adjudicated truth has been manufactured. The required two-person independent human labeling remains incomplete.']
    (ROOT/'deliverables/model_annotation_findings.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    compare()
