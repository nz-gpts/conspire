# Frequency investigation

Measure these independently:

- `conspiracy`
- `conspiracies`
- `conspiracy theory`
- `conspiracy theories`
- `conspiracy theorist`
- `conspiracy theorists`

Do not merge them until each series has been inspected.

## Corpus separation

Google Books Ngram measures a digitized-books corpus. It is **not** a measurement of the web.

Web-era sources must be stored as separate series with their own corpus definitions. News, forums, social platforms and general web crawls must not be silently combined.

## Change points

`src/change_points.py` ranks abrupt year-to-year changes as candidates for investigation. A flagged year is an observation, not an explanation. Historical events are attached only after the change is measured.
