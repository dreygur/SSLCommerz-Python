from __future__ import annotations

import hashlib
from unittest.mock import MagicMock

import pytest

from sslcommerz_python_api.exceptions import SSLCommerzValidationError
from sslcommerz_python_api.service import SSLCommerzService


def _build_valid_ipn(store_pass: str, fields: dict) -> dict:
    store_pass_hash = hashlib.md5(store_pass.encode()).hexdigest()
    check_params = dict(fields)
    check_params["store_passwd"] = store_pass_hash
    sign_string = "&".join(f"{k}={v}" for k, v in sorted(check_params.items()))
    verify_sign = hashlib.md5(sign_string.encode()).hexdigest()
    return {**fields, "verify_key": ",".join(fields.keys()), "verify_sign": verify_sign}


@pytest.fixture
def service():
    return SSLCommerzService(MagicMock(), store_pass="mypass")


def test_valid_ipn_returns_true(service):
    ipn_data = _build_valid_ipn("mypass", {"amount": "100.00", "currency": "BDT"})
    assert service.verify_ipn(ipn_data) is True


def test_tampered_amount_raises(service):
    ipn_data = _build_valid_ipn("mypass", {"amount": "100.00", "currency": "BDT"})
    ipn_data["amount"] = "9999.00"
    with pytest.raises(SSLCommerzValidationError, match="signature mismatch"):
        service.verify_ipn(ipn_data)


def test_wrong_store_pass_raises():
    service = SSLCommerzService(MagicMock(), store_pass="wrongpass")
    ipn_data = _build_valid_ipn("correctpass", {"amount": "100.00"})
    with pytest.raises(SSLCommerzValidationError, match="signature mismatch"):
        service.verify_ipn(ipn_data)


def test_missing_verify_key_raises(service):
    with pytest.raises(SSLCommerzValidationError, match="missing required fields"):
        service.verify_ipn({"verify_sign": "abc"})


def test_missing_verify_sign_raises(service):
    with pytest.raises(SSLCommerzValidationError, match="missing required fields"):
        service.verify_ipn({"verify_key": "amount"})


def test_empty_ipn_raises(service):
    with pytest.raises(SSLCommerzValidationError):
        service.verify_ipn({})
