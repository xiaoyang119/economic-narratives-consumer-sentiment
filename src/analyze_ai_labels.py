"""Descriptive downstream analysis of AI labels; no ground-truth accuracy claims."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ['price_level_frame', 'inflation_rate_frame', 'household_frame',
          'aggregate_frame', 'forecast_frame']
TONES = ['negative', 'neutral', 'positive']


def summarize(frame):
    n = len(frame)
    counts = frame.tone.value_counts().reindex(TONES, fill_value=0)
    return {'n': n, 'tone_counts': {k: int(v) for k, v in counts.items()},
            'negative_share': float(counts['negative']/n),
            'frames': {c: {'n': int(frame[c].eq('1').sum()),
                          'share': float(frame[c].eq('1').mean())} for c in FRAMES},
            'numeric_claim_n': int(frame.numeric_claim.eq('1').sum()),
            'political_attribution': {k: int(v) for k,v in frame.political_credit_blame.value_counts().items()},
            'verified_numeric_claim_n': int(frame.factual_calibration.isin(
                ['matches_official_release','mismatches_official_release']).sum())}


def analyze():
    inputs = {'Claude Sonnet5.5': 'annotator_A_filled.csv', 'DeepSeek V41-Flash': 'annotator_B.csv'}
    data = {k: pd.read_csv(ROOT/'annotations'/v,dtype=str).fillna('') for k,v in inputs.items()}
    provenance = json.loads((ROOT/'annotations/ANNOTATION_PROVENANCE.json').read_text())
    assert provenance['human_paired_n'] == 0
    reference = pd.read_csv(ROOT/'annotations/annotator_A.csv',dtype=str).fillna('')
    for name,f in data.items():
        if len(f)!=300 or f.item_id.duplicated().any() or set(f.item_id)!=set(reference.item_id):
            raise ValueError(f'{name}: unexpected annotation sample')
        for c in FRAMES+['numeric_claim']:
            if not set(f[c]).issubset({'0','1'}): raise ValueError(f'Invalid {c}')
        if not set(f.tone).issubset(TONES): raise ValueError('Invalid tone')
        original=f.merge(reference[['item_id','text','source_kind','published_date']],on='item_id',suffixes=('_new','_original'),validate='one_to_one')
        if not all(original[c+'_new'].eq(original[c+'_original']).all() for c in ['text','source_kind','published_date']):
            raise ValueError('Sample metadata changed')
        f['month']=f.published_date.str[:7]
    result = {'status':'exploratory_AI_labeled_descriptive_analysis',
              'unit':'headline or Reddit post title', 'sample_n':300,
              'weighting':'unweighted stratified annotation sample; not population estimates',
              'versions':'user-reported', 'human_validated':False,
              'accuracy':None,'precision':None,'recall':None,'F1':None,
              'causal_effect':None,'media_sentiment_regression':'not estimated: four monthly bins',
              'models':{}}
    for name,f in data.items():
        model={'overall':summarize(f),
               'by_source_kind':{k:summarize(g) for k,g in f.groupby('source_kind')},
               'by_month':{k:summarize(g) for k,g in f.groupby('month')},
               'tone_within_frames':{c:{k:summarize(g) for k,g in f.groupby(c)} for c in FRAMES}}
        result['models'][name]=model
    out=ROOT/'results/ai_label_analysis.json'
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    names=list(data)
    def pct(x): return f'{100*x:.1f}%'
    lines=['# Exploratory analysis using AI-classified media texts','',
        'A fixed stratified sample of 300 headlines and Reddit post titles was labeled by Claude Sonnet5.5 and DeepSeek V41-Flash (version identifiers supplied by the user). These are AI outputs, not human annotations. Actual prompts and blinding were not recorded. No model is used as ground truth, and disagreement is retained rather than resolved into manufactured consensus. All proportions below describe this unweighted sample.', '',
        '## Economic tone', '', '| Label | '+ ' | '.join(names)+' |', '|---|---:|---:|']
    for tone in TONES:
        lines.append('| '+tone.title()+' | '+' | '.join(f'{result["models"][n]["overall"]["tone_counts"][tone]} ({pct(result["models"][n]["overall"]["tone_counts"][tone]/300)})' for n in names)+' |')
    lines+=['','## Negative tone by source type','','| Source type | Items | '+' | '.join(names)+' |','|---|---:|---:|---:|']
    for k in ['national','local','social']:
        rows=[result['models'][n]['by_source_kind'][k] for n in names]
        lines.append(f'| {k} | {rows[0]["n"]} | '+' | '.join(pct(r['negative_share']) for r in rows)+' |')
    lines+=['','Differences are descriptive. Source type is confounded with topic, timing, sampling and wording. Small local-news cells limit comparisons. Neither negative content nor a source difference establishes bias.','','## Framing','','| Frame | '+' | '.join(names)+' |','|---|---:|---:|']
    for c in FRAMES:
        lines.append('| '+c.replace('_frame','').replace('_',' ').title()+' | '+' | '.join(f'{result["models"][n]["overall"]["frames"][c]["n"]} ({pct(result["models"][n]["overall"]["frames"][c]["share"])})' for n in names)+' |')
    lines+=['','Frames can co-occur. Rate-focused coverage need not imply low household pressure, because slower price growth does not mean lower price levels. Text flags do not establish a psychological mechanism.','','## Monthly descriptions','','| Month | Items | '+' | '.join(n+' negative' for n in names)+' |','|---|---:|---:|---:|']
    for month in sorted(result['models'][names[0]]['by_month']):
        rows=[result['models'][n]['by_month'][month] for n in names]
        lines.append(f'| {month} | {rows[0]["n"]} | '+' | '.join(pct(r['negative_share']) for r in rows)+' |')
    lines+=['','Only four monthly bins are available. October ends on 14 October and is sampled more heavily. These rates cannot establish a trend, election effect, media-sentiment association or predictive improvement. No regression on four bins is presented.','','## Political attribution and factual calibration','','| Measure | '+' | '.join(names)+' |','|---|---:|---:|']
    for k in ['credit','blame','both','mention_only','none']:
        lines.append('| '+k+' | '+' | '.join(str(result['models'][n]['overall']['political_attribution'].get(k,0)) for n in names)+' |')
    for label,key in [('Numerical claims flagged','numeric_claim_n'),('Numerical claims verified against an official release','verified_numeric_claim_n')]:
        lines.append('| '+label+' | '+' | '.join(str(result['models'][n]['overall'][key]) for n in names)+' |')
    lines+=['','Credit and blame refer to model-coded attribution, not political bias. A flag for a number is not a completed fact check. Neither annotation file contains a verified numerical match or mismatch, so misinformation rates remain unavailable.','','## Findings supported by both label sets','']
    for c in ['inflation_rate_frame','price_level_frame','household_frame','aggregate_frame']:
        shares=[result['models'][n]['overall']['frames'][c]['share'] for n in names]
        lines.append(f'- {c.replace("_frame", "").replace("_", " ").capitalize()} appears in {pct(min(shares))} to {pct(max(shares))} of sampled texts across the two label sets.')
    lines+=['','Both label sets contain more negative than positive items. This supports the narrow description that negative economic implications are more common than positive ones in this selected sample under both classifiers. It does not establish disproportionate negativity relative to economic events or the broader media population.','','## What changes in the project','',
        'The AI labels now support descriptive tone, framing, source, month and political-attribution tables. Economic forecast results are unchanged. Accuracy, precision, recall and F1 on this project remain unavailable without an independently established reference set. Human agreement and adjudicated truth are not claimed. The existing retrospective external news-index test remains separate from this four-month text sample.']
    (ROOT/'deliverables/ai_label_analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v['overall'] for k,v in result['models'].items()},indent=2))
    return result


if __name__=='__main__': analyze()
