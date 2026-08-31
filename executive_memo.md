# Executive Memo — Collections Performance

## Decision
**Do not accept the reported “11% month-on-month recovery improvement” as proven. Do not release the full ₹10 Cr as an unconditional rollout.**

## What happened?
An independent payment layer was created from the raw collections data. SUCCESS payments were retained, unambiguous payment references were canonicalized, and conflicting references were quarantined. The conservative layer contains 13,566 unique payment references versus 17,880 raw SUCCESS rows. Raw successful payment value is approximately ₹134.15 Cr; the conservative canonical value is approximately ₹101.42 Cr.

The complete-month recovery series from January through July is volatile. January→July recovery is approximately **-0.8%**, not +11% month-on-month. August is treated as incomplete and is excluded from the headline trend.

## Why?
**Fact:** payment duplication/reference conflicts are material.

**Strong Evidence:** cleaning and denominator reconstruction materially affect reported recovery.

**Correlation:** portfolio mix, DPD, campaign, channel, vendor, agent and targeting changes can explain observed differences.

**Hypothesis:** part of the reported improvement may be reporting/attribution/denominator driven.

**Not established:** that any one operational lever caused a sustained recovery improvement.

## ₹10 Cr recommendation
**Choose: Better borrower targeting — but fund it as a controlled experiment, not a blind rollout.**

The historical targeting counterfactual that holds the January strategy mix constant produces virtually the same Jan–Jul recovery as observed (difference about ₹8.6K). This means the observed strategy-mix change alone does not explain the recovery movement.

Because this is observational, a causal ROI cannot be responsibly estimated from the current data. Therefore the correct financial recommendation is to condition the ₹10 Cr release on experimental evidence rather than fabricate an ROI.

### Experiment
Randomize eligible accounts within DPD × risk × loan-type strata.

Primary KPI: incremental ₹ recovered per eligible account over a fixed attribution window.

Secondary KPIs: recovery rate, paid-account rate, cost per ₹ recovered and complaints.

### Financial gate
Release the ₹10 Cr only if the experiment demonstrates a statistically credible incremental recovery whose lower confidence bound clears the ₹10 Cr investment hurdle plus an agreed risk buffer.

## Confidence
- **High:** the blanket +11% claim is not demonstrated.
- **High:** payment quality materially affects reported recovery.
- **Medium:** targeting is a sensible experimental priority.
- **Low:** any point estimate of causal ₹10 Cr ROI before the experiment.
