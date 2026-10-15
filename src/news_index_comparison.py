"""Retrospective comparison with the SF Fed historical news index.

The economic inputs are genuine vintages. The historical news index is today's
reconstructed series, without vintage archives, so this is NOT a real-time
media forecast test. It must be reported separately from the core forecasts.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from analyze import ROOT,ols,predict,load_snapshot,save_json,bootstrap_mean_ci

def run():
    w=load_workbook(ROOT/'data/raw/frbsf_news_sentiment.xlsx',read_only=True,data_only=True)
    rows=list(w['Data'].values);d=pd.DataFrame(rows[1:],columns=['date','news_sentiment']).dropna();d.date=pd.to_datetime(d.date)
    d=d[d.date<='2026-10-14'];d.to_csv(ROOT/'data/processed/frbsf_news_daily.csv',index=False)
    monthly=d.groupby(d.date.dt.to_period('M')).news_sentiment.mean();monthly.index=(monthly.index+2).to_timestamp().strftime('%Y-%m-%d');monthly.name='news_index_lag2'
    f=pd.read_csv(ROOT/'data/processed/forecast_features.csv',index_col=0).join(monthly).dropna();f.to_csv(ROOT/'data/processed/news_index_features.csv')
    specs={'Macro baseline':['unemployment','inflation','gdp_growth'],
      'Macro plus news index':['unemployment','inflation','gdp_growth','news_index_lag2'],
      'Macro plus news and controls':['unemployment','inflation','gdp_growth','news_index_lag2','income_growth','price_3y'],
      'Dynamic economic baseline':['unemployment','inflation','gdp_growth','sentiment_last'],
      'Dynamic plus news index':['unemployment','inflation','gdp_growth','sentiment_last','news_index_lag2'],
      'Dynamic plus news and controls':['unemployment','inflation','gdp_growth','sentiment_last','news_index_lag2','income_growth','price_3y']}
    targets=pd.read_csv(ROOT/'data/processed/sentiment_targets.csv',index_col=0).iloc[:,0];records=[];coef=[]
    for origin,row in f[f.index>='2018-01-01'].iterrows():
        if origin>'2026-09-01':continue
        available=load_snapshot(origin).UMCSENT.dropna();available.index=available.index.strftime('%Y-%m-%d')
        for name,cols in specs.items():
            tr=f.loc[f.index<origin,cols].join(available.rename('target')).dropna()
            fit=ols(tr[cols],tr.target);pred=float(predict(fit,row[cols])[0]);actual=float(targets.loc[origin]);records.append({'month':origin,'model':name,'prediction':pred,'actual':actual,'error':actual-pred,'information_status':'retrospective_news_index_without_historical_vintages'})
            if 'news_index_lag2' in cols:
                k=cols.index('news_index_lag2');coef.append({'month':origin,'model':name,'news_coefficient':float(fit['beta'][k+1]/fit['sd'][k])})
    p=pd.DataFrame(records);p.to_csv(ROOT/'results/news_index_forecasts.csv',index=False);pd.DataFrame(coef).to_csv(ROOT/'results/news_index_coefficient_paths.csv',index=False)
    result={'status':'retrospective_only','source':'https://www.frbsf.org/research-and-insights/data-and-indicators/daily-news-sentiment-index/','source_updated':'2026-10-12','daily_n':len(d),'first_date':d.date.min().date().isoformat(),'last_date':d.date.max().date().isoformat(),'index_lag':'mean of calendar month t-2','real_time_claim':False,'limitation':'current reconstructed news-index values and historical methodology; original publication vintages unavailable; conservative date lag does not eliminate revision or construction look-ahead','metrics':[],'comparisons':[]}
    for window,start in [('2018 onward','2018-01-01'),('2021 onward','2021-01-01')]:
        selected=p[p.month>=start];errors=selected.pivot(index='month',columns='model',values='error')
        for name,g in selected.groupby('model',sort=False):
            result['metrics'].append({'window':window,'model':name,'n':len(g),'RMSE':float(np.sqrt(np.mean(g.error**2))),'MAE':float(np.abs(g.error).mean())})
        for baseline,extra in [('Macro baseline','Macro plus news index'),('Dynamic economic baseline','Dynamic plus news index')]:
            difference=errors[extra].to_numpy()**2-errors[baseline].to_numpy()**2
            result['comparisons'].append({'window':window,'baseline':baseline,'augmented':extra,'mean_squared_loss_difference':float(difference.mean()),'block_bootstrap_95_ci':bootstrap_mean_ci(difference)})
    save_json(ROOT/'results/news_index_comparison.json',result)
    print(pd.DataFrame(result['metrics']).to_string(index=False))
    return result

if __name__=='__main__':run()
