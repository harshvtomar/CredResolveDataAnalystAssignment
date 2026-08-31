# Golden Dataset Specification

## Purpose
Create a trustworthy analytical layer from the raw collections systems without assuming that any one source is the system of record.

## Source-of-truth decisions
- Account identity: `accounts.account_id`; borrower identity resolved through `borrower_id`.
- Payment event: `payments`; successful recovery requires `payment_status = SUCCESS`.
- Campaign exposure: `daily_targeting` + `campaigns`, anchored to event time rather than latest interaction.
- Historical account eligibility: `account_status_history`, not the current account snapshot alone.
- Agent identity: reconcile `agent_id` with `employee_code` and effective dates.

## Payment deduplication
1. Normalize payment status.
2. Keep SUCCESS records for recovery.
3. Profile each `payment_reference`.
4. If one reference maps to multiple accounts or amounts, quarantine it.
5. If one reference is unambiguous, retain the earliest event and remove retries/duplicates.
6. Preserve all rejected/quarantined records for auditability.

## Timestamp treatment
- Parse all event timestamps explicitly.
- Preserve raw timestamp.
- Convert to one business timezone for daily/hourly reporting.
- Retain timezone/source fields to support forensic checks.
- Do not silently overwrite original timestamps.

## Missing data
- Never convert missing agent/channel/campaign to a real category.
- Use explicit `UNKNOWN` only where a metric requires a bucket.
- Exclude missing values only when the metric definition explicitly requires the field.
- Report missingness as a quality metric.

## Historical changes
- Use effective-dated history where available.
- Version disposition mappings.
- Do not use current campaign definitions to rewrite historical events.

## Exclusion rules
- Duplicate exact records: remove from analytical fact layer, retain audit count.
- Conflicting payment references: quarantine until reconciled.
- Invalid/unparseable timestamps: exclude from time-based metrics and report.
- Partial August: exclude from full-month trend comparisons until completeness is confirmed.

## Raw → Rejected/Corrected → Golden
Raw records remain immutable.
Corrected/rejected records are traceable using a reason code.
Golden records contain the canonical business key and transformation version.

## Quantified cleaning impact
From the supplied analysis:
- Raw SUCCESS payment rows: 17,880
- Canonical unambiguous payment references: 13,566
- Conflicting payment-reference rows: 3,799
- Raw successful payment value: approximately ₹134.15 Cr
- Conservative canonical value: approximately ₹101.42 Cr

This demonstrates that payment cleaning materially changes reported recovery.
