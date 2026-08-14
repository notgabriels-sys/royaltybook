# Royaltybook scope boundary

Royaltybook works from a local TOML declaration. A clean check proves only that the stated schema and arithmetic are internally consistent: positive declared cent amounts, exactly 10,000 declared recipient basis points, deductions no greater than gross declared income, and payouts that reconcile to the distributable total.

It does not know whether an agreement exists, which version controls, whether a contribution or release is eligible, whether the declared split applies to a period or revenue source, or whether a deduction is permitted. It does not fetch distributor reports, payment processor records, bank statements, accounting systems, contracts, tax documents, or release-platform data.

Every generated recipient row begins with `UNVERIFIED` as its payment state. The generated payment-review sheet deliberately leaves evidence, checker, and date columns blank. Filling those fields requires a person to inspect the relevant real-world records.

Amounts are intentionally supplied as integer cents. Royaltybook does not infer currency conversion, rounding conventions from an agreement, tax treatment, withholding, recoupment terms, payment timing, minimum thresholds, carry-forward rules, chargebacks, refunds, or accounting standards. If any of those affect a settlement, represent the agreed final pre-split values in the input only after checking the actual agreement and records.

The tool does not contact anyone or any service. It makes no network request, has no browser or payment integration, and never changes the statement source file. `build` only writes a new local output directory and refuses to overwrite an existing one.
