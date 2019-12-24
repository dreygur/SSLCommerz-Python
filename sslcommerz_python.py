from typing import Dict
from decimal import Decimal
from uuid import uuid4

import _constants as const


class SSLCPayment:
    sslc_is_sandbox : bool
    sslc_store_id : str
    sslc_store_pass : str
    sslc_mode_name : str
    integration_data : Dict[str, str] = {}

    def __init__(self, sslc_is_sandbox=True, sslc_store_id='', sslc_store_pass='') -> None:
        self.sslc_mode_name = self.set_sslcommerz_mode(sslc_is_sandbox)
        self.sslc_is_sandbox = sslc_is_sandbox
        self.sslc_store_id = sslc_store_id
        self.sslc_store_pass = sslc_store_pass
        self.sslc_session_api = 'https://' + self.sslc_mode_name + '.' + const.SSLCZ_SESSION_API
        self.sslc_validation_api = 'https://' + self.sslc_mode_name + '.' + const.SSLCZ_VALIDATION_API

    @staticmethod
    def set_sslcommerz_mode(sslc_is_sandbox: bool) -> str:
        if sslc_is_sandbox is True or sslc_is_sandbox == 1:
            return 'sandbox'
        else:
            return 'securepay'

    def set_user_info(self):
        pass

    def set_integration(self, total_amount: Decimal, currency: str, product_category: str,
                        success_url: str, fail_url: str, cancel_url: str, ipn_url: str='') -> None:
        self.integration_data['store_id'] = self.sslc_store_id
        self.integration_data['store_passwd'] = self.sslc_store_pass
        self.integration_data['tran_id'] = str(uuid4())
        self.integration_data['total_amount'] = total_amount
        self.integration_data['currency'] = currency
        self.integration_data['product_category'] = product_category
        self.integration_data['success_url'] = success_url
        self.integration_data['fail_url'] = fail_url
        self.integration_data['cancel_url'] = cancel_url
        self.integration_data['ipn_url'] = ipn_url