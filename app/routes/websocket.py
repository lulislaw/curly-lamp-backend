# backend/app/routes/ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws_manager import manager

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)

@router.websocket("/appeals")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для real-time обновлений списка обращений.
    Клиенты будут подключаться к ws://<host>:<port>/ws/appeals,
    а мы в цикле держим соединение, пока клиент не отключится.
    """
    # Регистрируем подключение в менеджере
    await manager.connect(websocket)
    try:
        while True:
            # Ожидаем входящие сообщения от клиента (например, пинги).
            # В нашем случае клиент ничего не шлёт, но всё равно нужно
            # «чтобы WebSocket соединение оставалось живым».
            await websocket.receive_text()
            # Если вы хотите обрабатывать сообщения от клиента,
            # можно здесь разбить JSON и делать что-то.
    except WebSocketDisconnect:
        # Как только клиент отключился, убираем его из списка
        manager.disconnect(websocket)
