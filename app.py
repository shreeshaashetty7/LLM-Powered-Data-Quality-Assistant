
import json
import urllib.request
import urllib.error
from pathlib import Path

import pandas as pd
import streamlit as st

from quality_checker import run_quality_checks


# Find the project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"


# Set up the dashboard
st.set_page_config(
    page_title="Data Quality Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("LLM-Powered Data Quality Assistant")
st.caption(
    "Detect, review and explain data-quality issues using Python and AI."
)


# Create two action buttons
button1, button2 = st.columns(2)

with button1:
    if st.button("Run Data Quality Checks", type="primary"):
        try:
            records, findings = run_quality_checks()

            st.success(
                f"Checked {records:,} records and found "
                f"{findings:,} data-quality findings."
            )
        except Exception as error:
            st.error(f"Could not run the checks: {error}")

with button2:
    if st.button("Generate AI Analysis"):
        prompt_path = REPORTS_DIR / "llm_analysis_prompt.txt"

        try:
            prompt = prompt_path.read_text(encoding="utf-8")

            request_data = {
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            }

            request = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps(request_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(
                request, timeout=180
            ) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

            ai_report = result["response"]

            output_path = (
                REPORTS_DIR / "llm_analysis_report.txt"
            )
            output_path.write_text(
                ai_report, encoding="utf-8"
            )

            st.success("AI analysis generated successfully!")

        except urllib.error.URLError:
            st.error(
                "Could not connect to Ollama. "
                "Check that Ollama is running."
            )
        except Exception as error:
            st.error(f"Could not generate the AI analysis: {error}")


# Load project files
def load_csv(file_path):
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()


customers = load_csv(DATA_DIR / "synthetic_customers.csv")
report = load_csv(REPORTS_DIR / "data_quality_report.csv")
issue_summary = load_csv(REPORTS_DIR / "issue_summary.csv")
severity_summary = load_csv(REPORTS_DIR / "severity_summary.csv")
column_summary = load_csv(REPORTS_DIR / "column_summary.csv")


# Check whether reports are available
if customers.empty:
    st.warning("Customer dataset not found.")
    st.stop()

if report.empty:
    st.info("Click Run Data Quality Checks to create the report.")
    st.stop()


# Display key metrics
st.subheader("Quality Overview")

high_count = int((report["severity"] == "High").sum())
medium_count = int((report["severity"] == "Medium").sum())
low_count = int((report["severity"] == "Low").sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Customer Records", f"{len(customers):,}")
col2.metric("Total Findings", f"{len(report):,}")
col3.metric("High Severity", f"{high_count:,}")
col4.metric("Columns with Issues", f"{report['column'].nunique():,}")


# Display charts
st.subheader("Data Quality Findings")

left, right = st.columns(2)

with left:
    st.write("**Issues by Type**")

    if not issue_summary.empty:
        chart = issue_summary.set_index("issue_type")["issue_count"]
        st.bar_chart(chart)

with right:
    st.write("**Issues by Severity**")

    severity_chart = pd.DataFrame({
        "Severity": ["High", "Medium", "Low"],
        "Count": [high_count, medium_count, low_count]
    })

    st.bar_chart(severity_chart.set_index("Severity"))


# Show issues by column
st.subheader("Issues by Column")

if not column_summary.empty:
    chart = column_summary.set_index("column")["issue_count"]
    st.bar_chart(chart)


# Filter individual findings
st.subheader("Explore Findings")

filter1, filter2 = st.columns(2)

with filter1:
    issue_options = ["All"] + sorted(
        report["issue_type"].dropna().unique().tolist()
    )
    selected_issue = st.selectbox(
        "Issue Type", issue_options
    )

with filter2:
    severity_options = ["All"] + sorted(
        report["severity"].dropna().unique().tolist()
    )
    selected_severity = st.selectbox(
        "Severity", severity_options
    )

filtered_report = report.copy()

if selected_issue != "All":
    filtered_report = filtered_report[
        filtered_report["issue_type"] == selected_issue
    ]

if selected_severity != "All":
    filtered_report = filtered_report[
        filtered_report["severity"] == selected_severity
    ]

st.write(f"Showing {len(filtered_report):,} findings")
st.dataframe(filtered_report, use_container_width=True)


# Display the latest AI explanation
st.subheader("AI-Generated Analysis")

ai_path = REPORTS_DIR / "llm_analysis_report.txt"

if ai_path.exists():
    st.markdown(ai_path.read_text(encoding="utf-8"))
else:
    st.info("Click Generate AI Analysis to create an explanation.")


# Download the reports
st.subheader("Download Files")

st.download_button(
    "Download Issue Report",
    data=report.to_csv(index=False).encode("utf-8"),
    file_name="data_quality_report.csv",
    mime="text/csv"
)

st.download_button(
    "Download Customer Dataset",
    data=customers.to_csv(index=False).encode("utf-8"),
    file_name="synthetic_customers.csv",
    mime="text/csv"
)

if ai_path.exists():
    st.download_button(
        "Download AI Analysis",
        data=ai_path.read_text(encoding="utf-8"),
        file_name="llm_analysis_report.txt",
        mime="text/plain"
    )

st.caption(
    "This demonstration uses synthetic data. Findings are alerts "
    "for review; the original customer data is not automatically corrected."
)
