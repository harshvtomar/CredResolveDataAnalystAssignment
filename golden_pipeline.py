import pandas as pd
from pathlib import Path

DATA = Path("raw")

def read(name):
    return pd.read_csv(DATA / f"{name}.csv")

payments = read("payments")
accounts = read("accounts")

payments["event_at"] = pd.to_datetime(payments["event_at"], errors="coerce")
payments["status_norm"] = payments["payment_status"].astype(str).str.upper().str.strip()

successful = payments[payments.status_norm.eq("SUCCESS")].copy()

ref_profile = (
    successful.groupby("payment_reference")
    .agg(
        ref_rows=("payment_id","size"),
        ref_accounts=("account_id","nunique"),
        ref_amounts=("amount","nunique"),
    )
    .reset_index()
)

successful = successful.merge(ref_profile, on="payment_reference", how="left")

# Conflicting references are quarantined.
quarantined = successful[
    (successful.ref_accounts > 1) |
    (successful.ref_amounts > 1)
].copy()

# Golden payment layer: only unambiguous references; earliest event retained.
golden_payments = (
    successful[
        (successful.ref_accounts == 1) &
        (successful.ref_amounts == 1)
    ]
    .sort_values(["payment_reference","event_at","payment_id"])
    .drop_duplicates("payment_reference", keep="first")
    .copy()
)

golden_payments["month"] = golden_payments["event_at"].dt.to_period("M").astype(str)

monthly = (
    golden_payments.groupby("month")
    .agg(
        recovered=("amount","sum"),
        payments=("payment_reference","nunique"),
        paid_accounts=("account_id","nunique"),
    )
    .reset_index()
)

monthly["mom_pct"] = monthly["recovered"].pct_change() * 100

golden_payments.to_csv("golden_payments.csv", index=False)
quarantined.to_csv("quarantined_payment_references.csv", index=False)
monthly.to_csv("monthly_recovery.csv", index=False)

print(monthly)
