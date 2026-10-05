# DP_Fraud_Case – build

Builds `fraud_case` (one row per fraud case) from the case-management extract `sources/data/raw/DP_Fraud_Case.csv`.
It uses the same contract-driven `dp_framework` as DP_Member_360 (copied unchanged).

## Layout
```
contracts/
  sources.py        # extract: 13 typed columns, patterns, allowed values
  fraud_case.py     # product: 13 + 5 derived + 2 audit columns; dq_exceptions
src/dp_framework/   # shared framework (do not edit here; change it in DP_Member_360 first)
src/fraud_case/
  config.py         # paths, member_360 lookup path, Settings (DQ-10 severity, critical SLA days)
  transform.py      # days_to_close, case_age_days, loss_confirmation_ratio, member lookup
  dq_rules.py       # DQ-01..DQ-12
  exceptions.py     # MEMBER_NOT_FOUND, CRITICAL_CASE_AGED
  run.py            # pipeline + CLI
sql/ddl/            # generated from contracts
tests/              # pytest; tests/data/member_360.csv = Member 360 as built today (10 members)
```

## Run
```bash
pip install pandas pytest
# needs member_360.csv from DP_Member_360 (default path) or --member-ref
python -m src.fraud_case.run --as-of 2026-10-04
python -m src.fraud_case.run --member-ref tests/data/member_360.csv --as-of 2026-10-04
```
Outputs:
- `fraud_case.db`: `raw_fraud_case_extract`, `stg_fraud_case_extract`, `fraud_case`, `rejects`, `dq_results`, `run_log`, `dq_exceptions`
- `out/`: `fraud_case.csv`, `dq_exceptions.csv`, `data_contract.json`, `data_contract.md`

## Test
```bash
pytest -q
```

## Common changes
| Change | Where |
|---|---|
| A type or allowed value | `contracts/*.py`, then `python -m src.fraud_case.run --write-ddl` |
| Confirmed Fraud with $0 loss should reject | `Settings.confirmed_zero_loss_severity = "reject"` |
| Critical SLA | `Settings.critical_sla_days` |

Docs: the PRD, dictionary, stories, test report and Jira links are in `output/DP_Fraud_Case/`.
