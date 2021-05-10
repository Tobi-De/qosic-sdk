import secrets
from .exceptions import InvalidProvider

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

MTN_PREFIXES = ["97", "96", "66", "67", "61", "62", "69", "91", "90", "51"]
MOOV_PREFIXES = ["68", "98", "99", "95", "94", "60", "64", "63", "65"]


def guess_provider(phone_number: str) -> str:
    phone_number = clean_phone_number(phone_number)
    # Ex: 22963588213
    prefixe = phone_number[3:5]
    if prefixe in MOOV_PREFIXES:
        return "MOOV"
    if prefixe in MTN_PREFIXES:
        return "MTN"
    raise InvalidProvider


def get_random_string(length: int = 8, allowed_chars: str = RANDOM_STRING_CHARS) -> str:
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def clean_phone_number(phone_number):
    pass
