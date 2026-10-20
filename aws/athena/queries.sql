-- Replace database/table names with the Glue Catalog names in your account.

-- units sold by category.
select i.category as category, sum(s.units_sold) as units_sold 
from inventory i left join sales s 
on i.product_id=s.product_id
group by category

-- units sold and its avg per day.
SELECT
    product_id,
    SUM(units_sold) AS units_sold_7d,
    ROUND(SUM(units_sold) / 7.0, 2) AS avg_units_per_day
FROM grocery.daily_sales
WHERE sale_date >= date_add('day', -7, current_date)
  AND sale_date < current_date
GROUP BY product_id
ORDER BY  avg_units_per_day DESC;
SELECT *, projected_unsold * unit_cost AS estimated_waste_cost
FROM estimate
ORDER BY estimated_waste_cost DESC
LIMIT 10;


-- items expiring in next 2 days
select product_name,
expiry_date, 
quantity_on_hand,
round((quantity_on_hand)/2,2) as avg_quantity_to_be_sold_per_day
from inventory
where cast(expiry_date as DATE) between current_date and date_add('day',2,current_date)
