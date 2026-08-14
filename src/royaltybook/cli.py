"""Command-line entry point for local declared Royaltybook calculations."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from royaltybook.config import ConfigError, StatementPlan, load_statement
from royaltybook.report import document, write_bundle
from royaltybook.service import CalculationError, StatementAssessment, calculate


def build_parser() -> argparse.ArgumentParser:
    """Create the small explicit CLI surface for read-only checking and new packet generation."""

    parser = argparse.ArgumentParser(
        prog="royaltybook",
        description="Calculate declared royalty arithmetic and local payment-review records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "build"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("plan", type=Path, help="Declared TOML royalty statement")
        subparser.add_argument(
            "--json", action="store_true", help="Print machine-readable calculation"
        )
        if command == "build":
            subparser.add_argument(
                "--output", required=True, type=Path, help="New local output directory"
            )
    return parser


def concise_text(plan: StatementPlan, assessment: StatementAssessment) -> str:
    """Render a short result that separates arithmetic from real-world proof."""

    return "\n".join(
        [
            f"Statement: {plan.statement.title}",
            "Calculation state: READY FOR HUMAN REVIEW",
            f"Declared distributable cents: {assessment.distributable_cents}",
            "Payment review status: UNVERIFIED",
            (
                "Royaltybook does not validate agreements, terms, receipts, deductions, tax, "
                "currency treatment, payment, or payment evidence."
            ),
        ]
    )


def run(plan_path: Path) -> tuple[StatementPlan, StatementAssessment]:
    """Load and calculate one declaration without contacting any outside system."""

    plan = load_statement(plan_path)
    return plan, calculate(plan)


def main(argv: Sequence[str] | None = None) -> int:
    """Run local statement validation or create one new review packet."""

    args = build_parser().parse_args(argv)
    try:
        plan, assessment = run(args.plan)
        if args.command == "build":
            bundle = write_bundle(assessment, args.output)
            payload = document(assessment)
            payload["output_directory"] = str(bundle.output_path)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"Wrote local royalty-review packet: {bundle.output_path}")
                print(concise_text(plan, assessment))
        elif args.json:
            print(json.dumps(document(assessment), indent=2, sort_keys=True))
        else:
            print(concise_text(plan, assessment))
        return 0
    except (CalculationError, ConfigError, FileExistsError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
