#!/usr/bin/env python

class SSLCommerz:
  def __init__(self,
    sslc_is_sandbox: bool = True,
    sslc_store_id: str    = '',
    sslc_store_pass: str  = ''
  ) -> None:
    """Creates a session

    Args:
      sslc_is_sandbox (bool, optional): Sandbox or live api. Defaults to True.
      sslc_store_id (str, optional): Store ID.
      sslc_store_pass (str, optional): Store Password.
    """
    # Configurations
    self.SSLCZ_SESSION_API = 'sslcommerz.com/gwprocess/v4/api.php'
    self.SSLCZ_VALIDATION_API = 'sslcommerz.com/validator/api/validationserverAPI.php'
    self.sslc_mode_name = self.set_sslcommerz_mode(sslc_is_sandbox)
    self.sslc_is_sandbox = sslc_is_sandbox
    self.sslc_store_id = sslc_store_id
    self.sslc_store_pass = sslc_store_pass
    self.sslc_session_api = 'https://' + self.sslc_mode_name + '.' + self.SSLCZ_SESSION_API
    self.sslc_validation_api = 'https://' + self.sslc_mode_name + '.' + self.SSLCZ_VALIDATION_API
    self.integration_data: Dict[str, str] = {}

  @staticmethod
  def set_sslcommerz_mode(sslc_is_sandbox: bool) -> str:
    """Set status of the api whether sandbox or live

    Args:
        sslc_is_sandbox (bool): True for sandbox api False for the live one

    Returns:
        str: 'sandbox' or 'securepay'
    """
    if sslc_is_sandbox is True or sslc_is_sandbox == 1:
      return 'sandbox'
    return 'securepay'