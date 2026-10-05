"""Validate orders, run SQLite analysis, reconcile totals and render a report."""
import json
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def clean_orders(raw):
    data = raw.drop_duplicates().copy()
    duplicate_rows = len(raw) - len(data)
    # Conflicting primary keys require human review instead of arbitrary selection.
    if data.order_id.isna().any() or data.order_id.duplicated().any():
        raise ValueError('Missing or conflicting order IDs')
    missing_region = int(data.region.isna().sum())
    data['region'] = data.region.fillna('Unknown')
    data['channel'] = data.channel.str.strip().str.title()
    dates = pd.to_datetime(data.order_date, format='%Y-%m-%d', errors='coerce')
    numeric = ['quantity','unit_price_paise','unit_cost_paise','discount_pct']
    for col in numeric:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    valid = (dates.between('2025-01-01','2025-12-31')
             & data.customer_id.notna()
             & data.quantity.gt(0) & data.quantity.mod(1).eq(0)
             & data.unit_price_paise.gt(0) & data.unit_price_paise.mod(1).eq(0)
             & data.unit_cost_paise.ge(0) & data.unit_cost_paise.mod(1).eq(0)
             & data.discount_pct.between(0,100) & data.discount_pct.mod(1).eq(0)
             & data.status.isin(['Completed','Returned','Cancelled'])
             & data.region.isin(['North','South','East','West','Unknown'])
             & data.channel.isin(['Organic','Paid Search','Marketplace'])
             & data.category.isin(['Electronics','Home','Accessories','Fitness']))
    rejected = data.loc[~valid].copy()
    rejected['rejection_reason'] = 'Failed required field, date, category or numeric validation'
    data = data.loc[valid].sort_values('order_id').copy()
    data[numeric] = data[numeric].astype('int64')
    gross = data.quantity * data.unit_price_paise
    # Integer half-up rounding to the nearest paise, once per order.
    discounted = (gross * (100 - data.discount_pct) + 50) // 100
    data['net_revenue_paise'] = discounted.where(data.status.eq('Completed'), 0)
    data['cogs_paise'] = (data.quantity * data.unit_cost_paise).where(data.status.eq('Completed'),0)
    data['gross_profit_paise'] = data.net_revenue_paise - data.cogs_paise
    quality = dict(raw_rows=len(raw), exact_duplicates_removed=duplicate_rows,
                   missing_regions_labeled=missing_region, quarantined_rows=len(rejected),
                   valid_orders=len(data))
    return data, rejected, quality


