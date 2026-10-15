"""Build a self-contained dashboard that runs locally without a server."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def build():
    def load(name):return json.loads((ROOT/'results'/name).read_text())
    def records(path):return json.loads(pd.read_csv(path).to_json(orient='records'))
    data={'cutoff':'2026-10-14','forecasts':records(ROOT/'results/forecasts.csv'),'metrics':load('forecast_metrics.json'),
      'corpus':json.loads((ROOT/'data/processed/corpus_coded.json').read_text()),'summary':load('corpus_summary.json'),
      'benchmark':load('nlp_benchmark.json'),'audit':load('data_audit.json'),'subgroups':load('survey_subgroups.json'),'news_index':load('news_index_comparison.json'),
      'model_annotations':load('model_annotation_comparison.json'),
      'media':records(ROOT/'results/media_monthly_pilot.csv'),
      'events':[{'date':'2026-09-30','event':'August PCE and Q2 GDP third estimate released','source':'https://www.bea.gov/news/schedule/full'},
                {'date':'2026-10-02','event':'September employment report released','source':'https://www.bls.gov/news.release/empsit.nr0.htm'},
                {'date':'2026-10-09','event':'October preliminary sentiment released','source':'https://www.sca.isr.umich.edu/'},
                {'date':'2026-10-23','event':'October final sentiment scheduled','source':'https://www.sca.isr.umich.edu/'},
                {'date':'2026-10-29','event':'Q3 advance GDP and September PCE scheduled','source':'https://www.bea.gov/news/schedule/full'}]}
    (ROOT/'results/dashboard_snapshot.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    html=(ROOT/'src/dashboard_template.html').read_text()
    html=html.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    out=ROOT/'deliverables/dashboard.html';out.write_text(html,encoding='utf-8');print(out)

if __name__=='__main__':build()
