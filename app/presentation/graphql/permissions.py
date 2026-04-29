from strawberry.permission import BasePermission
from strawberry.types import Info

from app.core.security import get_auth_from_header


class IsAuthenticated(BasePermission):
    message = "Unauthorized."

    def has_permission(self, source: object, info: Info, **kwargs: object) -> bool:
        get_auth_from_header(info)
        return True
