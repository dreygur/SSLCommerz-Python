# SSLCOMMERZ Payment Gateway Python API [![Publish Python Package](https://github.com/dreygur/SSLCommerz-Python/actions/workflows/publish.yml/badge.svg)](https://github.com/dreygur/SSLCommerz-Python/actions/workflows/publish.yml)
Provides a python module to implement payment gateway in python based web apps.

## Installation
Via PIP
```sh
pip install sslcommerz-python-api
```
or
```sh
pip install git+https://github.com/dreygur/SSLCommerz-Python.git
```

## Projected use
```python3
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal

mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id='your_sslc_store_id', sslc_store_pass='your_sslc_store_passcode')

mypayment.set_urls(success_url='example.com/success', fail_url='example.com/failed', cancel_url='example.com/cancel', ipn_url='example.com/payment_notification')

mypayment.set_product_integration(total_amount=Decimal('20.20'), currency='BDT', product_category='clothing', product_name='demo-product', num_of_item=2, shipping_method='YES', product_profile='None')

mypayment.set_customer_info(name='John Doe', email='johndoe@email.com', address1='demo address', address2='demo address 2', city='Dhaka', postcode='1207', country='Bangladesh', phone='01711111111')

mypayment.set_shipping_info(shipping_to='demo customer', address='demo address', city='Dhaka', postcode='1209', country='Bangladesh')

# If you want to post some additional values
mypayment.set_additional_values(value_a='cusotmer@email.com', value_b='portalcustomerid', value_c='1234', value_d='uuid')

response_data = mypayment.init_payment()
```

## Response parameters
### When Successfull with Auth and Payloads provided
- status
- sessionkey
- GatewayPageURL

#### Example
```python
>>> response_data['status']
SUCCESS
>>> response_data['sessionkey']
F650E87F23DD2A8FFCB4E4E333C13B28
>>> response_data['GatewayPageURL']
https://sandbox.sslcommerz.com/EasyCheckOut/testcdef650e87f23dd2a8ffcb4234fasf3b28
```

### When Failed
- status
- failedreason

#### Example
```python
>>> response_data['status']
FAILED
>>> response_data['failedreason']
'Store Credential Error Or Store is De-active'
```