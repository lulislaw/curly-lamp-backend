import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.websocket import router as ws_router
from app.settings.config import settings
from app.database import get_db

from app.routes.camera_hardware import router as camera_router
from app.routes.appeal import router as appeal_router
from app.routes.reference import router as reference_router
from app.routes.export import router as export_router
from app.routes.images import router as images_router
from fastapi.staticfiles import StaticFiles
from app.routes import building_config

app = FastAPI(title="Appeals Service", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appeal_router)

app.include_router(reference_router)
app.include_router(ws_router)
app.include_router(camera_router)
app.include_router(export_router)
app.include_router(images_router)
app.include_router(building_config.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
