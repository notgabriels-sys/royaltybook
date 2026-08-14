"""Fictional statement fixtures shared by Royaltybook tests."""

from __future__ import annotations

from pathlib import Path

VALID_PLAN = """\
[statement]
title = "Fictional Q1 statement"
period = "2026-Q1"
currency = "EUR"
requirements_basis = "Fictional test agreement; confirm actual terms and records directly."

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
note = "Synthetic test receipt."

[[income]]
id = "direct-sales"
source = "Fictional shop record"
category = "Direct"
amount_cents = 30000
note = "Synthetic test receipt."

[[deductions]]
id = "processing-fee"
description = "Fictional declared processing fee."
amount_cents = 20000
note = "Synthetic test deduction."
"""


def write_plan(tmp_path: Path, content: str = VALID_PLAN, name: str = "statement.toml") -> Path:
    """Write a fictional statement plan for an isolated test."""

    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path
