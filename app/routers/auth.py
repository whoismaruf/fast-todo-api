from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.dependencies import (
    bcrypt_context,
    create_access_token,
    authenticate_user,
    get_current_user,
    get_db,
)
from app.models import User
from app.schema import (
    CreateUserRequest,
    TokenResponse,
    PasswordChangeRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, user_request: CreateUserRequest):
    existing_user = (
        db.query(User)
        .filter((User.email == user_request.email) | (User.username == user_request.username))  # type: ignore
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email or username already registered"
        )
    user_model = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True,
        role=user_request.role if hasattr(user_request, "role") else "user",
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_user(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=30),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_me(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get("id")).first()  # type: ignore
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model


@router.post("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    db: db_dependency,
    current_user: Annotated[dict, Depends(get_current_user)],
    password_change: PasswordChangeRequest,
):
    user_model = db.query(User).filter(User.id == current_user.get("id")).first()  # type: ignore
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(
        password_change.old_password, user_model.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user_model.hashed_password = bcrypt_context.hash(password_change.new_password)
    db.add(user_model)
    db.commit()
    return {"msg": "Password updated successfully"}
