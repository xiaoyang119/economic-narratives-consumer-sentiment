"""Download public source snapshots, preserving provenance and failures."""
from pathlib import Path
import urllib.request, urllib.parse, gzip, json, hashlib, concurrent.futures,re
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'; RAW.mkdir(parents=True,exist_ok=True)
CUTOFF='2026-10-14'

def fetch(name,url):
    path=RAW/name
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; AcademicResearch/1.0)'})
        with urllib.request.urlopen(request,timeout=40) as response:
            data=response.read()
            if data[:2]==b'\x1f\x8b': data=gzip.decompress(data)
            content_type=response.headers.get('Content-Type','')
        if 'reddit.com/' in url:
            text=data.decode('utf-8')
            text=re.sub(r'<author>.*?</author>','',text,flags=re.S)
            text=re.sub(r'/u/[A-Za-z0-9_-]+','/u/REDACTED',text)
            text=re.sub(r'(reddit\.com/user/)[A-Za-z0-9_-]+',r'\1REDACTED',text)
            data=text.encode('utf-8')
        path.write_bytes(data)
        return {'file':str(path.relative_to(ROOT)),'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':content_type,'status':'ok'}
    except Exception as exc:
        return {'file':str(path.relative_to(ROOT)),'url':url,'status':'failed','error':str(exc)}

def main():
    jobs=[]
    for sid in ['UNRATE','UMCSENT','PCEPI','A191RL1Q225SBEA','DSPIC96','U6RATE','MORTGAGE30US','TDSP']:
        jobs.append((sid+'.csv',f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=2008-01-01&coed={CUTOFF}'))
    jobs.extend([
      ('news_test.xml','https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':'US inflation economy after:2026-09-01 before:2026-10-14','hl':'en-US','gl':'US','ceid':'US:en'})),
      ('reddit_test.xml','https://www.reddit.com/r/Economics/search.rss?'+urllib.parse.urlencode({'q':'inflation','restrict_sr':'on','sort':'new','limit':'100'})),
      ('michigan_home.html','https://www.sca.isr.umich.edu/'),
      ('frbsf_news_sentiment.xlsx','https://www.frbsf.org/wp-content/uploads/news_sentiment_data.xlsx?2026-10-14'),
      ])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda j:fetch(*j),jobs))
    (RAW/'manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    for r in results: print(r['file'],r['status'],r.get('bytes',r.get('error')))

if __name__=='__main__': main()
