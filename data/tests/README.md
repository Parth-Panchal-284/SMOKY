# Test datasets

Five files, each stressing a different part of the pipeline.

| File | Stresses | What should catch it |
|---|---|---|
| `1_date_chaos.csv` | 9 date formats incl. epoch, ISO-8601, Japanese text; nulls as `NULL`/`N/A`/`-`/`none`/`NaN`; negative age | SCHEMA_MD |
| `2_duplicate_swamp.csv` | Same entity via accents, casing, honorifics, punctuation, name order (Wei Zhang / Zhang Wei), email `+tags` | DUPLICATE_MD |
| `3_outlier_minefield.csv` | Negative bill, age 999 and -7, weight `1.2e3` and `0.00001`, temp 412.7, HR 0 and 240, `1.0E7` | ANOMALY_MD |
| `4_parser_torture.csv` | Embedded commas/newlines/tabs, escaped quotes, emoji, RTL Arabic, 180-char field, zero-width space | the CSV reader |
| `5_schema_nightmare.csv` | Duplicate headers (`Amount`/`amount`), an entirely empty column, header with trailing space, booleans as true/TRUE/1/yes/no, numbers as words | SCHEMA_MD |

## Worth knowing before you run them

The deterministic profiler scores `2_duplicate_swamp` and `3_outlier_minefield`
at **100** — it finds nothing wrong. That is not a bug, it is the point:

- the profiler's duplicate check is exact-match-after-normalisation, so
  `José García` vs `Jose Garcia` vs `Zhang Wei`/`Wei Zhang` slip past it
- the health score penalises nulls, mixed dates and duplicates — not outliers

So these two files isolate exactly what the LLM specialists add over
deterministic checks. If DUPLICATE_MD and ANOMALY_MD are working, they will
find plenty in files the profiler calls perfect.

## Run one

    node --env-file=.env run.mjs --mode both --csv data/tests/2_duplicate_swamp.csv

Or upload it in Triage at http://127.0.0.1:8501/?page=triage
