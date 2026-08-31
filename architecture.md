# Production Analytics Architecture

```text
RAW SOURCES
borrowers | accounts | agents | sessions | campaigns | targeting
calls | attempts | dispositions | WhatsApp | SMS | field
PTP | payments | vendors | complaints | status history
        |
        v
STAGING
schema normalization • source metadata • raw timestamps
        |
        v
CLEAN
type validation • ID normalization • disposition version mapping
duplicate detection • timezone normalization
        |
        v
GOLDEN
borrower • account • agent • campaign • targeting • payment • interaction
        |
        v
FEATURE
DPD • risk • cohort • exposure • attempts • contact • RPC • PTP
recovery • agent hours • channel • vendor • cost
        |
        v
METRICS
recovery ₹ • recovery/account • recovery/agent-hour
contact rate • RPC • PTP rate • PTP kept rate
cost/₹ recovered • channel conversion
        |
        v
CEO DASHBOARD
```

## Production controls

### Data contracts
Each source publishes schema, primary key, event timestamp, ingestion timestamp, timezone and allowed categorical values.

### Primary keys
Every fact table must enforce uniqueness of its canonical event key. Payment reference conflicts are quarantined rather than silently overwritten.

### Incremental processing
Use ingestion watermark plus event-time lookback. Reprocess a rolling late-data window.

### Late data / backfills
Maintain immutable raw data. Late events trigger partition-level recomputation for affected dates.

### Data quality
- PK uniqueness
- FK integrity
- null thresholds
- accepted status values
- timestamp plausibility
- duplicate payment-reference checks
- source freshness
- reconciliation totals

### Monitoring
Daily alerts for recovery jumps, denominator drops, duplicate-rate spikes, missing vendors/agents, unusual channel mix and schema drift.

### Lineage
Every metric must point to source table → clean transformation → golden entity → feature → metric definition.
