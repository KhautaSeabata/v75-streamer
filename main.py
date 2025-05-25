import asyncio
import websockets
import json
import uuid
import time
import requests

# Firebase Realtime Database URL
FIREBASE_DB_URL = "https://vix75-f6684-default-rtdb.firebaseio.com"

# Symbol for Vix 150 (1s)
SYMBOL = "R_150"

# Firebase path for ticks
def get_firebase_path(symbol, unique_id):
    return f"/ticks/{symbol}/{unique_id}.json"

# Store tick in Firebase
def store_tick_in_firebase(symbol, tick_time, tick_price):
    unique_id = str(uuid.uuid4())
    path = get_firebase_path(symbol, unique_id)
    url = FIREBASE_DB_URL + path

    data = {
        "symbol": symbol,
        "epoch": tick_time,
        "quote": tick_price
    }

    try:
        response = requests.put(url, data=json.dumps(data))
        if response.status_code == 200:
            print(f"Stored tick at {tick_time}: {tick_price}")
        else:
            print(f"Failed to store tick: {response.text}")
    except Exception as e:
        print(f"Exception storing tick: {e}")

# Deriv WebSocket handler
async def deriv_ws():
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"

    async with websockets.connect(url) as websocket:
        # Subscribe to tick data
        subscribe_msg = {
            "ticks": SYMBOL,
            "subscribe": 1
        }
        await websocket.send(json.dumps(subscribe_msg))
        print(f"Subscribed to {SYMBOL}")

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)

                if "tick" in data:
                    tick = data["tick"]
                    tick_time = tick["epoch"]
                    tick_price = tick["quote"]
                    store_tick_in_firebase(SYMBOL, tick_time, tick_price)
            except Exception as e:
                print(f"Error receiving tick: {e}")
                await asyncio.sleep(1)

# Run WebSocket client
if __name__ == "__main__":
    asyncio.run(deriv_ws())
