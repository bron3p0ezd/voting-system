from settings.exceptions import ServiceException


class PollNotFoundException(ServiceException):
    pass


class PollUnavailableException(ServiceException):
    pass
