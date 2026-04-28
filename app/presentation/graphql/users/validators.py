from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

SafeUsername = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
]

class CreateUserInputValidator(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    username: SafeUsername
    email: EmailStr
    role: Literal["USER", "ADMIN"] = "USER"
    is_active: bool = True


class LoginInputValidator(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    username: SafeUsername
    email: EmailStr
