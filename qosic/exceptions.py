from httpx import Request


class ProviderNotFoundError(Exception):
    def __init__(self, phone: str):
        message = f"{phone}: A valid provider was not found for the given phone number."
        super().__init__(message)


class InvalidPhoneError(Exception):
    def __init__(self, phone: str, message: str = None):
        message = (
            message or f"{phone} : Invalid phone number. Expected format: 299XXXXXXXX"
        )
        super().__init__(message)


class RequestError(Exception):
    def __init__(self, request: Request, message: str = None):
        message = message or f"An error occurred while requesting {repr(request.url)}."
        super().__init__(message)


class InvalidCredentialsError(Exception):
    def __init__(
        self,
        message="Your api credentials are invalid, check back your client instance.",
    ):
        super().__init__(message)


class PollRuntimeError(Exception):
    """Exception raised if polling function fails. Polling is used in the case
    of an MTN payment requets to get the status of the payment"""
