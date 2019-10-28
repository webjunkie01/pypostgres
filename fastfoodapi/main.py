import json
import asyncio
import aiopg
from starlette.endpoints import WebSocketEndpoint
from fastapi import Depends, FastAPI, HTTPException
from starlette.websockets import WebSocket
from pydantic import BaseModel


dsn = "dbname=fast_food_db user=food_user password=password host=127.0.0.1"

app = FastAPI()

#pydantic model 
class Order(BaseModel):
    name: str
    price: float
    quantity: int
    id: int


@app.websocket_route("/order_events")
class WebSocketOrders(WebSocketEndpoint):

    encoding = "json"

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive, send)
        self.connected: bool = False
        self.loop = asyncio.get_event_loop()
        self.websocket: WebSocket = {}

    @asyncio.coroutine
    async def listen(self, conn, channel):
        async with conn.cursor() as cur:
            await cur.execute("LISTEN {0}".format(channel))
            while self.connected:
                msg = await conn.notifies.get()
                payload: dict = json.loads(msg.payload)
                if payload.get("action") == "INSERT":
                    insert_data: Order = payload.get("data")
                    await self.websocket.send_json(
                        {"message": "New order", "data": insert_data}
                    )
                elif payload.get("action") == "UPDATE":
                    update_data: Order = payload.get("data")
                    await self.websocket.send_json(
                        {"message": "Order update", "data": update_data}
                    )

    @asyncio.coroutine
    async def db_events(self, data: dict, channel: str):
        async with aiopg.create_pool(dsn) as pool:
            async with pool.acquire() as conn:
                try:
                    await asyncio.gather(
                        self.listen(conn, channel), return_exceptions=False
                    )
                except:
                    print("releasing connection")

    async def on_receive(self, websocket: WebSocket, data: dict):
        channel: str = data.get("channel")
        asyncio.ensure_future(self.db_events(data, channel), loop=self.loop)

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connected = True
        self.websocket = websocket
        await self.websocket.send_json({"message": "Welcome"})

    async def on_close(self, websocket):
        self.connected = False
        self.loop.close()
        self.websocket.close()
