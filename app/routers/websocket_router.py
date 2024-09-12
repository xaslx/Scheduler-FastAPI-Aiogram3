import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List

websocket_router: APIRouter = APIRouter()


class UserCounter:
    def __init__(self):
        self.sockets: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.sockets.append(websocket)
        await self._send_count()

    async def disconnect(self, websocket: WebSocket):
        self.sockets.remove(websocket)
        await self._send_count()

    async def _send_count(self):
        if self.sockets:
            count_str = str(len(self.sockets))
            task_to_socket = {
                asyncio.create_task(websocket.send_text(count_str)): websocket
                for websocket in self.sockets
            }

            if task_to_socket:
                done, pending = await asyncio.wait(task_to_socket)
                for task in done:
                    if task.exception() is not None:
                        websocket = task_to_socket[task]
                        if websocket in self.sockets:
                            self.sockets.remove(websocket)


counter: UserCounter = UserCounter()


@websocket_router.websocket("/counter")
async def websocket_endpoint(websocket: WebSocket):
    await counter.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await counter.disconnect(websocket)
