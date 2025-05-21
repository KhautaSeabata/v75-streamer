# main.py
import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_25"

ohlc_minute = None
ohlc_data = {}

def get_minute(epoch):
    return epoch - (epoch % 60)

def push_ohlc_to_firebase(ohlc):
    url = f"{FIREBASE_URL}/1minVix25.json"
    response = requests.post(url, json=ohlc)
    if response.status_code == 200:
        print("[1MIN OHLC] Pushed:", ohlc)
    else:
        print("[1MIN OHLC] Failed to push:", response.text)

async def stream_ticks():
    global ohlc_minute, ohlc_data

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
                        epoch = tick["epoch"]
                        quote = tick["quote"]
                        tick_data = {
                            "symbol": tick["symbol"],
                            "epoch": epoch,
                            "quote": quote
                        }

                        # Push raw tick
                        tick_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
                        requests.post(tick_url, json=tick_data)

                        # OHLC logic
                        minute = get_minute(epoch)
                        if ohlc_minute is None:
                            ohlc_minute = minute
                            ohlc_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }
                        elif minute == ohlc_minute:
                            ohlc_data["high"] = max(ohlc_data["high"], quote)
                            ohlc_data["low"] = min(ohlc_data["low"], quote)
                            ohlc_data["close"] = quote
                        else:
                            # Push previous OHLC to Firebase
                            push_ohlc_to_firebase(ohlc_data)
                            # Start new candle
                            ohlc_minute = minute
                            ohlc_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }

        except Exception as e:
            print("[ERROR] Retrying in 5 seconds:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
