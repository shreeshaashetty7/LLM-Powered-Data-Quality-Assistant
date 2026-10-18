
from pathlib import Path
import sys
import pandas as pd

# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent

# Allow Python to find quality_checker.py
sys.path.insert(0, str(BASE_DIR))

from quality_checker import run_quality_checks


# Run the data-quality checker
records_checked, findings_found = run_quality_checks()

# Load the dataset and generated report
customers = pd.read_csv(
    BASE_DIR / "data" / "synthetic_customers.csv"
)

report = pd.read_csv(
    BASE_DIR / "reports" / "data_quality_report.csv"
)


# Test 1: Check that the dataset has enough records
assert len(customers) >= 2000, "Dataset has too few records"

# Test 2: Check that the expected columns exist
assert customers.shape[1] == 13, "Unexpected number of columns"

# Test 3: Check that the report contains findings
assert not report.empty, "No data-quality findings were generated"

# Test 4: Check that all expected issue types were detected
expected_issues = {
    "Missing Value",
    "Duplicate Record",
    "Invalid Date",
    "Invalid Email",
    "Inconsistent Formatting",
    "Unexpected Category",
    "Invalid Value"
}

detected_issues = set(report["issue_type"])
missing_issues = expected_issues - detected_issues

assert not missing_issues, (
    f"These issue types were not detected: {missing_issues}"
)

# Test 5: Check that severity labels are valid
valid_severities = {"High", "Medium", "Low"}

assert set(report["severity"]).issubset(valid_severities), (
    "Unexpected severity label found"
)

# Test 6: Check that the reported count matches the report
assert findings_found == len(report), (
    "The reported finding count does not match the report"
)

print("All automated tests passed!")
print("Customer records checked:", records_checked)
print("Data-quality findings:", findings_found)
print("Issue types detected:", len(detected_issues))
