#!/usr/bin/env python3
"""Local daily batch prototype for the Smart Food-Waste Tracker."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def run(data_dir: Path, output_dir: Path, report_date: date | None) -> None:
    sales_rows = read_csv(data_dir / "sales.csv")
    inventory_rows = read_csv(data_dir / "inventory.csv")
    quality = {"sales_rows_read": len(sales_rows), "inventory_rows_read": len(inventory_rows),
               "sales_rows_rejected": 0, "inventory_rows_rejected": 0, "warnings": []}

    sales: dict[tuple[str, date], int] = defaultdict(int)
    valid_sale_dates: list[date] = []
    for row in sales_rows:
        try:
            day, product, units = parse_day(row["sale_date"]), row["product_id"].strip(), int(row["units_sold"])
            if not product or units < 0:
                raise ValueError("empty product_id or negative units_sold")
            sales[(product, day)] += units
            valid_sale_dates.append(day)
        except (ValueError, KeyError):
            quality["sales_rows_rejected"] += 1
    if not valid_sale_dates:
        raise ValueError("No valid sales rows; cannot infer report date")
    report_date = report_date or max(valid_sale_dates)

    batches: list[dict] = []
    seen: set[str] = set()
    for row in inventory_rows:
        try:
            batch_id, product_id = row["batch_id"].strip(), row["product_id"].strip()
            qty, cost = int(row["quantity_on_hand"]), float(row["unit_cost"])
            expiry = parse_day(row["expiry_date"])
            if not batch_id or not product_id or batch_id in seen or qty < 0 or cost < 0:
                raise ValueError("missing/duplicate ID or negative quantity/cost")
            seen.add(batch_id)
            batches.append({**row, "batch_id": batch_id, "product_id": product_id,
                            "quantity_on_hand": qty, "unit_cost": cost, "expiry_date": expiry})
        except (ValueError, KeyError):
            quality["inventory_rows_rejected"] += 1

    window_start = report_date - timedelta(days=7)
    results = []
    for batch in batches:
        product = batch["product_id"]
        sold = sum(sales[(product, window_start + timedelta(days=i))] for i in range(7))
        avg_daily = sold / 7
        expiry = batch["expiry_date"]
        days_left = (expiry - report_date).days
        selling_days = max(0, days_left + 1)
        projected = min(batch["quantity_on_hand"], avg_daily * selling_days)
        at_risk = max(0.0, batch["quantity_on_hand"] - projected)
        unsold_fraction = at_risk / batch["quantity_on_hand"] if batch["quantity_on_hand"] else 0.0
        urgency = 1.0 if days_left <= 0 else 1.0 / days_left
        score = unsold_fraction * urgency
        results.append({
            "batch_id": batch["batch_id"], "product_id": product, "product_name": batch["product_name"],
            "category": batch["category"], "report_date": report_date.isoformat(),
            "expiry_date": expiry.isoformat(), "days_until_expiry": days_left,
            "quantity_on_hand": batch["quantity_on_hand"], "units_sold_last_7_days": sold,
            "avg_daily_units_sold": round(avg_daily, 2), "projected_units_sold_by_expiry": round(projected, 2),
            "projected_unsold_units": round(at_risk, 2),
            "estimated_waste_cost": round(at_risk * batch["unit_cost"], 2),
            "risk_score": round(score, 4),
            "suggested_action": "Review for discount or donation" if at_risk > 0 and days_left <= 2 else
                                ("Monitor stock" if at_risk > 0 else "No action suggested")
        })

    results.sort(key=lambda r: (r["risk_score"], r["estimated_waste_cost"]), reverse=True)
    quality["report_date"] = report_date.isoformat()
    quality["inventory_rows_accepted"] = len(batches)
    quality["sales_rows_accepted"] = len(sales_rows) - quality["sales_rows_rejected"]
    if not batches:
        quality["warnings"].append("No valid inventory batches were available.")
    output_dir.mkdir(parents=True, exist_ok=True)
    if results:
        with (output_dir / "cleaned_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
        with (output_dir / "top10_at_risk.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results[:10])
    (output_dir / "data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    print(f"Report date: {report_date}; batches ranked: {len(results)}")
    print(f"Wrote reports to: {output_dir.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--report-date", type=parse_day, help="YYYY-MM-DD; defaults to latest valid sales date")
    args = parser.parse_args()
    run(args.data_dir, args.output_dir, args.report_date)


if __name__ == "__main__":
    main()
