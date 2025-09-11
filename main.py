import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from dotenv import load_dotenv

from app import models
from app.routers.auth import router as auth_router
from app.routers.todos import router as todos_router
from app.routers.admin import router as admin_router
from app.database import engine

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Todo Application",
    description="A simple Todo application with user authentication and admin management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},  # hides schema section
)

# Add CORS middleware
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(admin_router)
