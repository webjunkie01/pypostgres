from fastapi import FastAPI
from starlette.testclient import TestClient
from starlette.websockets import WebSocket
from main import app, WebSocketOrders
import json
from starlette.endpoints import WebSocketEndpoint
import websockets



json_args = {"method":"subscribe","channel": "orders" }

# async def app(scope, receive, send):
#     assert scope['type'] == 'websocket'
#     websocket = WebSocket(scope, receive=receive, send=send)
#     await websocket.accept()
#     await websocket.send_json(json_args)
#     await websocket.close()

client = TestClient(app)

def test_connection():
    with client.websocket_connect("ws://localhost:8000/order_events") as websocket:
        o = WebSocketOrders(websocket.scope,websocket.receive,websocket.send)
        data = websocket.receive_json()
        assert data.get('message') == 'Welcome'

#TODO
def test_subscription():
    with client.websocket_connect("ws://localhost:8000/order_events") as websocket:
        data = websocket.send_json(json_args)
        websocket.close()
        assert True



