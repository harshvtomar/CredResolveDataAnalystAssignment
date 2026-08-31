# Statistical Investigation

## Required questions
The analysis explicitly checks for:
- portfolio mix
- DPD
- client
- geography
- language
- agent and tenure
- campaign
- channel
- telephony vendor
- calling time
- attempt frequency
- borrower segment
- cohort effects
- selection/survivorship bias
- Simpson's paradox
- attribution-window bias
- time-series effects

## Method

Use transparent stratified comparisons rather than a black-box model.

For each material segment:
1. Construct monthly eligible population from historical status.
2. Calculate recovery ₹ / eligible account.
3. Calculate recovery rate and paid-account rate.
4. Compare within DPD/risk/loan-type strata.
5. Reweight later months to the baseline portfolio mix.
6. Compare raw and mix-adjusted changes.
7. Repeat with fixed attribution windows.

## Interpretation rule

A change in aggregate recovery is not operational improvement unless it persists after controlling for material portfolio composition.

## Simpson's paradox check

For each segment, compare the sign of the within-segment change to the aggregate change. If segment-level directions disagree with aggregate direction, flag Simpson's paradox and report the mix contribution.

## Selection/survivorship

Never define the denominator as “accounts that remained in the active targeting file.” Use historical eligibility/status snapshots so unsuccessful accounts cannot disappear from the denominator.

## Attribution window

Use a fixed window (recommended 7 days for campaign attribution) and test sensitivity at 3, 7 and 14 days. A channel should not receive credit merely because it was the latest interaction before payment.

## Time series

Use complete months only for the headline trend. Treat August as incomplete until data completeness is verified.
