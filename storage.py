"""JSON-file persistence with safe (atomic) writes."""
import json
import os
import tempfile
from decimal import InvalidOperation
from pathlib import Path

from .exceptions import ExpenseNotFoundError, StorageError
from .models import Expense

DEFAULT_PATH = Path(os.environ.get("EXPENSE_FILE", Path.home() / ".expense_tracker.json"))


def load_expenses(path: Path = DEFAULT_PATH) -> list[Expense]:
    """Return all saved expenses; an absent file means an empty list."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        raise StorageError(f"Data file {path} is corrupted: {exc}") from exc
    except OSError as exc:
        raise StorageError(f"Cannot read {path}: {exc.strerror}") from exc

    if not isinstance(raw, list):
        raise StorageError(f"Data file {path} has an unexpected format.")
    try:
        return [Expense.from_dict(item) for item in raw]
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise StorageError(f"Data file {path} contains an invalid record: {exc!r}") from exc


def save_expenses(expenses: list[Expense], path: Path = DEFAULT_PATH) -> None:
    """Write to a temp file then rename, so a crash can't corrupt existing data."""
    tmp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in expenses], f, indent=2)
        os.replace(tmp_name, path)
    except OSError as exc:
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise StorageError(f"Cannot write {path}: {exc.strerror}") from exc


def next_id(expenses: list[Expense]) -> int:
    return max((e.id for e in expenses), default=0) + 1


def find_expense(expenses: list[Expense], expense_id: int) -> Expense:
    for expense in expenses:
        if expense.id == expense_id:
            return expense
    raise ExpenseNotFoundError(f"No expense found with ID {expense_id}.")
