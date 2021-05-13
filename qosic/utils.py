"""Utils that are used in models.py file"""

import secrets

ALLOWED_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_string(
    length: int = 12, allowed_chars: str = ALLOWED_STRING_CHARS, **kwargs
) -> str:
    return "".join(secrets.choice(allowed_chars) for _ in range(length))


def is_allowed_string(value: str) -> bool:
    for char in value:
        if char not in ALLOWED_STRING_CHARS:
            return False
    return True
