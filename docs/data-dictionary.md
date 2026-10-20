# Data dictionary and assumptions

Dates use ISO format `YYYY-MM-DD`. Quantities are units, not cases.

## `sales.csv`

| Column | Meaning |
|---|---|
| `sale_date` | Business date of recorded sales |
| `product_id` | Stable store product identifier |
| `units_sold` | Units sold that day; zero is allowed |

## `inventory.csv`

| Column | Meaning |
|---|---|
| `batch_id` | Unique identifier for an expiry-dated batch |
| `product_id` | Stable store product identifier |
| `product_name` | Display name |
| `category` | Store category |
| `quantity_on_hand` | Current units in this batch |
| `unit_cost` | Store's estimated cost per unit in its local currency |
| `expiry_date` | Last date the batch is considered sellable for this exercise |

## Model behavior

- Report date is supplied with `--report-date`; absent that, the latest date in sales data is used.
- The sales velocity window is the seven calendar days ending the day before report date. Missing product-days count as zero.
- Projected sales are average daily sales multiplied by the number of selling days from report date through expiry date, inclusive. Expired batches get zero projected sales.
- Projected unsold units are current quantity less projected sales, floored at zero and capped at current quantity.
- Estimated waste cost is projected unsold units times unit cost.
- Risk score is `unsold_fraction * urgency`, where urgency is 1 for expired batches and otherwise `1 / days_until_expiry` (minimum one day). This ranks imminently expiring stock with substantial unsold quantity highly. It is a prioritization heuristic, not a probability.
- Product-level sales velocity is applied to each batch of that product. This can overstate demand available to a batch when several batches share a product; a later version should allocate sales across batches using FEFO (first-expiring-first-out).
- All sample products, sales, dates, and costs are fictional. Currency is unspecified; cost values use whatever currency the store supplies.
