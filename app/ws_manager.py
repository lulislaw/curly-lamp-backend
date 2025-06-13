# backend/app/ws_manager.py

from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        # Список активных WebSocket-подключений
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        При новом подключении: принимаем WebSocket-запрос и добавляем в список.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Убираем WebSocket из списка (клиент断ил соединение).
        """
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        """
        Рассылаем сообщение (json-словарь) всем активным WebSocket-клиентам.
        """
        text_data = json.dumps(message)
        # Преобразуем каждое соединение в строку JSON
        for connection in list(self.active_connections):
            try:
                await connection.send_text(text_data)
            except Exception:
                # Если отправка «упала» (например, соединение разорвано),
                # удаляем этот WebSocket из списка
                self.disconnect(connection)


# Создаём глобальный синглтон-менеджер, чтобы все обработчики могли его использовать
manager = ConnectionManager()
