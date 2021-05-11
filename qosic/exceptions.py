from httpx import Request


class ProviderNotFoundError(Exception):
    def __init__(self, phone: str):
        message = f"{phone}: A valid provider was not found for the given phone number"
        super().__init__(message)


class InvalidPhoneNumberError(Exception):
    def __init__(self, phone: str):
        message = f"{phone} : Invalid phone number"
        super().__init__(message)


class RequestError(Exception):
    def __init__(self, request: Request):
        message = f"An error occurred while requesting {repr(request.url)}."
        super().__init__(message)


class InvalidCredentialError(Exception):
    def __init__(self, message="Your credentials are invalid"):
        super().__init__(message)


class PollRuntimeError(Exception):
    """Exception raised if polling function fails"""


class PollTimeoutError(Exception):
    """Exception raised if polling function times out"""

    def __init__(self, values):
        message = f"result : {values}"
        super().__init__(message)
