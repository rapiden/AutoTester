class Error(Exception):
    """"Base class for exceptions."""

    @staticmethod
    def exception_hook(exception_type, value, traceback):
        print(f'Uncaught Exception.\nException type: {exception_type}\nMessage: {value}')


class ParameterError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, parameter: str, message: str) -> None:
        self.parameter = parameter
        self.message = message


class TestError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, parameter: str, message: str) -> None:
        self.parameter = parameter
        self.message = message


class GDTConnectionError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class ActionAlreadyExistsError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class ActionDoesNotExistError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class SimEngineConnectionError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class SimEngineInjectionError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class ImageComparatorError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class SVNError(Error):
    """Exception raised for invalid parameters passed to a function.

    Attributes:
        parameter -- the parameter in which the error occurred.
        message -- explanation of the error.
    """

    def __init__(self, parameter: str, message: str) -> None:
        self.parameter = parameter
        self.message = message
