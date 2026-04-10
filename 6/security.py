import secrets
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .schemas import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
basic_security = HTTPBasic()

# In-memory user store: username -> UserInDB
users_db: dict[str, UserInDB] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_current_user(credentials: HTTPBasicCredentials = Depends(basic_security)) -> str:
    user = users_db.get(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Timing-safe comparison via passlib verify (bcrypt is constant-time per hash)
    password_ok = verify_password(credentials.password, user.hashed_password)
    # Also guard against username enumeration with compare_digest on the username
    username_ok = secrets.compare_digest(credentials.username, user.username)
    if not (password_ok and username_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
