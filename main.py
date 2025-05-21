# main.py
import asyncio
import websockets
import json
import requests
import time

FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_25"

async def stream_ticks():
    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                await ws.send(json.dumps({
                    "ticks": SYMBOL,
                    "subscribe": 1
                }))
                print(f"[STARTED] Subscribed to {SYMBOL} ticks...")

                while True:
                    message = await ws.recv()
                    data = json.loads(message)

                    if "tick" in data:
                        tick = data["tick"]
                        tick_data = {
                            "symbol": tick["symbol"],
                            "epoch": tick["epoch"],
                            "quote": tick["quote"]
                        }

                        firebase_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
                        response = requests.post(firebase_url, json=tick_data)
                        if response.status_code == 200:
                            print("Tick pushed:", tick_data)
                        else:
                            print("Failed to push tick:", response.text)

        except Exception as e:
            print("[ERROR] Retrying in 5 seconds:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
