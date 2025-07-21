# backend/app/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.websocket import router as ws_router
from app.settings.config import settings
from app.database import get_db
from app.routes.camera_hardware import router as camera_router
# Подключаем роутеры
from app.routes.appeal import router as appeal_router
from app.routes.reference import router as reference_router
from app.routes.export import router as export_router
from app.routes.images import router as images_router
from fastapi.staticfiles import StaticFiles
from app.routes import building_config
app = FastAPI(title="Appeals Service", version="1.0.0")

# Если фронтенд на http://localhost:5173, разрешаем CORS
origins = [
    "http://localhost:5173",  # адрес вашего Vite-фронтенда
    # Если вы хотите тестировать с http://127.0.0.1:5173, тоже можно добавить:
    "http://127.0.0.1:5173",
    # Можно указать "*" для разработки, но НЕ РЕКОМЕНДУЕТСЯ в проде:
    # "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # какие Origin разрешены
    allow_credentials=True,
    allow_methods=["*"],              # разрешить все HTTP-методы (GET, POST, PATCH, DELETE и т. д.)
    allow_headers=["*"],              # разрешить все заголовки
)
# Регистрируем роутер для сущности Appeal
app.include_router(appeal_router)

# Регистрируем роутер для справочников
app.include_router(reference_router)
app.include_router(ws_router)
app.include_router(camera_router)
app.include_router(export_router)
app.include_router(images_router)
app.include_router(building_config.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
