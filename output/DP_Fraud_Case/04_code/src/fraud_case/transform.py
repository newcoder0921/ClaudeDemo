"""Fraud Case business rules: one small function per derived column."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

from contracts.fraud_case import FRAUD_CASE

CLOSED = "Closed"
_SECONDS_PER_DAY = Decimal(86_400)


def days_to_close(opened: datetime, closed: datetime | None) -> Decimal | None:
    if closed is None:
        return None
    seconds = Decimal(int((closed - opened).total_seconds()))
    return (seconds / _SECONDS_PER_DAY).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def case_age_days(opened: datetime, is_closed: bool, as_of: date) -> int | None:
    """Whole days from opening to the start of the run date; closed cases have no age."""
    if is_closed:
        return None
    return (datetime.combine(as_of, time()) - opened).days


def loss_confirmation_ratio(confirmed: Decimal, suspected: Decimal, is_closed: bool) -> Decimal | None:
    if not is_closed or not suspected:
        return None
    return (confirmed / suspected).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def load_member_reference(path: Path) -> set[str]:
    """Member IDs published by DP_Member_360."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"member_360 reference not found: {path}. "
                                "Build DP_Member_360 first or pass --member-ref.")
    return set(pd.read_csv(path, usecols=["member_id"], dtype=str)["member_id"].str.strip())


def build_fraud_case(extract: pd.DataFrame, member_ids: set[str], as_of: date, load_ts: datetime,
                     batch_id: str) -> pd.DataFrame:
    rows = []
    for r in extract.to_dict("records"):
        closed = r["case_status"] == CLOSED
        rows.append({
            **{c: r[c] for c in extract.columns if c in FRAUD_CASE.column_names},
            "is_closed": closed,
            "days_to_close": days_to_close(r["case_open_ts"], r["case_close_ts"]) if closed else None,
            "case_age_days": case_age_days(r["case_open_ts"], closed, as_of),
            "loss_confirmation_ratio": loss_confirmation_ratio(
                r["confirmed_loss_amount"], r["suspected_loss_amount"], closed),
            "member_found_flag": r["member_id"] in member_ids,
            "dp_load_ts": load_ts,
            "dp_batch_id": batch_id,
        })
    return pd.DataFrame(rows, columns=FRAUD_CASE.column_names, dtype=object)
