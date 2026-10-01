import re

from ..errors import APIError

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def require_json(request):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError("Request body must be a JSON object.", 400, "invalid_json")
    return data


def required_string(data, field, max_length=255):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise APIError(f"{field} is required.", 400, "validation_error")
    value = value.strip()
    if len(value) > max_length:
        raise APIError(f"{field} must be at most {max_length} characters.", 400, "validation_error")
    return value


def validate_email(value):
    value = value.strip().lower()
    if len(value) > 255 or not EMAIL_RE.fullmatch(value):
        raise APIError("Enter a valid email address.", 400, "validation_error")
    return value


def validate_password(value):
    if not isinstance(value, str) or len(value) < 8 or len(value) > 128:
        raise APIError("Password must be between 8 and 128 characters.", 400, "validation_error")
    return value
