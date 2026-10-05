"""Exception report for fraud operations: valid cases that still need a human look."""
from __future__ import annotations

import pandas as pd

from contracts.fraud_case import DQ_EXCEPTIONS

COLUMNS = [c for c in DQ_EXCEPTIONS.column_names if c != "dp_batch_id"]


def members_not_found(product: pd.DataFrame) -> list[dict]:
    rows = product[product["member_found_flag"] != True]  # noqa: E712 - object column of bools
    return [{"exception_type": "MEMBER_NOT_FOUND", "case_id": r["case_id"], "member_id": r["member_id"],
             "detail": "member_id not in member_360; case kept"} for r in rows.to_dict("records")]


def critical_cases_aged(product: pd.DataFrame, sla_days: int) -> list[dict]:
    aged = [r for r in product.to_dict("records")
            if r["priority"] == "Critical" and r["case_age_days"] is not None and r["case_age_days"] > sla_days]
    return [{"exception_type": "CRITICAL_CASE_AGED", "case_id": r["case_id"], "member_id": r["member_id"],
             "detail": f"{r['case_status']} for {r['case_age_days']} days (SLA {sla_days})"} for r in aged]


def find_exceptions(product: pd.DataFrame, sla_days: int, batch_id: str) -> pd.DataFrame:
    rows = members_not_found(product) + critical_cases_aged(product, sla_days)
    return pd.DataFrame(rows, columns=COLUMNS, dtype=object).assign(dp_batch_id=batch_id)
