# Fraud Case – stories and build status

Source: [PRD_Fraud_Case.md](PRD_Fraud_Case.md), section 8, with types from sections 5–6, mapping from section 7 and DQ rules from section 10.
Code: [04_code/](04_code/README.md) · Tests: `pytest -q` → 80 passed · Test report: [Test_Report_Fraud_Case.md](Test_Report_Fraud_Case.md)

| Story | Jira | Status |
|---|---|---|
| FR-01 Ingest case extract | SCRUM-26 | Built |
| FR-02 Standardize data types | SCRUM-27 | Built |
| FR-03 Lifecycle and loss checks | SCRUM-28 | Built (DQ-10 severity is a switch until Q6 is decided) |
| FR-04 Link to Member 360 | SCRUM-29 | Built (90/100 unmatched until Member 360 has a full member feed, Q1) |
| FR-05 Derived case metrics | SCRUM-30 | Built (SLA days is a switch until Q5 is decided) |
| FR-06 Publish and govern | SCRUM-31 | Built locally; catalog and access roles are platform tasks |

## FR-01 Ingest case extract
- [x] 100 rows in raw: `test_ingest.py::test_raw_row_count_matches_file`
- [x] Quoted amounts stay in one column: `test_quoted_amounts_stay_in_one_column`
- [x] Rerun doesn't duplicate rows: `test_rerun_does_not_duplicate_raw_rows`
- [x] Changed header fails fast with the file name: `test_changed_header_fails_fast`
- [x] Load metadata on every row: `test_raw_rows_carry_load_metadata`

## FR-02 Standardize data types
- [x] All 13 columns typed: `test_standardize.py::test_all_13_columns_have_contract_types`, `test_staging_table_declares_contract_types`
- [x] FC0000007 suspected = 1060.33; FC0000002 close = 2026-08-04 16:00: `test_amounts_and_timestamps_parse`
- [x] Bad values / malformed IDs / unknown categories / duplicate IDs → rejects with column, raw value and reason: `test_unparseable_amount_is_rejected`, `test_malformed_member_id_is_rejected`, `test_value_outside_allowed_list_is_rejected`, `test_duplicate_case_ids_are_rejected`
- [x] 0 rejects on the sample: `test_sample_has_no_rejects`

## FR-03 Lifecycle and loss checks
- [x] Sample passes DQ-06..DQ-11: `test_lifecycle.py::test_sample_passes_lifecycle_rules`
- [x] DQ-06 (3 variants), DQ-07, DQ-08 reject with the rule ID: `test_incomplete_lifecycle_is_rejected`, `test_close_before_open_is_rejected`, `test_confirmed_above_suspected_is_rejected`
- [x] DQ-09 warns and keeps the case: `test_false_positive_with_loss_warns_and_keeps_case`
- [x] DQ-10 warns by default; switchable to reject: `test_confirmed_fraud_without_loss_*`
- [x] DQ-11 rejects cases opened after the run date: `test_cases_opened_after_run_date_are_rejected`

## FR-04 Link to Member 360
- [x] 10 TRUE / 90 FALSE with today's member_360: `test_member_link.py::test_member_found_flag`
- [x] All 100 kept; 90 MEMBER_NOT_FOUND exceptions: `test_unmatched_cases_are_kept_and_reported`
- [x] DQ-12 = Warn, doesn't block: `test_member_rule_warns_without_blocking`
- [x] Missing lookup file → clear error: `test_missing_member_reference_fails_clearly`

## FR-05 Derived case metrics
- [x] FC0000002 → 3.00 days, ratio 0.8000; FC0000001 → age 63: `test_metrics.py::test_known_cases`
- [x] NULL rules by lifecycle: `test_metrics_null_by_lifecycle`
- [x] Ranges: days 1–12, Confirmed Fraud ratio 0.35–0.80, False Positive 0: `test_sample_metric_ranges`
- [x] CRITICAL_CASE_AGED = 15 (SLA 30), configurable: `test_critical_case_aging_exception`, `test_sla_days_is_configurable`

## FR-06 Publish and govern
- [x] 100 rows; DQ-01..DQ-05 Pass; all 12 rules recorded: `test_publish.py::test_all_cases_published`, `test_blocking_rules_pass`, `test_every_rule_recorded`
- [x] A blocking failure keeps the previous table: `test_blocking_failure_keeps_previous_product`
- [x] CSV starts with the sample's 13 columns, in order: `test_csv_starts_with_sample_columns`
- [x] DDL in sync; 20 typed columns in SQLite: `test_committed_ddl_matches_contracts`, `test_product_table_declares_contract_types`
- [x] Idempotent rerun: `test_rerun_is_idempotent`
- [ ] Catalog entry, access roles, consumer sign-off — platform and people tasks
