"""Filtering, summarising, formatting and CSV export."""
import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from .exceptions import StorageError
from .models import Expense


def filter_expenses(expenses, category=None, month=None):
    result = expenses
    if category:
        result = [e for e in result if e.category.lower() == category.lower()]
    if month:
        result = [e for e in result if e.date.strftime("%Y-%m") == month]
    return result


def sort_expenses(expenses, key="date"):
    if key == "amount":
        return sorted(expenses, key=lambda e: e.amount, reverse=True)
    return sorted(expenses, key=lambda e: (e.date, e.id))


def total(expenses) -> Decimal:
    return sum((e.amount for e in expenses), Decimal("0.00"))


def totals_by_category(expenses) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for e in expenses:
        totals[e.category] += e.amount
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def format_table(expenses) -> str:
    if not expenses:
        return "No expenses found."
    header = f"{'ID':>4}  {'Date':<10}  {'Category':<14}  {'Amount':>10}  Description"
    lines = [header, "-" * len(header)]
    for e in expenses:
        lines.append(
            f"{e.id:>4}  {e.date.isoformat():<10}  {e.category[:14]:<14}  "
            f"{e.amount:>10,.2f}  {e.description}"
        )
    lines.append("-" * len(header))
    lines.append(f"{'Total':>32}  {total(expenses):>10,.2f}")
    return "\n".join(lines)


def format_summary(expenses) -> str:
    if not expenses:
        return "No expenses found."
    grand = total(expenses)
    lines = [f"{'Category':<16} {'Total':>12}  {'Share':>6}", "-" * 40]
    for category, amount in totals_by_category(expenses).items():
        share = amount / grand * 100
        bar = "#" * int(share // 5)
        lines.append(f"{category[:16]:<16} {amount:>12,.2f}  {share:>5.1f}%  {bar}")
    lines.append("-" * 40)
    lines.append(f"{'TOTAL':<16} {grand:>12,.2f}   ({len(expenses)} expenses)")
    return "\n".join(lines)


def export_csv(expenses, path: Path) -> None:
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "category", "amount", "description"])
            for e in expenses:
                writer.writerow([e.id, e.date.isoformat(), e.category, e.amount, e.description])
    except OSError as exc:
        raise StorageError(f"Cannot write {path}: {exc.strerror}") from exc
