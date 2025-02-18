class TemporaryError(Exception):
    """exception type for temporary errors (e.g. a timeout)"""
    def __init__(self, message):
        self.message = message
    
class PermanentError(Exception):
    """exception type for permanent errors (e.g. invalid argument or resource not found)"""
    def __init__(self, message):
        self.message = message

class InternalError(Exception):
    """
    exception type for errors that should not appear during normal
    operation (invalid state / got invalid data from greenbone)
    """
    def __init__(self, message):
        self.message = message
