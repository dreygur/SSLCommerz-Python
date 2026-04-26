from __future__ import annotations

import warnings
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


def test_sslcsession_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from sslcommerz_python_api._compat import SSLCSession
        SSLCSession(sslc_is_sandbox=True, sslc_store_id="sid", sslc_store_pass="pass")
    assert any(issubclass(warning.category, DeprecationWarning) for warning in w)


def test_sslcsession_init_payment_returns_dict():
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        from sslcommerz_python_api._compat import SSLCSession
        session = SSLCSession(sslc_is_sandbox=True, sslc_store_id="sid", sslc_store_pass="pass")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "status": "SUCCESS",
        "sessionkey": "SESS456",
        "GatewayPageURL": "https://sandbox.sslcommerz.com/pay",
    }
    with patch("sslcommerz_python_api.repository.requests.post", return_value=mock_resp):
        session.set_urls(
            success_url="https://x.com/s",
            fail_url="https://x.com/f",
            cancel_url="https://x.com/c",
        )
        session.set_product_integration(
            total_amount=Decimal("20.20"),
            currency="BDT",
            product_category="clothes",
            product_name="shirt",
            num_of_item=1,
            shipping_method="YES",
        )
        session.set_customer_info(
            name="Jane",
            email="jane@x.com",
            address1="123 St",
            city="Dhaka",
            postcode="1207",
            country="Bangladesh",
            phone="01700000000",
        )
        result = session.init_payment()

    assert result["status"] == "SUCCESS"
    assert result["sessionkey"] == "SESS456"
    assert "GatewayPageURL" in result


def test_sslcsession_init_payment_failure_returns_failed_dict():
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        from sslcommerz_python_api._compat import SSLCSession
        session = SSLCSession(sslc_is_sandbox=True, sslc_store_id="sid", sslc_store_pass="pass")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "FAILED", "failedreason": "Bad creds"}
    with patch("sslcommerz_python_api.repository.requests.post", return_value=mock_resp):
        session.set_urls("s", "f", "c")
        session.set_product_integration(Decimal("10"), "BDT", "cat", "prod", 1, "NO")
        result = session.init_payment()

    assert result["status"] == "FAILED"
    assert "failedreason" in result
