
import pandas as pd
from pathlib import Path

# Find the project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "synthetic_customers.csv"
REPORTS_DIR = BASE_DIR / "reports"


def run_quality_checks():

    # Load customer data
    df = pd.read_csv(DATA_PATH)
    issues = []

    # Store each problem found
    def add_issue(row, issue_type, column, value, severity, action):
        issues.append({
            "record_number": row + 2,
            "customer_id": df.iloc[row]["customer_id"],
            "issue_type": issue_type,
            "column": column,
            "current_value": str(value),
            "severity": severity,
            "recommended_action": action
        })

    # Check missing values
    for column in df.columns:
        for row in df.index[df[column].isna()]:
            add_issue(
                row, "Missing Value", column, "Missing",
                "Medium", "Review the missing value."
            )

    # Check duplicate records
    for row in df.index[df.duplicated(keep=False)]:
        add_issue(
            row, "Duplicate Record", "Entire Record",
            "Duplicate row", "Medium",
            "Review before removing the duplicate."
        )

    # Check invalid dates
    date_columns = [
        "date_of_birth", "signup_date", "last_payment_date"
    ]

    for column in date_columns:
        dates = pd.to_datetime(df[column], errors="coerce")
        bad_rows = df.index[df[column].notna() & dates.isna()]

        for row in bad_rows:
            add_issue(
                row, "Invalid Date", column, df.loc[row, column],
                "High", "Verify the date."
            )

    # Check email formats
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    bad_emails = df.index[
        df["email"].notna()
        & ~df["email"].astype(str).str.match(email_pattern)
    ]

    for row in bad_emails:
        add_issue(
            row, "Invalid Email", "email", df.loc[row, "email"],
            "Medium", "Verify the email address."
        )

    # Check category formatting
    for column in ["subscription_plan", "payment_status"]:
        original = df[column].astype("string")
        cleaned = original.str.strip().str.title()

        bad_rows = df.index[
            original.notna() & original.ne(cleaned)
        ]

        for row in bad_rows:
            add_issue(
                row, "Inconsistent Formatting", column,
                df.loc[row, column], "Low",
                "Review spaces and capitalization."
            )

    # Check approved subscription plans
    valid_plans = ["Basic", "Standard", "Premium", "Family"]

    plans = (
        df["subscription_plan"]
        .astype("string").str.strip().str.title()
    )

    bad_plans = df.index[
        df["subscription_plan"].notna()
        & ~plans.isin(valid_plans)
    ]

    for row in bad_plans:
        add_issue(
            row, "Unexpected Category", "subscription_plan",
            df.loc[row, "subscription_plan"], "Medium",
            "Check whether this plan is approved."
        )

    # Check negative fees
    fees = pd.to_numeric(df["monthly_fee"], errors="coerce")

    for row in df.index[fees < 0]:
        add_issue(
            row, "Invalid Value", "monthly_fee",
            df.loc[row, "monthly_fee"], "High",
            "Verify the fee against approved pricing."
        )

    # Convert findings into a table
    columns = [
        "record_number", "customer_id", "issue_type", "column",
        "current_value", "severity", "recommended_action"
    ]

    report = pd.DataFrame(issues, columns=columns)

    # Create the reports folder
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save detailed findings
    report.to_csv(
        REPORTS_DIR / "data_quality_report.csv", index=False
    )

    # Save summary by issue type
    issue_summary = (
        report["issue_type"].value_counts()
        .rename_axis("issue_type")
        .reset_index(name="issue_count")
    )

    if len(report) > 0:
        issue_summary["percentage"] = (
            issue_summary["issue_count"] / len(report) * 100
        ).round(2)

    issue_summary.to_csv(
        REPORTS_DIR / "issue_summary.csv", index=False
    )

    # Save summary by severity
    severity_summary = (
        report["severity"].value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
        .rename_axis("severity")
        .reset_index(name="issue_count")
    )

    severity_summary.to_csv(
        REPORTS_DIR / "severity_summary.csv", index=False
    )

    # Save summary by column
    column_summary = (
        report["column"].value_counts()
        .rename_axis("column")
        .reset_index(name="issue_count")
    )

    column_summary.to_csv(
        REPORTS_DIR / "column_summary.csv", index=False
    )

    # Prepare an updated prompt for the local AI model
    prompt = f"""
You are a data quality analyst.

Analyze findings from a synthetic customer dataset.
Explain the overall situation, common problems, their impact,
which problems to investigate first, and practical next steps.

Distinguish frequent problems from high-severity problems.
Use only the supplied information.
Do not claim the data has been corrected.
Counts represent findings, not necessarily unique customers.

Issues by type:
{issue_summary.to_string(index=False)}

Issues by severity:
{severity_summary.to_string(index=False)}

Issues by column:
{column_summary.to_string(index=False)}
"""

    (REPORTS_DIR / "llm_analysis_prompt.txt").write_text(
        prompt, encoding="utf-8"
    )

    return len(df), len(report)


# Run the checks when this file is executed
if __name__ == "__main__":
    records, findings = run_quality_checks()

    print("Data-quality checks completed!")
    print("Customer records checked:", records)
    print("Issues found:", findings)
    print("Reports saved in:", REPORTS_DIR)
