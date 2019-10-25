import json
import asyncio
import aiopg
from starlette.endpoints import WebSocketEndpoint
from fastapi import Depends, FastAPI, HTTPException
from starlette.websockets import WebSocket

dsn = "dbname=fast_food_db user=food_user password=password host=127.0.0.1"

app = FastAPI()


@app.websocket_route("/order_events")
class WebSocketOrders(WebSocketEndpoint):
    
    encoding = "json"
    
    def __init__(self, scope, receive, send):
        super().__init__(scope, receive, send)
        self.connected = False
        self.loop = asyncio.get_event_loop()
        self.websocket = {}

    @asyncio.coroutine
    async def listen(self, conn, channel):
        
        async with conn.cursor() as cur:
            await cur.execute("LISTEN {0}".format(channel))
            while True:

                msg = await conn.notifies.get()
                payload = json.loads(msg.payload)

                if payload.get("action") == "INSERT":
                    await self.websocket.send_json(
                        {"message": "New order", "data": payload.get("data")}
                    )
                elif payload.get("action") == "UPDATE":
                    await self.websocket.send_json(
                        {"message": "Order update", "data": payload.get("data")}
                    )

    async def db_events(self, data: dict, websocket: WebSocket, channel: str):
        async with aiopg.create_pool(dsn) as pool:
            async with pool.acquire() as conn:
                await asyncio.gather(self.listen(conn, channel))

    async def on_receive(self, websocket: WebSocket, data: dict):
        channel: str = data.get("channel")
        asyncio.ensure_future(self.db_events(data, websocket, channel), loop=self.loop)


    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connected = True
        self.websocket = websocket
        await self.websocket.send_json({"message": "Welcome", "data": {}})
        

    async def on_close(self, websocket):
        self.connected = False
        self.websocket.close()
        websocket.close()
