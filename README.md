# Royaltybook

Royaltybook is an offline, declared royalty-statement reconciler for independent releases and labels. Put the income and pre-split deduction values you intend to review into one local TOML file, state each recipient’s share in integer basis points, and generate a clear statement plus an explicitly **UNVERIFIED** payment-review sheet.

It is designed for the moment after someone has gathered the values they want to discuss but before anyone treats a calculation as a settlement or a payment. All examples are fictional.

## What it does

- Requires each amount as an integer number of cents, avoiding floating-point rounding drift.
- Requires recipient shares to total exactly 10,000 basis points (100.00%).
- Checks that declared pre-split deductions do not exceed declared income.
- Calculates gross income, deductions, distributable total, and per-recipient entitlements.
- Distributes leftover cents deterministically: largest fractional remainder first, then recipient ID for exact ties.
- Builds a Markdown statement, CSV payout list, JSON record, local file-hash manifest, and a blank-evidence payment-review sheet.

```text
royalty-review-packet/
├── ROYALTY_STATEMENT.md
├── payouts.csv
├── PAYMENT_REVIEW.md
├── statement.json
└── manifest.json
```

## What it does not establish

Royaltybook does **not** validate an agreement, ownership, rights, consent, eligibility, revenue source, receipt, deduction, currency conversion, tax, accounting treatment, recoupment term, payment, or payment evidence. It does not fetch platform reports, log into any account, send money, contact anyone, or modify the source TOML.

A clean calculation is not a contract interpretation, an accounting statement, or proof that anybody has been paid. The generated `PAYMENT_REVIEW.md` begins with every row marked `UNVERIFIED`; add evidence only after independently checking the real agreement and records. See the full [scope boundary](docs/scope-boundary.md).

## Relationship to Creditledger

[Creditledger](https://github.com/notgabriels-sys/creditledger) checks declared contributor/track credits and allocation groups. Royaltybook starts later: it reconciles one dated, declared income-and-deduction pool into arithmetic-only recipient entitlements and a payment-evidence review record. It never infers that an allocation is a valid royalty term.

## Install

Requires Python 3.11 or later.

```sh
uv tool install .
```

For development:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'
```

## Use

Start with the fictional example and replace every value with a current, human-checked declaration.

```sh
royaltybook check examples/statement-example.toml
royaltybook check examples/statement-example.toml --json
royaltybook build examples/statement-example.toml --output ./delivery/statement-q1
```

`check` is read-only. `build` refuses to replace an existing output directory and returns:

- `0` — the declared schema and internal arithmetic reconcile; external facts remain unverified.
- `1` — invalid/missing TOML, invalid declared values, deductions above income, or an existing output directory.

## Input format

```toml
[statement]
title = "Fictional Q1 royalty statement"
period = "2026-Q1"
currency = "EUR"
requirements_basis = "Fictional example only; confirm actual terms and records directly."

[[recipients]]
id = "artist"
name = "Example Artist"
share_basis_points = 7000

[[recipients]]
id = "label"
name = "Example Label"
share_basis_points = 3000

[[income]]
id = "digital-receipts"
source = "Fictional platform report"
category = "Digital"
amount_cents = 120000
note = "Synthetic example amount."

[[deductions]]
id = "processing-fee"
description = "Fictional declared processing fee."
amount_cents = 20000
note = "Synthetic example deduction."
```

`statement.currency` is a declared three-letter uppercase code. Royaltybook does not validate the code, conversion, denomination, or any currency-specific accounting rule. The input amount unit is always the declared number of cents.

## Calculation rule

```text
gross declared income − declared pre-split deductions = distributable cents
recipient entitlement = distributable cents × recipient basis points ÷ 10,000
```

Each provisional entitlement is first rounded down to a whole cent. Any remaining cents go to the highest fractional remainders; tied remainders go to the lexically earlier lowercase recipient ID. This makes every final payout sum exactly to the declared distributable total, with no hidden rounding adjustment.

## Practical review sequence

1. Check the controlling agreement and decide which receipts and agreed deductions belong in the period.
2. Enter those already-reviewed values as integer cents, recording the basis in `requirements_basis`.
3. Run `royaltybook check`, then inspect the generated statement if the arithmetic is internally clean.
4. Review the calculated payout rows with the relevant people and actual records.
5. Use `PAYMENT_REVIEW.md` to record independent evidence only after payment is checked. Do not change an `UNVERIFIED` row based solely on this tool’s calculation.

## Development

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Royaltybook uses Python’s standard library only at runtime. It has no network, browser, upload, payment, or destructive-file capability.

---

---

---

<!-- funnel-footer -->
Part of the Gabriel Tools + Code catalog — [browse all tools, products, repositories, and services](https://gabriel-tools-and-code.notgabriels960914.chatgpt.site/).

Free and open source: [theme-contrast](https://github.com/notgabriels-sys/theme-contrast) (WCAG contrast checking for colour themes) · [htmlshot](https://github.com/notgabriels-sys/htmlshot) (HTML → exact-size PNG/PDF) · [50 dark themes for Claude Code](https://github.com/notgabriels-sys/claude-code-50-dark-themes).

Hologram People soundware and Gabriel audio/product work are linked from the master catalog above.

Mixing and mastering enquiries — [public preview](https://gabriel-mixing-and-mastering-d1dmyt.v2.appdeploy.ai/).
