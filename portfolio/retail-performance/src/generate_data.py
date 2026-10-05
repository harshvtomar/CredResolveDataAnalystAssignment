"""Create deterministic synthetic retail orders. No external or personal data."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate():
    rng = random.Random(42)
    rows = []
    categories = {'Electronics': (3500, .72), 'Home': (1400, .57),
                  'Accessories': (650, .42), 'Fitness': (1800, .60)}
    for i in range(1, 1201):
        category = rng.choice(list(categories))
        base_price, cost_ratio = categories[category]
        price = rng.randrange(int(base_price * .7), int(base_price * 1.4)) * 100
        order_date = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        rows.append(dict(order_id=f'O{i:05}', customer_id=f'C{rng.randrange(1,351):04}',
                         order_date=order_date.isoformat(), region=rng.choice(['North','South','East','West']),
                         category=category, channel=rng.choice(['Organic','Paid Search','Marketplace']),
                         quantity=rng.randrange(1,5), unit_price_paise=price,
                         unit_cost_paise=round(price * cost_ratio),
                         discount_pct=rng.choice([0,0,5,10,15,20]),
                         status=rng.choices(['Completed','Returned','Cancelled'],[86,9,5])[0]))
    # Deliberate quality defects: exact duplicates, missing regions, invalid quantities.
    for row in rows[:12]:
        row['region'] = ''
    for row in rows[12:18]:
        row['quantity'] = -1
    for row in rows[18:30]:
        row['channel'] = ' paid search '
    rows.extend(dict(row) for row in rows[100:120])
    rng.shuffle(rows)
    (ROOT / 'data').mkdir(exist_ok=True)
    with (ROOT / 'data/orders_raw.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f'Generated {len(rows):,} synthetic raw rows (seed 42).')


if __name__ == '__main__':
    generate()
