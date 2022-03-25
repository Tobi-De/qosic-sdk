from __future__ import annotations

from dataclasses import dataclass

import httpx
import polling2
from phonenumbers import PhoneNumber

from .constants import (
    MTN_PREFIXES,
    MOOV_PREFIXES,
    MTN_PAYMENT_STATUS_PATH,
    MTN_PAYMENT_PATH,
    MTN_REFUND_PATH,
    MOOV_PAYMENT_PATH,
)
from .utils import get_random_string, Result, get_json_response


# try:
#     response = self._http_client.post(path, json=payload)
# except (json.decoder.JSONDecodeError, httpx.RequestError):
#     raise RequestError(
#         f"An error occurred while requesting {self.context + path}."
#     )
# else:
#     if httpx.codes.is_server_error(value=response.status_code):
#         raise ServerError(
#             f"The qos server seems to fail for some reason, you can set your"
#             f" client active_logging to true for more details, check your client auth "
#             f" informations, providers ClientID and try again."
#         )
#     elif response.status_code == httpx.codes.UNAUTHORIZED:
#         raise InvalidCredentialsError("Your client credentials are invalid")
#     elif response.status_code == httpx.codes.NOT_FOUND:
#         raise InvalidClientIdError(
#             f"Your client Id is invalid : {payload['clientid']}"
#         )
#     elif response.status_code == httpx.codes.EXPECTATION_FAILED:
#         raise UserAccountNotFound(
#             "A mobile money account was not found for the given phone number"
#         )
# return response


def _validate_reference_factory(func: callable) -> None:
    ref = func()
    assert isinstance(ref, str), "Your factory function should return strings"
    assert len(ref) > 6, "Your factory function generate too short strings"
    assert len(ref) <= 16, "Your factory function generate too long strings"


@dataclass
class MTN:
    client_id: str
    step: int = 30
    timeout: int = 60 * 2
    max_tries: int | None = None
    allowed_prefixes: list[str] = MTN_PREFIXES
    refund_path: str = MTN_REFUND_PATH
    payment_path: str = MTN_PAYMENT_PATH
    payment_status_path: str = MTN_PAYMENT_STATUS_PATH
    reference_factory: callable = get_random_string

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)
        assert 10 <= self.step >= 90, "Step must be between 10 and 90"
        assert 60 <= self.timeout >= 60 * 5, "Timeout must be between 60 and 60 * 5"
        assert (
            self.max_tries * self.step <= self.timeout
        ), f"max_tries exceed timeout: {self.max_tries} * {self.step} > {self.timeout}"
        assert (
            self.step < self.timeout
        ), f"Your step must be inferior to your timeout: {self.step} >= {self.timeout}"

    def pay(
        self,
        client: httpx.Client,
        *,
        phone: PhoneNumber,
        amount: int,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Result:
        data = {
            "clientid": self.client_id,
            "msisdn": f"229{phone.national_number}",
            "amount": str(amount),
            "transref": self.reference_factory(),
            "firstname": first_name,
            "lastname": last_name,
        }
        response = client.post(url=self.payment_path, data=data)

        if response.status_code == httpx.codes.ACCEPTED:
            try:
                status = polling2.poll(
                    target=self._check_status,
                    check_success=polling2.is_value(Result.Status.CONFIRMED),
                    step=self.step,
                    timeout=self.timeout,
                    max_tries=self.max_tries,
                    args=[self],
                    kwargs={"reference": data["transref"], "client": client},
                )
            except polling2.TimeoutException:
                status = Result.Status.FAILED
        else:
            status = Result.Status.FAILED
        error = ""
        return Result(
            reference=data["transref"],
            client_id=self.client_id,
            status=status,
            error=error,
        )

    def _check_status(self, *, client: httpx.Client, reference: str) -> Result.Status:
        response = client.post(
            url=self.payment_status_path,
            data={"clientid": self.client_id, "transref": reference},
        )
        json_content = get_json_response(response)
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
            url=self.refund_path,
            data={"clientid": self.client_id, "transref": reference},
        )

        if response.status_code == httpx.codes.OK:
            status = Result.Status.CONFIRMED
            error = None
        else:
            status = Result.Status.FAILED
            error = ""
        return Result(
            reference=reference,
            client_id=self.client_id,
            status=status,
            error=error,
        )


@dataclass
class MOOV:
    client_id: str
    allowed_prefixes: list[str] = MOOV_PREFIXES
    payment_path: str = MOOV_PAYMENT_PATH
    reference_factory: callable = get_random_string

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)

    def pay(
        self,
        client: httpx.Client,
        *,
        phone: PhoneNumber,
        amount: int,
        first_name: str,
        last_name: str,
    ) -> Result:
        data = {
            "clientid": self.client_id,
            "msisdn": f"229{phone.national_number}",
            "amount": str(amount),
            "transref": self.get_reference(),
            "firstname": first_name,
            "lastname": last_name,
        }
        response = client.post(url=self.payment_path, data=data)
        json_content = get_json_response(response)
        if (
            response.status_code == httpx.codes.OK
            and json_content["responsecode"] == "0"
        ):
            status = Result.Status.CONFIRMED
        else:
            status = Result.Status.FAILED
        error = ""
        return Result(
            reference=data["transref"],
            client_id=self.client_id,
            status=status,
            error=error,
        )

    def refund(self, client: httpx.Client, *, reference: str) -> Result:
        raise NotImplementedError()
