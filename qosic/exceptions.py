class ServerError(Exception):
    """Occurs when the qos server is busy or fails for some reason"""


class UserAccountNotFound(Exception):
    pass


class ProviderNotFoundError(Exception):
    pass


class InvalidPhoneError(Exception):
    pass


class RequestError(Exception):
    pass


class InvalidClientIdError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class PollRuntimeError(Exception):
    """Exception raised if polling function fails. Polling is used in the case
    of an MTN payment requets to get the status of the payment"""
