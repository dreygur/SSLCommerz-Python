# SSLCOMMERZ Payment Gateway Python API
[![Downloads](https://static.pepy.tech/personalized-badge/sslcommerz-python-api?period=total&units=international_system&left_color=blue&right_color=grey&left_text=Downloads)](https://pepy.tech/project/sslcommerz-python-api)

Python wrapper for the SSLCommerz payment gateway. Requires Python 3.10+.

## Installation

```sh
pip install sslcommerz-python-api
```

or from git

```sh
pip install git+https://github.com/dreygur/SSLCommerz-Python.git
```

## Usage

### Initiate Payment

```python
from decimal import Decimal
from uuid import uuid4

from sslcommerz_python_api import SSLCommerzService
from sslcommerz_python_api.models import CustomerInfo, PaymentRequest, ShippingInfo

service = SSLCommerzService.create(
    store_id='your_store_id',
    store_pass='your_store_pass',
    is_sandbox=True,
)

request = PaymentRequest(
    store_id='your_store_id',
    store_pass='your_store_pass',
    tran_id=str(uuid4()),
    total_amount=Decimal('20.20'),
    currency='BDT',
    success_url='https://example.com/success',
    fail_url='https://example.com/failed',
    cancel_url='https://example.com/cancel',
    ipn_url='https://example.com/ipn',
    product_name='demo-product',
    product_category='clothing',
    num_of_item=2,
    shipping_method='YES',
    customer=CustomerInfo(
        name='John Doe',
        email='johndoe@email.com',
        address1='demo address',
        address2='demo address 2',
        city='Dhaka',
        postcode='1207',
        country='Bangladesh',
        phone='01711111111',
    ),
    shipping=ShippingInfo(
        ship_name='demo customer',
        address='demo address',
        city='Dhaka',
        postcode='1209',
        country='Bangladesh',
    ),
    value_a='extra-a',
    value_b='extra-b',
)

response = service.initiate_payment(request)
print(response.gateway_url)   # redirect user here
print(response.session_key)
print(response.is_success)    # True / False
```

### Response

On success, `initiate_payment` returns a `PaymentResponse` dataclass:

| Field | Type | Description |
|---|---|---|
| `status` | `str` | `"SUCCESS"` or `"FAILED"` |
| `session_key` | `str` | SSLCommerz session key |
| `gateway_url` | `str` | URL to redirect the user to |
| `is_success` | `bool` | convenience property |

On failure, raises `SSLCommerzAPIError`.

### Validate Transaction

```python
from sslcommerz_python_api.exceptions import SSLCommerzValidationError

try:
    result = service.validate_transaction(val_id='VAL_ID_FROM_IPN')
    print(result.status)   # "VALIDATED"
    print(result.data)     # full raw response dict
except SSLCommerzValidationError as e:
    print(f"Validation failed: {e}")
```

### Verify IPN Signature

```python
# ipn_data = POST body received from SSLCommerz webhook
try:
    service.verify_ipn(ipn_data)
    # signature valid — process the order
except SSLCommerzValidationError:
    # signature mismatch — reject
    pass
```

### Error Handling

```python
from sslcommerz_python_api.exceptions import (
    SSLCommerzAPIError,
    SSLCommerzValidationError,
    SSLCommerzError,
)

try:
    response = service.initiate_payment(request)
except SSLCommerzAPIError as e:
    print(e.reason)        # SSLCommerz failure reason
    print(e.status_code)   # HTTP status code if available
except SSLCommerzError:
    # catch-all for any library error
    pass
```

### Logging

The library logs via Python's standard `logging` module under the `sslcommerz_python_api` namespace.

```python
import logging

# enable for all loggers
logging.basicConfig(level=logging.DEBUG)

# or target just this library
logging.getLogger("sslcommerz_python_api").setLevel(logging.DEBUG)
```

| Level | Events |
|---|---|
| `DEBUG` | HTTP request URL + transaction/val ID before each call |
| `DEBUG` | Response status after each call |
| `WARNING` | Payment initiation failed (FAILED status from API) |
| `WARNING` | Transaction not validated |

## Migration from v1

`SSLCSession` still works but emits a `DeprecationWarning`. Switch to `SSLCommerzService` at your convenience — the old builder API is not planned for removal in the near term.

## Acknowledgements

Fork of [Shahed Mehbub's](https://github.com/shahedex) [sslcommerz-python](https://github.com/shahedex/sslcommerz-payment-gateway-python).
