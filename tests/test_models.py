from __future__ import annotations

from decimal import Decimal

import pytest

from sslcommerz_python_api.models import (
    CustomerInfo,
    PaymentRequest,
    PaymentResponse,
    ShippingInfo,
    ValidationResponse,
)


def _base_request(**overrides):
    defaults = dict(
        store_id="sid",
        store_pass="pass",
        tran_id="T1",
        total_amount=Decimal("10.00"),
        currency="BDT",
        success_url="s",
        fail_url="f",
        cancel_url="c",
    )
    defaults.update(overrides)
    return PaymentRequest(**defaults)


def test_payment_request_valid():
    r = _base_request()
    assert r.store_id == "sid"
    assert r.total_amount == Decimal("10.00")


def test_payment_request_negative_amount_raises():
    with pytest.raises(ValueError, match="total_amount must be positive"):
        _base_request(total_amount=Decimal("-1.00"))


def test_payment_request_zero_amount_raises():
    with pytest.raises(ValueError, match="total_amount must be positive"):
        _base_request(total_amount=Decimal("0"))


def test_payment_request_empty_store_id_raises():
    with pytest.raises(ValueError, match="store_id is required"):
        _base_request(store_id="")


def test_payment_request_empty_store_pass_raises():
    with pytest.raises(ValueError, match="store_pass is required"):
        _base_request(store_pass="")


def test_payment_response_is_success():
    r = PaymentResponse(status="SUCCESS", session_key="K", gateway_url="u")
    assert r.is_success is True


def test_payment_response_is_not_success():
    r = PaymentResponse(status="FAILED")
    assert r.is_success is False


def test_validation_response_is_validated():
    r = ValidationResponse(status="VALIDATED", data={})
    assert r.is_validated is True


def test_validation_response_not_validated():
    r = ValidationResponse(status="INVALID_TRANSACTION", data={})
    assert r.is_validated is False


def test_customer_info_defaults():
    c = CustomerInfo(
        name="N", email="e@x.com", address1="a",
        city="c", postcode="p", country="BD", phone="0",
    )
    assert c.address2 == ""


def test_shipping_info_fields():
    s = ShippingInfo(ship_name="Wh", address="42", city="Ctg", postcode="4000", country="BD")
    assert s.ship_name == "Wh"
