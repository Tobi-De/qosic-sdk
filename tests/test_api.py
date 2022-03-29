import httpx
import pytest
from pytest_httpx import HTTPXMock

from qosic import Client, MOOV, MTN
from qosic.config import (
    MTN_REFUND_PATH,
    MTN_PAYMENT_PATH,
    MTN_PAYMENT_STATUS_PATH,
    MOOV_PAYMENT_PATH,
)
from qosic.errors import InvalidCredentialsError, ServerError
from qosic.utils import get_random_string

MTN_PHONE_NUMBER = "22991617451"
MOOV_PHONE_NUMBER = "22963588213"


@pytest.fixture
def client():
    providers = [
        MTN(id=get_random_string()),
        MOOV(id=get_random_string()),
    ]
    return Client(
        login=get_random_string(),
        password=get_random_string(),
        providers=providers,
    )


def test_request_refund_ok_response(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MTN_REFUND_PATH
    httpx_mock.add_response(
        url=url, method="POST", status_code=httpx.codes.OK, json={"responsecode": "00"}
    )
    result = client.refund(reference=get_random_string())
    assert result.success


def test_request_refund_rejected(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MTN_REFUND_PATH
    httpx_mock.add_response(url=url, method="POST", status_code=httpx.codes.BAD_REQUEST)
    result = client.refund(reference=get_random_string())
    assert not result.success


def test_request_refund_unauthorized_response(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MTN_REFUND_PATH
    httpx_mock.add_response(
        url=url, method="POST", status_code=httpx.codes.UNAUTHORIZED
    )
    with pytest.raises(InvalidCredentialsError):
        client.refund(reference=get_random_string())


def test_request_refund_gateway_timeout_response(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MTN_REFUND_PATH
    httpx_mock.add_response(
        url=url, method="POST", status_code=httpx.codes.GATEWAY_TIMEOUT
    )
    with pytest.raises(ServerError):
        client.refund(reference=get_random_string())


def test_request_payment_mtn_ok_response(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.base_url + MTN_PAYMENT_PATH
    payment_status_url = client.base_url + MTN_PAYMENT_STATUS_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.ACCEPTED
    )
    httpx_mock.add_response(
        url=payment_status_url,
        method="POST",
        status_code=httpx.codes.OK,
        json={"responsecode": "00"},
    )
    result = client.pay(
        phone=MTN_PHONE_NUMBER, amount=2000, first_name="jean", last_name="pierre"
    )
    assert result.success


def test_request_payment_mtn_refused(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.base_url + MTN_PAYMENT_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.FORBIDDEN
    )
    result = client.pay(
        phone=MTN_PHONE_NUMBER, amount=2000, first_name="jean", last_name="pierre"
    )
    assert not result.success


def test_request_payment_mtn_rejected(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.base_url + MTN_PAYMENT_PATH
    payment_status_url = client.base_url + MTN_PAYMENT_STATUS_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.ACCEPTED
    )
    httpx_mock.add_response(
        url=payment_status_url,
        method="POST",
        status_code=httpx.codes.OK,
    )
    result = client.pay(
        phone=MTN_PHONE_NUMBER, amount=2000, first_name="jean", last_name="dnd"
    )
    assert not result.success


def test_request_payment_moov_ok_response(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MOOV_PAYMENT_PATH
    httpx_mock.add_response(
        url=url,
        method="POST",
        status_code=httpx.codes.OK,
        json={"responsecode": "0"},
    )
    result = client.pay(
        phone=MOOV_PHONE_NUMBER, amount=2000, first_name="jean", last_name="nb"
    )
    assert result.success


def test_request_payment_moov_rejected(client: Client, httpx_mock: HTTPXMock):
    url = client.base_url + MOOV_PAYMENT_PATH
    httpx_mock.add_response(
        url=url,
        method="POST",
        status_code=httpx.codes.OK,
    )
    result = client.pay(
        phone=MOOV_PHONE_NUMBER, amount=2000, first_name="jean", last_name="nb"
    )
    assert not result.success
