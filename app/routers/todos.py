from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.dependencies import get_db, get_current_user
from app.schema import TodoRequest, TodoResponse

router = APIRouter(
    tags=["Todos"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
    return db.query(models.Todo).filter(models.Todo.owner_id == user.get("id")).all()  # type: ignore


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == user.get("id"))  # type: ignore
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = models.Todo(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == user.get("id"))  # type: ignore
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)
    db.add(todo_model)
    db.commit()
    return todo_model


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id)  # type: ignore
        .filter(models.Todo.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todo).filter(
        models.Todo.id == todo_id, models.Todo.owner_id == user.get("id")  # type: ignore
    ).delete()
    db.commit()
    return None
