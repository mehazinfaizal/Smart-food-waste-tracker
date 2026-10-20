# Smart Food-Waste Tracker

A beginner-friendly daily batch project for a small grocery store. It reads sales, current inventory, and item expiry dates from CSV files, checks and joins them, estimates the value likely to expire unsold, and writes a ranked report of the 10 items staff should review first.

## How it works

1. Reads daily sales and expiry-dated inventory CSV files.
2. Cleans and transforms the data with AWS Glue.
3. Stores cleaned data in Amazon S3 as Parquet.
4. Uses Amazon Athena to analyze sales and expiry risk.
5. Optionally sends alerts through Amazon SNS.
