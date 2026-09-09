class AppBaseException(Exception):
    pass


class ServiceException(AppBaseException):
    pass


class RepositoryException(AppBaseException):
    pass
