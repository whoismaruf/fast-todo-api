from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

from app import models
from app.routers.auth import router as auth_router
from app.routers.todos import router as todos_router
from app.routers.admin import router as admin_router
from app.database import engine

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(admin_router)
