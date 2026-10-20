-- Replace database/table names with the Glue Catalog names in your account.

-- Recent sales velocity by product (last seven completed days).
SELECT product_id,
       SUM(units_sold) AS units_sold_7d,
       SUM(units_sold) / 7.0 AS avg_daily_units
FROM grocery.daily_sales
WHERE sale_date >= date_add('day', -7, current_date)
  AND sale_date < current_date
GROUP BY product_id
ORDER BY units_sold_7d DESC;

-- Join batch inventory to recent sales and estimate unsold stock through expiry.
WITH velocity AS (
    SELECT product_id, SUM(units_sold) / 7.0 AS avg_daily_units
    FROM grocery.daily_sales
    WHERE sale_date >= date_add('day', -7, current_date)
      AND sale_date < current_date
    GROUP BY product_id
), estimate AS (
    SELECT i.batch_id, i.product_id, i.product_name, i.category,
           i.quantity_on_hand, i.unit_cost, i.expiry_date,
           COALESCE(v.avg_daily_units, 0.0) AS avg_daily_units,
           greatest(0, date_diff('day', current_date, i.expiry_date) + 1) AS selling_days,
           greatest(0.0, i.quantity_on_hand -
               least(i.quantity_on_hand, COALESCE(v.avg_daily_units, 0.0) *
               greatest(0, date_diff('day', current_date, i.expiry_date) + 1))) AS projected_unsold
    FROM grocery.inventory i
    LEFT JOIN velocity v ON i.product_id = v.product_id
)
SELECT *, projected_unsold * unit_cost AS estimated_waste_cost
FROM estimate
ORDER BY estimated_waste_cost DESC
LIMIT 10;
