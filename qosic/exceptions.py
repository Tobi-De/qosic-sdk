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
