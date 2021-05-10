"""Main module."""

from dataclasses import dataclass
import httpx
from .utils import get_random_string, guess_provider, clean_phone_number

REFUND_URL = "/QosicBridge/user/refund"
MTN_PAYMENT_URL = "/QosicBridge/user/requestpayment"
MTN_PAYMENT_STATUS_URL = "/QosicBridge/user/gettransactionstatus"
MOOV_PAYMENT_URL = "/QosicBridge/user/requestpaymentmv"


@dataclass
class Response:
    pass


@dataclass
class Client:
    client_id: str
    login: str
    password: str
    context: str = "http://qosic.net:8443"

    def request_payment(self, phone_number: str, amount: int, **kwargs) -> Response:
        payload = {
            "clientid": self.client_id,
            "msisdn": clean_phone_number(phone_number),
            "amount": str(amount),
            "transref": get_random_string(),
            "firstname": (
                kwargs.pop("first_name", None) or kwargs.pop("firstname", None)
            ),
            "lastname": kwargs.pop("last_name", None) or kwargs.pop("lastname", None),
        }

        provider = guess_provider(phone_number)
        if provider == "MTN":
            response = self._make_mtn_payment(payload)
        else:
            response = self.request_moov_payment(payload)
        return response

    def _make_mtn_payment(self, payload) -> Response:
        url = self.context + MTN_PAYMENT_URL
        httpx.post(
            url,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            json=payload,
        )
        return Response()

    def _get_transaction_status(self) -> Response:
        pass

    def _make_moov_payment(self, payload) -> Response:
        url = self.context + MOOV_PAYMENT_URL
        httpx.post(
            url,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            json=payload,
        )
        return Response()

    def refund() -> Response:
        return Response()
