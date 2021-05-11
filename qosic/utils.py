import logging
import re
import secrets
import time
from typing import Callable, Union

from .exceptions import (
    InvalidPhoneNumberError,
    PollRuntimeError,
    PollTimeoutError,
    ProviderNotFoundError,
)

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


MTN_PREFIXES = ["97", "96", "66", "67", "61", "62", "69", "91", "90", "51"]
MOOV_PREFIXES = ["68", "98", "99", "95", "94", "60", "64", "63", "65"]

LOGGER = logging.getLogger(__name__)


def guess_provider(phone: str) -> str:
    phone = clean_phone(phone)
    prefixe = phone[3:5]
    if prefixe in MOOV_PREFIXES:
        return "MOOV"
    if prefixe in MTN_PREFIXES:
        return "MTN"
    raise ProviderNotFoundError(phone=phone)


def get_random_string(length: int = 8, allowed_chars: str = RANDOM_STRING_CHARS) -> str:
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def clean_phone(phone: str):
    if not re.fullmatch(r"(\+?)\d{11}", phone):
        raise InvalidPhoneNumberError
    if "+" in phone:
        return phone[1:]
    return phone


def poll(
    target: Callable,
    step: int,
    timeout: int,
    kwargs: Union[dict, None] = None,
    check_success: Callable = lambda val: bool(val),
):

    kwargs = kwargs or dict()
    values = list()

    max_time = time.time() + timeout
    last_item = None
    while True:
        try:
            val = target(**kwargs)
            last_item = val
        except Exception as e:
            raise PollRuntimeError(f"poll() catch an exception: {e}")
        else:
            # Condition passes, this is the only "successful" exit from the polling function
            if check_success(val):
                return val

        values.append(last_item)

        # Check the time after to make sure the poll function is called at least once
        if time.time() >= max_time:
            return last_item
            # raise PollTimeoutError(values)

        time.sleep(step)
