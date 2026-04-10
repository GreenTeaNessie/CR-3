from fastapi import FastAPI, HTTPException, status
from .schemas import TodoCreate, TodoUpdate, TodoOut
from .database import get_connection
from .init_db import init_db

app = FastAPI()

init_db()


def _row_to_todo(row) -> TodoOut:
    return TodoOut(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description) VALUES (?, ?)",
        (todo.title, todo.description),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return _row_to_todo(row)


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return _row_to_todo(row)


@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    title = todo.title if todo.title is not None else row["title"]
    description = todo.description if todo.description is not None else row["description"]
    completed = int(todo.completed) if todo.completed is not None else row["completed"]

    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (title, description, completed, todo_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return _row_to_todo(updated)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
