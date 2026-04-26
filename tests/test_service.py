from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from sslcommerz_python_api.exceptions import SSLCommerzAPIError, SSLCommerzValidationError
from sslcommerz_python_api.models import CustomerInfo, PaymentRequest
from sslcommerz_python_api.service import SSLCommerzService


@pytest.fixture
def fake_repo():
    return MagicMock()


@pytest.fixture
def service(fake_repo):
    return SSLCommerzService(repository=fake_repo, store_pass="testpass")


@pytest.fixture
def sample_request():
    return PaymentRequest(
        store_id="test_store",
        store_pass="testpass",
        tran_id="TXN-001",
        total_amount=Decimal("100.00"),
        currency="BDT",
        success_url="https://example.com/success",
        fail_url="https://example.com/fail",
        cancel_url="https://example.com/cancel",
        customer=CustomerInfo(
            name="John Doe",
            email="john@example.com",
            address1="123 Main St",
            city="Dhaka",
            postcode="1207",
            country="Bangladesh",
            phone="01711111111",
        ),
    )


def test_initiate_payment_success(service, fake_repo, sample_request):
    fake_repo.initiate_payment.return_value = {
        "status": "SUCCESS",
        "sessionkey": "SESS123",
        "GatewayPageURL": "https://sandbox.sslcommerz.com/pay",
    }
    response = service.initiate_payment(sample_request)
    assert response.is_success
    assert response.session_key == "SESS123"
    assert response.gateway_url == "https://sandbox.sslcommerz.com/pay"


def test_initiate_payment_failed_raises(service, fake_repo, sample_request):
    fake_repo.initiate_payment.return_value = {
        "status": "FAILED",
        "failedreason": "Store Credential Error",
    }
    with pytest.raises(SSLCommerzAPIError, match="Store Credential Error"):
        service.initiate_payment(sample_request)


def test_validate_transaction_success(service, fake_repo):
    fake_repo.validate_transaction.return_value = {
        "status": "VALIDATED",
        "val_id": "VAL001",
        "amount": "100.00",
    }
    resp = service.validate_transaction("VAL001")
    assert resp.is_validated
    assert resp.data["val_id"] == "VAL001"


def test_validate_transaction_invalid_raises(service, fake_repo):
    fake_repo.validate_transaction.return_value = {"status": "INVALID_TRANSACTION"}
    with pytest.raises(SSLCommerzValidationError):
        service.validate_transaction("BAD_ID")


def test_validate_transaction_empty_val_id_raises(service, fake_repo):
    with pytest.raises(SSLCommerzValidationError, match="val_id must not be empty"):
        service.validate_transaction("")
    fake_repo.validate_transaction.assert_not_called()
