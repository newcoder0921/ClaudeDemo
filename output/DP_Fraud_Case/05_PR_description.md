## SCRUM-25: Fraud Case data product – PRD, contracts, build and tests

**Jira:** [SCRUM-25](https://monishapm.atlassian.net/browse/SCRUM-25) (Feature epic) · stories [SCRUM-26](https://monishapm.atlassian.net/browse/SCRUM-26)–[SCRUM-31](https://monishapm.atlassian.net/browse/SCRUM-31)
**Related:** SCRUM-17 (Member 360) provides the member lookup. This PR is independent: it carries its own copy of `dp_framework`.

### Summary
- Builds `fraud_case`, one governed, typed row per fraud case, from the case-management extract.
- Lifecycle and loss checks (DQ-06..DQ-11) and derived metrics: is_closed, days_to_close, case_age_days, loss_confirmation_ratio.
- Links cases to Member 360. Per the PO decision, unmatched cases are **kept and flagged**.
- Built with the `prd-to-data-product` workflow.

### What changed
| Path | What |
|---|---|
| `sources/data/raw/DP_Fraud_Case.csv` | Case-management extract (100 cases) |
| `data/output/product/DP_Fraud_Case.csv` | Same file, used as the target sample (columns and order) |
| `output/DP_Fraud_Case/PRD_Fraud_Case.{md,docx}` | PRD: dictionary with types, mapping, DQ, open questions |
| `output/DP_Fraud_Case/Data_Dictionary_Fraud_Case.xlsx` | Source, target and mapping sheets |
| `output/DP_Fraud_Case/stories.md` | Each story's acceptance criteria → test |
| `output/DP_Fraud_Case/Test_Report_Fraud_Case.md` | Test inventory, DQ results, hand-checked values |
| `output/DP_Fraud_Case/04_code/contracts/` | Extract contract (13 cols) and product contract (20 cols) |
| `output/DP_Fraud_Case/04_code/src/fraud_case/` | config, transform, dq_rules, exceptions, run (CLI) |
| `output/DP_Fraud_Case/04_code/src/dp_framework/` | Shared framework (copied unchanged) |
| `output/DP_Fraud_Case/04_code/sql/ddl/` | DDL generated from the contracts |
| `output/DP_Fraud_Case/04_code/tests/` | 80 pytest tests + member_360 test data |

### Story → test traceability
| Story | Jira | Status | Tests |
|---|---|---|---|
| FR-01 Ingest | SCRUM-26 | Done | `test_ingest.py` (5) |
| FR-02 Types | SCRUM-27 | Done | `test_standardize.py` (9), `test_types.py` (24) |
| FR-03 Lifecycle & loss | SCRUM-28 | Done (DQ-10 severity is a switch) | `test_lifecycle.py` (15) |
| FR-04 Member link | SCRUM-29 | Done | `test_member_link.py` (4) |
| FR-05 Metrics | SCRUM-30 | Done (SLA days is a switch) | `test_metrics.py` (8) |
| FR-06 Publish | SCRUM-31 | Done locally | `test_publish.py` (15) |

### How to test
```bash
cd output/DP_Fraud_Case/04_code
pip install pandas pytest
pytest -q
python -m src.fraud_case.run --member-ref tests/data/member_360.csv --as-of 2026-10-04
```

### Test results
- `pytest -q` → **80 passed**
- Pipeline run → **SUCCESS**:
  - 100 rows, 0 rejects
  - DQ-01..DQ-11 Pass; DQ-12 Warn (90 members not in Member 360 yet, as expected)
  - 105 exceptions: 90 MEMBER_NOT_FOUND, 15 CRITICAL_CASE_AGED

### Open questions (PRD section 11)
- Q1: 90 of 100 members aren't in member_360 yet.
- Q2: Account IDs are A + 7 digits, while the banking sources use A + 5.
- Q3: Time zone is not stated.
- Q4: Queue routing ignores case type.
- Q5: All 60 open cases are 30–63 days old. What is the SLA per priority?
- Q6: Should Confirmed Fraud with $0 loss warn or reject?
- Q7: There is no status history.

### Checklist
- [x] Tests pass
- [x] DDL in sync with contracts (enforced by a test)
- [x] Docs: PRD, dictionary, stories, test report, README
- [x] No secrets; no PII beyond pseudonymous IDs
- [x] Generated files (`*.db`, `out/`) are git-ignored
