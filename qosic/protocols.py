from __future__ import annotations

from typing import Protocol

import httpx
from phonenumbers import PhoneNumber

from qosic.utils import Result


class Provider(Protocol):
    """Abstract base class for providers supported by the QosIC platform, you can check
    their docs at https://www.qosic.com/docs/. For now only two providers are supported,
    MTN and MOOV
    :param client_id: Your client ID, check on your QosIc account
    :param get_reference: A custom factory function to generate transfer references
    :param allowed_prefixes: list of phone number prefixes allowed
    """

    client_id: str
    allowed_prefixes: list[str]
    reference_factory: callable

    def pay(
        self,
        client: httpx.Client,
        *,
        phone: PhoneNumber,
        amount: int,
        first_name: str,
        last_name: str,
    ) -> Result:
        ...

    def refund(self, client: httpx.Client, *, reference: str, client_id: str) -> Result:
        ...
