"""Derived case metrics and the critical-case aging exception."""
from datetime import date, datetime
from decimal import Decimal

from src.fraud_case.config import Settings
from src.fraud_case.transform import case_age_days, days_to_close, loss_confirmation_ratio
from tests.conftest import by_case, run_build


def test_days_to_close():
    assert days_to_close(datetime(2026, 8, 1, 16), datetime(2026, 8, 4, 16)) == Decimal("3.00")
    assert days_to_close(datetime(2026, 8, 1, 8), datetime(2026, 8, 1, 20)) == Decimal("0.50")
    assert days_to_close(datetime(2026, 8, 1, 8), None) is None


def test_case_age_days():
    assert case_age_days(datetime(2026, 8, 1, 8), False, date(2026, 10, 4)) == 63
    assert case_age_days(datetime(2026, 8, 1, 8), True, date(2026, 10, 4)) is None


def test_loss_confirmation_ratio():
    assert loss_confirmation_ratio(Decimal("299.50"), Decimal("374.38"), True) == Decimal("0.8000")
    assert loss_confirmation_ratio(Decimal("0"), Decimal("511.57"), True) == Decimal("0.0000")
    assert loss_confirmation_ratio(Decimal("10"), Decimal("0"), True) is None
    assert loss_confirmation_ratio(Decimal("10"), Decimal("20"), False) is None


def test_known_cases(result):
    rows = by_case(result.product)
    assert rows.loc["FC0000002", ["is_closed", "days_to_close", "loss_confirmation_ratio"]].tolist() == \
        [True, Decimal("3.00"), Decimal("0.8000")]
    assert rows.loc["FC0000001", ["is_closed", "case_age_days"]].tolist() == [False, 63]


def test_metrics_null_by_lifecycle(result):
    for r in result.product.to_dict("records"):
        if r["is_closed"]:
            assert r["case_age_days"] is None and r["days_to_close"] is not None
        else:
            assert r["days_to_close"] is None and r["loss_confirmation_ratio"] is None
            assert r["case_age_days"] is not None


def test_sample_metric_ranges(result):
    p = result.product
    closed = p[p["is_closed"] == True]  # noqa: E712
    assert len(closed) == 40
    assert min(closed["days_to_close"]) == Decimal("1.00") and max(closed["days_to_close"]) == Decimal("12.00")
    confirmed = closed[closed["resolution_code"] == "Confirmed Fraud"]["loss_confirmation_ratio"]
    assert len(confirmed) == 27
    assert min(confirmed) == Decimal("0.3500") and max(confirmed) == Decimal("0.8000")
    assert set(closed[closed["resolution_code"] == "False Positive"]["loss_confirmation_ratio"]) == {Decimal("0.0000")}


def test_critical_case_aging_exception(result):
    aged = result.exceptions[result.exceptions["exception_type"] == "CRITICAL_CASE_AGED"]
    rows = by_case(result.product)
    assert len(aged) == 15
    assert all(rows.loc[c, "priority"] == "Critical" and rows.loc[c, "case_age_days"] > 30 for c in aged["case_id"])


def test_sla_days_is_configurable(tmp_path):
    res = run_build(tmp_path, settings=Settings(critical_sla_days=45))
    aged = res.exceptions[res.exceptions["exception_type"] == "CRITICAL_CASE_AGED"]
    assert set(aged["case_id"]) == {"FC0000011", "FC0000015", "FC0000019", "FC0000031",
                                    "FC0000035", "FC0000039", "FC0000051"}
