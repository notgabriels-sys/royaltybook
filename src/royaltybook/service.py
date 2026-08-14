"""Exact integer-cent calculation for declared Royaltybook statements."""

from __future__ import annotations

from dataclasses import dataclass

from royaltybook.config import Recipient, StatementPlan


class CalculationError(ValueError):
    """Raised when internally declared statement totals cannot be reconciled."""


@dataclass(frozen=True)
class Payout:
    """One deterministic calculated entitlement, with payment evidence deliberately absent."""

    recipient: Recipient
    amount_cents: int
    rounding_remainder: int


@dataclass(frozen=True)
class StatementAssessment:
    """A reproducible calculation ready for human review, not a payment or contract fact."""

    plan: StatementPlan
    gross_income_cents: int
    deductions_cents: int
    distributable_cents: int
    payouts: tuple[Payout, ...]
    status: str


def apportion(distributable_cents: int, recipients: tuple[Recipient, ...]) -> tuple[Payout, ...]:
    """Allocate whole cents by largest remainder, breaking exact ties by recipient ID."""

    provisional: list[list[object]] = []
    for recipient in recipients:
        whole_cents, remainder = divmod(distributable_cents * recipient.share_basis_points, 10_000)
        provisional.append([recipient, whole_cents, remainder])
    allocated_cents = sum(int(row[1]) for row in provisional)
    leftover_cents = distributable_cents - allocated_cents
    order = sorted(
        range(len(provisional)),
        key=lambda index: (-int(provisional[index][2]), provisional[index][0].id),
    )
    for index in order[:leftover_cents]:
        provisional[index][1] = int(provisional[index][1]) + 1
    payouts = tuple(
        Payout(
            recipient=row[0],
            amount_cents=int(row[1]),
            rounding_remainder=int(row[2]),
        )
        for row in provisional
    )
    if sum(payout.amount_cents for payout in payouts) != distributable_cents:
        raise CalculationError("could not reconcile calculated payouts to the distributable total")
    return payouts


def calculate(plan: StatementPlan) -> StatementAssessment:
    """Calculate declared totals without judging receipts, terms, or payment proof."""

    gross_income_cents = sum(line.amount_cents for line in plan.income)
    deductions_cents = sum(line.amount_cents for line in plan.deductions)
    if deductions_cents > gross_income_cents:
        raise CalculationError("declared deductions exceed declared income")
    distributable_cents = gross_income_cents - deductions_cents
    return StatementAssessment(
        plan=plan,
        gross_income_cents=gross_income_cents,
        deductions_cents=deductions_cents,
        distributable_cents=distributable_cents,
        payouts=apportion(distributable_cents, plan.recipients),
        status="calculation_ready_for_human_review",
    )
