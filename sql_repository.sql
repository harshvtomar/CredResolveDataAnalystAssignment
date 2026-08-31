-- ============================================================
-- Collections Assignment: Golden Dataset + Independent Metrics
-- PostgreSQL-style SQL
-- ============================================================

-- 01_payment_reference_audit.sql
WITH s AS (
    SELECT *
    FROM payments
    WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
)
SELECT
    payment_reference,
    COUNT(*) AS rows_per_reference,
    COUNT(DISTINCT account_id) AS accounts_per_reference,
    COUNT(DISTINCT amount) AS amounts_per_reference,
    MIN(event_at) AS first_event_at,
    MAX(event_at) AS last_event_at
FROM s
GROUP BY payment_reference
HAVING COUNT(*) > 1
    OR COUNT(DISTINCT account_id) > 1
    OR COUNT(DISTINCT amount) > 1
ORDER BY rows_per_reference DESC;


-- 02_golden_payments.sql
-- Conservative rule:
--   * SUCCESS only
--   * payment_reference must map to exactly one account and one amount
--   * retain earliest event for the reference
--   * conflicting references are quarantined rather than guessed
WITH successful AS (
    SELECT *
    FROM payments
    WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
),
profile AS (
    SELECT
        payment_reference,
        COUNT(*) AS ref_rows,
        COUNT(DISTINCT account_id) AS ref_accounts,
        COUNT(DISTINCT amount) AS ref_amounts
    FROM successful
    GROUP BY payment_reference
),
ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY s.payment_reference
            ORDER BY s.event_at, s.payment_id
        ) AS rn
    FROM successful s
    JOIN profile p
      ON s.payment_reference = p.payment_reference
    WHERE p.ref_accounts = 1
      AND p.ref_amounts = 1
)
SELECT *
FROM ranked
WHERE rn = 1;


-- 03_monthly_recovery.sql
WITH golden_payments AS (
    -- replace with materialized golden_payments table
    SELECT * FROM golden_payments
)
SELECT
    DATE_TRUNC('month', event_at) AS month,
    SUM(amount) AS recovered_rupees,
    COUNT(DISTINCT payment_reference) AS successful_payments,
    COUNT(DISTINCT account_id) AS paid_accounts
FROM golden_payments
GROUP BY 1
ORDER BY 1;


-- 04_call_metrics.sql
WITH calls_clean AS (
    SELECT *
    FROM calls
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY call_id
        ORDER BY event_at, call_id
    ) = 1
)
SELECT
    DATE_TRUNC('month', event_at) AS month,
    COUNT(*) AS attempts,
    COUNT(DISTINCT account_id) AS accounts_called,
    SUM(CASE WHEN UPPER(call_status) = 'ANSWERED' THEN 1 ELSE 0 END) AS answered,
    SUM(CASE WHEN UPPER(call_status) = 'ANSWERED' THEN 1 ELSE 0 END)::DECIMAL
      / NULLIF(COUNT(*),0) AS contact_rate
FROM calls_clean
GROUP BY 1
ORDER BY 1;


-- 05_ptp_metrics.sql
SELECT
    DATE_TRUNC('month', event_at) AS month,
    COUNT(DISTINCT ptp_id) AS ptps,
    SUM(promised_amount) AS promised_amount,
    COUNT(DISTINCT CASE WHEN UPPER(status) = 'KEPT' THEN ptp_id END) AS kept_ptps,
    COUNT(DISTINCT CASE WHEN UPPER(status) = 'KEPT' THEN ptp_id END)::DECIMAL
      / NULLIF(COUNT(DISTINCT ptp_id),0) AS ptp_kept_rate
FROM promises_to_pay
GROUP BY 1
ORDER BY 1;


-- 06_fk_quality.sql
SELECT 'calls.account_id' AS check_name, COUNT(*) AS orphan_rows
FROM calls c LEFT JOIN accounts a ON c.account_id=a.account_id
WHERE a.account_id IS NULL
UNION ALL
SELECT 'payments.account_id', COUNT(*)
FROM payments p LEFT JOIN accounts a ON p.account_id=a.account_id
WHERE a.account_id IS NULL;


-- 07_denominator_snapshot.sql
-- Use account_status_history to reconstruct eligibility at month-end.
-- Never use only the current accounts table for historical denominators.
WITH month_ends AS (
    SELECT DATE_TRUNC('month', d)::date + INTERVAL '1 month - 1 day' AS month_end
    FROM GENERATE_SERIES('2026-01-01'::date,'2026-08-01'::date,'1 month') d
)
SELECT
    m.month_end,
    COUNT(DISTINCT h.account_id) AS eligible_accounts
FROM month_ends m
JOIN account_status_history h
  ON h.event_at <= m.month_end
WHERE UPPER(h.status) NOT IN ('CLOSED','WRITTEN_OFF')
GROUP BY 1
ORDER BY 1;
