"""Main module."""
import json.decoder
from typing import List

import httpx
from pydantic import BaseModel, HttpUrl, PrivateAttr, validate_arguments, constr, conint

from .exceptions import (
    UserAccountNotFound,
    InvalidCredentialsError,
    RequestError,
    ServerError,
    InvalidClientIdError,
)
from .helpers import (
    clean_phone,
    guess_provider,
    poll,
    log_request,
    log_response,
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
    :param active_logging: if set to True, the client will log every request and response
    """

    providers: List[Provider]
    login: str
    password: str
    context: HttpUrl = "https://qosic.net:8443"
    active_logging: bool = False
    _http_client: httpx.Client = PrivateAttr()
    _collected_responses: List[httpx.Response] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._http_client = httpx.Client(
            base_url=self.context,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            verify=False,
            timeout=80,
        )
        self._collected_responses = list()
        if self.active_logging:
            self._http_client.event_hooks = {
                "request": [log_request],
                "response": [log_response, self._update_responses],
            }

    @property
    def collected_responses(self):
        return self._collected_responses

    def _update_responses(self, r: httpx.Response):
        self._collected_responses.append(r)

    @validate_arguments
    def _send_request(self, path: str, payload: dict) -> httpx.Response:
        try:
            response = self._http_client.post(path, json=payload)
        except (json.decoder.JSONDecodeError, httpx.RequestError):
            raise RequestError(
                f"An error occurred while requesting {self.context + path}."
            )
        else:
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
        return response

    def _make_mtn_payment(self, payload: dict, provider: MTN) -> Result.State:
        response = self._send_request(path=provider.payment_path, payload=payload)

        if response.status_code == httpx.codes.ACCEPTED:
            config = provider.config if provider.config else MtnConfig()
            state = poll(
                target=self._fetch_transaction_status,
                kwargs={
                    "trans_ref": payload["transref"],
                    "provider": provider,
                },
                **config.dict(),
            )
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
        elif response.status_code == httpx.codes.EXPECTATION_FAILED:
            raise UserAccountNotFound(
                f"A mobile money account was not found for the given"
                f" phone - transref {trans_ref}"
            )
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

    @validate_arguments
    def request_payment(
        self,
        phone: constr(regex=r"(\+?)\d{11}", strip_whitespace=True),
        amount: conint(gt=0),
        first_name: str = None,
        last_name: str = None,
    ) -> Result:
        provider = guess_provider(phone=phone, providers=self.providers)
        payload = {
            "clientid": provider.client_id,
            "msisdn": clean_phone(phone),
            "amount": str(amount),
            "transref": provider.transref_factory(
                provider_name=self.__class__.__name__
            ),
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

    @validate_arguments
    def request_refund(
        self, trans_ref: str, phone: constr(regex=r"(\+?)\d{11}", strip_whitespace=True)
    ) -> Result:
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