def main():
    output = ROOT / 'reports'
    output.mkdir(exist_ok=True)
    orders, rejected, quality = clean_orders(pd.read_csv(ROOT / 'data/orders_raw.csv'))
    orders.to_csv(output / 'orders_clean.csv', index=False)
    rejected.to_csv(output / 'quarantined_orders.csv', index=False)
    db = output / 'retail.sqlite'
    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as con:
        orders.to_sql('orders', con, index=False)
        con.execute('CREATE UNIQUE INDEX order_pk ON orders(order_id)')
        con.executescript((ROOT / 'sql/analysis.sql').read_text())
        tables = {name: pd.read_sql_query(f'SELECT * FROM {name}', con) for name in
                  ['monthly_performance','category_performance','customer_segments','channel_performance']}
    for name, table in tables.items():
        table.to_csv(output / f'{name}.csv', index=False, float_format='%.6f')
    monthly, categories, customers, channels = tables.values()
    revenue = int(orders.net_revenue_paise.sum()) / 100
    profit = int(orders.gross_profit_paise.sum()) / 100
    completed = int(orders.status.eq('Completed').sum())
    returned = int(orders.status.eq('Returned').sum())
    # Independent pandas aggregates reconcile SQL groupings and monetary totals.
    for label, table, key in [('category',categories,'category'),('channel',channels,'channel')]:
        expected = orders.groupby(key).net_revenue_paise.sum().sort_index() / 100
        actual = table.set_index(key).net_revenue_inr.sort_index()
        assert (expected - actual).abs().max() < .005, label
    assert abs(monthly.net_revenue_inr.sum() - revenue) < .005
    assert abs(monthly.gross_profit_inr.sum() - profit) < .005
    assert abs(customers.monetary_inr.sum() - revenue) < .005
    assert monthly.completed_orders.sum() == completed
    assert quality['raw_rows'] == quality['exact_duplicates_removed'] + quality['quarantined_rows'] + len(orders)
    kpis = dict(net_revenue_inr=revenue, gross_profit_inr=profit,
                gross_margin_pct=100 * profit / revenue,
                completed_orders=completed, return_rate_pct=100 * returned / (completed+returned),
                average_order_value_inr=revenue / completed, purchasing_customers=len(customers),
                repeat_customer_share_pct=100 * customers.frequency.ge(2).mean())
    (output / 'metrics.json').write_text(json.dumps({'quality':quality,'kpis':kpis}, indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                         'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'retail42'})
    fig, axes = plt.subplots(2,2,figsize=(14,9), layout='constrained')
    fig.suptitle('Retail performance | Synthetic 2025 portfolio dataset', fontsize=19, fontweight='bold')
    ax = axes[0,0]
    ax.plot(monthly.month.str[5:], monthly.net_revenue_inr / 100000, color='#167d9a', marker='o',lw=2.5)
    ax.set(title='Monthly net revenue', xlabel='Month of 2025',ylabel='INR lakh')
    ax.grid(axis='y',alpha=.2)
    cat = categories.sort_values('gross_profit_inr')
    axes[0,1].barh(cat.category, cat.gross_profit_inr / 100000,color='#167d9a')
    axes[0,1].set(title='Gross profit by category',xlabel='INR lakh')
    axes[1,0].bar(categories.category,categories.return_rate_pct,color='#de8e41')
    axes[1,0].set(title='Returned / fulfilled orders',ylabel='Return rate (%)')
    segments = customers.segment.value_counts().sort_index()
    axes[1,1].bar(segments.index,segments.values,color=['#84bcb5','#167d9a','#bcc8d7'])
    axes[1,1].set(title='Customer activity as of 1 Jan 2026',ylabel='Purchasing customers')
    fig.savefig(output / 'dashboard.svg',metadata={'Date':None})
    fig.savefig(output / 'dashboard.png',dpi=140)
    plt.close(fig)
    top = categories.loc[categories.gross_profit_inr.idxmax()]
    most_returns = categories.loc[categories.return_rate_pct.idxmax()]
    report = f'''# Retail performance findings

**Synthetic data only.** These results describe the seeded demonstration dataset, not a real business.

## Results for calendar 2025

| Metric | Result |
| --- | ---: |
| Net revenue | INR {revenue:,.2f} |
| Gross profit | INR {profit:,.2f} |
| Gross margin | {kpis['gross_margin_pct']:.2f}% |
| Completed orders | {completed:,} |
| Average completed order value | INR {kpis['average_order_value_inr']:,.2f} |
| Return rate among fulfilled orders | {kpis['return_rate_pct']:.2f}% |
| Purchasing customers | {len(customers):,} |
| Within-year repeat customer share | {kpis['repeat_customer_share_pct']:.2f}% |

## Interpretation and next steps

1. **{top['category']} contributes the most gross profit:** INR {top['gross_profit_inr']:,.2f}.
   In a real project, inspect stock availability and contribution after shipping and marketing before reallocating budget.
2. **{most_returns['category']} has the highest observed return rate:** {most_returns['return_rate_pct']:.2f}%.
   Inspect return reasons and sample sizes before attributing this to product quality. The generator does not encode a causal category effect.
3. **{int((customers.segment == 'Lapsed').sum())} purchasing customers have no completed purchase in the last 90 days.**
   A randomized outreach test could measure incremental purchases, with a holdout and contact-cost tracking.
4. Monthly revenue changes reflect the synthetic draw. One year is insufficient to establish seasonality.

## Data quality and reconciliation

- Raw records: {quality['raw_rows']:,}; exact duplicate rows removed: {quality['exact_duplicates_removed']}.
- Quarantined invalid records: {quality['quarantined_rows']}; valid unique orders: {quality['valid_orders']:,}.
- Missing regions labelled Unknown: {quality['missing_regions_labeled']}; no regional imputation.
- SQL revenue reconciles against pandas by category and channel, and against customer and monthly totals.
- Monthly profit and completed-order counts reconcile to the validated order table.

## Limits

Final order status is attributed to the original order date. This is a final-status order-cohort view, not a cash-flow or refund-timing report.
Returned orders have zero revenue and zero product cost under an assumed fully recoverable return.
Shipping, return handling, tax, overhead and acquisition costs are absent. Gross profit is not net profit or campaign ROI.
The customer window starts on 1 Jan 2025; prior purchases and later behavior are unknown.
'''
    (output / 'findings.md').write_text(report)
    print(json.dumps({'quality':quality,'kpis':kpis,'reconciliation':'passed'}, indent=2))


if __name__ == '__main__':
    main()
