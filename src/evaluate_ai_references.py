"""Evaluate frozen classifiers against two explicitly provisional AI references."""
from pathlib import Path
import json
import hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
LABELS=['negative','neutral','positive']


def metrics(actual,predicted):
    matrix=[[int(((actual==a)&(predicted==p)).sum()) for p in LABELS] for a in LABELS]
    classes=[]
    for i,label in enumerate(LABELS):
        tp=matrix[i][i];support=sum(matrix[i]);predicted_n=sum(row[i] for row in matrix)
        precision=tp/predicted_n if predicted_n else 0.
        recall=tp/support if support else 0.
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.
        classes.append({'label':label,'support':support,'predicted_n':predicted_n,
                        'precision':precision,'recall':recall,'F1':f1})
    return {'n':len(actual),'accuracy':sum(matrix[i][i] for i in range(3))/len(actual),
            'macro_precision':sum(c['precision'] for c in classes)/3,
            'macro_recall':sum(c['recall'] for c in classes)/3,
            'macro_F1':sum(c['F1'] for c in classes)/3,
            'weighted_F1':sum(c['F1']*c['support'] for c in classes)/len(actual),
            'classes':classes,'labels':LABELS,'confusion_matrix':matrix}


def evaluate():
    inputs={'Claude Sonnet5.5':ROOT/'annotations/annotator_A_filled.csv',
            'DeepSeek V41-Flash':ROOT/'annotations/annotator_B.csv'}
    corpus=pd.read_csv(ROOT/'data/processed/corpus_coded.csv',dtype=str).fillna('')
    expected=pd.read_csv(ROOT/'annotations/annotator_A.csv',dtype=str).fillna('')
    if corpus.item_id.duplicated().any():raise ValueError('Duplicate corpus IDs')
    result={'status':'provisional_AI_reference_evaluation','independent_human_validated':False,
            'reference_assumption':'Each AI label set is treated separately as a provisional correct reference for scoring only.',
            'not_estimated':'True corpus accuracy, human agreement and adjudicated corpus F1',
            'scope':'Unweighted stratified 300-item pilot; no retraining or prompt tuning performed.',
            'zero_division':'Precision/recall/F1 set to zero when denominator is zero; fixed three-class macro averages.',
            'confusion_matrix_orientation':'rows=AI reference, columns=classifier prediction',
            'references':{}}
    lines=['# Classifier evaluation against provisional AI reference labels','',
        'For this exploratory evaluation, each user-supplied AI label set is temporarily treated as the correct reference, separately. A is Claude Sonnet5.5 and B is DeepSeek V41-Flash (user-reported identifiers). Results measure performance relative to that reference, not independently verified accuracy. No human validation or adjudicated truth is claimed. The same frozen 300-item sample and original classifier predictions are used for every comparison; neither classifier is retrained.', '',
        '## Overall results','','| AI reference | Classifier | Items | Reference accuracy | Macro precision | Macro recall | Macro F1 |','|---|---|---:|---:|---:|---:|---:|']
    errors=[]
    for reference,path in inputs.items():
        frame=pd.read_csv(path,dtype=str).fillna('')
        if len(frame)!=300 or frame.item_id.duplicated().any() or set(frame.item_id)!=set(expected.item_id):raise ValueError('Expected the original 300 unique sample IDs')
        if not set(frame.tone).issubset(LABELS):raise ValueError('Invalid reference labels')
        joined=frame[['item_id','text','source_kind','published_date','tone']].merge(
            corpus[['item_id','text','source_kind','published_date','tone','dictionary_tone']],
            on='item_id',suffixes=('_reference','_classifier'),validate='one_to_one')
        if len(joined)!=300:raise ValueError('Missing classifier predictions')
        for c in ['text','source_kind','published_date']:
            if not joined[c+'_reference'].eq(joined[c+'_classifier']).all():raise ValueError('Reference sample metadata changed')
        if not set(joined.tone_classifier).issubset(LABELS) or not set(joined.dictionary_tone).issubset(LABELS):raise ValueError('Invalid predictions')
        ref_result={'file':path.relative_to(ROOT).as_posix(),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'classifiers':{}}
        for classifier,column in [('Naive Bayes','tone_classifier'),('Dictionary','dictionary_tone')]:
            overall=metrics(joined.tone_reference,joined[column])
            groups={k:metrics(g.tone_reference,g[column]) for k,g in joined.groupby('source_kind_reference')}
            ref_result['classifiers'][classifier]={'overall':overall,'by_source_kind':groups}
            lines.append(f'| {reference} | {classifier} | 300 | {overall["accuracy"]:.1%} | {overall["macro_precision"]:.3f} | {overall["macro_recall"]:.3f} | {overall["macro_F1"]:.3f} |')
            for _,row in joined[joined.tone_reference.ne(joined[column])].iterrows():
                errors.append({'reference':reference,'classifier':classifier,'item_id':row.item_id,
                    'text':row.text_reference,'source_kind':row.source_kind_reference,
                    'reference_label':row.tone_reference,'classifier_label':row[column],
                    'interpretation':'Disagreement with provisional AI reference; not verified error.'})
        result['references'][reference]=ref_result
    for reference,ref in result['references'].items():
        lines+=['',f'## Reference: {reference}','','### Class-level scores','','| Classifier | Reference class | Support | Predicted items | Precision | Recall | F1 |','|---|---|---:|---:|---:|---:|---:|']
        for name,values in ref['classifiers'].items():
            for c in values['overall']['classes']:
                lines.append(f'| {name} | {c["label"]} | {c["support"]} | {c["predicted_n"]} | {c["precision"]:.3f} | {c["recall"]:.3f} | {c["F1"]:.3f} |')
        lines+=['','### Source-specific scores','','| Classifier | Source type | Items | Reference accuracy | Macro F1 |','|---|---|---:|---:|---:|']
        for name,values in ref['classifiers'].items():
            for source,m in values['by_source_kind'].items():
                lines.append(f'| {name} | {source} | {m["n"]} | {m["accuracy"]:.1%} | {m["macro_F1"]:.3f} |')
        for name,values in ref['classifiers'].items():
            lines+=['',f'### {name}: confusion matrix','',
                    'Rows are reference labels; columns are classifier predictions.','','| Reference / predicted | Negative | Neutral | Positive |','|---|---:|---:|---:|']
            lines += ['| '+label+' | '+' | '.join(str(v) for v in row)+' |' for label,row in zip(LABELS,values['overall']['confusion_matrix'])]
    lines+=['','## Findings conditional on the AI references','']
    for reference,ref in result['references'].items():
        nb=ref['classifiers']['Naive Bayes']['overall'];dic=ref['classifiers']['Dictionary']['overall']
        lines.append(f'- Using {reference} as the provisional reference, dictionary macro F1 is {dic["macro_F1"]:.3f} versus {nb["macro_F1"]:.3f} for Naive Bayes. Negative-class recall is {dic["classes"][0]["recall"]:.1%} versus {nb["classes"][0]["recall"]:.1%}.')
    lines+=['','Under both references, the dictionary scores higher overall and within each source type. This reverses the external Financial PhraseBank ranking and suggests a domain-transfer or label-definition problem in the original classifier, conditional on reference quality. Neither classifier has strong three-class macro F1 on this pilot under either AI reference. These results do not justify treating either as a validated media-bias measure.','',
        '## Interpretation and limits','',
        'The metrics depend on the chosen AI reference. A low score identifies a mismatch with that reference and can arise from classifier domain transfer, differences in tone definitions, or reference-label errors. Model-generated labels are not a substitute for an independently established standard. The stratified sample was selected partly using the existing classifier outputs, so these unweighted scores are sample-specific and should not be generalized to the full media population.', '',
        'Macro scores average the three fixed classes equally. Undefined class scores are set to zero; small source/class cells require caution. The positive reference class is small, particularly under Claude. No model was tuned on these labels, and no independent holdout evaluation of a newly tuned model is implied.', '',
        'Political attribution and framing descriptions remain exploratory. Factual accuracy is not estimated: neither AI reference supplies verified official numerical matches or mismatches. Economic forecasts and causal conclusions remain unchanged. The item-level disagreement inventory is saved separately for future review.']
    (ROOT/'results/ai_reference_evaluation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (ROOT/'results/ai_reference_disagreements.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'deliverables/ai_reference_evaluation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[:14]))
    return result


if __name__=='__main__':evaluate()
