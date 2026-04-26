from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sslcommerz_python_api.exceptions import SSLCommerzAPIError
from sslcommerz_python_api.models import CustomerInfo, PaymentRequest, ShippingInfo
from sslcommerz_python_api.repository import SSLCommerzRepository


@pytest.fixture
def repo():
    return SSLCommerzRepository(store_id="sid", store_pass="pass", is_sandbox=True)


@pytest.fixture
def sample_request():
    return PaymentRequest(
        store_id="sid",
        store_pass="pass",
        tran_id="T1",
        total_amount=Decimal("50.00"),
        currency="BDT",
        success_url="https://x.com/s",
        fail_url="https://x.com/f",
        cancel_url="https://x.com/c",
    )


def test_sandbox_url_used(repo, sample_request):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "SUCCESS", "sessionkey": "K", "GatewayPageURL": "u"}
    with patch("sslcommerz_python_api.repository.requests.post", return_value=mock_resp) as mock_post:
        repo.initiate_payment(sample_request)
    assert "sandbox.sslcommerz.com" in mock_post.call_args[0][0]


def test_live_url_used(sample_request):
    live_repo = SSLCommerzRepository(store_id="sid", store_pass="pass", is_sandbox=False)
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "SUCCESS", "sessionkey": "K", "GatewayPageURL": "u"}
    with patch("sslcommerz_python_api.repository.requests.post", return_value=mock_resp) as mock_post:
        live_repo.initiate_payment(sample_request)
    assert "securepay.sslcommerz.com" in mock_post.call_args[0][0]


def test_connection_error_raises_api_error(repo, sample_request):
    from requests.exceptions import ConnectionError as ReqConnectionError
    with patch("sslcommerz_python_api.repository.requests.post", side_effect=ReqConnectionError("down")):
        with pytest.raises(SSLCommerzAPIError):
            repo.initiate_payment(sample_request)


def test_validate_connection_error_raises_api_error(repo):
    from requests.exceptions import ConnectionError as ReqConnectionError
    with patch("sslcommerz_python_api.repository.requests.get", side_effect=ReqConnectionError("down")):
        with pytest.raises(SSLCommerzAPIError):
            repo.validate_transaction("VAL001")


def test_build_payload_basic_fields():
    request = PaymentRequest(
        store_id="sid",
        store_pass="pass",
        tran_id="T3",
        total_amount=Decimal("20.00"),
        currency="BDT",
        success_url="s",
        fail_url="f",
        cancel_url="c",
    )
    payload = SSLCommerzRepository._build_payload(request)
    assert payload["store_id"] == "sid"
    assert payload["total_amount"] == "20.00"
    assert payload["tran_id"] == "T3"
    assert "cus_name" not in payload
    assert "ship_name" not in payload


def test_build_payload_with_customer():
    request = PaymentRequest(
        store_id="sid",
        store_pass="pass",
        tran_id="T4",
        total_amount=Decimal("20.00"),
        currency="BDT",
        success_url="s",
        fail_url="f",
        cancel_url="c",
        customer=CustomerInfo(
            name="Jane",
            email="jane@x.com",
            address1="addr",
            city="Dhaka",
            postcode="1000",
            country="BD",
            phone="01700000000",
        ),
    )
    payload = SSLCommerzRepository._build_payload(request)
    assert payload["cus_name"] == "Jane"
    assert payload["cus_email"] == "jane@x.com"


def test_build_payload_with_shipping():
    request = PaymentRequest(
        store_id="sid",
        store_pass="pass",
        tran_id="T5",
        total_amount=Decimal("20.00"),
        currency="BDT",
        success_url="s",
        fail_url="f",
        cancel_url="c",
        shipping=ShippingInfo(
            ship_name="Warehouse",
            address="42 Ship Rd",
            city="Chittagong",
            postcode="4000",
            country="BD",
        ),
    )
    payload = SSLCommerzRepository._build_payload(request)
    assert payload["ship_name"] == "Warehouse"
    assert payload["ship_add1"] == "42 Ship Rd"
