"""Boundary tests for cleaning and revenue accounting."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
from analyze import clean_orders


class CleaningTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(order_id='O1',customer_id='C1',order_date='2025-12-31',region=None,
                   category='Home',channel=' organic ',quantity=2,unit_price_paise=10000,
                   unit_cost_paise=6000,discount_pct=10,status='Completed')
        return {**row,**changes}

    def test_discount_profit_and_duplicate(self):
        data, rejected, quality = clean_orders(pd.DataFrame([self.row(),self.row()]))
        self.assertEqual(data.iloc[0].net_revenue_paise,18000)
        self.assertEqual(data.iloc[0].gross_profit_paise,6000)
        self.assertEqual(data.iloc[0].region,'Unknown')
        self.assertEqual(data.iloc[0].channel,'Organic')
        self.assertEqual(quality['exact_duplicates_removed'],1)
        self.assertTrue(rejected.empty)

    def test_return_and_cancel_are_zero(self):
        rows = [self.row(order_id=f'O{i}',status=s) for i,s in enumerate(['Returned','Cancelled'])]
        data,_,_ = clean_orders(pd.DataFrame(rows))
        self.assertEqual(data.net_revenue_paise.sum(),0)
        self.assertEqual(data.cogs_paise.sum(),0)

    def test_invalid_rows_quarantined(self):
        rows = [self.row(order_id='1',quantity=-1),self.row(order_id='2',order_date='bad'),
                self.row(order_id='3',discount_pct=101),self.row(order_id='4',customer_id=None),
                self.row(order_id='5',quantity=1.5),self.row(order_id='6',order_date='2026-01-01')]
        data,rejected,_ = clean_orders(pd.DataFrame(rows))
        self.assertTrue(data.empty)
        self.assertEqual(len(rejected),6)

    def test_conflicting_ids_fail(self):
        with self.assertRaises(ValueError):
            clean_orders(pd.DataFrame([self.row(),self.row(quantity=3)]))

    def test_half_paise_rounds_up(self):
        data,_,_ = clean_orders(pd.DataFrame([self.row(quantity=1,unit_price_paise=101,discount_pct=50)]))
        self.assertEqual(data.iloc[0].net_revenue_paise,51)


if __name__ == '__main__':
    unittest.main()
