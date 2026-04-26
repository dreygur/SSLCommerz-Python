from __future__ import annotations

import warnings
from decimal import Decimal
from uuid import uuid4

from .models import CustomerInfo, PaymentRequest, ShippingInfo
from .service import SSLCommerzService


class SSLCSession:
    """Backward-compatible builder API from v1. Use SSLCommerzService for new code.

    Emits a DeprecationWarning on construction. Wraps SSLCommerzService
    internally and translates builder calls into a PaymentRequest dataclass.
    The init_payment() return shape matches the v1 dict format exactly.
    """

    def __init__(
        self,
        sslc_is_sandbox: bool = True,
        sslc_store_id: str = "",
        sslc_store_pass: str = "",
    ) -> None:
        """Initialize a legacy builder session.

        Args:
            sslc_is_sandbox: Use sandbox endpoint if True, live if False.
            sslc_store_id: SSLCommerz store ID credential.
            sslc_store_pass: SSLCommerz store password credential.
        """
        warnings.warn(
            "SSLCSession is deprecated. Use SSLCommerzService.create() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._service = SSLCommerzService.create(
            store_id=sslc_store_id,
            store_pass=sslc_store_pass,
            is_sandbox=sslc_is_sandbox,
        )
        self._store_id = sslc_store_id
        self._store_pass = sslc_store_pass
        self._urls: dict = {}
        self._product: dict = {}
        self._customer: dict | None = None
        self._shipping: dict | None = None
        self._extras: dict = {}

    def set_urls(
        self,
        success_url: str,
        fail_url: str,
        cancel_url: str,
        ipn_url: str = "",
    ) -> None:
        """Set redirect and notification URLs for the payment session.

        Args:
            success_url: URL to redirect to on successful payment.
            fail_url: URL to redirect to on payment failure.
            cancel_url: URL to redirect to on cancellation.
            ipn_url: URL for the Instant Payment Notification webhook.
        """
        self._urls = dict(
            success_url=success_url,
            fail_url=fail_url,
            cancel_url=cancel_url,
            ipn_url=ipn_url,
        )

    def set_product_integration(
        self,
        total_amount: Decimal,
        currency: str,
        product_category: str,
        product_name: str,
        num_of_item: int,
        shipping_method: str,
        product_profile: str = "None",
    ) -> None:
        """Set product and transaction details.

        Args:
            total_amount: Transaction total as a Decimal.
            currency: ISO 4217 currency code (e.g. "BDT").
            product_category: Category of the product.
            product_name: Name of the product.
            num_of_item: Number of items in the order.
            shipping_method: Shipping method indicator ("YES" / "NO").
            product_profile: SSLCommerz product profile identifier.
        """
        self._product = dict(
            total_amount=total_amount,
            currency=currency,
            product_category=product_category,
            product_name=product_name,
            num_of_item=num_of_item,
            shipping_method=shipping_method,
            product_profile=product_profile,
        )

    def set_customer_info(
        self,
        name: str,
        email: str,
        address1: str,
        city: str,
        postcode: str,
        country: str,
        phone: str,
        address2: str = "",
    ) -> None:
        """Set customer billing information.

        Args:
            name: Customer full name.
            email: Customer email address.
            address1: Primary billing address line.
            city: Billing city.
            postcode: Billing postal code.
            country: Billing country.
            phone: Customer phone number.
            address2: Optional secondary address line.
        """
        self._customer = dict(
            name=name,
            email=email,
            address1=address1,
            city=city,
            postcode=postcode,
            country=country,
            phone=phone,
            address2=address2,
        )

    def set_shipping_info(
        self,
        shipping_to: str,
        address: str,
        city: str,
        postcode: str,
        country: str,
    ) -> None:
        """Set shipping destination information.

        Args:
            shipping_to: Name of the shipping recipient.
            address: Shipping address line.
            city: Shipping city.
            postcode: Shipping postal code.
            country: Shipping country.
        """
        self._shipping = dict(
            ship_name=shipping_to,
            address=address,
            city=city,
            postcode=postcode,
            country=country,
        )

    def set_additional_values(
        self,
        value_a: str = "",
        value_b: str = "",
        value_c: str = "",
        value_d: str = "",
    ) -> None:
        """Set optional custom pass-through values.

        These values are returned unchanged in the SSLCommerz callback.

        Args:
            value_a: Custom pass-through value A.
            value_b: Custom pass-through value B.
            value_c: Custom pass-through value C.
            value_d: Custom pass-through value D.
        """
        self._extras = dict(value_a=value_a, value_b=value_b, value_c=value_c, value_d=value_d)

    def init_payment(self) -> dict:
        """Initiate the payment session and return a v1-compatible response dict.

        Builds a PaymentRequest from accumulated builder state, calls the
        service, and returns a plain dict matching the v1 response shape.

        Returns:
            Dict with keys: status, sessionkey, GatewayPageURL on success.
            Dict with keys: status, failedreason on failure.
        """
        request = PaymentRequest(
            store_id=self._store_id,
            store_pass=self._store_pass,
            tran_id=str(uuid4()),
            customer=CustomerInfo(**self._customer) if self._customer else None,
            shipping=ShippingInfo(**self._shipping) if self._shipping else None,
            **self._product,
            **self._urls,
            **self._extras,
        )
        try:
            resp = self._service.initiate_payment(request)
            return {
                "status": resp.status,
                "sessionkey": resp.session_key,
                "GatewayPageURL": resp.gateway_url,
            }
        except Exception as exc:
            return {"status": "FAILED", "failedreason": str(exc)}
