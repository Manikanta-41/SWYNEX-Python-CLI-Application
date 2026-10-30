# Expense Tracker CLI

A command-line expense tracker in pure Python 3.9+ (no dependencies).

## Usage (run from this folder)

```
python -m expense_tracker add 12.50 food "Lunch at cafe"
python -m expense_tracker add 40 transport "Metro pass" --date 2026-10-01
python -m expense_tracker list --month 2026-10 --sort amount
python -m expense_tracker edit 1 --amount 14.00
python -m expense_tracker summary
python -m expense_tracker delete 2 --yes
python -m expense_tracker export out.csv
```

Data is stored in `~/.expense_tracker.json`. Override with `--file path.json`
or the `EXPENSE_FILE` environment variable.

## Layout

| Module | Responsibility |
|---|---|
| `validators.py` | Input validation (amount, date, category, ...) |
| `exceptions.py` | Custom exception hierarchy |
| `models.py` | `Expense` dataclass + (de)serialisation |
| `storage.py` | JSON persistence with atomic writes |
| `reports.py` | Filtering, sorting, summaries, CSV export |
| `cli.py` | argparse commands and top-level error handling |
# SWYNEX-Python-CLI-Application
