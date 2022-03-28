from __future__ import annotations

from typing import Protocol

from httpx import Client

from .utils import Result, Payer


class Provider(Protocol):
    id: str
    allowed_prefixes: list[str]
    reference_factory: callable[[Payer], str]

    def pay(self, http_client: Client, *, payer: Payer) -> Result:
        ...

    def refund(self, http_client: Client, *, reference: str) -> Result:
        ...
