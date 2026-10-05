# Data dictionary

Source: `src/generate_data.py`, pseudo-random seed 42. All records are fictional.
Grain: one category-level order per `order_id`, before injected exact duplicates.
One order has one customer, category and channel. Currency: INR, stored as integer paise (100 paise = INR 1).

| Column | Type / unit | Meaning |
| --- | --- | --- |
| order_id | String | Unique order key after exact deduplication |
| customer_id | String | Fictional customer key, C0001–C0350 |
| order_date | ISO date | Original order date in 2025 |
| region | Category | North, South, East or West; missing values become Unknown |
| category | Category | Electronics, Home, Accessories or Fitness |
| channel | Category | Organic, Paid Search or Marketplace; trim and title-case before validation |
| quantity | Positive integer | Units in the order |
| unit_price_paise | Positive integer paise | Per-unit price before discount |
| unit_cost_paise | Nonnegative integer paise | Per-unit product cost |
| discount_pct | Integer 0–100 | Percentage discount; 10 means 10% |
| status | Category | Completed, Returned or Cancelled at the reporting snapshot |

Deliberate defects: 20 duplicate records, 12 missing regions, six negative quantities and 12 channel labels with inconsistent spacing/case. These defect groups do not overlap except that exact duplicates repeat otherwise valid rows.

Generated price base values in INR: Electronics 3,500; Home 1,400; Accessories 650; Fitness 1,800. Unit prices are uniform integer draws from 70% (inclusive) to 140% (exclusive) of each base. Product cost ratios are respectively 72%, 57%, 42% and 60%. Quantities range from 1 to 4. Discount draws use `[0, 0, 5, 10, 15, 20]`. Final-status weights are 86:9:5 for completed:returned:cancelled. These are simulation assumptions, not market estimates.

Derived order fields: `net_revenue_paise`, `cogs_paise` and `gross_profit_paise`. They are zero for cancelled and returned orders under the stated accounting simplification. Gross profit can be negative for a valid input and is never clipped to zero.
