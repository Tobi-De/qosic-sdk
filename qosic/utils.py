from __future__ import annotations

import re
import secrets
from enum import Enum
from logging import Logger
from string import ascii_letters, digits
from typing import TYPE_CHECKING

import httpx
from dataclasses import dataclass

from .errors import ProviderNotFoundError, InvalidPhoneNumberError

if TYPE_CHECKING:
    from .protocols import Provider


def log_request(request: httpx.Request, /, *, logger: Logger):
    logger.info(f"REQUEST: {request.method} {request.url} - Waiting for response")
    logger.info(request.read())


def log_response(response: httpx.Response, /, *, logger: Logger):
    request = response.request
    logger.info(
        f"RESPONSE: {request.method} {request.url} - Status {response.status_code}"
    )
    logger.info(f"{response.read()}")


def get_random_string(length: int = 12) -> str:
    return "".join(secrets.choice(ascii_letters + digits) for _ in range(length))


def provider_by_phone(*, phone: str, providers: list[Provider]) -> Provider:
    prefix = phone[3:5]
    for provider in providers:
        if prefix in provider.allowed_prefixes:
            return provider
    raise ProviderNotFoundError(
        f"A provider was not found for the given phone number: {phone}"
    )


@dataclass(frozen=True)
class Result:
    """A helper class to summarize the responses from the server."""

    class Status(str, Enum):
        CONFIRMED = "CONFIRMED"
        FAILED = "FAILED"

    status: Status
    reference: str
    provider: Provider
    response: httpx.Response

    @property
    def success(self) -> bool:
        return self.status == self.Status.CONFIRMED


@dataclass(frozen=True)
class Payer:
    phone: str
    amount: int
    first_name: str
    last_name: str

    def __post_init__(self):
        if not re.fullmatch(r"[0-9]{11}", self.phone):
            raise InvalidPhoneNumberError(
                f"Invalid format for {self.phone}, ex: 229XXXXXXXX"
            )
