"""Supplement the search pilot with direct publisher RSS feeds."""
import json,concurrent.futures
from fetch_data import fetch,RAW
JOBS=[('direct_npr.xml','https://feeds.npr.org/1006/rss.xml','national','NPR'),
 ('direct_cnbc.xml','https://www.cnbc.com/id/20910258/device/rss/rss.html','national','CNBC'),
 ('direct_foxbusiness.xml','https://moxie.foxbusiness.com/google-publisher/economy.xml','national','Fox Business'),
 ('direct_calmatters.xml','https://calmatters.org/category/economy/feed/','local','CalMatters'),
 ('direct_texastribune.xml','https://www.texastribune.org/feeds/sections/economy/','local','The Texas Tribune'),
 ('direct_reddit_economy.xml','https://www.reddit.com/r/economy/new.rss?limit=100','social','r/economy')]
if __name__=='__main__':
    def one(j):
        n,u,k,s=j;r=fetch(n,u);r.update(source_kind=k,publisher=s,window_start='2026-07-01',window_end='2026-10-15',query='Direct publisher economics/business feed');return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:r=list(p.map(one,JOBS))
    (RAW/'extra_feed_manifest.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
    for x in r:print(x['file'],x['status'],x.get('bytes',x.get('error')))
