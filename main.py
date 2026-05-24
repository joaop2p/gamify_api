from config.config import Config
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from src.routes.auth import router as auth_router

app = FastAPI(title="Gamify", description="API for Gamify application", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=Config().get_env("API_KEY"))
app.include_router(auth_router, prefix='/v1')