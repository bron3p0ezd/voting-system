from settings.exceptions import ServiceException


class InvalidAdminPollException(ServiceException):
    pass


class AdminPollNotFoundException(ServiceException):
    pass
