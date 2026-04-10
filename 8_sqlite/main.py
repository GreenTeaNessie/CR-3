import sqlite3
from fastapi import FastAPI, HTTPException, status
from .schemas import UserCreate
from .database import get_connection
from .init_db import init_db

app = FastAPI()

init_db()


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    finally:
        conn.close()
    return {"message": f"User '{user.username}' registered successfully"}
