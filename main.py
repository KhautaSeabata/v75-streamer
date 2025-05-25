import asyncio
import websockets
import json
import requests

# Firebase setup
FIREBASE_DB_URL = "https://company-bdb78-default-rtdb.firebaseio.com"
SYMBOL = "R_150"
MAX_TICKS = 999
FIREBASE_PATH = f"/ticks/{SYMBOL}/latest.json"

# Tick buffer
tick_buffer = []

def store_buffer_in_firebase():
    url = FIREBASE_DB_URL + FIREBASE_PATH
    try:
        response = requests.put(url, data=json.dumps(tick_buffer))
        if response.status_code == 200:
            print(f"✅ Stored {len(tick_buffer)} ticks.")
        else:
            print(f"❌ Failed to store: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def handle_new_tick(tick_time, tick_price):
    global tick_buffer
    tick = {
        "symbol": SYMBOL,
        "epoch": tick_time,
        "quote": tick_price
    }

    if len(tick_buffer) >= MAX_TICKS:
        tick_buffer.pop(0)  # Delete the oldest tick

    tick_buffer.append(tick)
    store_buffer_in_firebase()

async def deriv_ws():
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps({
            "ticks": SYMBOL,
            "subscribe": 1
        }))
        print(f"📡 Subscribed to {SYMBOL}")

        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)

                if "tick" in data:
                    tick = data["tick"]
                    tick_time = tick["epoch"]
                    tick_price = tick["quote"]
                    handle_new_tick(tick_time, tick_price)
            except Exception as e:
                print(f"⚠️ WebSocket error: {e}")
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(deriv_ws())
