"""Portable local Royaltybook statement packets and evidence boundaries."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from royaltybook.service import StatementAssessment


@dataclass(frozen=True)
class StatementBundle:
    """Generated local statement files, none of which establishes payment completion."""

    output_path: Path
    statement_path: Path
    payouts_path: Path
    payment_review_path: Path
    document_path: Path
    manifest_path: Path


def cents_text(cents: int, currency: str) -> str:
    """Format a declared integer-cent amount for a human review document."""

    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{currency} {sign}{whole:,}.{fraction:02d}"


def percent_text(basis_points: int) -> str:
    """Render an exact ten-thousand-point allocation as a familiar percentage."""

    return f"{basis_points / 100:.2f}%"


def markdown_cell(value: object) -> str:
    """Keep human declarations inside reliable Markdown table cells."""

    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def document(assessment: StatementAssessment) -> dict[str, object]:
    """Return declared inputs and reproducible arithmetic, not payment facts."""

    plan = assessment.plan
    return {
        "schema_version": 1,
        "status": assessment.status,
        "payment_review_status": "unverified",
        "statement": {
            "title": plan.statement.title,
            "period": plan.statement.period,
            "currency": plan.statement.currency,
            "requirements_basis": plan.statement.requirements_basis,
        },
        "income": [
            {
                "id": line.id,
                "source": line.source,
                "category": line.category,
                "amount_cents": line.amount_cents,
                "note": line.note,
            }
            for line in plan.income
        ],
        "deductions": [
            {
                "id": line.id,
                "description": line.description,
                "amount_cents": line.amount_cents,
                "note": line.note,
            }
            for line in plan.deductions
        ],
        "totals": {
            "gross_income_cents": assessment.gross_income_cents,
            "deductions_cents": assessment.deductions_cents,
            "distributable_cents": assessment.distributable_cents,
        },
        "payouts": [
            {
                "recipient_id": payout.recipient.id,
                "recipient_name": payout.recipient.name,
                "share_basis_points": payout.recipient.share_basis_points,
                "calculated_payout_cents": payout.amount_cents,
                "rounding_remainder": payout.rounding_remainder,
                "payment_status": "UNVERIFIED",
                "payment_evidence_reference": None,
            }
            for payout in assessment.payouts
        ],
        "scope_boundary": (
            "Declared integer-cent arithmetic only; no validation of contracts, rights, "
            "terms, receipts, deductions, tax, currency treatment, payment, or consent."
        ),
    }


def render_statement_markdown(assessment: StatementAssessment) -> str:
    """Render declared lines and derived totals in a reviewable local statement."""

    plan = assessment.plan
    currency = plan.statement.currency
    lines = [
        f"# Royalty statement — {plan.statement.title}",
        "",
        "**State:** DECLARED CALCULATION — EXTERNAL RECEIPTS, TERMS, AND PAYMENTS UNVERIFIED  ",
        f"**Period (declared):** {plan.statement.period}  ",
        f"**Currency (declared):** {currency}  ",
        f"**Requirements basis (declared):** {plan.statement.requirements_basis}",
        "",
        "## Declared income",
        "",
        "| ID | Source | Category | Amount | Note |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for line in plan.income:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{line.id}`",
                    markdown_cell(line.source),
                    markdown_cell(line.category),
                    cents_text(line.amount_cents, currency),
                    markdown_cell(line.note),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            f"**Declared gross income:** {cents_text(assessment.gross_income_cents, currency)}",
            "",
            "## Declared pre-split deductions",
            "",
            "| ID | Description | Amount | Note |",
            "| --- | --- | ---: | --- |",
        ]
    )
    if plan.deductions:
        for line in plan.deductions:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{line.id}`",
                        markdown_cell(line.description),
                        cents_text(line.amount_cents, currency),
                        markdown_cell(line.note),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| — | No declared deductions | — | — |")
    lines.extend(
        [
            "",
            f"**Declared deductions:** {cents_text(assessment.deductions_cents, currency)}  ",
            f"**Distributable total:** {cents_text(assessment.distributable_cents, currency)}",
            "",
            "## Calculated recipient entitlements",
            "",
            "| Recipient | Share | Calculated entitlement | Payment state |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for payout in assessment.payouts:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{markdown_cell(payout.recipient.name)} (`{payout.recipient.id}`)",
                    percent_text(payout.recipient.share_basis_points),
                    cents_text(payout.amount_cents, currency),
                    "UNVERIFIED",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Scope boundary",
            "",
            (
                "Royaltybook calculates only values you declare locally. It does not validate "
                "agreements, ownership, rights, consent, source statements, receipts, deduction "
                "eligibility, currency conversion, tax, accounting treatment, payment, or payment "
                "evidence. Confirm the actual agreement and records directly."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def render_payment_review(assessment: StatementAssessment) -> str:
    """Render a human evidence gate that never turns a calculation into a payment claim."""

    currency = assessment.plan.statement.currency
    lines = [
        f"# Payment review — {assessment.plan.statement.title}",
        "",
        "**Review state:** UNVERIFIED — complete this after checking actual payment evidence.",
        "",
        "| Recipient | Entitlement | Payment status | Evidence | Checked by | Checked on |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for payout in assessment.payouts:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{markdown_cell(payout.recipient.name)} (`{payout.recipient.id}`)",
                    cents_text(payout.amount_cents, currency),
                    "UNVERIFIED",
                    "",
                    "",
                    "",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "A calculated entitlement is not evidence of payment, contractual obligation, or tax "
            "treatment. Add real-world evidence after independently checking relevant records.",
            "",
        ]
    )
    return "\n".join(lines)


def sha256(path: Path) -> str:
    """Return a generated-file fingerprint for the portable local manifest."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_payouts_csv(assessment: StatementAssessment, path: Path) -> None:
    """Write calculated payouts with blank payment-evidence fields for a human review workflow."""

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "recipient_id",
                "recipient_name",
                "share_basis_points",
                "calculated_payout_cents",
                "payment_status",
                "payment_evidence_reference",
            ],
        )
        writer.writeheader()
        for payout in assessment.payouts:
            writer.writerow(
                {
                    "recipient_id": payout.recipient.id,
                    "recipient_name": payout.recipient.name,
                    "share_basis_points": payout.recipient.share_basis_points,
                    "calculated_payout_cents": payout.amount_cents,
                    "payment_status": "UNVERIFIED",
                    "payment_evidence_reference": "",
                }
            )


