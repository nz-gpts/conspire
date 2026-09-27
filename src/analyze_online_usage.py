#!/usr/bin/env python3
"""Measure WHEN a term rises online and WHO contributes to the rise.

Input: LOCO corpus JSON (LOCO.json). This script deliberately uses document
metadata + text rather than treating LOCO's conspiracy/mainstream labels as
the thing being measured.

Outputs CSVs under cases/<case>/results:
  yearly_term_usage.csv
  yearly_source_usage.csv
  change_points.csv
  source_contribution_at_change_points.csv
"""
import argparse, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd

PHRASES = ["conspiracy", "conspiracy theory", "conspiracy theorist"]

def pick(row, *names):
    for n in names:
        if n in row and row[n] not in (None, ""): return row[n]
    return None

def load_rows(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for k in ("documents","data","rows"):
            if isinstance(data.get(k), list): return data[k]
        return list(data.values())
    return data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("loco_json")
    ap.add_argument("--case", default="conspiracy")
    args=ap.parse_args()
    rows=load_rows(args.loco_json)
    out=Path("cases")/args.case/"results"; out.mkdir(parents=True, exist_ok=True)
    docs=[]
    for r in rows:
        text=str(pick(r,"text","document","content","body") or "")
        date=pick(r,"date","upload_date","published","publication_date")
        site=str(pick(r,"website","domain","source","site") or "UNKNOWN")
        if not date: continue
        dt=pd.to_datetime(date, errors="coerce")
        if pd.isna(dt): continue
        rec={"year":int(dt.year),"site":site,"tokens":max(1,len(re.findall(r"\b\w+\b",text)))}
        low=text.lower()
        for p in PHRASES:
            rec[p]=len(re.findall(r"\b"+re.escape(p)+r"\b",low))
        docs.append(rec)
    df=pd.DataFrame(docs)
    if df.empty: raise SystemExit("No dated documents parsed; inspect LOCO field names.")

    annual=[]
    for year,g in df.groupby("year"):
        toks=g.tokens.sum()
        for p in PHRASES:
            n=int(g[p].sum())
            annual.append({"year":year,"term":p,"mentions":n,"documents":int((g[p]>0).sum()),
                           "all_documents":len(g),"tokens":int(toks),
                           "mentions_per_million_tokens":n/toks*1_000_000})
    a=pd.DataFrame(annual).sort_values(["term","year"])
    a.to_csv(out/"yearly_term_usage.csv",index=False)

    src=[]
    for (year,site),g in df.groupby(["year","site"]):
        for p in PHRASES:
            n=int(g[p].sum())
            if n: src.append({"year":year,"site":site,"term":p,"mentions":n,
                              "documents":int((g[p]>0).sum()),"tokens":int(g.tokens.sum())})
    s=pd.DataFrame(src)
    s.to_csv(out/"yearly_source_usage.csv",index=False)

    cps=[]
    for p,g in a.groupby("term"):
        g=g.sort_values("year").copy()
        vals=g.mentions_per_million_tokens
        # transparent first-pass detector: year-on-year log-rate jump.
        g["log_rate"]=vals.map(lambda x: math.log1p(x))
        g["delta"]=g.log_rate.diff()
        for _,r in g.nlargest(min(5,len(g)),"delta").iterrows():
            if pd.notna(r.delta):
                cps.append({"term":p,"year":int(r.year),"rate_per_million":r.mentions_per_million_tokens,
                            "log_rate_delta":r.delta,"method":"top year-on-year log(rate+1) increase"})
    c=pd.DataFrame(cps).sort_values(["term","log_rate_delta"],ascending=[True,False])
    c.to_csv(out/"change_points.csv",index=False)

    contrib=[]
    if not s.empty:
        for _,cp in c.iterrows():
            q=s[(s.term==cp.term)&(s.year==cp.year)].sort_values("mentions",ascending=False)
            total=q.mentions.sum()
            for _,r in q.head(20).iterrows():
                contrib.append({"term":cp.term,"year":cp.year,"site":r.site,"mentions":r.mentions,
                                "share_of_mentions_that_year":r.mentions/total if total else 0})
    pd.DataFrame(contrib).to_csv(out/"source_contribution_at_change_points.csv",index=False)
    print(f"Parsed {len(df):,} dated documents; wrote results to {out}")

if __name__=="__main__": main()
