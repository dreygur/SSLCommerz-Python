from __future__ import annotations


class SSLCommerzError(Exception):
    """Base exception for all SSLCommerz library errors.

    Catch this to handle any error raised by the library without
    distinguishing between API failures and validation failures.
    """


class SSLCommerzAPIError(SSLCommerzError):
    """Raised when an HTTP request to SSLCommerz fails or the API returns an error.

    Covers both network-level failures (connection error, timeout) and
    API-level failures (HTTP 200 but status == "FAILED").

    Attributes:
        status_code: HTTP status code, if available.
        reason: The failedreason string returned by SSLCommerz, if available.
    """

    def __init__(self, message: str, status_code: int | None = None, reason: str = "") -> None:
        """Initialize with a message and optional HTTP status code and reason.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code from the failed response, if any.
            reason: The failedreason field from the SSLCommerz response, if any.
        """
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason


class SSLCommerzValidationError(SSLCommerzError):
    """Raised when IPN signature verification or transaction validation fails.

    Attributes:
        val_id: The transaction validation ID involved, if applicable.
    """

    def __init__(self, message: str, val_id: str = "") -> None:
        """Initialize with a message and optional validation ID.

        Args:
            message: Human-readable error description.
            val_id: The val_id that failed validation, if applicable.
        """
        super().__init__(message)
        self.val_id = val_id
