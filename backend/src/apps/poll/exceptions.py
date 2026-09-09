from settings.exceptions import ServiceException


class PollNotFoundException(ServiceException):
    pass


class PollUnavailableException(ServiceException):
    pass


class InvalidVoteException(ServiceException):
    pass


class DuplicateVoteException(ServiceException):
    pass


class InvalidParticipantTokenException(ServiceException):
    pass
