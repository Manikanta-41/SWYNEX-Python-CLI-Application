"""Input validation. Every function returns a clean value or raises ValidationError."""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError

MAX_AMOUNT = Decimal("1000000")
MAX_CATEGORY_LEN = 30
MAX_DESCRIPTION_LEN = 100
_CATEGORY_RE = re.compile(r"^[A-Za-z][A-Za-z &\-]*$")


def validate_amount(value) -> Decimal:
    """Positive number, at most 2 decimal places, up to MAX_AMOUNT."""
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValidationError(f"Amount '{value}' is not a valid number.") from None
    if not amount.is_finite():
        raise ValidationError("Amount must be a finite number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if amount != amount.quantize(Decimal("0.01")):
        raise ValidationError("Amount can have at most 2 decimal places.")
    if amount > MAX_AMOUNT:
        raise ValidationError(f"Amount cannot exceed {MAX_AMOUNT}.")
    return amount.quantize(Decimal("0.01"))


def validate_date(value) -> date:
    """Date in YYYY-MM-DD format that is not in the future."""
    try:
        parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(f"Date '{value}' must be a real date in YYYY-MM-DD format.") from None
    if parsed > date.today():
        raise ValidationError("Date cannot be in the future.")
    return parsed


def validate_category(value) -> str:
    """Letters, spaces, '&' and '-' only; normalised to Title Case."""
    category = " ".join(str(value).split())
    if not category:
        raise ValidationError("Category cannot be empty.")
    if len(category) > MAX_CATEGORY_LEN:
        raise ValidationError(f"Category must be at most {MAX_CATEGORY_LEN} characters.")
    if not _CATEGORY_RE.match(category):
        raise ValidationError("Category may only contain letters, spaces, '&' and '-'.")
    return category.title()


def validate_description(value) -> str:
    description = " ".join(str(value).split())
    if not description:
        raise ValidationError("Description cannot be empty.")
    if len(description) > MAX_DESCRIPTION_LEN:
        raise ValidationError(f"Description must be at most {MAX_DESCRIPTION_LEN} characters.")
    return description


def validate_month(value) -> str:
    """Month filter in YYYY-MM format."""
    text = str(value).strip()
    try:
        datetime.strptime(text, "%Y-%m")
    except ValueError:
        raise ValidationError(f"Month '{value}' must be in YYYY-MM format.") from None
    return text


def validate_id(value) -> int:
    try:
        expense_id = int(str(value).strip())
    except ValueError:
        raise ValidationError(f"ID '{value}' must be a whole number.") from None
    if expense_id < 1:
        raise ValidationError("ID must be a positive number.")
    return expense_id
