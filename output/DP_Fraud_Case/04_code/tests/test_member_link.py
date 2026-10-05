"""Member 360 link: unmatched cases are kept, flagged and reported."""
import pytest

from tests.conftest import by_case, run_build


def test_member_found_flag(result):
    flags = by_case(result.product)["member_found_flag"]
    assert sum(1 for f in flags if f is True) == 10
    assert sum(1 for f in flags if f is False) == 90
    assert flags["FC0000010"] is True and flags["FC0000011"] is False


def test_unmatched_cases_are_kept_and_reported(result):
    assert len(result.product) == 100
    missing = result.exceptions[result.exceptions["exception_type"] == "MEMBER_NOT_FOUND"]
    assert len(missing) == 90
    assert "M000001" not in set(missing["member_id"])


def test_member_rule_warns_without_blocking(result):
    dq12 = result.dq_results.set_index("rule_id").loc["DQ-12"]
    assert (dq12["status"], dq12["rows_failed"]) == ("Warn", 90)
    assert result.status == "SUCCESS"


def test_missing_member_reference_fails_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="member_360 reference not found"):
        run_build(tmp_path, member_ref=tmp_path / "nope.csv")
