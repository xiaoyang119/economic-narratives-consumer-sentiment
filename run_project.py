"""Rebuild the frozen research snapshot, offline by default."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--offline',action='store_true',help='Use retained snapshots; this is the default');p.add_argument('--refresh',action='store_true',help='Refetch public sources for the frozen cutoff; may change corpus coverage');p.add_argument('--report',action='store_true',help='Also rebuild the report PDF and Markdown');args=p.parse_args()
    if args.offline and args.refresh:p.error('Choose --offline or --refresh')
    scripts=[]
    if args.refresh:scripts+=['fetch_data.py','fetch_extra_feeds.py','collect_corpus.py','fetch_vintages.py']
    scripts+=['analyze.py','media_comparison.py','news_index_comparison.py','compare_model_annotations.py','analyze_ai_labels.py','build_dashboard.py','evaluate_annotations.py']
    if args.report:scripts+=['build_report.py']
    for script in scripts:subprocess.run([sys.executable,str(ROOT/'src'/script)],cwd=ROOT,check=True)
    print('Research outputs rebuilt. Documents describe the frozen 2026-10-14 cutoff. See README.md for source and validation limits.')

if __name__=='__main__':main()
