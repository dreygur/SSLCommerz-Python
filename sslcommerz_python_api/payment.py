#!/usr/bin/env python

from typing import Dict
from decimal import Decimal
from uuid import uuid4
import requests
import json

# Internal Import
from sslcommerz_python_api.base import SSLCommerz

class SSLCSession(SSLCommerz):
  def __init__(self,
    sslc_is_sandbox: bool = True,
    sslc_store_id: str = '',
    sslc_store_pass: str = ''
  ) -> None:
    """[summary]

    Args:
      sslc_is_sandbox (bool, optional): Defines to use sandbox api or not. Defaults to True.
      sslc_store_id (str, optional): Store ID from SSLCommerz. Defaults to ''.
      sslc_store_pass (str, optional): Store Password for SSLCommerz store. Defaults to ''.
    """
    super().__init__(sslc_is_sandbox, sslc_store_id, sslc_store_pass)

  def set_urls(self,
    success_url: str,
    fail_url: str,
    cancel_url: str,
    ipn_url: str = ''
  ) -> None:
    """Sets urls for IPN

    Args:
      success_url (str): Success URL
      fail_url (str): Fail URL
      cancel_url (str): Cancel  URL
      ipn_url (str, optional): IPN URL. Defaults to ''.
    """
    self.integration_data.update({
      'success_url': success_url,
      'fail_url': fail_url,
      'cancel_url': cancel_url,
      'ipn_url': ipn_url,
    })

  def set_product_integration(self,
    total_amount: Decimal,
    currency: str,
    product_category: str,
    product_name: str,
    num_of_item: int,
    shipping_method: str,
    product_profile: str='None'
  ) -> None:
    """Set Product Integtration

    Args:
      total_amount (Decimal): Total Amount
      currency (str): Currency
      product_category (str): Peoduct's Category
      product_name (str): Product's Name
      num_of_item (int): Number of items
      shipping_method (str): Shipping Method
      product_profile (str, optional): Product's Description. Defaults to 'None'.
    """
    self.integration_data.update({
      'store_id': self.sslc_store_id,
      'store_passwd': self.sslc_store_pass,
      'tran_id': str(uuid4()),
      'total_amount': total_amount,
      'currency': currency,
      'product_category': product_category,
      'product_name': product_name,
      'num_of_item': num_of_item,
      'shipping_method': shipping_method,
      'product_profile': product_profile,
    })

  def set_customer_info(self,
    name: str,
    email: str,
    address1: str,
    city: str,
    postcode: str,
    country: str,
    phone: str,
    address2: str=''
  ) -> None:
    """[summary]

    Args:
      name (str): Customer's Name
      email (str): Customer's E-mail
      address1 (str): Address
      city (str): City
      postcode (str): Postcode
      country (str): Country
      phone (str): Phone/Mobile Number
      address2 (str, optional): Optional Address. Defaults to ''.
    """
    self.integration_data.update({
      'cus_name': name,
      'cus_email': email,
      'cus_add1': address1,
      'cus_add2': address2,
      'cus_city': city,
      'cus_postcode': postcode,
      'cus_country': country,
      'cus_phone': phone,
    })

  def set_shipping_info(self,
    shipping_to: str,
    address: str,
    city: str,
    postcode: str,
    country: str
  ) -> None:
    """Shipping Address

    Args:
      shipping_to (str): Customer's Name
      address (str): Address
      city (str): City
      postcode (str): Postcode
      country (str): Country
    """
    self.integration_data.update({
      'ship_name': shipping_to,
      'ship_add1': address,
      'ship_city': city,
      'ship_postcode': postcode,
      'ship_country': country,
    })

  def set_additional_values(self,
    value_a: str = '',
    value_b: str = '',
    value_c: str = '',
    value_d: str = ''
  ) -> None:
    """Additional Values

    Args:
      value_a (str, optional): Additional Value. Defaults to ''.
      value_b (str, optional): Additional Value. Defaults to ''.
      value_c (str, optional): Additional Value. Defaults to ''.
      value_d (str, optional): Additional Value. Defaults to ''.
    """
    self.integration_data.update({
      'value_a': value_a,
      'value_b': value_b,
      'value_c': value_c,
      'value_d': value_d,
    })

  def init_payment(self) -> Dict:
    """Initialize the Payment

    Returns:
        Dict: Response From SSLCommerz API
    """
    post_url: str = self.sslc_session_api
    post_data: Dict = self.integration_data
    response_sslc = requests.post(post_url, post_data)
    response_data: Dict[str, str] = {}

    if response_sslc.status_code == 200:
      response_json = json.loads(response_sslc.text)
      if response_json['status'] == 'FAILED':
        response_data.update({
          'status': response_json['status'],
          'failedreason': response_json['failedreason'],
        })
        return response_data

      response_data.update({
        'status': response_json['status'],
        'sessionkey': response_json['sessionkey'],
        'GatewayPageURL': response_json['GatewayPageURL'],
      })

      return response_data

    response_json = json.loads(response_sslc.text)
    response_data.update({
      'status': response_json['status'],
      'failedreason': response_json['failedreason'],
    })

    return response_data