def write_bundle(assessment: StatementAssessment, output_path: Path) -> StatementBundle:
    """Build a new local statement packet without overwriting a previous review artefact."""

    if output_path.exists():
        raise FileExistsError(f"output directory already exists: {output_path}")
    output_path.mkdir(parents=True)
    statement_path = output_path / "ROYALTY_STATEMENT.md"
    payouts_path = output_path / "payouts.csv"
    payment_review_path = output_path / "PAYMENT_REVIEW.md"
    document_path = output_path / "statement.json"
    manifest_path = output_path / "manifest.json"
    statement_path.write_text(render_statement_markdown(assessment), encoding="utf-8")
    write_payouts_csv(assessment, payouts_path)
    payment_review_path.write_text(render_payment_review(assessment), encoding="utf-8")
    document_path.write_text(
        json.dumps(document(assessment), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    generated_files = (statement_path, payouts_path, payment_review_path, document_path)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": assessment.status,
                "source_plan": {
                    "file_name": assessment.plan.source_path.name,
                    "sha256": sha256(assessment.plan.source_path),
                },
                "generated_files": [
                    {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                    for path in generated_files
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return StatementBundle(
        output_path=output_path,
        statement_path=statement_path,
        payouts_path=payouts_path,
        payment_review_path=payment_review_path,
        document_path=document_path,
        manifest_path=manifest_path,
    )
