"""Custom exceptions so callers can handle each failure type precisely."""


class ExpenseTrackerError(Exception):
    """Base class for all application errors."""


class ValidationError(ExpenseTrackerError):
    """User input failed validation."""


class StorageError(ExpenseTrackerError):
    """The data file could not be read, parsed, or written."""


class ExpenseNotFoundError(ExpenseTrackerError):
    """No expense exists with the requested ID."""
