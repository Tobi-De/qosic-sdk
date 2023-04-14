from __future__ import annotations

import contextlib

import httpx
import polling2
from dataclasses import dataclass, field

from qosic.mobile_carriers.utils import (
    _generic_reference_factory,
    _validate_reference_factory,
    _req_body_from_payer,
    _handle_common_errors,
    _extract_json,
    _resp_is_ok,
)
from ...utils import Payer, Result

MTN_PAYMENT_PATH = "/QosicBridge/user/requestpayment"
MTN_PAYMENT_STATUS_PATH = "/QosicBridge/user/gettransactionstatus"
MTN_PREFIXES = ["51", "52", "53", "61", "62", "66", "67", "69", "90", "91", "96", "97"]
MTN_REFUND_PATH = "/QosicBridge/user/refund"


@dataclass(frozen=True)
class MTN:
    id: str
    step: int = 10
    timeout: int = 60 * 2
    max_tries: int | None = None
    allowed_prefixes: list[str] = field(default_factory=lambda: MTN_PREFIXES)
    reference_factory: callable = _generic_reference_factory

    def __post_init__(self):
        _validate_reference_factory(self.reference_factory)
        assert 5 <= self.step <= 30, f"Step {self.step} must be between 5 and 30"
        assert (
            60 <= self.timeout <= 180
        ), f"Timeout {self.timeout}  must be between 60 and 180"
        if self.max_tries:
            assert (
                self.max_tries * self.step <= self.timeout
            ), f"max_tries exceed timeout: {self.max_tries} * {self.step} > {self.timeout}"

    def pay(self, client: httpx.Client, *, payer: Payer) -> Result:
        body = _req_body_from_payer(self, payer)
        response = client.post(url=MTN_PAYMENT_PATH, json=body)
        _handle_common_errors(response, provider=self, payer=payer)
        res_dict = {
            "reference": body["transref"],
            "mobile_carrier": self,
            "status": Result.Status.FAILED,
            "response": response,
            "phone": payer.phone,
        }
        if response.status_code != httpx.codes.ACCEPTED:
            return Result(**res_dict)
        with contextlib.suppress(polling2.TimeoutException, MTNPaymentRejected):
            res_dict["status"] = polling2.poll(
                target=self._check_status,
                check_success=polling2.is_value(Result.Status.CONFIRMED),
                step=self.step,
                timeout=self.timeout,
                max_tries=self.max_tries,
                kwargs={"reference": body["transref"], "client": client},
            )
        return Result(**res_dict)

    def _check_status(self, *, client: httpx.Client, reference: str) -> Result.Status:
        response = client.post(
            url=MTN_PAYMENT_STATUS_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        json_content = _extract_json(response)
        if not _resp_is_ok(response) or json_content["responsecode"] is None:
            raise MTNPaymentRejected()
        if _resp_is_ok(response) and json_content["responsecode"] == "00":
            return Result.Status.CONFIRMED
        return Result.Status.FAILED

    def refund(self, client: httpx.Client, *, reference: str, phone: str) -> Result:
        response = client.post(
            url=MTN_REFUND_PATH,
            json={"clientid": self.id, "transref": reference},
        )
        _handle_common_errors(response, provider=self)
        ok = _resp_is_ok(response) and _extract_json(response)["responsecode"] == "00"
        status = Result.Status.CONFIRMED if ok else Result.Status.FAILED
        return Result(
            reference=reference,
            mobile_carrier=self,
            status=status,
            response=response,
            phone=phone,
        )


class MTNPaymentRejected(Exception):
    pass
