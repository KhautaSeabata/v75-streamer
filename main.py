import asyncio
import json
import websockets
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials from local file
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

async def stream_v75_candles():
    uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"

    async with websockets.connect(uri) as websocket:
        request = {
            "ticks_history": "R_75",
            "style": "candles",
            "granularity": 60,  # 1-minute candles
            "end": "latest",
            "subscribe": 1
        }
        await websocket.send(json.dumps(request))

        print("Subscribed to V75 candlestick data...")

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)

                if "candles" in data:
                    for candle in data["candles"]:
                        ts = str(candle["epoch"])
                        db.collection("v75_candles").document(ts).set({
                            "open": candle["open"],
                            "high": candle["high"],
                            "low": candle["low"],
                            "close": candle["close"],
                            "time": candle["epoch"]
                        })
                        print(f"Saved candle @ {candle['epoch']}")
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_v75_candles())
