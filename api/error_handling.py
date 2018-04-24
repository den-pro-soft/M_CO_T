"""Contains classes related to error handling"""


class BaseApiError(Exception):
    """Base class for API exceptions"""
    status_code = 500

    def __init__(self, payload):
        Exception.__init__(self)
        self.payload = payload

    def to_dict(self):
        """Converts this exception to a dict representation"""
        converted = dict()
        converted['payload'] = self.payload
        return converted


class InvalidUsage(BaseApiError):
    """Exception for simple errors"""
    status_code = 450


class NotAuthorized(BaseApiError):
    """Exception for login related errors"""
    status_code = 403


class MustBeAdmin(BaseApiError):
    """Exception for unauthorized admin API request"""
    status_code = 455

    def __init__(self):
        BaseApiError.__init__(self, "Must be admin")


class InfrastructureError(BaseApiError):
    """Exception for infrastructure problems"""
