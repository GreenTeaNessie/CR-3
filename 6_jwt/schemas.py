from pydantic import BaseModel
from typing import Literal

Role = Literal["admin", "user", "guest"]


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: Role
