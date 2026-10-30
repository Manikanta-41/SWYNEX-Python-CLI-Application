"""Command-line interface: argument parsing, command handlers, top-level error handling."""
import argparse
import sys
from datetime import date
from pathlib import Path

from . import reports, storage, validators
from .exceptions import ExpenseTrackerError, ValidationError
from .models import Expense


def _arg(validator):
    """Adapt a validator so argparse reports ValidationError as a usage error."""
    def wrapper(value):
        try:
            return validator(value)
        except ValidationError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from None
    wrapper.__name__ = validator.__name__
    return wrapper


# ---------- command handlers ----------

def cmd_add(args) -> int:
    expenses = storage.load_expenses(args.file)
    expense = Expense(
        id=storage.next_id(expenses),
        amount=args.amount,
        category=args.category,
        description=args.description,
        date=args.date or date.today(),
    )
    expenses.append(expense)
    storage.save_expenses(expenses, args.file)
    print(f"Added expense #{expense.id}: {expense.amount:,.2f} on {expense.category} ({expense.date})")
    return 0


def cmd_list(args) -> int:
    expenses = storage.load_expenses(args.file)
    expenses = reports.filter_expenses(expenses, args.category, args.month)
    print(reports.format_table(reports.sort_expenses(expenses, args.sort)))
    return 0


def cmd_edit(args) -> int:
    changes = {k: v for k, v in
               {"amount": args.amount, "category": args.category,
                "description": args.description, "date": args.date}.items() if v is not None}
    if not changes:
        raise ValidationError("Nothing to edit: provide at least one of --amount, --category, --description, --date.")
    expenses = storage.load_expenses(args.file)
    expense = storage.find_expense(expenses, args.id)
    for field, value in changes.items():
        setattr(expense, field, value)
    storage.save_expenses(expenses, args.file)
    print(f"Updated expense #{expense.id}.")
    return 0


def cmd_delete(args) -> int:
    expenses = storage.load_expenses(args.file)
    expense = storage.find_expense(expenses, args.id)
    if not args.yes:
        try:
            answer = input(f"Delete #{expense.id} ({expense.description}, {expense.amount})? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return 0
    expenses.remove(expense)
    storage.save_expenses(expenses, args.file)
    print(f"Deleted expense #{expense.id}.")
    return 0


def cmd_summary(args) -> int:
    expenses = reports.filter_expenses(storage.load_expenses(args.file), month=args.month)
    if args.month:
        print(f"Summary for {args.month}\n")
    print(reports.format_summary(expenses))
    return 0


def cmd_export(args) -> int:
    expenses = reports.sort_expenses(storage.load_expenses(args.file))
    reports.export_csv(expenses, args.output)
    print(f"Exported {len(expenses)} expenses to {args.output}")
    return 0


# ---------- parser ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense_tracker", description="Track your expenses from the terminal.")
    parser.add_argument("--file", type=Path, default=storage.DEFAULT_PATH,
                        help=f"data file (default: {storage.DEFAULT_PATH})")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    p = sub.add_parser("add", help="add a new expense")
    p.add_argument("amount", type=_arg(validators.validate_amount))
    p.add_argument("category", type=_arg(validators.validate_category))
    p.add_argument("description", type=_arg(validators.validate_description))
    p.add_argument("--date", type=_arg(validators.validate_date), help="YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="list expenses")
    p.add_argument("--category", type=_arg(validators.validate_category))
    p.add_argument("--month", type=_arg(validators.validate_month), help="YYYY-MM")
    p.add_argument("--sort", choices=["date", "amount"], default="date")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("edit", help="edit an existing expense")
    p.add_argument("id", type=_arg(validators.validate_id))
    p.add_argument("--amount", type=_arg(validators.validate_amount))
    p.add_argument("--category", type=_arg(validators.validate_category))
    p.add_argument("--description", type=_arg(validators.validate_description))
    p.add_argument("--date", type=_arg(validators.validate_date))
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("delete", help="delete an expense")
    p.add_argument("id", type=_arg(validators.validate_id))
    p.add_argument("-y", "--yes", action="store_true", help="skip confirmation")
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("summary", help="totals by category")
    p.add_argument("--month", type=_arg(validators.validate_month), help="YYYY-MM")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("export", help="export all expenses to CSV")
    p.add_argument("output", type=Path, help="destination .csv file")
    p.set_defaults(func=cmd_export)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ExpenseTrackerError as exc:          # expected, user-facing errors
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as exc:                    # last-resort safety net
        print(f"Unexpected error: {exc!r}", file=sys.stderr)
        return 2
