# Counterfactual: What if targeting had not changed?

## Treatment
Accounts exposed to the new targeting strategy after the strategy change.

## Control
Comparable eligible accounts remaining under the legacy strategy.

## Preferred identification strategy
Randomize eligible accounts within DPD × risk × loan-type strata to treatment/control. Keep the treatment definition stable for the full attribution window.

## Historical observational estimate
As a diagnostic, hold the January strategy mix fixed and apply each month's observed strategy-specific recovery-per-target to that fixed mix.

Across Jan–Jul, this counterfactual differs from observed targeting-attributed recovery by only about ₹8.6K, effectively zero relative to the recovery base.

### Interpretation
**Strong Evidence:** changing the aggregate strategy mix does not explain the observed recovery movement in this simple counterfactual.

**Important limitation:** this is not a causal estimate. Strategy assignment may be confounded by borrower selection, DPD, risk, geography, agent capacity and campaign eligibility.

## Assumptions
- Comparable measurement window.
- Stable payment definition.
- No major unobserved shock differentially affecting treatment/control.
- Accurate historical targeting exposure.
- No differential missingness.

## Limitations
- Observational targeting is subject to confounding.
- Some event histories are incomplete/late.
- August is partial.
- A randomized experiment is required for a defensible incremental-recovery estimate.
