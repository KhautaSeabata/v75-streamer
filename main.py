import asyncio
import json
import websockets
import aiohttp
import time

FIREBASE_DB_URL = "https://fir-8908c-default-rtdb.firebaseio.com"
FIREBASE_PATH = "/ticks/R_75"

async def send_tick_to_firebase(session, tick):
    epoch = tick['epoch']
    url = f"{FIREBASE_DB_URL}{FIREBASE_PATH}/{epoch}.json"
    async with session.put(url, json=tick) as resp:
        if resp.status == 200:
            print(f"Saved tick at epoch {epoch}: {tick['quote']}")
        else:
            text = await resp.text()
            print(f"Failed to save tick at epoch {epoch}. Status: {resp.status}, Response: {text}")

async def deriv_websocket():
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as websocket, aiohttp.ClientSession() as session:
        subscribe_msg = {
            "ticks": "R_75",
            "subscribe": 1
        }
        await websocket.send(json.dumps(subscribe_msg))

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                if 'tick' in data:
                    tick = data['tick']
                    await send_tick_to_firebase(session, tick)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)  # simple retry delay

if __name__ == "__main__":
    asyncio.run(deriv_websocket())
