#!/usr/bin/env python

"""Tests for `qosic` package."""

import httpx
import pytest
from pytest_httpx import HTTPXMock
import phonenumbers
from qosic import Client, MOOV, MTN, MtnConfig, OPERATION_REJECTED, OPERATION_CONFIRMED
from qosic.constants import (
    REFUND_PATH,
    MTN_PAYMENT_PATH,
    MTN_PAYMENT_STATUS_PATH,
    MOOV_PAYMENT_PATH,
)
from qosic.exceptions import (
    InvalidCredentialsError,
    InvalidClientIdError,
    ServerError,
    RequestError,
)
from qosic import get_random_string

MTN_PHONE_NUMBER = phonenumbers.parse("+22991617451")
MOOV_PHONE_NUMBER = phonenumbers.parse("+22963588213")


@pytest.fixture
def client():
    providers = [
        MTN(client_id=get_random_string(), config=MtnConfig(step=30, timeout=60)),
        MOOV(client_id=get_random_string()),
    ]
    return Client(
        login=get_random_string(),
        password=get_random_string(),
        providers=providers,
    )


def test_request_refund_ok_response(client: Client, httpx_mock: HTTPXMock):
    url = client.context + REFUND_PATH
    httpx_mock.add_response(url=url, method="POST", status_code=httpx.codes.OK)
    result = client.request_refund(trans_ref=get_random_string(), phone=MTN_PHONE_NUMBER)
    assert result.state == OPERATION_CONFIRMED


def test_request_refund_rejected(client: Client, httpx_mock: HTTPXMock):
    url = client.context + REFUND_PATH
    httpx_mock.add_response(url=url, method="POST", status_code=httpx.codes.BAD_REQUEST)
    result = client.request_refund(trans_ref=get_random_string(), phone=MTN_PHONE_NUMBER)
    assert result.state == OPERATION_REJECTED


def test_request_refund_bad_provider(client: Client, httpx_mock: HTTPXMock):
    with pytest.raises(AssertionError):
        client.request_refund(trans_ref=get_random_string(), phone=MOOV_PHONE_NUMBER)


def test_request_refund_unauthorized_response(client: Client, httpx_mock: HTTPXMock):
    url = client.context + REFUND_PATH
    httpx_mock.add_response(
        url=url, method="POST", status_code=httpx.codes.UNAUTHORIZED
    )
    with pytest.raises(InvalidCredentialsError):
        client.request_refund(trans_ref=get_random_string(), phone=MTN_PHONE_NUMBER)


def test_request_refund_not_found_response(client: Client, httpx_mock: HTTPXMock):
    url = client.context + REFUND_PATH
    httpx_mock.add_response(url=url, method="POST", status_code=httpx.codes.NOT_FOUND)
    with pytest.raises(InvalidClientIdError):
        client.request_refund(trans_ref=get_random_string(), phone=MTN_PHONE_NUMBER)


def test_request_refund_gateway_timeout_response(client: Client, httpx_mock: HTTPXMock):
    url = client.context + REFUND_PATH
    httpx_mock.add_response(
        url=url, method="POST", status_code=httpx.codes.GATEWAY_TIMEOUT
    )
    with pytest.raises(ServerError):
        client.request_refund(trans_ref=get_random_string(), phone=MTN_PHONE_NUMBER)


def test_request_payment_mtn_ok_response(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.context + MTN_PAYMENT_PATH
    payment_status_url = client.context + MTN_PAYMENT_STATUS_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.ACCEPTED
    )
    httpx_mock.add_response(
        url=payment_status_url,
        method="POST",
        status_code=httpx.codes.OK,
        json={"responsecode": "00"},
    )
    result = client.request_payment(phone=MTN_PHONE_NUMBER, amount=2000)
    assert result.state == OPERATION_CONFIRMED


def test_request_payment_mtn_refused(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.context + MTN_PAYMENT_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.FORBIDDEN
    )
    result = client.request_payment(phone=MTN_PHONE_NUMBER, amount=2000)
    assert result.state == OPERATION_REJECTED


def test_request_payment_mtn_rejected(client: Client, httpx_mock: HTTPXMock):
    payment_url = client.context + MTN_PAYMENT_PATH
    payment_status_url = client.context + MTN_PAYMENT_STATUS_PATH
    httpx_mock.add_response(
        url=payment_url, method="POST", status_code=httpx.codes.ACCEPTED
    )
    httpx_mock.add_response(
        url=payment_status_url,
        method="POST",
        status_code=httpx.codes.OK,
    )
    result = client.request_payment(phone=MTN_PHONE_NUMBER, amount=2000)
    assert result.state == OPERATION_REJECTED


def test_request_payment_moov_ok_response(client: Client, httpx_mock: HTTPXMock):
    url = client.context + MOOV_PAYMENT_PATH
    httpx_mock.add_response(
        url=url,
        method="POST",
        status_code=httpx.codes.OK,
        json={"responsecode": "0"},
    )
    result = client.request_payment(phone=MOOV_PHONE_NUMBER, amount=2000)
    assert result.state == OPERATION_CONFIRMED


def test_request_payment_moov_rejected(client: Client, httpx_mock: HTTPXMock):
    url = client.context + MOOV_PAYMENT_PATH
    httpx_mock.add_response(
        url=url,
        method="POST",
        status_code=httpx.codes.OK,
    )
    result = client.request_payment(phone=MOOV_PHONE_NUMBER, amount=2000)
    assert result.state == OPERATION_REJECTED


def test_send_request(client: Client, httpx_mock: HTTPXMock):
    fake_path = "/fakepath"
    with pytest.raises(RequestError):
        client._send_request(path=fake_path, payload={})

    real_url = client.context + MTN_PAYMENT_PATH
    httpx_mock.add_response(url=real_url, status_code=httpx.codes.UNAUTHORIZED)
    with pytest.raises(InvalidCredentialsError):
        client._send_request(path=MTN_PAYMENT_PATH, payload={})

    real_url2 = client.context + MTN_PAYMENT_STATUS_PATH
    httpx_mock.add_response(url=real_url2, status_code=httpx.codes.NOT_FOUND)
    with pytest.raises(InvalidClientIdError):
        client._send_request(
            path=MTN_PAYMENT_STATUS_PATH, payload={"clientid": get_random_string()}
        )
