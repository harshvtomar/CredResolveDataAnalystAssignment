# Data Quality & Forensics Report

## Executive summary

The dataset contains intentional and business-realistic data quality risks. The most material issue for the recovery claim is payment duplication/reference conflict.

| Issue | Detection | Treatment | Business impact |
|---|---|---|---|
| Duplicate payment references | Group SUCCESS payments by payment_reference | Deduplicate unambiguous references; quarantine conflicts | Can materially inflate recovery |
| Exact duplicate calls | Duplicate row / call_id checks | Retain canonical event | Inflates attempt/contact metrics |
| Borrower duplicates | Exact duplicate + identity-key checks | Resolve to stable borrower identity | Can distort account/borrower denominators |
| Multiple agent identifiers | employee_code ↔ agent_id mapping | Effective-dated identity map | Can fragment agent performance |
| Timezone differences | Compare timezone fields and parsed event timestamps | Normalize reporting timezone, retain raw | Can shift day/hour attribution |
| Campaign definition changes | Compare campaign/strategy versions over time | Version campaign definitions | Can create false campaign lift |
| Historical status changes | Compare current accounts to account_status_history | Reconstruct historical eligibility | Prevents denominator manipulation |
| Late events | Event timestamp vs ingestion/update time | Watermark + backfill | Prevents premature period closure |

## Key quantified finding

Raw SUCCESS payment value is approximately **₹134.15 Cr** versus approximately **₹101.42 Cr** under the conservative canonical payment layer. This is a roughly **₹32.73 Cr** difference.

Therefore raw payment totals should not be used as the primary recovery KPI.

## Forensic classification

**Fact:** duplicate/conflicting payment references exist.

**Strong Evidence:** canonicalization materially reduces recoverable payment value.

**Correlation:** targeting/channel differences can coincide with recovery differences.

**Hypothesis:** the reported improvement may partly reflect data/denominator/attribution changes.

**Not established:** that any single operational lever caused the recovery change.
