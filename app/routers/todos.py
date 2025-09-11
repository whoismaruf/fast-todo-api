from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.dependencies import get_db, get_current_user
from app.schema import TodoRequest, TodoResponse
from app.redis_client import get_cache_service, CacheService

router = APIRouter(
    tags=["Todos"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
cache_dependency = Annotated[CacheService, Depends(get_cache_service)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency, cache: cache_dependency):
    user_id = user.get("id")
    cache_key = f"user_todos:{user_id}"
    
    # Try to get from cache first
    cached_todos = cache.get(cache_key)
    if cached_todos is not None:
        return cached_todos
    
    # If not in cache, get from database
    todos = db.query(models.Todo).filter(models.Todo.owner_id == user_id).all()  # type: ignore
    
    # Serialize todos for caching
    todos_data = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "completed": todo.completed,
            "owner_id": todo.owner_id
        }
        for todo in todos
    ]
    
    # Cache the result
    cache.set(cache_key, todos_data)
    
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, cache: cache_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("id")
    cache_key = f"todo:{todo_id}:{user_id}"
    
    # Try to get from cache first
    cached_todo = cache.get(cache_key)
    if cached_todo is not None:
        return cached_todo
    
    # If not in cache, get from database
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id)  # type: ignore
        .first()
    )
    
    if todo_model is not None:
        # Serialize todo for caching
        todo_data = {
            "id": todo_model.id,
            "title": todo_model.title,
            "description": todo_model.description,
            "priority": todo_model.priority,
            "completed": todo_model.completed,
            "owner_id": todo_model.owner_id
        }
        
        # Cache the result
        cache.set(cache_key, todo_data)
        
        return todo_model
    
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(
    user: user_dependency, db: db_dependency, cache: cache_dependency, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("id")
    todo_model = models.Todo(**todo_request.model_dump(), owner_id=user_id)
    db.add(todo_model)
    db.commit()
    
    # Invalidate user's todos cache after creating new todo
    cache.delete(f"user_todos:{user_id}")
    
    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    cache: cache_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("id")
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id)  # type: ignore
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)
    db.add(todo_model)
    db.commit()
    
    # Invalidate both specific todo cache and user's todos list cache
    cache.delete(f"todo:{todo_id}:{user_id}")
    cache.delete(f"user_todos:{user_id}")
    
    return todo_model


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, cache: cache_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user.get("id")
    todo_model = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id)  # type: ignore
        .filter(models.Todo.owner_id == user_id)
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(models.Todo).filter(
        models.Todo.id == todo_id, models.Todo.owner_id == user_id  # type: ignore
    ).delete()
    db.commit()
    
    # Invalidate both specific todo cache and user's todos list cache
    cache.delete(f"todo:{todo_id}:{user_id}")
    cache.delete(f"user_todos:{user_id}")
    
    return None
