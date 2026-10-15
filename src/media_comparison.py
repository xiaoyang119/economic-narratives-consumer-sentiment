"""Fit the required three models only when sufficient longitudinal media exist.

Optional input: data/incoming/historical_media.csv with publication date, text,
source and source_kind. No artificial historical media values are generated.
"""
import json,sys
from pathlib import Path
import pandas as pd
import numpy as np
from analyze import ROOT,ols,predict,nb_predict,text_measures,load_snapshot,save_json,bootstrap_mean_ci

def run():
    incoming=ROOT/'data/incoming/historical_media.csv'
    if incoming.exists():
        d=pd.read_csv(incoming)
        required={'published_date','text','source','source_kind'}
        if not required.issubset(d.columns):raise ValueError('Historical media requires '+str(sorted(required)))
        model=json.loads((ROOT/'results/tone_model.json').read_text());model['logprob']=np.asarray(model['logprob']);model['logprior']=np.asarray(model['logprior'])
        d=d.drop_duplicates(['text','published_date']).copy();d['tone_score']=[{'negative':-1,'neutral':0,'positive':1}[nb_predict(model,t)[0]] for t in d.text]
        d['frame_price_level']=[text_measures(t)['frame_price_level'] for t in d.text]
        d['month']=pd.to_datetime(d.published_date).dt.to_period('M').astype(str)
    else:
        d=pd.read_csv(ROOT/'data/processed/corpus_coded.csv');d['month']=d.published_date.str[:7];d['tone_score']=d.tone.map({'negative':-1,'neutral':0,'positive':1})
    # News and social observations measure different units. Use news in the primary
    # monthly comparison, keeping Reddit as a separate descriptive series.
    news=d[d.source_kind.isin(['national','local'])]
    monthly=news.groupby('month').agg(media_tone=('tone_score','mean'),media_price_frame=('frame_price_level','mean'),items=('text','size'))
    monthly=monthly[monthly['items']>=10]
    monthly.index=(pd.PeriodIndex(monthly.index,freq='M')+1).to_timestamp().strftime('%Y-%m-%d')
    f=pd.read_csv(ROOT/'data/processed/forecast_features.csv',index_col=0).join(monthly,how='inner').dropna()
    # Historical title content must precede each origin. At least 36 training
    # months and 12 scored months are required for a modest primary comparison.
    if len(f)<48:
        status={'status':'not_estimable','usable_months':len(f),'required_months':48,'minimum_news_items_per_month':10,'reason':'insufficient historical news coverage','models':['Economic','Economic plus media','Economic plus media plus household controls'],'missing_months_are_zero_filled':False}
        save_json(ROOT/'results/media_model_comparison.json',status);print(json.dumps(status,indent=2));return status
    specs={'Economic':['unemployment','inflation','gdp_growth','sentiment_last'],
      'Economic plus media':['unemployment','inflation','gdp_growth','sentiment_last','media_tone','media_price_frame'],
      'Economic plus media plus household controls':['unemployment','inflation','gdp_growth','sentiment_last','media_tone','media_price_frame','income_growth','price_3y']}
    targets=pd.read_csv(ROOT/'data/processed/sentiment_targets.csv',index_col=0).iloc[:,0];records=[]
    for origin,row in f.iloc[36:].iterrows():
        vintage=load_snapshot(origin).UMCSENT.dropna();vintage.index=vintage.index.strftime('%Y-%m-%d')
        for model,cols in specs.items():
            tr=f.loc[f.index<origin,cols].join(vintage.rename('target')).dropna()
            if len(tr)<36:continue
            fit=ols(tr[cols],tr.target);pred=float(predict(fit,row[cols])[0]);actual=float(targets.loc[origin])
            records.append({'month':origin,'model':model,'prediction':pred,'actual':actual,'error':actual-pred,'training_n':len(tr)})
    p=pd.DataFrame(records)
    if p.empty:raise ValueError('Insufficient vintage-available targets despite input coverage')
    common=p.groupby('month').model.nunique();p=p[p.month.isin(common[common==3].index)];p.to_csv(ROOT/'results/media_model_forecasts.csv',index=False)
    if p.month.nunique()<12:raise ValueError('At least 12 common held-out months are required')
    result={'status':'estimated_exploratory','common_holdout_months':int(p.month.nunique()),'media_lag':'previous complete calendar month','training_minimum':36,'metrics':[],'sampling_limit':'retrospective collection cannot establish historically representative sampling or respondent exposure'}
    errors=p.pivot(index='month',columns='model',values='error')
    for name,g in p.groupby('model'):
        e=g.error.to_numpy();loss=errors[name].to_numpy()**2-errors.Economic.to_numpy()**2
        result['metrics'].append({'model':name,'RMSE':float(np.sqrt(np.mean(e**2))),'MAE':float(np.abs(e).mean()),'squared_loss_difference_vs_economic':float(loss.mean()),'block_bootstrap_95_ci':bootstrap_mean_ci(loss)})
    save_json(ROOT/'results/media_model_comparison.json',result);return result

if __name__=='__main__':run()
