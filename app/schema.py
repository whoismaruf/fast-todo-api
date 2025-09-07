from pydantic import BaseModel, Field
from typing import List, Optional


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, min_length=3, max_length=300)
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, Bread, Eggs, Butter",
                "priority": 2,
                "completed": False,
            }
        }
    }


class TodoResponse(TodoRequest):
    id: int
    owner_id: int

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=5, max_length=55)
    username: str = Field(min_length=3, max_length=30)
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=20)
    role: Optional[str] = Field(default="user")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "username": "adminuser",
                "first_name": "Admin",
                "last_name": "User",
                "password": "strongpassword",
                "role": "user",
            }
        }
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: Optional[str]
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    role: str

    model_config = {"from_attributes": True}


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=20)
    new_password: str = Field(min_length=6, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "strongpassword",
                "new_password": "newstrongpassword",
            }
        }
    }
