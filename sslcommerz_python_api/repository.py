from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import requests
from requests.exceptions import RequestException

from .exceptions import SSLCommerzAPIError
from .models import PaymentRequest

logger = logging.getLogger(__name__)

_SESSION_PATH = "sslcommerz.com/gwprocess/v4/api.php"
_VALIDATION_PATH = "sslcommerz.com/validator/api/validationserverAPI.php"


class AbstractSSLCommerzRepository(ABC):
    """Abstract interface for SSLCommerz HTTP operations.

    Inject a subclass into SSLCommerzService to swap out the real HTTP
    implementation for a fake in tests.
    """

    @abstractmethod
    def initiate_payment(self, request: PaymentRequest) -> dict[str, Any]:
        """POST a payment initiation request to SSLCommerz.

        Args:
            request: Fully populated PaymentRequest dataclass.

        Returns:
            Raw JSON response dict from the SSLCommerz API.

        Raises:
            SSLCommerzAPIError: On any HTTP or network failure.
        """
        ...

    @abstractmethod
    def validate_transaction(self, val_id: str) -> dict[str, Any]:
        """GET transaction validation status from SSLCommerz.

        Args:
            val_id: Validation ID returned by SSLCommerz in the IPN or redirect.

        Returns:
            Raw JSON response dict from the SSLCommerz validation API.

        Raises:
            SSLCommerzAPIError: On any HTTP or network failure.
        """
        ...


class SSLCommerzRepository(AbstractSSLCommerzRepository):
    """Concrete HTTP implementation of AbstractSSLCommerzRepository.

    Uses the requests library to communicate with the SSLCommerz REST API.
    Supports sandbox and live environments.

    Attributes:
        _store_id: SSLCommerz store ID credential.
        _store_pass: SSLCommerz store password credential.
        _timeout: HTTP request timeout in seconds.
        _session_url: Full URL for payment session initiation.
        _validation_url: Full URL for transaction validation.
    """

    def __init__(
        self,
        store_id: str,
        store_pass: str,
        is_sandbox: bool = True,
        timeout: int = 30,
    ) -> None:
        """Initialize the repository with store credentials and environment settings.

        Args:
            store_id: SSLCommerz store ID.
            store_pass: SSLCommerz store password.
            is_sandbox: Use sandbox endpoint if True, live endpoint if False.
            timeout: HTTP request timeout in seconds. Defaults to 30.
        """
        self._store_id = store_id
        self._store_pass = store_pass
        self._timeout = timeout
        mode = "sandbox" if is_sandbox else "securepay"
        self._session_url = f"https://{mode}.{_SESSION_PATH}"
        self._validation_url = f"https://{mode}.{_VALIDATION_PATH}"

    def initiate_payment(self, request: PaymentRequest) -> dict[str, Any]:
        """POST payment data to SSLCommerz and return the raw response dict.

        Args:
            request: Fully populated PaymentRequest dataclass.

        Returns:
            Raw JSON response dict (contains status, sessionkey, GatewayPageURL, etc.).

        Raises:
            SSLCommerzAPIError: On connection error, timeout, or non-2xx HTTP response.
        """
        payload = self._build_payload(request)
        logger.debug("POST %s tran_id=%s", self._session_url, request.tran_id)
        try:
            response = requests.post(self._session_url, data=payload, timeout=self._timeout)
            response.raise_for_status()
        except RequestException as exc:
            raise SSLCommerzAPIError(
                f"SSLCommerz HTTP request failed: {exc}",
                status_code=getattr(getattr(exc, "response", None), "status_code", None),
            ) from exc
        data: dict[str, Any] = response.json()
        logger.debug("SSLCommerz session response status=%s", data.get("status"))
        return data

    def validate_transaction(self, val_id: str) -> dict[str, Any]:
        """GET transaction validation data from SSLCommerz.

        Args:
            val_id: The validation ID to look up.

        Returns:
            Raw JSON response dict (contains status and transaction details).

        Raises:
            SSLCommerzAPIError: On connection error, timeout, or non-2xx HTTP response.
        """
        params = {
            "val_id": val_id,
            "store_id": self._store_id,
            "store_passwd": self._store_pass,
            "format": "json",
        }
        logger.debug("GET %s val_id=%s", self._validation_url, val_id)
        try:
            response = requests.get(self._validation_url, params=params, timeout=self._timeout)
            response.raise_for_status()
        except RequestException as exc:
            raise SSLCommerzAPIError(
                f"SSLCommerz validation HTTP request failed: {exc}",
                status_code=getattr(getattr(exc, "response", None), "status_code", None),
            ) from exc
        data: dict[str, Any] = response.json()
        logger.debug("SSLCommerz validation response status=%s", data.get("status"))
        return data

    @staticmethod
    def _build_payload(request: PaymentRequest) -> dict[str, Any]:
        """Map a PaymentRequest dataclass to the SSLCommerz API field names.

        Args:
            request: The payment request to serialize.

        Returns:
            Dict of form-encoded fields ready to POST to SSLCommerz.
        """
        payload: dict[str, Any] = {
            "store_id": request.store_id,
            "store_passwd": request.store_pass,
            "tran_id": request.tran_id,
            "total_amount": str(request.total_amount),
            "currency": request.currency,
            "success_url": request.success_url,
            "fail_url": request.fail_url,
            "cancel_url": request.cancel_url,
            "ipn_url": request.ipn_url,
            "product_name": request.product_name,
            "product_category": request.product_category,
            "product_profile": request.product_profile,
            "num_of_item": request.num_of_item,
            "shipping_method": request.shipping_method,
            "value_a": request.value_a,
            "value_b": request.value_b,
            "value_c": request.value_c,
            "value_d": request.value_d,
        }
        if request.customer:
            payload.update({
                "cus_name": request.customer.name,
                "cus_email": request.customer.email,
                "cus_add1": request.customer.address1,
                "cus_add2": request.customer.address2,
                "cus_city": request.customer.city,
                "cus_postcode": request.customer.postcode,
                "cus_country": request.customer.country,
                "cus_phone": request.customer.phone,
            })
        if request.shipping:
            payload.update({
                "ship_name": request.shipping.ship_name,
                "ship_add1": request.shipping.address,
                "ship_city": request.shipping.city,
                "ship_postcode": request.shipping.postcode,
                "ship_country": request.shipping.country,
            })
        return payload
