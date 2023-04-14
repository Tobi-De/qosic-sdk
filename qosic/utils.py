from __future__ import annotations

import re
import secrets
from enum import Enum
from logging import Logger
from string import ascii_letters, digits
from typing import TYPE_CHECKING

import httpx
from dataclasses import dataclass

from .errors import MobileCarrierNotFoundError, InvalidPhoneNumberError

if TYPE_CHECKING:
    from .protocols import MobileCarrier


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


def guess_mobile_carrier_from(
    *, phone: str, mobile_carriers: list[MobileCarrier]
) -> MobileCarrier:
    prefix = phone[3:5]
    for carrier in mobile_carriers:
        if prefix in carrier.allowed_prefixes:
            return carrier
    raise MobileCarrierNotFoundError(
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
    phone: str
    mobile_carrier: MobileCarrier
    response: httpx.Response

    @property
    def success(self) -> bool:
        return self.status == self.Status.CONFIRMED


@dataclass(frozen=True)
class Payer:
    phone: str
    amount: int
    first_name: str | None = None
    last_name: str | None = None

    def __post_init__(self):
        if not re.fullmatch(r"\d{11}", self.phone):
            raise InvalidPhoneNumberError(
                f"Invalid format for {self.phone}, ex: 229XXXXXXXX"
            )
