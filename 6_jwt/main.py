from fastapi import FastAPI, HTTPException, Request, status, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .schemas import UserCreate, UserLogin, Token, UserInDB
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
    users_db,
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role,
    )
    return {"message": f"User '{user.username}' registered successfully"}


@app.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, credentials: UserLogin):
    user = users_db.get(credentials.username)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(user.username, user.role)
    return Token(access_token=token)


@app.get("/protected_resource")
def protected_resource(user: UserInDB = Depends(get_current_user)):
    return {"message": f"Hello, {user.username}! You have access.", "role": user.role}


@app.get("/admin")
def admin_only(user: UserInDB = Depends(require_role("admin"))):
    return {"message": f"Welcome, admin {user.username}!"}


@app.get("/user")
def user_and_admin(user: UserInDB = Depends(require_role("admin", "user"))):
    return {"message": f"Welcome, {user.username}! Role: {user.role}"}


@app.get("/guest")
def all_roles(user: UserInDB = Depends(require_role("admin", "user", "guest"))):
    return {"message": f"Welcome, {user.username}! Role: {user.role}"}
