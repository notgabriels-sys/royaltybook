"""Tests for exact declared-statement arithmetic."""

from __future__ import annotations

import pytest

from royaltybook.config import load_statement
from royaltybook.service import CalculationError, calculate
from tests.helpers import VALID_PLAN, write_plan


def test_calculates_income_deductions_and_payouts_in_integer_cents(tmp_path):
    assessment = calculate(load_statement(write_plan(tmp_path)))

    assert assessment.gross_income_cents == 150000
    assert assessment.deductions_cents == 20000
    assert assessment.distributable_cents == 130000
    assert {payout.recipient.id: payout.amount_cents for payout in assessment.payouts} == {
        "artist": 91000,
        "label": 39000,
    }
    assert sum(payout.amount_cents for payout in assessment.payouts) == 130000


def test_rejects_deductions_that_exceed_declared_income(tmp_path):
    invalid = VALID_PLAN.replace("amount_cents = 20000", "amount_cents = 160000")

    with pytest.raises(CalculationError, match="exceed declared income"):
        calculate(load_statement(write_plan(tmp_path, invalid)))


def test_apportions_leftover_cents_deterministically_by_remainder_then_id(tmp_path):
    rounded = """\
[statement]
title = "Fictional rounding case"
period = "2026-Q1"
currency = "EUR"
requirements_basis = "Synthetic rounding test."

[[recipients]]
id = "a"
name = "A"
share_basis_points = 3333

[[recipients]]
id = "b"
name = "B"
share_basis_points = 3333

[[recipients]]
id = "c"
name = "C"
share_basis_points = 3334

[[income]]
id = "receipt"
source = "Synthetic record"
category = "Test"
amount_cents = 101
note = "Synthetic rounding input."
"""
    assessment = calculate(load_statement(write_plan(tmp_path, rounded)))

    assert {payout.recipient.id: payout.amount_cents for payout in assessment.payouts} == {
        "a": 34,
        "b": 33,
        "c": 34,
    }


def test_marks_a_valid_calculation_ready_for_human_review(tmp_path):
    assessment = calculate(load_statement(write_plan(tmp_path)))

    assert assessment.status == "calculation_ready_for_human_review"
