# Test Report – DP_Fraud_Case

- **Date:** 2026-10-05
- **Jira:** SCRUM-25 (stories SCRUM-26 to SCRUM-31)
- **Code:** `output/DP_Fraud_Case/04_code`
- **Environment:** Python 3.14.4, pandas, pytest, SQLite

## Result
- `pytest -q` → **80 passed, 0 failed**
- Real run `python -m src.fraud_case.run --as-of 2026-10-04` (member lookup: Member 360's published output) → **SUCCESS**, exit 0:
  - 100 rows published, 0 rejects
  - 105 exceptions: 90 MEMBER_NOT_FOUND + 15 CRITICAL_CASE_AGED

## Test inventory
| File | Story | Tests | What it proves |
|---|---|---|---|
| `test_ingest.py` | FR-01 | 5 | Row count, metadata, quoted amounts, rerun, header check |
| `test_standardize.py` | FR-02 | 9 | All 13 types; bad amount / ID / category / duplicate → rejects |
| `test_lifecycle.py` | FR-03 | 15 | Each of DQ-06..DQ-11 on the sample and with injected bad data |
| `test_member_link.py` | FR-04 | 4 | Flag counts, kept and reported, Warn not block, missing lookup |
| `test_metrics.py` | FR-05 | 8 | Metric functions, known cases, NULL rules, ranges, SLA exception |
| `test_publish.py` | FR-06 | 15 | Gate, table types, CSV shape and format, contract, DDL, idempotency, run log |
| `test_types.py` | Framework | 24 | Shared type parsers (currency, dates, booleans, lengths) |
| **Total** | | **80** | |

## DQ results (real run)
| Rule | Table | Severity | Checked | Failed | Status |
|---|---|---|---|---|---|
| DQ-06 | Fraud_Case_Extract | reject | 100 | 0 | Pass |
| DQ-07 | Fraud_Case_Extract | reject | 100 | 0 | Pass |
| DQ-08 | Fraud_Case_Extract | reject | 100 | 0 | Pass |
| DQ-09 | Fraud_Case_Extract | warn | 100 | 0 | Pass |
| DQ-10 | Fraud_Case_Extract | warn | 100 | 0 | Pass |
| DQ-11 | Fraud_Case_Extract | reject | 100 | 0 | Pass |
| DQ-01 | fraud_case | block | 100 | 0 | Pass |
| DQ-02 | fraud_case | block | 100 | 0 | Pass |
| DQ-03 | fraud_case | block | 100 | 0 | Pass |
| DQ-04 | fraud_case | block | 100 | 0 | Pass |
| DQ-05 | fraud_case | block | 100 | 0 | Pass |
| DQ-12 | fraud_case | warn | 100 | 90 | Warn (expected: Member 360 has 10 members) |

## Hand-checked values
| Case | Check | Expected | Actual |
|---|---|---|---|
| FC0000002 | days_to_close (8/1 16:00 → 8/4 16:00) | 3.00 | 3.00 |
| FC0000002 | loss_confirmation_ratio (299.50 / 374.38) | 0.8000 | 0.8000 |
| FC0000001 | case_age_days (8/1 08:00 → 10/4) | 63 | 63 |
| FC0000011 | Oldest open Critical case | 60 days | 60 days |
| SLA 45 | Critical cases aged > 45 days | FC11, 15, 19, 31, 35, 39, 51 | same 7 |

## Not covered by automated tests
- Performance at volume (sample only has 100 rows)
- Access roles / catalog (platform tasks)
