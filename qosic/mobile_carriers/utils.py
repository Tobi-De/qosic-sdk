from __future__ import annotations

import json

import httpx
from httpx import codes

from qosic.errors import (
    InvalidCredentialsError,
    InvalidProviderIDError,
    UserAccountNotFoundError,
    ServerError,
)
from qosic.protocols import MobileCarrier
from qosic.utils import Payer, get_random_string


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
    provider = kwargs.get("provider")
    if provider and codes.NOT_FOUND == status:
        raise InvalidProviderIDError(
            f"Your {provider.__class__.__name__} Id is invalid"
        )
    if codes.UNAUTHORIZED == status:
        raise InvalidCredentialsError("Your qosic credentials are invalid")
    payer = kwargs.get("payer")
    if payer and codes.EXPECTATION_FAILED == status:
        raise UserAccountNotFoundError(
            f"A mobile money account was not found for {payer.phone}"
        )


def _validate_reference_factory(func: callable) -> None:
    ref = func()
    assert isinstance(ref, str), "Your factory function should return strings"
    assert len(ref) > 6, "Your factory function generate too short strings"
    assert len(ref) <= 16, "Your factory function generate too long strings"


def _req_body_from_payer(provider: MobileCarrier, payer: Payer) -> dict:
    return {
        "clientid": provider.id,
        "msisdn": payer.phone,
        "amount": str(payer.amount),
        "transref": provider.reference_factory(payer),
        "firstname": payer.first_name or "",
        "lastname": payer.last_name or "",
    }


def _resp_is_ok(response: httpx.Response):
    return response.status_code == httpx.codes.OK
