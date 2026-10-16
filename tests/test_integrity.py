"""Integrity checks for the actual scientific risks in this project."""
import unittest,json,zipfile,io,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

class ResearchIntegrity(unittest.TestCase):
    def test_all_vintage_headers_match_requested_dates(self):
        manifest=json.loads((ROOT/'data/raw/vintage_manifest.json').read_text())
        self.assertEqual(len(manifest),202)
        for row in manifest:
            path=ROOT/row['file'];self.assertTrue(path.exists())
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if not name.endswith('.csv'):continue
                    headers=pd.read_csv(io.BytesIO(z.read(name)),nrows=0).columns[1:]
                    for h in headers:self.assertTrue(h.endswith('_'+row['vintage_date'].replace('-','')))
    def test_economic_observations_precede_origin(self):
        f=pd.read_csv(ROOT/'data/processed/forecast_features.csv')
        for field in ['unemployment_observation','pce_observation','gdp_observation','sentiment_observation']:
            self.assertTrue((pd.to_datetime(f[field])<=pd.to_datetime(f.vintage_date)).all())
            self.assertTrue((pd.to_datetime(f[field])<pd.to_datetime(f.month)).all())
        last=f.iloc[-1]
        self.assertEqual(last.gdp_observation,'2026-04-01')
        self.assertAlmostEqual(last.inflation,3.4190318245,places=8)
    def test_future_gdp_is_not_used(self):
        for p in (ROOT/'data/raw/vintages').glob('*.zip'):
            with zipfile.ZipFile(p) as z:
                d=pd.read_csv(io.BytesIO(z.read('quarterly.csv')))
                self.assertFalse((d.observation_date>='2026-07-01').any())
    def test_forecast_scores_reconcile(self):
        f=pd.read_csv(ROOT/'results/forecasts.csv');m=json.loads((ROOT/'results/forecast_metrics.json').read_text())
        for row in m:
            if row['window']!='All scored':continue
            subset=f[(f.model==row['model'])&(f.month<='2026-09-01')]
            self.assertEqual(len(subset),105)
            expected=float(np.sqrt(np.mean((subset.actual-subset.prediction)**2)))
            self.assertAlmostEqual(expected,row['RMSE'],places=10)
        self.assertTrue((f[f.month=='2026-10-01'].target_status=='preliminary').all())
    def test_corpus_dates_ids_and_sources(self):
        rows=json.loads((ROOT/'data/processed/corpus_coded.json').read_text())
        self.assertGreaterEqual(len(rows),300);self.assertEqual(len(rows),len({r['item_id'] for r in rows}))
        self.assertTrue(all('2026-07-01'<=r['published_date']<='2026-10-14' for r in rows))
        self.assertEqual({r['source_kind'] for r in rows},{'national','local','social'})
        self.assertFalse(any('getaddrinfo' in r['text'] for r in rows))
    def test_independent_human_labels_are_not_fabricated(self):
        a=pd.read_csv(ROOT/'annotations/annotator_A.csv');b=pd.read_csv(ROOT/'annotations/annotator_B.csv')
        self.assertEqual(len(a),300);self.assertEqual(set(a.item_id),set(b.item_id))
        self.assertTrue(a.tone.isna().all())
        provenance=json.loads((ROOT/'annotations/ANNOTATION_PROVENANCE.json').read_text())
        self.assertFalse(provenance['independent_human_annotation_completed'])
        self.assertEqual(provenance['human_paired_n'],0)
        self.assertEqual(set(provenance['models']),{'Claude','DeepSeek'})
        compare=json.loads((ROOT/'results/model_annotation_comparison.json').read_text())
        self.assertEqual(compare['paired_n'],300)
        self.assertFalse(compare['ground_truth_available'])
        self.assertAlmostEqual(compare['tone']['agreement'],228/300)
        self.assertNotIn('model_probability',a.columns);self.assertNotIn('source',a.columns)
        s=json.loads((ROOT/'results/corpus_summary.json').read_text());self.assertIsNone(s['project_corpus_macro_F1']);self.assertIsNone(s['human_agreement'])
    def test_external_benchmark_supports_reconcile(self):
        b=json.loads((ROOT/'results/nlp_benchmark.json').read_text())
        self.assertEqual(b['train_n']+b['test_n'],b['deduplicated_n'])
        for model in ['Naive Bayes','Dictionary']:
            c=np.array(b[model]['confusion_matrix']);self.assertEqual(int(c.sum()),b['test_n']);self.assertAlmostEqual(float(np.trace(c)/c.sum()),b[model]['accuracy'])
    def test_retrospective_index_is_not_claimed_real_time(self):
        news=json.loads((ROOT/'results/news_index_comparison.json').read_text())
        self.assertFalse(news['real_time_claim']);self.assertEqual(news['status'],'retrospective_only')
        self.assertEqual(len(news['metrics']),12)
        rows=pd.read_csv(ROOT/'results/news_index_forecasts.csv')
        self.assertEqual(set(rows.information_status),{'retrospective_news_index_without_historical_vintages'})
    def test_ai_labels_do_not_become_ground_truth(self):
        result=json.loads((ROOT/'results/ai_label_analysis.json').read_text())
        self.assertFalse(result['human_validated'])
        for key in ['accuracy','precision','recall','F1','causal_effect']:
            self.assertIsNone(result[key])
        for name,path in [('Claude Sonnet5.5','annotator_A_filled.csv'),('DeepSeek V41-Flash','annotator_B.csv')]:
            f=pd.read_csv(ROOT/'annotations'/path)
            model=result['models'][name]
            self.assertEqual(sum(model['overall']['tone_counts'].values()),300)
            self.assertEqual(sum(x['n'] for x in model['by_source_kind'].values()),300)
            self.assertEqual(sum(x['n'] for x in model['by_month'].values()),300)
            self.assertEqual(model['overall']['tone_counts']['negative'],int(f.tone.eq('negative').sum()))
            self.assertEqual(model['overall']['verified_numeric_claim_n'],0)
    def test_report_and_dashboard_integrity(self):
        p=PdfReader(ROOT/'deliverables/research_report.pdf');self.assertEqual(len(p.pages),12)
        text='\n'.join(page.extract_text() for page in p.pages)
        for phrase in ['14.10','4.75','46.3','independent human','retrospective','Causal design']:
            self.assertIn(phrase.lower(),text.lower())
        html=(ROOT/'deliverables/dashboard.html').read_text();self.assertNotIn('__DATA__',html);self.assertNotIn('<script src=',html)
    def test_no_username_fields_retained(self):
        for p in list((ROOT/'data/raw/social').glob('*.xml'))+[ROOT/'data/raw/direct_reddit_economy.xml',ROOT/'data/raw/reddit_test.xml']:
            text=p.read_text();self.assertNotIn('<author>',text)

if __name__=='__main__':unittest.main()
