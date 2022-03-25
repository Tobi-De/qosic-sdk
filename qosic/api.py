from __future__ import annotations

from dataclasses import dataclass, field

import httpx
import phonenumbers

from .constants import QOSIC_BASE_URL
from .exceptions import ProviderNotFoundError
from .protocols import Provider
from .utils import Result


@dataclass
class Client:
    """The synchronous client that will be used to make the request to the QosIc api
    :param providers: The list of your provider
    :param login: Your server authentication login/user
    :param password: Your server authentication password
    :param base_url: The QosIC server root domain if you ever need to change it
    """

    login: str
    password: str
    providers: list[Provider]
    base_url: str = QOSIC_BASE_URL
    _http_client: httpx.Client = field(init=False)

    def __post_init__(self):
        self._http_client = httpx.Client(
            base_url=self.base_url,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            verify=False,
            timeout=80,
        )

    def __del__(self):
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()

    def pay(
        self,
        phone: str,
        amount: int,
        first_name: str,
        last_name: str,
    ) -> Result:
        phone = phonenumbers.parse(phone)
        prefix = str(phone.national_number)[:2]
        try:
            provider = [
                provider
                for provider in self.providers
                if prefix in provider.allowed_prefixes
            ][0]
        except IndexError:
            raise ProviderNotFoundError(
                f"A provider was not found for the given phone number: {phone}"
            )
        return provider.pay(
            self._http_client,
            phone=phone,
            amount=amount,
            first_name=first_name,
            last_name=last_name,
        )

    def refund(self, reference: str, client_id: str) -> Result:
        try:
            provider = [
                provider
                for provider in self.providers
                if provider.client_id == client_id
            ][0]
        except IndexError:
            raise ProviderNotFoundError(
                f"A provider was not found for the given client id: {client_id}"
            )
        return provider.refund(
            self._http_client, reference=reference, client_id=client_id
        )
