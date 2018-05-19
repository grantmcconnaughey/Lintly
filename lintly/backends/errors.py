
class GitClientError(Exception):
    """Base class for all exceptions while querying Git clients like GitHub or GitLab."""

    def __init__(self, message=None, status_code=None):
        super(GitClientError, self).__init__(message)
        self.status_code = status_code


class UnauthorizedError(GitClientError):
    pass


class NotFoundError(GitClientError):
    pass


class NotSupportedError(GitClientError):
    pass
