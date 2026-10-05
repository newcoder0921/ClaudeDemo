"""Paths and business switches for Fraud Case. Change behaviour here, not in the logic."""
from dataclasses import dataclass
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = CODE_DIR.parents[2]

SOURCE_DIR = PROJECT_ROOT / "sources" / "data" / "raw"
SAMPLE_PRODUCT_CSV = PROJECT_ROOT / "data" / "output" / "product" / "DP_Fraud_Case.csv"
# Member 360 publishes this file; override with --member-ref.
MEMBER_REFERENCE_CSV = PROJECT_ROOT / "output" / "DP_Member_360" / "04_code" / "out" / "member_360.csv"
DB_PATH = CODE_DIR / "fraud_case.db"
OUT_DIR = CODE_DIR / "out"
DDL_DIR = CODE_DIR / "sql" / "ddl"

SOURCE_FILES = {"Fraud_Case_Extract": "DP_Fraud_Case.csv"}

CONTRACT_META = {
    "version": "0.1",
    "owner": "Product Owner - Fraud & Risk Data",
    "refresh": "Daily full rebuild, ready by 07:00 ET",
    "change_policy": "New columns are additive; type changes need 30 days' notice",
    "source_prd": "output/DP_Fraud_Case/PRD_Fraud_Case.md",
    "jira": "SCRUM-25",
    "depends_on": "DP_Member_360 (member_360.member_id)",
}


@dataclass(frozen=True)
class Settings:
    # Pending Risk decision: "warn" keeps Confirmed Fraud cases with $0 loss, "reject" removes them.
    confirmed_zero_loss_severity: str = "warn"
    # Pending Fraud Ops SLA definition.
    critical_sla_days: int = 30
