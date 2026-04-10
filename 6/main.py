import secrets
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .schemas import UserCreate, UserInDB
from .security import hash_password, get_current_user, users_db
from .settings import MODE, DOCS_USER, DOCS_PASSWORD

# Configure docs visibility based on MODE
if MODE == "PROD":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI()


# --- Task 6.3: protect /docs and /openapi.json in DEV mode ---
if MODE == "DEV":
    docs_auth = HTTPBasic()

    @app.middleware("http")
    async def protect_docs(request: Request, call_next):
        if request.url.path in ("/docs", "/openapi.json", "/redoc"):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Basic "):
                return JSONResponse(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                    content={"detail": "Docs access requires authentication"},
                )
            import base64
            try:
                decoded = base64.b64decode(auth[6:]).decode()
                username, password = decoded.split(":", 1)
            except Exception:
                return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
            user_ok = secrets.compare_digest(username, DOCS_USER)
            pass_ok = secrets.compare_digest(password, DOCS_PASSWORD)
            if not (user_ok and pass_ok):
                return JSONResponse(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                    content={"detail": "Invalid credentials"},
                )
        return await call_next(request)


# --- Task 6.2: register ---
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    return {"message": f"User '{user.username}' registered successfully"}


# --- Task 6.1 / 6.2: login with Basic Auth ---
@app.get("/login")
def login(username: str = Depends(get_current_user)):
    return {"message": "You got my secret, welcome"}
