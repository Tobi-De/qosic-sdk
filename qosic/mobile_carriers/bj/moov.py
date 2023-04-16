from __future__ import annotations

import httpx
from dataclasses import dataclass, field

from qosic.errors import FeatureNotImplementedError
from qosic.mobile_carriers.utils import (
    generic_reference_factory,
    validate_reference_factory,
    handle_common_errors,
    get_json_from,
    response_is_ok,
)
from ...utils import Payer, Result

MOOV_PREFIXES = ["55", "60", "63", "64", "65", "68", "94", "95", "98", "99"]
MOOV_PAYMENT_PATH = "/QosicBridge/user/requestpaymentmv"


@dataclass(frozen=True)
class MOOV:
    id: str
    allowed_prefixes: list[str] = field(default_factory=lambda: MOOV_PREFIXES)
    reference_factory: callable = generic_reference_factory

    def __post_init__(self):
        validate_reference_factory(self.reference_factory)

    def pay(self, client: httpx.Client, *, payer: Payer) -> Result:
        body = payer.to_qos_compliant_payment_request_body(self)
        response = client.post(url=MOOV_PAYMENT_PATH, json=body)
        handle_common_errors(response, provider=self, payer=payer)
        json_content = get_json_from(response)
        ok = response_is_ok(response) and json_content["responsecode"] == "0"
        status = Result.Status.CONFIRMED if ok else Result.Status.FAILED
        return Result(
            reference=body["transref"],
            mobile_carrier=self,
            status=status,
            response=response,
            phone=payer.phone,
        )

    def refund(self, client: httpx.Client, *, reference: str, phone: str) -> Result:
        raise FeatureNotImplementedError("MOOV does not support the refund operation")
