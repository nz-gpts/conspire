"""Simple, dependency-light change-point candidates for dated frequency series.

Input CSV columns: year,value
Output: ranked years whose year-over-year standardized change is unusual.

This flags candidates; it does not infer causes.
"""
from __future__ import annotations
import csv, math, statistics, sys

def load(path):
    rows=[]
    with open(path,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((int(r["year"]),float(r["value"])))
    return sorted(rows)

def candidates(rows):
    changes=[]
    for (y0,v0),(y1,v1) in zip(rows,rows[1:]):
        changes.append((y1,v1-v0))
    vals=[d for _,d in changes]
    if len(vals)<3:
        return []
    mean=statistics.mean(vals)
    sd=statistics.stdev(vals)
    if sd==0:
        return []
    return sorted(((abs((d-mean)/sd),y,d,(d-mean)/sd) for y,d in changes),reverse=True)

if __name__=="__main__":
    for score,year,delta,z in candidates(load(sys.argv[1]))[:20]:
        print(f"{year}\tdelta={delta:.8g}\tz={z:.3f}")
