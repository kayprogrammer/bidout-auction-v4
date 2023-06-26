from http import HTTPStatus
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.common.responses import CustomResponse


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class RequestError(Error):
    def __init__(
        self, err_msg: str, status_code: int = 400, data: dict = None, *args: object
    ) -> None:
        self.status_code = HTTPStatus(status_code)
        self.err_msg = err_msg
        self.data = data

        super().__init__(*args)


def custom_exception_handler(exc, context):
    try:
        response = exception_handler(exc, context)
        if isinstance(exc, AuthenticationFailed):
            exc_list = str(exc).split("DETAIL: ")
            return CustomResponse.error(message=exc_list[-1], status_code=401)
        elif isinstance(exc, RequestError):
            print(exc)
            return CustomResponse.error(message="Invalid Entry", data=exc.detail)
        elif isinstance(exc, ValidationError):
            errors = exc.detail
            for key in errors:
                errors[key] = str(errors[key][0])
            return CustomResponse.error(
                message="Invalid Entry", data=errors, status_code=422
            )
        else:
            return CustomResponse.error(
                message=exc.detail if hasattr(exc, "detail") else exc,
                status=response.status_code,
            )
    except:
        print(exc)
        return CustomResponse.error(message="Server Error", status_code=500)


# def request_error_handler(_: Request, exc: RequestError):
#     err_dict = {
#         "status": "failure",
#         "message": exc.err_msg,
#     }
#     if exc.data:
#         err_dict["data"] = exc.data
#     return Response(status_code=exc.status_code, content=err_dict)
