#!/usr/bin/env python

import hashlib
import requests
from typing import Dict

# Internal Import
from sslcommerz_python_api.base import SSLCommerz

class Validation(SSLCommerz):
  def __init__(self, sslc_is_sandbox=True, sslc_store_id='', sslc_store_pass='') -> None:
    super().__init__(sslc_is_sandbox, sslc_store_id, sslc_store_pass)

  def validate_transaction(self, validation_id):
    """Validate the Transaction with validation_id from SSLCommerz

    Args:
      validation_id (str): Validation ID from SSLCommerz

    Returns:
      dict: Validation Status
    """
    query_params: Dict[str, str] = {}
    response_data: Dict[str, str] = {}
    query_params['val_id'] = validation_id
    query_params['store_id'] = self.sslc_store_id
    query_params['store_passwd'] = self.sslc_store_pass
    query_params['format'] = 'json'

    validation_response = requests.get(
      self.sslc_validation_api,
      params=query_params
    )

    if validation_response.status_code == 200:
      validation_json = validation_response.json()
      if validation_json['status'] == 'VALIDATED':
        response_data['status'] = 'VALIDATED'
        response_data['data'] = validation_json
      else:
        response_data['status'] = validation_json['status']
        response_data['data'] = validation_json
    else:
      response_data['status'] = 'FAILED'
      response_data['data'] = 'Validation failed due to status code ' + str(validation_response.status_code)
    return response_data

  def validate_ipn_hash(self, ipn_data):
    if self.key_check(ipn_data, 'verify_key') and self.key_check(ipn_data, 'verify_sign'):
      check_params: Dict[str, str] = {}
      verify_key = ipn_data['verify_key'].split(',')

      for key in verify_key:
        check_params[key] = ipn_data[key]

      store_pass = self.sslc_store_pass.encode()
      store_pass_hash = hashlib.md5(store_pass).hexdigest()
      check_params['store_passwd'] = store_pass_hash
      check_params = self.sort_keys(check_params)

      sign_string = ''
      for key in check_params:
        sign_string += key[0] + '=' + str(key[1]) + '&'

      sign_string = sign_string.strip('&')
      sign_string_hash = hashlib.md5(sign_string.encode()).hexdigest()

      if sign_string_hash == ipn_data['verify_sign']:
        return True
      return False

  @staticmethod
  def key_check(data_dict, check_key):
    if check_key in data_dict.keys():
      return True
    return False

  @staticmethod
  def sort_keys(data_dict):
    return [(key, data_dict[key]) for key in sorted(data_dict.keys())]
