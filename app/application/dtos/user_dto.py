from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    role: str
    is_active: bool


@dataclass
class LoginResponseDTO:
    access_token: str
    token_type: str = "Bearer"
