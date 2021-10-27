"""Main module."""
import json.decoder
from typing import List

import httpx
import polling2
from phonenumbers import PhoneNumber
from pydantic import BaseModel, HttpUrl, PrivateAttr, validate_arguments, conint

from .exceptions import (
    UserAccountNotFound,
    InvalidCredentialsError,
    RequestError,
    ServerError,
    InvalidClientIdError,
)
from .helpers import (
    guess_provider,
    get_json_response,
)
from .models import (
    Provider,
    Result,
    MTN,
    MOOV,
    MtnConfig,
    OPERATION_REJECTED,
    OPERATION_CONFIRMED,
)


class Client(BaseModel):
    """The synchronous client that will be used to make the request to the QosIc api.
    :param providers: The list of your provider.
    :param login: Your server authentication login/user.
    :param password: Your server authentication password.
    :param context: The QosIC server root domain if you ever need to change it.
    """

    providers: List[Provider]
    login: str
    password: str
    context: HttpUrl = "https://qosic.net:8443"
    _http_client: httpx.Client = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._http_client = httpx.Client(
            base_url=self.context,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            verify=False,
            timeout=80,
        )

    @validate_arguments
    def _send_request(self, path: str, payload: dict) -> httpx.Response:
        try:
            response = self._http_client.post(path, json=payload)
        except (json.decoder.JSONDecodeError, httpx.RequestError):
            raise RequestError(
                f"An error occurred while requesting {self.context + path}."
            )
        else:
            print(payload)
            print(response)
            if httpx.codes.is_server_error(value=response.status_code):
                raise ServerError(
                    f"The qos server seems to fail for some reason, you can set your"
                    f" client active_logging to true for more details, check your client auth "
                    f" informations, providers ClientID and try again."
                )
            elif response.status_code == httpx.codes.UNAUTHORIZED:
                raise InvalidCredentialsError("Your client credentials are invalid")
            elif response.status_code == httpx.codes.NOT_FOUND:
                raise InvalidClientIdError(
                    f"Your client Id is invalid : {payload['clientid']}"
                )
            elif response.status_code == httpx.codes.EXPECTATION_FAILED:
                raise UserAccountNotFound(
                    "A mobile money account was not found for the given phone number"
                )
        return response

    def _make_mtn_payment(self, payload: dict, provider: MTN) -> Result.State:
        response = self._send_request(path=provider.payment_path, payload=payload)

        if response.status_code == httpx.codes.ACCEPTED:
            config = provider.config if provider.config else MtnConfig()
            try:
                state = polling2.poll(
                    target=self._fetch_transaction_status,
                    check_success=polling2.is_value(OPERATION_CONFIRMED),
                    kwargs={
                        "trans_ref": payload["transref"],
                        "provider": provider,
                    },
                    **config.dict(),
                )
            except polling2.TimeoutException:
                state = OPERATION_REJECTED
        else:
            state = OPERATION_REJECTED
        return state

    def _fetch_transaction_status(self, trans_ref: str, provider: MTN) -> Result.State:
        response = self._send_request(
            path=provider.payment_status_path,
            payload={"clientid": provider.client_id, "transref": trans_ref},
        )

        json_content = get_json_response(response)

        if (
            response.status_code == httpx.codes.OK
            and json_content["responsecode"] == "00"
        ):
            state = OPERATION_CONFIRMED
        else:
            state = OPERATION_REJECTED
        return state

    def _make_moov_payment(self, payload: dict, provider: MOOV) -> Result.State:
        response = self._send_request(path=provider.payment_path, payload=payload)

        json_content = get_json_response(response)

        if (
            response.status_code == httpx.codes.OK
            and json_content["responsecode"] == "0"
        ):
            state = OPERATION_CONFIRMED
        else:
            state = OPERATION_REJECTED
        return state

    @validate_arguments(config={"arbitrary_types_allowed": True})
    def request_payment(
        self,
        phone: PhoneNumber,
        amount: conint(gt=0),
        first_name: str = None,
        last_name: str = None,
    ) -> Result:
        provider = guess_provider(phone=phone, providers=self.providers)
        payload = {
            "clientid": provider.client_id,
            "msisdn": f"229{phone.national_number}",
            "amount": str(amount),
            "transref": provider.transref_factory(),
        }
        if first_name:
            payload["firstname"] = first_name
        if last_name:
            payload["lastname"] = last_name

        payment_function = (
            self._make_mtn_payment
            if isinstance(provider, MTN)
            else self._make_moov_payment
        )
        state = payment_function(payload, provider)  # noqa
        return Result(
            client_id=provider.client_id,
            trans_ref=payload["transref"],
            state=state,
            phone=payload["msisdn"],
            amount=str(amount),
        )

    @validate_arguments(config={"arbitrary_types_allowed": True})
    def request_refund(self, trans_ref: str, phone: PhoneNumber) -> Result:
        provider = guess_provider(phone=phone, providers=self.providers)
        assert isinstance(provider, MTN), "Refund are available only MTN phone numbers"

        response = self._send_request(
            path=provider.refund_path,
            payload={"clientid": provider.client_id, "transref": trans_ref},
        )

        if response.status_code == httpx.codes.OK:
            state = OPERATION_CONFIRMED
        else:
            state = OPERATION_REJECTED
        return Result(client_id=provider.client_id, trans_ref=trans_ref, state=state)

    def __del__(self):
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()
