from __future__ import annotations

from functools import partial

import httpx
from dataclasses import dataclass, field

from .logger import logger as _logger
from .protocols import MobileCarrier
from .utils import Result, guess_mobile_carrier_from, Payer, log_response, log_request


@dataclass
class Client:
    """The synchronous client that will be used to make the request to the QosIc api
    :param mobile_carriers: The list of configured mobile carriers to use to communicate with the API.
    :param login: Your server authentication login/user
    :param password: Your server authentication password
    :param logger: Custom logger
    :param base_url: The QosIC server root domain if you ever need to change it
    """

    login: str
    password: str
    mobile_carriers: list[MobileCarrier]
    base_url: str = "https://qosic.net:8443"
    logger: bool = _logger
    _http_client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self):
        self._http_client = httpx.Client(
            base_url=self.base_url,
            auth=(self.login, self.password),
            headers={"content-type": "application/json"},
            verify=False,
            timeout=80,
            event_hooks={
                "request": [partial(log_request, logger=self.logger)],
                "response": [partial(log_response, logger=self.logger)],
            },
        )

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
        first_name: str = "",
        last_name: str = "",
    ) -> Result:
        payer = Payer(
            phone=phone, amount=amount, first_name=first_name, last_name=last_name
        )
        mobile_carrier = guess_mobile_carrier_from(
            phone=phone, mobile_carriers=self.mobile_carriers
        )
        return mobile_carrier.pay(self._http_client, payer=payer)

    def refund(self, reference: str, phone: str) -> Result:
        mobile_carrier = guess_mobile_carrier_from(
            phone=phone, mobile_carriers=self.mobile_carriers
        )
        return mobile_carrier.refund(
            self._http_client, reference=reference, phone=phone
        )
