from rest_framework.permissions import BasePermission
from apps.accounts.auth import Authentication
from uuid import UUID

from apps.common.exceptions import RequestError


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        http_auth = request.META.get("HTTP_AUTHORIZATION")
        if not http_auth:
            raise RequestError(err_msg="Auth Bearer not provided!", status_code=401)
        user = Authentication.decodeAuthorization(http_auth)
        if not user:
            raise RequestError(
                err_msg="Auth token invalid or expired!", status_code=401
            )
        request.user = user
        if request.user and request.user.is_authenticated:
            return True
        return False


def is_uuid(value):
    try:
        return str(UUID(value))
    except:
        return None
