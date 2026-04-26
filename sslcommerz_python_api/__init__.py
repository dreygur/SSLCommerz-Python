"""
SSLCommerz Python API

Primary API:
    from sslcommerz_python_api import SSLCommerzService
    from sslcommerz_python_api.models import PaymentRequest, CustomerInfo, ShippingInfo
    from sslcommerz_python_api.exceptions import SSLCommerzError, SSLCommerzAPIError

Deprecated (backward compat):
    from sslcommerz_python_api import SSLCSession
"""

from sslcommerz_python_api.service import SSLCommerzService
from sslcommerz_python_api._compat import SSLCSession
from sslcommerz_python_api import exceptions, models

__all__ = [
    "SSLCommerzService",
    "SSLCSession",
    "exceptions",
    "models",
]
