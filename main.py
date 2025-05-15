# main.py
import asyncio
import json
import websockets
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Load Firebase credentials
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

async def stream_v75_candles():
    uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(uri) as websocket:
        request = {
            "ticks_history": "R_75",
            "style": "candles",
            "granularity": 60,
            "end": "latest",
            "subscribe": 1
        }
        await websocket.send(json.dumps(request))

        while True:
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
                    print(f"Saved candle at {candle['epoch']}")

if __name__ == "__main__":
    asyncio.run(stream_v75_candles())
