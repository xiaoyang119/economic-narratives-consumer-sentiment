"""Validate independent annotations and report agreement and AI accuracy.

Refuses missing, duplicate, or copied annotator IDs; blank files are not labels.
"""
import sys,json
from pathlib import Path
import pandas as pd
import numpy as np
from analyze import classification_metrics,save_json,ROOT

def evaluate():
    folder=ROOT/'annotations';a=pd.read_csv(folder/'annotator_A.csv').fillna('');b=pd.read_csv(folder/'annotator_B.csv').fillna('')
    for name,frame in [('A',a),('B',b)]:
        if frame.item_id.duplicated().any():raise ValueError(f'Duplicate item IDs in annotator {name}')
        if not set(frame.tone).issubset({'','negative','neutral','positive'}):raise ValueError('Invalid tone label')
    both=a[['item_id','tone','annotator_id']].merge(b[['item_id','tone','annotator_id']],on='item_id',suffixes=('_A','_B'))
    done=both[(both.tone_A!='')&(both.tone_B!='')]
    if len(done)<300:
        print(f'Human validation incomplete: {len(done)} paired tone labels; at least 300 required. No agreement or corpus F1 reported.')
        return {'status':'incomplete','paired_n':len(done)}
    if (done.annotator_id_A=='').any() or (done.annotator_id_B=='').any() or (done.annotator_id_A==done.annotator_id_B).any():raise ValueError('Two distinct real annotator IDs are required')
    agreement=float((done.tone_A==done.tone_B).mean());pa=done.tone_A.value_counts(normalize=True);pb=done.tone_B.value_counts(normalize=True);pe=sum(pa.get(k,0)*pb.get(k,0) for k in ['negative','neutral','positive']);kappa=(agreement-pe)/(1-pe) if pe<1 else None
    result={'status':'agreement_calculated_adjudication_required','paired_n':len(done),'raw_agreement':agreement,'cohen_kappa':kappa}
    adjud=folder/'adjudicated.csv'
    if adjud.exists():
        truth=pd.read_csv(adjud);corpus=pd.read_csv(ROOT/'data/processed/corpus_coded.csv');joined=truth.merge(corpus,on='item_id',suffixes=('_human','_AI'))
        result['overall_AI']=classification_metrics(joined.tone_human,joined.tone_AI)
        result['by_source_kind']={k:classification_metrics(g.tone_human,g.tone_AI) for k,g in joined.groupby('source_kind')}
    save_json(ROOT/'results/human_validation.json',result);return result

if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
