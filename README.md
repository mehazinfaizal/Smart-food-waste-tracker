# Smart Food-Waste Tracker

A beginner-friendly daily batch project for a small grocery store. It reads sales, current inventory, and item expiry dates from CSV files, checks and joins them, estimates the value likely to expire unsold, and writes a ranked report of the 10 items staff should review first.

## Run the local prototype

Requires Python 3.10 or newer. The prototype uses only the Python standard library.

```powershell
python src/run_pipeline.py --data-dir data --output-dir outputs
```

Generated files:

- `outputs/top10_at_risk.csv` — ranked recommendations for staff.
- `outputs/cleaned_inventory.csv` — cleaned, joined inventory and sales data.
- `outputs/data_quality.json` — input counts, rejected rows, and warnings.

The sample data is synthetic. Keep one row per product batch in `inventory.csv`; a product can have multiple batches with different expiry dates.

## Baseline model

For each batch, the pipeline calculates average daily sales from the seven days before the report date, projects sales through expiry, estimates unsold units, and multiplies those units by unit cost. A transparent risk score combines the fraction of stock likely to remain unsold with expiry urgency. This is a prioritization heuristic, not a trained forecast or food-safety recommendation. Staff should verify stock and follow applicable food-safety rules.

See [docs/data-dictionary.md](docs/data-dictionary.md) for the input schema and assumptions.

## AWS learning path

1. Upload daily sales and expiry-dated inventory CSVs to separate S3 `raw/` prefixes.
2. Use AWS Glue to validate and transform the data, writing Parquet under `cleaned/`.
3. Register the cleaned tables in the Glue Data Catalog.
4. Query sales and expiry risk with Athena using [aws/athena/queries.sql](aws/athena/queries.sql).
5. Schedule the daily Glue job with EventBridge Scheduler.
6. Optionally use QuickSight for a dashboard and SNS for risk alerts.
7. Compare predictions with recorded waste before improving the model.

The Glue and Athena files are starter examples; set your own bucket, database, IAM role, and column mapping before deployment. This repository does not create AWS resources or incur cloud costs.

## Security

Do not commit AWS account-specific ARNs, credentials, access keys, or private store data. Limit the Glue role's S3 access to the project paths and grant `sns:Publish` only on the intended topic. Generated local reports are ignored by Git.

## Project layout

```
data/                 synthetic sample CSVs
src/run_pipeline.py   local daily batch pipeline
aws/glue/             Glue transformation starter
aws/athena/           Athena analysis queries
docs/                 data dictionary and assumptions
```
