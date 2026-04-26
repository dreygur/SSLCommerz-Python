from __future__ import annotations

import hashlib
import logging

from .exceptions import SSLCommerzAPIError, SSLCommerzValidationError
from .models import PaymentRequest, PaymentResponse, ValidationResponse
from .repository import AbstractSSLCommerzRepository, SSLCommerzRepository

logger = logging.getLogger(__name__)


class SSLCommerzService:
    """Primary interface for SSLCommerz payment and validation operations.

    Orchestrates repository calls, interprets API responses, and raises
    typed domain exceptions on failure. Accepts a repository instance so
    the HTTP layer can be swapped out in tests.

    Use SSLCommerzService.create() for normal instantiation. Inject a
    custom AbstractSSLCommerzRepository via __init__ for testing.
    """

    def __init__(
        self,
        repository: AbstractSSLCommerzRepository,
        store_pass: str = "",
    ) -> None:
        """Initialize with a repository and store password.

        Args:
            repository: Repository implementation handling HTTP calls.
            store_pass: Store password used for IPN signature verification.
        """
        self._repo = repository
        self._store_pass = store_pass

    @classmethod
    def create(
        cls,
        store_id: str,
        store_pass: str,
        is_sandbox: bool = True,
        timeout: int = 30,
    ) -> SSLCommerzService:
        """Factory method for normal library usage.

        Constructs an SSLCommerzRepository internally — no need to
        instantiate it manually.

        Args:
            store_id: SSLCommerz store ID credential.
            store_pass: SSLCommerz store password credential.
            is_sandbox: Use sandbox endpoint if True, live endpoint if False.
            timeout: HTTP request timeout in seconds. Defaults to 30.

        Returns:
            A fully configured SSLCommerzService instance.
        """
        repo = SSLCommerzRepository(
            store_id=store_id,
            store_pass=store_pass,
            is_sandbox=is_sandbox,
            timeout=timeout,
        )
        return cls(repo, store_pass=store_pass)

    def initiate_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Initiate a payment session with SSLCommerz.

        Args:
            request: A fully constructed PaymentRequest dataclass.

        Returns:
            PaymentResponse with session_key and gateway_url on success.

        Raises:
            SSLCommerzAPIError: If the HTTP request fails or SSLCommerz
                returns status == "FAILED".
        """
        raw = self._repo.initiate_payment(request)
        if raw.get("status") == "FAILED":
            reason = raw.get("failedreason", "Unknown error")
            logger.warning("SSLCommerz payment initiation failed: %s", reason)
            raise SSLCommerzAPIError(
                f"SSLCommerz payment initiation failed: {reason}",
                reason=reason,
            )
        return PaymentResponse(
            status=raw["status"],
            session_key=raw.get("sessionkey", ""),
            gateway_url=raw.get("GatewayPageURL", ""),
        )

    def validate_transaction(self, val_id: str) -> ValidationResponse:
        """Validate a completed transaction by its validation ID.

        Args:
            val_id: The val_id returned by SSLCommerz in the IPN or redirect.

        Returns:
            ValidationResponse with status and full raw data dict.

        Raises:
            SSLCommerzValidationError: If val_id is empty or the transaction
                status is not "VALIDATED".
            SSLCommerzAPIError: If the HTTP request fails.
        """
        if not val_id:
            raise SSLCommerzValidationError("val_id must not be empty")
        raw = self._repo.validate_transaction(val_id)
        status = raw.get("status", "UNKNOWN")
        if status != "VALIDATED":
            logger.warning("Transaction %s not validated, status=%s", val_id, status)
            raise SSLCommerzValidationError(
                f"Transaction validation failed with status: {status}",
                val_id=val_id,
            )
        return ValidationResponse(status=status, data=raw)

    def verify_ipn(self, ipn_data: dict) -> bool:
        """Verify the IPN (Instant Payment Notification) signature locally.

        Recomputes the MD5 signature from the received IPN fields and
        compares it against the verify_sign field. No network call is made.

        Args:
            ipn_data: The POST body dict received from the SSLCommerz webhook.

        Returns:
            True if the signature matches.

        Raises:
            SSLCommerzValidationError: If verify_key or verify_sign are missing,
                or if the computed signature does not match verify_sign.
        """
        if "verify_key" not in ipn_data or "verify_sign" not in ipn_data:
            raise SSLCommerzValidationError(
                "IPN data missing required fields: verify_key and/or verify_sign"
            )
        store_pass_hash = hashlib.md5(self._store_pass.encode()).hexdigest()
        check_params: dict[str, str] = {
            key: ipn_data[key]
            for key in ipn_data["verify_key"].split(",")
        }
        check_params["store_passwd"] = store_pass_hash
        sign_string = "&".join(f"{k}={v}" for k, v in sorted(check_params.items()))
        computed_hash = hashlib.md5(sign_string.encode()).hexdigest()
        if computed_hash != ipn_data["verify_sign"]:
            raise SSLCommerzValidationError("IPN signature mismatch — possible tampering")
        return True
