# Retail performance findings

**Synthetic data only.** These results describe the seeded demonstration dataset, not a real business.

## Results for calendar 2025

| Metric | Result |
| --- | ---: |
| Net revenue | INR 4,677,664.75 |
| Gross profit | INR 1,433,298.67 |
| Gross margin | 30.64% |
| Completed orders | 1,034 |
| Average completed order value | INR 4,523.85 |
| Return rate among fulfilled orders | 8.25% |
| Purchasing customers | 329 |
| Within-year repeat customer share | 84.80% |

## Interpretation and next steps

1. **Electronics contributes the most gross profit:** INR 475,147.35.
   In a real project, inspect stock availability and contribution after shipping and marketing before reallocating budget.
2. **Accessories has the highest observed return rate:** 9.38%.
   Inspect return reasons and sample sizes before attributing this to product quality. The generator does not encode a causal category effect.
3. **143 purchasing customers have no completed purchase in the last 90 days.**
   A randomized outreach test could measure incremental purchases, with a holdout and contact-cost tracking.
4. Monthly revenue changes reflect the synthetic draw. One year is insufficient to establish seasonality.

## Data quality and reconciliation

- Raw records: 1,220; exact duplicate rows removed: 20.
- Quarantined invalid records: 6; valid unique orders: 1,194.
- Missing regions labelled Unknown: 12; no regional imputation.
- SQL revenue reconciles against pandas by category and channel, and against customer and monthly totals.
- Monthly profit and completed-order counts reconcile to the validated order table.

## Limits

Final order status is attributed to the original order date. This is a final-status order-cohort view, not a cash-flow or refund-timing report.
Returned orders have zero revenue and zero product cost under an assumed fully recoverable return.
Shipping, return handling, tax, overhead and acquisition costs are absent. Gross profit is not net profit or campaign ROI.
The customer window starts on 1 Jan 2025; prior purchases and later behavior are unknown.
