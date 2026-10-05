"""Product contracts: fraud_case and its exception report."""
from src.dp_framework.contract import Column as C, Table

from .sources import FRAUD_CASE_EXTRACT

DERIVED = (
    C("is_closed", "BOOLEAN", description="case_status = Closed."),
    C("days_to_close", "DECIMAL(7,2)", nullable=True, description="Days from open to close; closed cases only."),
    C("case_age_days", "INT", nullable=True, description="Whole days from open to run date; open cases only."),
    C("loss_confirmation_ratio", "DECIMAL(5,4)", nullable=True,
      description="confirmed / suspected loss; closed cases only."),
    C("member_found_flag", "BOOLEAN", description="member_id exists in member_360."),
    C("dp_load_ts", "TIMESTAMP", description="When the row was loaded."),
    C("dp_batch_id", "VARCHAR(36)", description="Pipeline run ID, for lineage."),
)

FRAUD_CASE = Table("fraud_case", FRAUD_CASE_EXTRACT.columns + DERIVED, grain="One row per fraud case",
                   description="Governed, typed fraud cases with lifecycle checks and loss metrics.")

DQ_EXCEPTIONS = Table("dq_exceptions", (
    C("exception_type", "VARCHAR(40)", description="Exception category."),
    C("case_id", "VARCHAR(10)", description="Case involved."),
    C("member_id", "VARCHAR(10)", nullable=True, description="Member on the case."),
    C("detail", "VARCHAR(200)", description="Plain-English explanation."),
    C("dp_batch_id", "VARCHAR(36)", description="Pipeline run ID."),
), grain="One row per exception found")
