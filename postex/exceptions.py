class UserDoesNotExist(Exception):
    """
    Api token is invalid or expired
    """
    pass

class UserNotActive(Exception):
    """
    Your account is not usable. contact with postex support
    """
    pass
