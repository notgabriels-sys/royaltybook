"""Tests for locally generated royalty-review records."""

from __future__ import annotations

import hashlib
import json

import pytest

from royaltybook.config import load_statement
from royaltybook.report import document, write_bundle
from royaltybook.service import calculate
from tests.helpers import write_plan


def test_document_keeps_payment_review_explicitly_unverified(tmp_path):
    assessment = calculate(load_statement(write_plan(tmp_path)))
    payload = document(assessment)

    assert payload["status"] == "calculation_ready_for_human_review"
    assert payload["payment_review_status"] == "unverified"
    assert payload["payouts"][0]["payment_status"] == "UNVERIFIED"


def test_build_writes_hashed_review_packet_without_overwriting(tmp_path):
    plan_path = write_plan(tmp_path)
    assessment = calculate(load_statement(plan_path))
    bundle = write_bundle(assessment, tmp_path / "packet")

    manifest = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))
    assert {item["path"] for item in manifest["generated_files"]} == {
        "PAYMENT_REVIEW.md",
        "ROYALTY_STATEMENT.md",
        "payouts.csv",
        "statement.json",
    }
    for item in manifest["generated_files"]:
        artifact = bundle.output_path / item["path"]
        assert artifact.stat().st_size == item["bytes"]
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == item["sha256"]
    assert "UNVERIFIED" in bundle.payment_review_path.read_text(encoding="utf-8")

    with pytest.raises(FileExistsError, match="already exists"):
        write_bundle(assessment, bundle.output_path)
