"""Strict TOML parsing for declared Royaltybook statements."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a declared royalty statement is structurally invalid."""


IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CURRENCY = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True)
class Statement:
    """Human-declared context for one internal royalty calculation."""

    title: str
    period: str
    currency: str
    requirements_basis: str


@dataclass(frozen=True)
class Recipient:
    """A declared recipient and its stated share of the distributable pool."""

    id: str
    name: str
    share_basis_points: int


@dataclass(frozen=True)
class IncomeLine:
    """One declared receipt line recorded in integer cents."""

    id: str
    source: str
    category: str
    amount_cents: int
    note: str


@dataclass(frozen=True)
class DeductionLine:
    """One declared pre-split deduction recorded in integer cents."""

    id: str
    description: str
    amount_cents: int
    note: str


@dataclass(frozen=True)
class StatementPlan:
    """A fully parsed local declaration; it is not proof of contractual terms or payments."""

    source_path: Path
    statement: Statement
    recipients: tuple[Recipient, ...]
    income: tuple[IncomeLine, ...]
    deductions: tuple[DeductionLine, ...]


def unexpected_fields(table: dict[str, Any], allowed: set[str], context: str) -> None:
    """Reject fields outside the compact, reviewable statement schema."""

    unknown = sorted(set(table) - allowed)
    if unknown:
        joined = ", ".join(unknown)
        raise ConfigError(f"unexpected {context} field(s): {joined}")


def require_table(value: object, context: str) -> dict[str, Any]:
    """Return a TOML table after making a precise type error readable to a human."""

    if not isinstance(value, dict):
        raise ConfigError(f"{context} must be a TOML table")
    return value


def require_list(value: object, context: str) -> list[object]:
    """Return a nonempty TOML array while preventing accidental table/string coercion."""

    if not isinstance(value, list) or not value:
        raise ConfigError(f"{context} must be a nonempty TOML array")
    return value


def require_text(table: dict[str, Any], key: str, context: str) -> str:
    """Read one required nonblank declared text value."""

    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{context}.{key} must be a nonblank string")
    return value.strip()


def require_cents(table: dict[str, Any], key: str, context: str) -> int:
    """Read a positive integer-cent amount without accepting boolean coercion."""

    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{context}.{key} must be a positive integer number of cents")
    return value


def require_basis_points(table: dict[str, Any], context: str) -> int:
    """Read one positive recipient share in the fixed 10,000-point allocation scale."""

    value = table.get("share_basis_points")
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= 10_000:
        raise ConfigError(f"{context}.share_basis_points must be an integer from 1 to 10,000")
    return value


def require_identifier(table: dict[str, Any], context: str) -> str:
    """Read a stable lowercase identifier used for deterministic arithmetic and documents."""

    value = require_text(table, "id", context)
    if not IDENTIFIER.fullmatch(value):
        raise ConfigError(f"{context}.id must use lowercase kebab-case")
    return value


def parse_statement(value: object) -> Statement:
    """Parse declared statement context without assessing its factual accuracy."""

    table = require_table(value, "statement")
    unexpected_fields(table, {"title", "period", "currency", "requirements_basis"}, "statement")
    currency = require_text(table, "currency", "statement")
    if not CURRENCY.fullmatch(currency):
        raise ConfigError("statement.currency must be a three-letter uppercase declared code")
    return Statement(
        title=require_text(table, "title", "statement"),
        period=require_text(table, "period", "statement"),
        currency=currency,
        requirements_basis=require_text(table, "requirements_basis", "statement"),
    )


def parse_recipients(value: object) -> tuple[Recipient, ...]:
    """Parse recipients and require their declared shares to total exactly 10,000 basis points."""

    recipients: list[Recipient] = []
    seen: set[str] = set()
    for index, raw in enumerate(require_list(value, "recipients"), start=1):
        context = f"recipients[{index}]"
        table = require_table(raw, context)
        unexpected_fields(table, {"id", "name", "share_basis_points"}, context)
        identifier = require_identifier(table, context)
        normalized = identifier.casefold()
        if normalized in seen:
            raise ConfigError(f"duplicate recipient id: {identifier}")
        seen.add(normalized)
        recipients.append(
            Recipient(
                id=identifier,
                name=require_text(table, "name", context),
                share_basis_points=require_basis_points(table, context),
            )
        )
    total = sum(recipient.share_basis_points for recipient in recipients)
    if total != 10_000:
        raise ConfigError(f"recipient shares must total exactly 10,000 basis points, not {total}")
    return tuple(recipients)


def parse_income(value: object) -> tuple[IncomeLine, ...]:
    """Parse nonnegative-proof-free declared income lines expressed only as integer cents."""

    lines: list[IncomeLine] = []
    seen: set[str] = set()
    for index, raw in enumerate(require_list(value, "income"), start=1):
        context = f"income[{index}]"
        table = require_table(raw, context)
        unexpected_fields(table, {"id", "source", "category", "amount_cents", "note"}, context)
        identifier = require_identifier(table, context)
        if identifier.casefold() in seen:
            raise ConfigError(f"duplicate income id: {identifier}")
        seen.add(identifier.casefold())
        lines.append(
            IncomeLine(
                id=identifier,
                source=require_text(table, "source", context),
                category=require_text(table, "category", context),
                amount_cents=require_cents(table, "amount_cents", context),
                note=require_text(table, "note", context),
            )
        )
    return tuple(lines)


def parse_deductions(value: object) -> tuple[DeductionLine, ...]:
    """Parse declared pre-split deduction lines with stable IDs and integer-cent amounts."""

    if value is None:
        return ()
    if not isinstance(value, list):
        raise ConfigError("deductions must be a TOML array when supplied")
    lines: list[DeductionLine] = []
    seen: set[str] = set()
    for index, raw in enumerate(value, start=1):
        context = f"deductions[{index}]"
        table = require_table(raw, context)
        unexpected_fields(table, {"id", "description", "amount_cents", "note"}, context)
        identifier = require_identifier(table, context)
        if identifier.casefold() in seen:
            raise ConfigError(f"duplicate deduction id: {identifier}")
        seen.add(identifier.casefold())
        lines.append(
            DeductionLine(
                id=identifier,
                description=require_text(table, "description", context),
                amount_cents=require_cents(table, "amount_cents", context),
                note=require_text(table, "note", context),
            )
        )
    return tuple(lines)


def load_statement(path: Path) -> StatementPlan:
    """Load one TOML declaration and validate its schema plus internal share arithmetic."""

    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError(f"statement file does not exist: {path}") from error
    except OSError as error:
        raise ConfigError(f"could not read statement file: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML statement: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigError("statement root must be a TOML table")
    unexpected_fields(raw, {"statement", "recipients", "income", "deductions"}, "top-level")
    for required in ("statement", "recipients", "income"):
        if required not in raw:
            raise ConfigError(f"missing required top-level table or array: {required}")
    return StatementPlan(
        source_path=path.resolve(),
        statement=parse_statement(raw["statement"]),
        recipients=parse_recipients(raw["recipients"]),
        income=parse_income(raw["income"]),
        deductions=parse_deductions(raw.get("deductions")),
    )
