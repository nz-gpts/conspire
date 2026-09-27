# Online-use analysis

This is the primary Conspire question: **when did a term begin appearing substantially more often online, and which sources contributed to the increase?**

## First corpus: LOCO

LOCO contains 96,743 web documents from 150 websites: 23,937 documents from 58 conspiracy-labelled sites and 72,806 from 92 mainstream sites. The published corpus metadata includes upload dates, website identity and social-media engagement measures. Mainstream documents range from 1853–2020; conspiracy-site documents from 2004–2020.

Dataset: https://osf.io/snpcg/
Paper: https://doi.org/10.3758/s13428-021-01698-z

## What we measure

We do **not** count documents merely because LOCO labelled their source as conspiracy/mainstream.

For each dated document we count literal occurrences of:
- `conspiracy`
- `conspiracy theory`
- `conspiracy theorist`

The first-pass pipeline then calculates annual mentions per million tokens, identifies the largest year-on-year increases, and ranks the websites contributing mentions at each candidate change point.

## Run

Download `LOCO.json` from the authors' OSF dataset, then:

```bash
python src/analyze_online_usage.py /path/to/LOCO.json --case conspiracy
```

Outputs:
- `cases/conspiracy/results/yearly_term_usage.csv`
- `cases/conspiracy/results/yearly_source_usage.csv`
- `cases/conspiracy/results/change_points.csv`
- `cases/conspiracy/results/source_contribution_at_change_points.csv`

## Critical limitation

LOCO is not "the internet." Its documents were retrieved by crossing predefined seed phrases with predefined lists of websites using Google. Its source composition and date coverage therefore affect observed rates. A LOCO change point is a **candidate web-corpus change point**, not proof of a global internet change.

The result must be checked against at least one independent corpus before Conspire calls it a broader online-use shift.
