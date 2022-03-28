class ServerError(Exception):
    pass


class UserAccountNotFoundError(Exception):
    pass


class ProviderNotFoundError(Exception):
    pass


class InvalidPhoneNumberError(Exception):
    pass


class InvalidProviderIDError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
