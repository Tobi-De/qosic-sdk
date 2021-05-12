"""Main module."""

from dataclasses import dataclass
from enum import Enum
from typing import List

import httpx

from .exceptions import (
    ProviderNotFoundError,
    InvalidCredentialsError,
    RequestError,
)
from .utils import clean_phone, get_random_string, guess_provider, poll

REFUND_PATH = "/QosicBridge/user/refund"
MTN_PAYMENT_PATH = "/QosicBridge/user/requestpayment"
MTN_PAYMENT_STATUS_PATH = "/QosicBridge/user/gettransactionstatus"
MOOV_PAYMENT_PATH = "/QosicBridge/user/requestpaymentmv"


class State(Enum):
    """A helper class that represents the state of your payment request."""

    CONFIRMED = 1, "Operation was successful"
    REJECTED = 0, "Operation was rejected"

    def __str__(self):
        return f"{self.name}: {self.value[1]}"

    def __bool__(self):
        return bool(self.value[0])


@dataclass
class Provider:
    """Represents a provider support by the QosIC platform, you can check
    their docs at https://www.qosic.com/docs/.For now only two providers are supported,
    MTN and MOOV.
    :param name: The name of the provider in capital letter
    :param client_id: Your client Id, check on your QosIc account.
    """

    name: str
    client_id: str


@dataclass
class Result:
    """A helper class to summarize the responses from the server."""

    state: State
    trans_ref: str
    client_id: str
    phone: str = None
    amount: str = None


@dataclass
class Client:
    """The synchronous client that will be used to make the request to the QosIc api.
    :param providers: The list of your provider.
    :param login: Your server authentication login/user.
    :param password: Your server authentication password.
    :param context: The QosIC server root domain if you ever need to change it.
    """

    providers: List[Provider]
    login: str
    password: str
    context: str = "https://qosic.net:8443"

    def request_payment(
        self, phone: str, amount: int, first_name: str = None, last_name: str = None
    ) -> Result:
        client_id = self.guess_client_id(phone=phone)
        payload = {
            "clientid": client_id,
            "msisdn": clean_phone(phone),
            "amount": str(amount),
            "transref": get_random_string(),
        }
        if first_name:
            payload["firstname"] = first_name
        if last_name:
            payload["lastname"] = last_name

        provider = guess_provider(phone)
        if provider == "MTN":
            state = self._make_mtn_payment(payload)
        else:
            state = self._make_moov_payment(payload)
        return Result(
            client_id=client_id,
            trans_ref=payload["transref"],
            state=state,
            phone=payload["msisdn"],
            amount=str(amount),
        )

    def refund(self, trans_ref: str, provider_name: str) -> Result:
        client_id = [p.name for p in self.providers if p.name == provider_name][0]
        if not client_id:
            raise ProviderNotFoundError

        url = self.context + REFUND_PATH
        response = self._send_request(
            url=url, payload={"clientid": client_id, "transref": trans_ref}
        )
        json_content = response.json()

        if response.status_code == 200 and json_content["responsecode"] == "00":
            state = State.CONFIRMED
        elif response.status_code == 401:
            raise InvalidCredentialsError
        elif response.status_code == 404:
            raise ProviderNotFoundError
        else:
            state = State.REJECTED
        return Result(client_id=client_id, trans_ref=trans_ref, state=state)

    def _send_request(self, url: str, payload: dict) -> httpx.Response:
        try:
            return httpx.post(
                url,
                auth=(self.login, self.password),
                headers={"content-type": "application/json"},
                json=payload,
                verify=False,
                timeout=80,
            )
        except httpx.RequestError as exc:
            raise RequestError(request=exc.request)

    def _make_mtn_payment(self, payload) -> State:
        url = self.context + MTN_PAYMENT_PATH
        response = self._send_request(url=url, payload=payload)
        json_content = response.json()

        if response.status_code == 202 and json_content["responsecode"] == "01":
            state = poll(
                target=self._fetch_transaction_status,
                step=30,
                timeout=60 * 2,
                kwargs={
                    "trans_ref": payload["transref"],
                    "client_id": payload["clientid"],
                },
            )
        elif response.status_code == 401:
            raise InvalidCredentialsError
        elif response.status_code == 404:
            raise ProviderNotFoundError(phone=payload["msisdn"])
        else:
            state = State.REJECTED
        return state

    def _fetch_transaction_status(self, trans_ref: str, client_id: str) -> State:
        url = self.context + MTN_PAYMENT_STATUS_PATH
        response = self._send_request(
            url=url, payload={"clientid": client_id, "transref": trans_ref}
        )
        json_content = response.json()

        if response.status_code == 200 and json_content["responsecode"] == "0":
            state = State.CONFIRMED
        elif response.status_code == 401:
            raise InvalidCredentialsError
        else:
            state = State.REJECTED
        return state

    def _make_moov_payment(self, payload: dict) -> State:
        url = self.context + MOOV_PAYMENT_PATH
        response = self._send_request(url=url, payload=payload)
        json_content = response.json()

        if response.status_code == 202 and json_content["responsecode"] == "0":
            state = State.CONFIRMED
        elif response.status_code == 401:
            raise InvalidCredentialsError
        else:
            state = State.REJECTED
        return state

    def guess_client_id(self, phone: str) -> str:
        provider_name = guess_provider(phone)
        for provider in self.providers:
            if provider_name == provider.name:
                return provider.client_id
        raise ProviderNotFoundError(phone)
