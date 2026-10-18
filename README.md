# LLM-Powered Data Quality Assistant

## Project Overview

This project detects common data-quality problems in a synthetic
customer subscription dataset. It uses Python and Pandas to identify
potential issues, creates reports and charts, and uses a local
language model through Ollama to explain the findings in simple English.

A Streamlit dashboard allows users to explore findings, filter results,
and download reports.

## Features

- Generates a synthetic customer dataset with 2,030 records.
- Detects missing values and duplicate records.
- Identifies invalid dates and email formats.
- Detects inconsistent category formatting.
- Flags unexpected subscription plans and negative fees.
- Creates detailed issue reports and summary CSV files.
- Uses a local LLM to explain findings and recommend next steps.
- Provides a Streamlit dashboard with charts and filters.
- Includes automated tests, dataset metadata, and data lineage notes.

## Technology Stack

- Python
- Pandas
- Matplotlib
- Streamlit
- Ollama
- Llama 3.2 (1B)
- Jupyter Notebook

## Project Structure

```text
LLM_Data_Quality_Assistant/
├── app.py
├── quality_checker.py
├── test_quality_checker.py
├── requirements.txt
├── README.md
├── data/
│   └── synthetic_customers.csv
├── notebooks/
│   └── data_quality_assistant.ipynb
└── reports/
    ├── data_quality_report.csv
    ├── issue_summary.csv
    ├── severity_summary.csv
    ├── column_summary.csv
    ├── llm_analysis_prompt.txt
    ├── llm_analysis_report.txt
    ├── metadata.json
    └── data_lineage.md
```

## Setup

### 1. Install Python packages

From the main project folder, run:

```bash
python -m pip install -r requirements.txt
```

### 2. Install Ollama

Install Ollama from:

https://ollama.com/download/windows

Download the model using:

```bash
ollama run llama3.2:1b
```

Keep Ollama available while generating AI analysis.

### 3. Run the data-quality checks

From the main project folder, run:

```bash
python quality_checker.py
```

This reads the synthetic dataset and creates the detailed report
and summary CSV files.

### 4. Launch the dashboard

From the main project folder, run:

```bash
python -m streamlit run app.py
```

Open the local address shown in the terminal if the browser
does not open automatically.

### 5. Run the automated tests

From the main project folder, run:

```bash
python test_quality_checker.py
```

The tests check that the dataset structure is appropriate and the
expected issue types are detected.

## Reports

The project produces:

- Detailed data-quality findings
- Issue counts and percentages
- Severity summaries
- Counts by affected column
- An AI-generated explanation
- Dataset metadata and lineage documentation

## Data and Privacy

The customer dataset is synthetic and intended for demonstration.
It does not represent actual customer records. The AI explanation
is generated locally through Ollama.

The checker flags potential data-quality issues; it does not
automatically correct or delete the original records.

## Limitations

- The sample dataset is synthetic, not a production dataset.
- Email validation uses a simple format check.
- Severity labels are rule-based and may need adjustment
  for a real business process.
- AI-generated explanations can be inaccurate and should be reviewed.
- The current automated tests cover selected checks, not every
  possible input or failure condition.

## Future Improvements

- Add configurable validation rules.
- Improve error handling and test coverage.
- Add historical monitoring and quality trends.
- Support uploading a user-provided CSV file.
- Add clearer explanations and review workflows for suggested fixes.
