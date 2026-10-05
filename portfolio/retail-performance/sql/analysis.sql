-- SQLite. The Python pipeline loads one validated row per order into orders.
-- Money is stored as integer paise. These views convert to INR only at output.
CREATE VIEW monthly_performance AS
WITH monthly AS (
  SELECT substr(order_date, 1, 7) AS month,
         COUNT(*) AS placed_orders,
         SUM(status = 'Completed') AS completed_orders,
         SUM(status = 'Returned') AS returned_orders,
         SUM(net_revenue_paise) / 100.0 AS net_revenue_inr,
         SUM(gross_profit_paise) / 100.0 AS gross_profit_inr
  FROM orders GROUP BY 1
), previous AS (
  SELECT *, LAG(net_revenue_inr) OVER (ORDER BY month) AS previous_revenue
  FROM monthly
)
SELECT *, 100.0 * (net_revenue_inr - previous_revenue)
          / NULLIF(previous_revenue, 0) AS revenue_mom_pct
FROM previous;

CREATE VIEW category_performance AS
SELECT category, COUNT(*) AS placed_orders,
       SUM(status = 'Completed') AS completed_orders,
       SUM(net_revenue_paise) / 100.0 AS net_revenue_inr,
       SUM(gross_profit_paise) / 100.0 AS gross_profit_inr,
       100.0 * SUM(gross_profit_paise) / NULLIF(SUM(net_revenue_paise),0) AS gross_margin_pct,
       100.0 * SUM(status = 'Returned') /
         NULLIF(SUM(status IN ('Completed','Returned')),0) AS return_rate_pct
FROM orders GROUP BY category;

-- Transparent business-rule segmentation, evaluated at 2026-01-01.
-- Orders before 2025 are not observed. This is within-window repeat behavior.
CREATE VIEW customer_segments AS
WITH customer AS (
  SELECT customer_id, COUNT(*) AS frequency,
         CAST(julianday('2026-01-01') - julianday(MAX(order_date)) AS INTEGER) AS recency_days,
         SUM(net_revenue_paise) / 100.0 AS monetary_inr
  FROM orders WHERE status = 'Completed' GROUP BY customer_id
)
SELECT *, CASE WHEN recency_days <= 90 AND frequency >= 3 THEN 'Active repeat'
               WHEN recency_days <= 90 THEN 'Active occasional'
               ELSE 'Lapsed' END AS segment
FROM customer;

CREATE VIEW channel_performance AS
SELECT channel, COUNT(*) AS placed_orders,
       SUM(net_revenue_paise) / 100.0 AS net_revenue_inr,
       SUM(gross_profit_paise) / 100.0 AS gross_profit_inr,
       100.0 * SUM(gross_profit_paise) / NULLIF(SUM(net_revenue_paise),0) AS gross_margin_pct
FROM orders GROUP BY channel;
