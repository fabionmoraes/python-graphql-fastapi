from strawberry.types import Info

from app.core.container import Container


def get_container_from_context(info: Info) -> Container:
    return info.context["container"]
