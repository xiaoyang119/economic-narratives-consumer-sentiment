"""Retrieve genuine historical data vintages, with exact header verification."""
import concurrent.futures,json,calendar,zipfile,io,csv
from datetime import date,timedelta
from fetch_data import ROOT,RAW,fetch
IDS=['UNRATE','PCEPI','GDPC1','DSPIC96','UMCSENT']

def jobs():
    for y in range(2010,2027):
        for m in range(1,13):
            if (y,m)>(2026,10):return
            origin=date(y,m,1); vintage=(origin-timedelta(days=1)).isoformat()
            yield origin.isoformat(),vintage

def one(job):
    origin,vintage=job;name='vintages/'+origin+'.zip';path=RAW/name
    url='https://alfred.stlouisfed.org/graph/alfredgraph.csv?id='+','.join(IDS)+'&vintage_date='+','.join([vintage]*len(IDS))+'&cosd=2005-01-01&coed='+vintage
    r=fetch(name,url) if not path.exists() else {'file':str(path.relative_to(ROOT)),'url':url,'status':'cached'}
    r.update(origin=origin,vintage_date=vintage)
    if path.exists():
        b=path.read_bytes()
        try:
            z=zipfile.ZipFile(io.BytesIO(b));headers=[]
            for n in z.namelist():
                if n.endswith('.csv'):headers.extend(next(csv.reader(io.StringIO(z.read(n).decode('utf-8-sig'))))[1:])
            expected={s+'_'+vintage.replace('-','') for s in IDS}
            if set(headers)!=expected:raise ValueError('Vintage header mismatch '+repr(headers))
            r['headers_verified']=True
        except Exception as e:r['status']='invalid';r['error']=str(e)
    return r

if __name__=='__main__':
    (RAW/'vintages').mkdir(exist_ok=True)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for i,r in enumerate(pool.map(one,jobs())):
            results.append(r)
            if (i+1)%30==0: print('Vintage snapshots',i+1,'valid',sum(x.get('headers_verified',False) for x in results),flush=True)
    (RAW/'vintage_manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('Finished',len(results),'snapshots; valid',sum(x.get('headers_verified',False) for x in results))
