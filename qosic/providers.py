from __future__ import annotations

import json

import httpx
import polling2
from dataclasses import dataclass, field
from httpx import codes

from . import config
from .errors import (
    InvalidCredentialsError,
    InvalidProviderIDError,
    UserAccountNotFoundError,
)
from .protocols import Provider
from .utils import Result, Payer, get_random_string


def _generic_reference_factory(*args, **kwargs) -> str:
    return get_random_string()


def _extract_json(response: httpx.Response):
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        return {"responsecode": None}


def _handle_errors(status_code: int, provider: Provider, payer: Payer):
    provider_name = provider.__class__.__name__
    errors = {
        codes.UNAUTHORIZED: InvalidCredentialsError(
            f"Your qosic credentials are invalid"
        ),
        codes.NOT_FOUND: InvalidProviderIDError(
            f"Your {provider_name} client Id is invalid"
        ),
        codes.EXPECTATION_FAILED: UserAccountNotFoundError(
            f"A mobile money account was not found for {payer.phone}"
        ),
    }
    error = errors.get(status_code, None)  # noqa
    if error:
        raise error


def _validate_reference_factory(func: callable) -> None:
    ref = func()
    assert isinstance(ref, str), "Your factory function should return strings"
    assert len(ref) > 6, "Your factory function generate too short strings"
    assert len(ref) <= 16, "Your factory function generate too long strings"


def _req_body_from_payer(provider: Provider, payer: Payer) -> dict:
    return {
        "clientid": provider.id,
        "msisdn": payer.phone,
        "amount": str(payer.amount),
        "transref": provider.reference_factory(payer),
        "firstname": payer.first_name,
        "lastname": payer.last_name,
    }


@dataclass(frozen=True)
class MTN:
    id: str
    step: int = 30
    timeout: int = 60 * 2
    max_tries: int | None = None
    allowed_prefixes: list[str] = field(default_factory=lambda: config.MTN_PREFIXES)
    reference_factory: callable = _generic_reference_factory

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)
        assert 10 <= self.step <= 90, f"Step ({self.step}) must be between 10 and 90"
        assert (
            60 <= self.timeout <= 60 * 5
        ), f"Timeout ({self.step}) must be between 60 and 60 * 5"
        assert (
            self.step < self.timeout
        ), f"Your step must be inferior to your timeout: {self.step} >= {self.timeout}"
        if self.max_tries:
            assert (
                self.max_tries * self.step <= self.timeout
            ), f"max_tries exceed timeout: {self.max_tries} * {self.step} > {self.timeout}"

    def pay(self, client: httpx.Client, *, payer: Payer) -> Result:
        body = _req_body_from_payer(self, payer)
        response = client.post(url=config.MTN_PAYMENT_PATH, json=body)
        _handle_errors(response.status_code, provider=self, payer=payer)
        if response.status_code == httpx.codes.ACCEPTED:
            try:
                status = polling2.poll(
                    target=self._check_status,
                    check_success=polling2.is_value(Result.Status.CONFIRMED),
                    step=self.step,
                    timeout=self.timeout,
                    max_tries=self.max_tries,
                    kwargs={"reference": body["transref"], "client": client},
                )
            except polling2.TimeoutException:
                status = Result.Status.FAILED
        else:
            status = Result.Status.FAILED
        return Result(
            reference=body["transref"], provider=self, status=status, response=response
        )

    def _check_status(self, *, client: httpx.Client, reference: str) -> Result.Status:
        response = client.post(
            url=config.MTN_PAYMENT_STATUS_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        json_content = _extract_json(response)
        if (
            response.status_code == httpx.codes.OK
            and json_content["responsecode"] == "00"
        ):
            status = Result.Status.CONFIRMED
        else:
            status = Result.Status.FAILED
        return status

    def refund(self, client: httpx.Client, *, reference: str) -> Result:
        response = client.post(
            url=config.MTN_REFUND_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        if response.status_code == httpx.codes.OK:
            status = Result.Status.CONFIRMED
        else:
            status = Result.Status.FAILED
        return Result(
            reference=reference, provider=self, status=status, response=response
        )


@dataclass(frozen=True)
class MOOV:
    id: str
    allowed_prefixes: list[str] = field(default_factory=lambda: config.MOOV_PREFIXES)
    reference_factory: callable = _generic_reference_factory

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)

    def pay(self, client: httpx.Client, *, payer: Payer) -> Result:
        body = _req_body_from_payer(self, payer)
        response = client.post(url=config.MOOV_PAYMENT_PATH, json=body)
        json_content = _extract_json(response)
        if (
            response.status_code == httpx.codes.OK
            and json_content["responsecode"] == "0"
        ):
            status = Result.Status.CONFIRMED
        else:
            status = Result.Status.FAILED
        return Result(
            reference=body["transref"], provider=self, status=status, response=response
        )

    def refund(self, client: httpx.Client, *, reference: str) -> Result:
        raise NotImplementedError()
