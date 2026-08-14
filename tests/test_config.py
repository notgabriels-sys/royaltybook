"""Tests for strict declared-statement parsing."""

from __future__ import annotations

import pytest

from royaltybook.config import ConfigError, load_statement
from tests.helpers import VALID_PLAN, write_plan


def test_loads_a_complete_declared_statement(tmp_path):
    plan = load_statement(write_plan(tmp_path))

    assert plan.statement.title == "Fictional Q1 statement"
    assert plan.statement.currency == "EUR"
    assert [recipient.id for recipient in plan.recipients] == ["artist", "label"]
    assert [line.amount_cents for line in plan.income] == [120000, 30000]


def test_rejects_shares_that_do_not_total_one_hundred_percent(tmp_path):
    path = write_plan(
        tmp_path, VALID_PLAN.replace("share_basis_points = 3000", "share_basis_points = 2999")
    )

    with pytest.raises(ConfigError, match="10,000 basis points"):
        load_statement(path)


def test_rejects_duplicate_recipient_ids(tmp_path):
    duplicate = VALID_PLAN.replace('id = "label"', 'id = "artist"')

    with pytest.raises(ConfigError, match="duplicate recipient id"):
        load_statement(write_plan(tmp_path, duplicate))


def test_rejects_unknown_top_level_fields(tmp_path):
    invalid = VALID_PLAN + '\n[untracked]\nvalue = "not allowed"\n'

    with pytest.raises(ConfigError, match="unexpected top-level"):
        load_statement(write_plan(tmp_path, invalid))
