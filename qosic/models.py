import secrets
from abc import ABC
from enum import Enum
from string import ascii_letters, digits
from typing import Optional, List, Callable

from pydantic import BaseModel, root_validator, conint, PrivateAttr, validator

from .constants import (
    MTN_PAYMENT_PATH,
    MTN_PAYMENT_STATUS_PATH,
    MTN_PREFIXES,
    MOOV_PREFIXES,
    MOOV_PAYMENT_PATH,
    REFUND_PATH,
)

ALLOWED_STRING_CHARS = ascii_letters + digits


def get_random_string(
    length: int = 12,
    allowed_chars: str = ALLOWED_STRING_CHARS,
) -> str:
    return "".join(secrets.choice(allowed_chars) for _ in range(length))


class Provider(BaseModel, ABC):
    """Abstract base class for providers supportted by the QosIC platform, you can check
    their docs at https://www.qosic.com/docs/. For now only two providers are supported,
    MTN and MOOV.
    :param client_id: Your client Id, check on your QosIc account.
    :param transref_factory: A custom factory function to generate transfer references
    :param allowed_prefixes: list of phone number prefixes allowed
    """

    client_id: str
    transref_factory: Callable = get_random_string
    allowed_prefixes: List[str]
    _payment_path: str = PrivateAttr()

    @property
    def payment_path(self):
        return self._payment_path

    @validator("transref_factory")
    def valid_ref_factory(cls, func):
        ref = func()
        assert isinstance(ref, str), "Your factory function should return strings"
        assert len(ref) > 6, "Your factory function generate too short strings"
        assert len(ref) <= 16, "Your factory function generate too long strings"
        return func


class MtnConfig(BaseModel):
    step: conint(ge=10, le=90) = 30
    timeout: conint(ge=60, le=60 * 5) = 60 * 2
    max_tries: Optional[int]

    @root_validator
    def validate_config(cls, data):
        step, timeout, max_tries = data.values()
        if max_tries:
            assert (
                max_tries * step <= timeout
            ), f"max_tries exceed timeout: {max_tries} * {step} > {timeout}"
        assert (
            step < timeout
        ), f"Your step must be inferior to your timeout: {step} >= {timeout}"
        return data


class MTN(Provider):
    config: Optional[MtnConfig]
    allowed_prefixes: List[str] = MTN_PREFIXES
    _refund_path: Optional[str] = PrivateAttr()
    _payment_status_path: Optional[str] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._refund_path = REFUND_PATH
        self._payment_path = MTN_PAYMENT_PATH
        self._payment_status_path = MTN_PAYMENT_STATUS_PATH

    @property
    def refund_path(self):
        return self._refund_path

    @property
    def payment_status_path(self):
        return self._payment_status_path


class MOOV(Provider):
    allowed_prefixes: List[str] = MOOV_PREFIXES

    def __init__(self, **data):
        super().__init__(**data)
        self._payment_path = MOOV_PAYMENT_PATH


class Result(BaseModel):
    """A helper class to summarize the responses from the server."""

    class State(Enum):
        """A helper class that represents the state of your payment request."""

        CONFIRMED = 1, "Operation was successful"
        REJECTED = 0, "Operation was rejected"

        def __str__(self):
            return f"{self.name}: {self.value[1]}"

        def __bool__(self):
            return bool(self.value[0])

    state: State
    trans_ref: str
    client_id: str
    phone: str = None
    amount: str = None


OPERATION_CONFIRMED = Result.State.CONFIRMED
OPERATION_REJECTED = Result.State.REJECTED
