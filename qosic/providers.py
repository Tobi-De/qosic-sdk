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
    ServerError,
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


def _handle_common_errors(response: httpx.Response, **kwargs) -> None:
    status: int = response.status_code  # noqa
    if codes.is_server_error(status):
        raise ServerError(
            "Qosic server if failing for some reason, active debug for more details."
        )
    provider = kwargs.get("provider", None)
    if provider and codes.NOT_FOUND == status:
        raise InvalidProviderIDError(
            f"Your {provider.__class__.__name__} Id is invalid"
        )
    if codes.UNAUTHORIZED == status:
        raise InvalidCredentialsError("Your qosic credentials are invalid")
    payer = kwargs.get("payer", None)
    if payer and codes.EXPECTATION_FAILED == status:
        raise UserAccountNotFoundError(
            f"A mobile money account was not found for {payer.phone}"
        )


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


def _resp_is_ok(response: httpx.Response):
    return response.status_code == httpx.codes.OK


class MTNPaymentRejected(Exception):
    pass


@dataclass(frozen=True)
class MTN:
    id: str
    step: int = 10
    timeout: int = 60 * 2
    max_tries: int | None = None
    allowed_prefixes: list[str] = field(default_factory=lambda: config.MTN_PREFIXES)
    reference_factory: callable = _generic_reference_factory

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)
        assert 5 <= self.step <= 30, f"Step {self.step} must be between 5 and 30"
        assert (
            60 <= self.timeout <= 180
        ), f"Timeout {self.timeout}  must be between 60 and 180"
        if self.max_tries:
            assert (
                self.max_tries * self.step <= self.timeout
            ), f"max_tries exceed timeout: {self.max_tries} * {self.step} > {self.timeout}"

    def pay(self, client: httpx.Client, *, payer: Payer) -> Result:
        body = _req_body_from_payer(self, payer)
        response = client.post(url=config.MTN_PAYMENT_PATH, json=body)
        _handle_common_errors(response, provider=self, payer=payer)
        res_dict = {
            "reference": body["transref"],
            "provider": self,
            "status": Result.Status.FAILED,
            "response": response,
        }
        if response.status_code != httpx.codes.ACCEPTED:
            return Result(**res_dict)
        try:
            res_dict["status"] = polling2.poll(
                target=self._check_status,
                check_success=polling2.is_value(Result.Status.CONFIRMED),
                step=self.step,
                timeout=self.timeout,
                max_tries=self.max_tries,
                kwargs={"reference": body["transref"], "client": client},
            )
        except (polling2.TimeoutException, MTNPaymentRejected):
            pass
        return Result(**res_dict)

    def _check_status(self, *, client: httpx.Client, reference: str) -> Result.Status:
        response = client.post(
            url=config.MTN_PAYMENT_STATUS_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        json_content = _extract_json(response)
        if not _resp_is_ok(response) or json_content["responsecode"] is None:
            raise MTNPaymentRejected()
        if _resp_is_ok(response) and json_content["responsecode"] == "00":
            return Result.Status.CONFIRMED
        return Result.Status.FAILED

    def refund(self, client: httpx.Client, *, reference: str) -> Result:
        response = client.post(
            url=config.MTN_REFUND_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        _handle_common_errors(response, provider=self)
        ok = _resp_is_ok(response) and _extract_json(response)["responsecode"] == "00"
        status = Result.Status.CONFIRMED if ok else Result.Status.FAILED
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
        _handle_common_errors(response, provider=self, payer=payer)
        json_content = _extract_json(response)
        ok = _resp_is_ok(response) and json_content["responsecode"] == "0"
        status = Result.Status.CONFIRMED if ok else Result.Status.FAILED
        return Result(
            reference=body["transref"], provider=self, status=status, response=response
        )

    def refund(self, client: httpx.Client, *, reference: str) -> Result:
        raise NotImplementedError()
