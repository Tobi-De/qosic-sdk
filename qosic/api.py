from __future__ import annotations

import httpx
from dataclasses import dataclass, field

from .config import QOSIC_BASE_URL
from .errors import ProviderNotFoundError
from .protocols import Provider
from .providers import MTN
from .utils import Result, provider_by_phone, Payer, log_response, log_request


@dataclass
class Client:
    """The synchronous client that will be used to make the request to the QosIc api
    :param providers: The list of your provider
    :param login: Your server authentication login/user
    :param password: Your server authentication password
    :param debug: If true print request and response to console
    :param base_url: The QosIC server root domain if you ever need to change it
    """

    login: str
    password: str
    providers: list[Provider]
    base_url: str = QOSIC_BASE_URL
    debug: bool = False
    _http_client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self):
        self._http_client = httpx.Client(
            base_url=self.base_url,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            verify=False,
            timeout=80,
        )
        if self.debug:
            self._http_client.event_hooks = {
                "request": [log_request],
                "response": [log_response],
            }

    def __del__(self):
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()

    def pay(
        self,
        *,
        phone: str,
        amount: int,
        first_name: str,
        last_name: str,
    ) -> Result:
        payer = Payer(phone, amount, first_name, last_name)
        provider = provider_by_phone(phone=phone, providers=self.providers)
        return provider.pay(self._http_client, payer=payer)

    def refund(self, reference: str) -> Result:
        # Only mtn support refund at the moment
        mtn = None
        for provider in self.providers:
            if isinstance(provider, MTN):
                mtn = provider
        if not mtn:
            raise ProviderNotFoundError(f"An mtn provider was not found")
        return mtn.refund(self._http_client, reference=reference)
