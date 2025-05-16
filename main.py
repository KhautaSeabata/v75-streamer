import asyncio
import websockets
import json
import requests
import time

# Firebase Realtime Database URL
FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com"

# Path in Firebase for Vix25 ticks
FIREBASE_TICKS_PATH = "/Vix25/ticks.json"

# Deriv WebSocket URL
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

async def stream_ticks():
    async with websockets.connect(DERIV_WS_URL) as ws:
        # Subscribe to Vix25 ticks
        await ws.send(json.dumps({"ticks": "R_25"}))
        print("✅ Subscribed to R_25 (Vix25)")

        async for message in ws:
            data = json.loads(message)
            if "tick" in data:
                tick = data["tick"]
                tick_payload = {
                    "epoch": tick["epoch"],
                    "quote": tick["quote"],
                    "timestamp": int(time.time())
                }

                # Store tick to Firebase
                try:
                    res = requests.post(FIREBASE_URL + FIREBASE_TICKS_PATH, json=tick_payload)
                    if res.status_code == 200:
                        print(f"✅ Tick stored: {tick_payload}")
                    else:
                        print(f"❌ Failed to store tick: {res.status_code} - {res.text}")
                except Exception as e:
                    print(f"❌ Exception while storing tick: {e}")
            elif "error" in data:
                print("❌ Deriv error:", data["error"])

async def main():
    while True:
        try:
            await stream_ticks()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            print("🔁 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
