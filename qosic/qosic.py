"""Main module."""

from dataclasses import dataclass
from enum import Enum
from typing import List

import httpx

from .exceptions import ProviderNotFoundError, InvalidCredentialError, RequestError
from .utils import clean_phone, get_random_string, guess_provider, poll


class State(Enum):
    SUCCESS = "Operation was successful"
    FAILURE = "Operation was unsuccessful"


@dataclass
class Provider:
    name: str
    client_id: str


@dataclass
class Result:
    state: State
    trans_ref: str
    client_id: str
    phone: str = None
    amount: str = None


@dataclass
class Client:
    providers: List[Provider]
    login: str
    password: str
    context: str = "https://qosic.net:8443"
    refund_path: str = "/QosicBridge/user/refund"
    mtn_payment_path: str = "/QosicBridge/user/requestpayment"
    mtn_payment_status_path: str = "/QosicBridge/user/gettransactionstatus"
    moov_payment_path: str = "/QosicBridge/user/requestpaymentmv"

    def request_payment(self, phone: str, amount: int, **kwargs) -> Result:
        client_id = self.guess_client_id(phone=phone)
        payload = {
            "clientid": client_id,
            "msisdn": clean_phone(phone),
            "amount": str(amount),
            "transref": get_random_string(),
            "firstname": (
                kwargs.pop("first_name", None) or kwargs.pop("firstname", None)
            ),
            "lastname": kwargs.pop("last_name", None) or kwargs.pop("lastname", None),
        }

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

        url = self.context + self.refund_path
        response = self._send_request(
            url=url, payload={"clientid": client_id, "transref": trans_ref}
        )

        if response.status_code == 200 and response.content.responsecode == "00":
            state = State.SUCCESS
        elif response.status_code == 401:
            raise InvalidCredentialError
        elif response.status_code == 404:
            raise ProviderNotFoundError
        else:
            state = State.FAILURE
        return Result(client_id=client_id, trans_ref=trans_ref, state=state)

    def _send_request(self, url: str, payload: dict) -> httpx.Response:
        try:
            return httpx.post(
                url,
                auth=(self.login, self.password),
                headers={"content-type": "application/json"},
                json=payload,
                verify=False,
                timeout=60,
            )
        except httpx.RequestError as exc:
            raise RequestError(request=exc.request)

    def _make_mtn_payment(self, payload) -> State:
        url = self.context + self.mtn_payment_path
        response = self._send_request(url=url, payload=payload)

        if response.status_code == 202 and response.content.responsecode == "01":
            state = poll(
                target=self._fetch_transaction_status,
                step=60,
                timeout=60 * 3,
                kwargs={
                    "trans_ref": payload["transref"],
                    "client_id": payload["clientid"],
                },
                check_success=lambda val: val == state.SUCCESS,
            )
        elif response.status_code == 401:
            raise InvalidCredentialError
        elif response.status_code == 404:
            raise ProviderNotFoundError(phone=payload["msisdn"])
        else:
            state = State.FAILURE
        return state

    def _fetch_transaction_status(self, trans_ref: str, client_id: str) -> State:
        url = self.context + self.mtn_payment_status_path
        response = self._send_request(
            url=url, payload={"clientid": client_id, "transref": trans_ref}
        )
        if response.status_code == 200 and response.content.responsecode == "0":
            state = State.SUCCESS
        elif response.status_code == 401:
            raise InvalidCredentialError
        else:
            state = State.FAILURE
        return state

    def _make_moov_payment(self, payload: dict) -> State:
        url = self.context + self.moov_payment_path
        response = self._send_request(url=url, payload=payload)
        if response.status_code == 202 and response.content.responsecode == "0":
            state = State.SUCCESS
        elif response.status_code == 401:
            raise InvalidCredentialError
        else:
            state = State.FAILURE
        return state

    def guess_client_id(self, phone: str) -> str:
        provider_name = guess_provider(phone)
        print(self.providers)
        for provider in self.providers:
            if provider_name == provider.name:
                return provider.client_id
        raise ProviderNotFoundError(phone)
