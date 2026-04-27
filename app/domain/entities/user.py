from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    username: str
    email: str
    role: str
    is_active: bool
