"""Helpers functions that are used in main module"""

import json
import logging
import re
import time
from typing import List, Callable, Optional

from httpx import Response, Request

from .exceptions import (
    InvalidPhoneError,
    ProviderNotFoundError,
    PollRuntimeError,
)
from .models import Provider

logging.basicConfig(level=logging.DEBUG, format="%(message)s")


def log_request(request: Request):
    json_content = json.loads(request.content)
    logging.debug(
        f"Request: {request.method} {request.url} - Waiting for response\n"
        f"Content: \n {json.dumps(json_content, indent=2, sort_keys=True)}"
    )


def log_response(response: Response):
    request = response.request
    logging.debug(
        f"Response: {request.method} {request.url} - Status {response.status_code}\n"
        f"Content : \n {json.dumps(response.json(), indent=2, sort_keys=True)}"
    )


def guess_provider(phone: str, providers: List[Provider]) -> Provider:
    phone = clean_phone(phone)
    prefixe = phone[3:5]
    for provider in providers:
        if prefixe in provider.allowed_prefixes:
            return provider
    raise ProviderNotFoundError(
        f"A provider was not found for the given phone number: {phone}"
    )


def clean_phone(phone: str):
    if not re.fullmatch(r"(\+?)\d{11}", phone):
        raise InvalidPhoneError(
            f"Your phone number {phone} is invalid. Format : 229XXXXXXXX"
        )
    if "+" in phone:
        return phone[1:]
    return phone


def poll(
    target: Callable,
    step: int,
    timeout: int,
    max_tries: Optional[int] = None,
    kwargs: Optional[dict] = None,
    check_success: Callable = lambda val: bool(val),
):
    kwargs = kwargs or dict()
    max_time = time.time() + timeout
    tries = 0
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

        tries += 1

        # Check the max tries at this point so it will not sleep before returning
        if max_tries is not None and tries >= max_tries:
            return last_item

        # Check the time after to make sure the poll function is called at least once
        if time.time() >= max_time:
            return last_item

        time.sleep(step)
