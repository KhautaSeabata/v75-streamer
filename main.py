import asyncio
import websockets
import json
import requests
import time

# Firebase Realtime Database REST endpoint
FIREBASE_TICKS_URL = "https://data-364f1-default-rtdb.firebaseio.com/Vix25/ticks.json"

# Deriv WebSocket endpoint
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

async def subscribe_and_store_ticks():
    async with websockets.connect(DERIV_WS_URL) as ws:
        # Subscribe to Volatility 25 Index ticks
        subscribe_msg = json.dumps({"ticks": "R_25"})
        await ws.send(subscribe_msg)
        print("✅ Subscribed to Vix25 ticks")

        async for message in ws:
            data = json.loads(message)
            if "tick" in data:
                tick = data["tick"]
                tick_data = {
                    "epoch": tick["epoch"],
                    "quote": tick["quote"],
                    "timestamp": int(time.time())
                }
                # Send to Firebase using REST
                response = requests.post(FIREBASE_TICKS_URL, json=tick_data)
                if response.status_code == 200:
                    print(f"✅ Tick stored: {tick_data}")
                else:
                    print(f"❌ Failed to store tick: {response.text}")
            elif "error" in data:
                print("❌ Error from Deriv:", data["error"])

async def main():
    while True:
        try:
            await subscribe_and_store_ticks()
        except Exception as e:
            print(f"⚠️ WebSocket error: {e}")
            print("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
