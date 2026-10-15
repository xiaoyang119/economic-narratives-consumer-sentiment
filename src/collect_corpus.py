"""Collect headline metadata only; preserve search dates and sampling limitations."""
from pathlib import Path
import sys,json,urllib.parse,xml.etree.ElementTree as ET,re,hashlib,html
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
import concurrent.futures
from fetch_data import fetch,RAW,ROOT

NATIONAL='(site:reuters.com OR site:apnews.com OR site:cnbc.com OR site:foxbusiness.com OR site:npr.org OR site:cnn.com)'
LOCAL='(site:texastribune.org OR site:calmatters.org OR site:chicagotribune.com OR site:inquirer.com OR site:startribune.com OR site:seattletimes.com OR site:denverpost.com OR site:ajc.com OR site:cleveland.com OR site:detroitnews.com)'
TERMS='(economy OR inflation OR unemployment OR "cost of living")'

def months():
    for year in range(2018,2027):
        for month in range(1,13):
            if (year,month)>(2026,10): return
            start=f'{year}-{month:02d}-01'
            end=f'{year+1}-01-01' if month==12 else f'{year}-{month+1:02d}-01'
            if (year,month)==(2026,10): end='2026-10-15'
            yield start,end

def collect():
    jobs=[]
    for start,end in months():
        for kind,sites in [('national',NATIONAL),('local',LOCAL)]:
            query=f'{TERMS} {sites} after:{start} before:{end}'
            url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'en-US','gl':'US','ceid':'US:en'})
            jobs.append((f'news/{start[:7]}_{kind}.xml',url,kind,start,end,query))
    for community in ['Economics','economy','personalfinance','news']:
        for term in ['inflation','unemployment','cost of living']:
            url=f'https://www.reddit.com/r/{community}/search.rss?'+urllib.parse.urlencode({'q':term,'restrict_sr':'on','sort':'new','limit':100})
            jobs.append((f'social/{community}_{term.replace(" ","_")}.xml',url,'social','','',term))
    (RAW/'news').mkdir(exist_ok=True);(RAW/'social').mkdir(exist_ok=True)
    def one(job):
        name,url,kind,start,end,q=job
        if (RAW/name).exists():
            result={'file':str((RAW/name).relative_to(ROOT)),'url':url,'status':'cached'}
        else: result=fetch(name,url)
        result.update(source_kind=kind,window_start=start,window_end=end,query=q)
        # Public usernames are unnecessary for this study. Remove them from retained feeds.
        if kind=='social' and (RAW/name).exists():
            p=RAW/name;text=p.read_text(encoding='utf-8')
            text=re.sub(r'<author>.*?</author>','',text,flags=re.S)
            text=re.sub(r'/u/[A-Za-z0-9_-]+','/u/REDACTED',text)
            text=re.sub(r'(reddit\.com/user/)[A-Za-z0-9_-]+',r'\1REDACTED',text)
            p.write_text(text,encoding='utf-8');result['privacy_transform']='removed author and username fields'
            result['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=[]
        for i,r in enumerate(pool.map(one,jobs)):
            results.append(r)
            if (i+1)%30==0: print('Collected',i+1,'of',len(jobs),flush=True)
    (RAW/'corpus_manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    parse(results)

def parse(manifest=None):
    if manifest is None: manifest=json.loads((RAW/'corpus_manifest.json').read_text())
    if (RAW/'extra_feed_manifest.json').exists():manifest=manifest+json.loads((RAW/'extra_feed_manifest.json').read_text())
    for name,q in [('additional_22.xml','US layoffs hiring jobs'),('additional_39.xml','US grocery prices housing affordability')]:
        manifest=manifest+[{'file':str((RAW/'news'/name).relative_to(ROOT)),'source_kind':'supplement','window_start':'2026-07-01','window_end':'2026-10-15','query':q+' after:2026-07-01 before:2026-10-15'}]
    rows=[]; exclusions=[]
    ns={'a':'http://www.w3.org/2005/Atom'}
    for item in manifest:
        p=ROOT/item['file']
        if not p.exists(): continue
        try: root=ET.fromstring(p.read_bytes())
        except ET.ParseError: continue
        if item['source_kind']!='social':
            entries=root.findall('./channel/item')
            for e in entries:
                title=e.findtext('title','');source=e.find('source');source_name=source.text if source is not None else item.get('publisher','')
                text=title.removesuffix(' - '+source_name)
                try: date=parsedate_to_datetime(e.findtext('pubDate')).date().isoformat()
                except Exception: continue
                if not (item['window_start']<=date<item['window_end']) or date>'2026-10-14':
                    exclusions.append({'reason':'outside_requested_window','title':text,'published_date':date});continue
                if re.search(r'local news, sports|^home$|^news$|^economy$',text,re.I):
                    exclusions.append({'reason':'homepage_or_non_article','title':text,'published_date':date});continue
                relevant=re.search(r'econom|inflation|unemploy|\bgdp\b|\bpce\b|\bcpi\b|payroll|layoff|hiring|job (?:market|growth|gains|loss|cuts|training)|\d[\d,]* jobs|cost.of.living|grocer|affordab|consumer (?:confidence|sentiment|spending)|household|mortgage|rent|wages|income|price|recession|business|tariff|tax|debt|tuition|lending|banking|deficit|manufactur|farmers|diesel|economic',text,re.I)
                if not relevant:
                    exclusions.append({'reason':'headline_not_economically_relevant','title':text,'published_date':date});continue
                kind=item['source_kind']
                if kind=='supplement':
                    locals=['Texas Tribune','Tallahassee','Greenville','WXLV','Spectrum','Democrat and Chronicle','Nevada Current','Civic Media','Deseret','Michigan Independent','AL.com','KVUE','Spotlight PA','New Orleans','WFMD','Idaho','Bozeman']
                    nationals=['Reuters','AP News','CNBC','CNN','Fox','CBS','Bloomberg','PBS','Newsweek','Forbes','USA Today','ABC News','Business Insider','Yahoo Finance','Investopedia','The Hill','New York Post','New York Times','Politico','NBC News','WSJ','Fortune','Kiplinger']
                    if any(k.lower() in source_name.lower() for k in locals):kind='local'
                    elif any(k.lower() in source_name.lower() for k in nationals):kind='national'
                    else:
                        exclusions.append({'reason':'outside_documented_publisher_pool','title':text,'published_date':date});continue
                rows.append({'text':text,'source':source_name,'source_kind':kind,'published_date':date,'url':e.findtext('link',''),'publisher_url':source.attrib.get('url','') if source is not None else '', 'observation_unit':'headline','retrieval_query':item['query'],'collection_file':item['file']})
        else:
            for e in root.findall('a:entry',ns):
                text=e.findtext('a:title','',ns);date=e.findtext('a:published','',ns)[:10]
                if not date or date>'2026-10-14': continue
                link=e.find('a:link',ns)
                match=re.search(r'/r/([^/]+)/',link.attrib.get('href','') if link is not None else '')
                community=match.group(1) if match else Path(item['file']).name.split('_')[0]
                rows.append({'text':text,'source':'r/'+community,'source_kind':'social','published_date':date,'url':link.attrib.get('href','') if link is not None else '', 'publisher_url':'https://www.reddit.com','observation_unit':'post_title','retrieval_query':item['query'],'collection_file':item['file']})
    unique={}
    for row in rows:
        foreign=re.search(r'\bindia\b|\bindian\b|\bgerman\w*\b|\bjapan\w*\b|\bbritain\b|\buk\b|\bbrazil\w*\b|\bcanada\b|\bcanadian\b|\bchina\b|\bchinese\b|\beurozone\b|\bunited kingdom\b|\bspain\b|\bphilippin\w*\b|\bsingapore\b|\baustralia\w*\b|\bargentina\b|\beuropean central bank\b|\bbank of england\b|\bengland\b|\bboj\b|\brba\b|\btürkiye\b|\bturkey\b|\beu investment\b|\biran.s (?:foreign|inflation)|\biran (?:reportedly|sells)',row['text'],re.I)
        us=re.search(r'\bu\.?s\.?\b|\bunited states\b|\bamerica\w*\b|federal reserve|\bfed\b|\bcbo\b|los angeles|new york|texas|california|us economy',row['text'],re.I)
        if foreign and not us:
            exclusions.append({'reason':'explicit_non_US_focus','title':row['text'],'published_date':row['published_date']});continue
        row['geographic_relevance']='explicit_US_or_cross_border' if us else 'inferred_from_US_outlet_or_community_not_individually_verified'
        key=re.sub(r'\W+',' ',html.unescape(row['text']).lower()).strip()
        if key in unique: unique[key]['duplicate_count']+=1;continue
        row['item_id']=hashlib.sha256(key.encode()).hexdigest()[:16];row['duplicate_count']=0
        unique[key]=row
    clean=list(unique.values())
    # Retain all deduplicated retrieved titles, not tone-selected titles.
    out=ROOT/'data'/'processed';out.mkdir(exist_ok=True)
    (out/'corpus.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'corpus_exclusions.json').write_text(json.dumps(exclusions,indent=2),encoding='utf-8')
    print('Corpus:',len(clean),'items;',len(rows)-len(clean),'duplicates;',len(exclusions),'date exclusions',flush=True)

if __name__=='__main__': collect()
