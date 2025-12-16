from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app.routes import router
from contextlib import asynccontextmanager

# Создание таблиц при запуске
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы БД созданы/обновлены")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Каёвский API",
    description="API для управления заявками на лабораторные работы",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включаем маршруты
app.include_router(router)

@app.get("/", tags=["root"])
async def read_root():
    """Приветственное сообщение"""
    return {
        "message": "Добро пожаловать в Каёвский API! 📚",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "kayevsky-api"}
