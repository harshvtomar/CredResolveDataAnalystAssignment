# Data Analyst Assignment — Ready-to-Submit Package

## Deliverables required by the assignment
1. SQL Repository → `sql_repository.sql`
2. Analysis Notebook → `analysis_notebook.ipynb`
3. Golden Dataset / Reproducible Pipeline → `golden_pipeline.py`, `golden_dataset_spec.md`
4. Data Quality Report → `data_quality_report.md`
5. Executive Dashboard → `ceo_dashboard.html`
6. Executive Memo → `executive_memo.md`
7. Architecture Diagram → `architecture.md`
8. Statistical Investigation → `statistical_investigation.md`
9. Counterfactual → `counterfactual_analysis.md`

## How to run
Place the supplied CSV files under a folder named `raw/`, then run:

    python golden_pipeline.py

The pipeline creates:
- golden_payments.csv
- quarantined_payment_references.csv
- monthly_recovery.csv

Open `analysis_notebook.ipynb` in Jupyter/VS Code.

## Submission note
The analysis intentionally does not manufacture a causal ROI where the observational data cannot identify one. The ₹10 Cr recommendation is therefore framed as a controlled, stage-gated targeting experiment.
