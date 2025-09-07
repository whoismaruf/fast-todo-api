from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.dependencies import get_current_user, get_db
from app.schema import TodoResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(
    user: user_dependency,
    db: db_dependency,
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).all()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if user.get("id") == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete current user")
    user_model = db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_model)
    db.commit()
    return "Successfully deleted"


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.Todo).all()


@router.get(
    "/todos/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse
)
async def get_todo_by_id(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()  # type: ignore
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()  # type: ignore
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
    return "Successfully deleted"
