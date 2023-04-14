class ServerError(Exception):
    pass


class UserAccountNotFoundError(Exception):
    pass


class MobileCarrierNotFoundError(Exception):
    pass


class FeatureNotImplementedError(NotImplementedError):
    pass


class InvalidPhoneNumberError(Exception):
    pass


class InvalidProviderIDError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
