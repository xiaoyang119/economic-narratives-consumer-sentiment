"""Inventory sources and create a shareable academic project archive."""
from pathlib import Path
import json,zipfile,hashlib,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]

def package():
    inventories=[];known={}
    for name in ['manifest.json','vintage_manifest.json','corpus_manifest.json','extra_feed_manifest.json']:
        for row in json.loads((ROOT/'data/raw'/name).read_text()):known[str(Path(row['file']))]=row
    supplement={'phrasebank.zip':'https://huggingface.co/datasets/takala/financial_phrasebank/resolve/main/data/FinancialPhraseBank-v1.0.zip','michigan_charts.html':'https://data.sca.isr.umich.edu/charts.php','michigan_2026_partisanship.pdf':'https://data.sca.isr.umich.edu/fetchdoc.php?docid=81444','michigan_2024_method.pdf':'https://www.sca.isr.umich.edu/files/methodtransitionannouncement2024.pdf','bea_august_2026.html':'https://www.bea.gov/news/2026/personal-income-and-outlays-august-2026','frbsf_news_sentiment.xlsx':'https://www.frbsf.org/wp-content/uploads/news_sentiment_data.xlsx?2026-10-14','frbsf_news_page.html':'https://www.frbsf.org/research-and-insights/data-and-indicators/daily-news-sentiment-index/'}
    chart_html=(ROOT/'data/raw/michigan_charts.html').read_text(encoding='utf-8')
    for name in ['1bh','5bh','2h','3h']:
        match=re.search(r'href="(get-chart[^"<>]+n='+name+r'&[^"<>]*f=xls[^"<>]*)"',chart_html)
        if match:supplement['michigan_'+name+'.xls']='https://data.sca.isr.umich.edu/'+match.group(1)
    for name,term in [('additional_22.xml','US layoffs hiring jobs'),('additional_39.xml','US grocery prices housing affordability')]:
        supplement[name]='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':term+' after:2026-07-01 before:2026-10-15','hl':'en-US','gl':'US','ceid':'US:en'})
    for file in (ROOT/'data/raw').rglob('*'):
        if not file.is_file():continue
        rel=str(file.relative_to(ROOT));meta=known.get(rel,{})
        inventories.append({'file':rel,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size,'url':meta.get('url',supplement.get(file.name,'')),'vintage_date':meta.get('vintage_date'),'source_note':'retained research snapshot; usernames removed from Reddit feeds' if 'reddit' in file.name.lower() or file.parent.name=='social' else ''})
    (ROOT/'results/source_inventory.json').write_text(json.dumps(inventories,indent=2),encoding='utf-8')
    with zipfile.ZipFile(ROOT/'data/raw/phrasebank.zip') as z:
        (ROOT/'data/PHRASEBANK_LICENSE.txt').write_bytes(z.read('FinancialPhraseBank-v1.0/License.txt'))
    out=ROOT/'deliverables/project_package.zip'
    files=[]
    for directory in ['src','tests','data','results','figures','annotations','prompts','deliverables']:
        for p in (ROOT/directory).rglob('*'):
            if p.is_file() and p!=out and '__pycache__' not in p.parts and not p.name.endswith('.pyc'):files.append(p)
    files += [ROOT/'README.md',ROOT/'requirements.txt',ROOT/'run_project.py',ROOT/'PROJECT_STATUS.md',ROOT/'Final_Project_Applications_in_Finance_Oct_2026.pdf',ROOT/'Perceptual_Bias_Data.xlsx']
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,p.relative_to(ROOT))
    print('Archive:',out,'files:',len(files),'bytes:',out.stat().st_size)

if __name__=='__main__':package()
