"""End-to-end CLI behaviour tests."""

from __future__ import annotations

import json

from royaltybook.cli import main
from tests.helpers import write_plan


def test_check_prints_machine_readable_declared_calculation(tmp_path, capsys):
    plan_path = write_plan(tmp_path)

    assert main(["check", str(plan_path), "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["totals"]["distributable_cents"] == 130000
    assert payload["payment_review_status"] == "unverified"


def test_build_creates_packet_and_refuses_existing_output(tmp_path, capsys):
    plan_path = write_plan(tmp_path)
    output = tmp_path / "packet"

    assert main(["build", str(plan_path), "--output", str(output)]) == 0
    assert (output / "payouts.csv").is_file()
    assert main(["build", str(plan_path), "--output", str(output)]) == 1
    assert "already exists" in capsys.readouterr().err


def test_invalid_plan_returns_nonzero_without_traceback(tmp_path, capsys):
    plan_path = write_plan(tmp_path, '[statement]\ntitle = "incomplete"\n')

    assert main(["check", str(plan_path)]) == 1
    assert capsys.readouterr().err.startswith("error:")
