import websocket
import json
import threading
import time
import requests
import pandas as pd

# Firebase URL
FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com"

# Global candle storage
candle_data = []

# Push a candle to Firebase
def push_candle_to_firebase(candle):
    try:
        epoch = candle[0]
        url = f"{FIREBASE_URL}/Vix10/{epoch}.json"
        payload = {
            "timestamp": epoch,
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4]
        }
        response = requests.put(url, json=payload)
        response.raise_for_status()
        print(f"✅ Pushed candle at {epoch} to Firebase.")
    except Exception as e:
        print("❌ Firebase Push Error:", e)

# Provide latest candles to web.py
def get_candles():
    return [
        {
            "timestamp": time.strftime('%H:%M:%S', time.gmtime(c[0])),
            "open": c[1],
            "high": c[2],
            "low": c[3],
            "close": c[4]
        } for c in candle_data[-50:]
    ]

# WebSocket handlers
def on_open(ws):
    subscribe = {
        "ticks_history": "R_10",
        "style": "candles",
        "granularity": 60,
        "count": 500,
        "subscribe": 1
    }
    ws.send(json.dumps(subscribe))

def on_message(ws, message):
    global candle_data

    data = json.loads(message)
    candles = []

    if "candles" in data:
        candles = data["candles"]
    elif "history" in data:
        candles = data["history"]["candles"]

    new_data = [
        [c["epoch"], c["open"], c["high"], c["low"], c["close"]]
        for c in candles
    ]

    # Detect new candles and avoid duplicates
    existing_timestamps = {c[0] for c in candle_data}
    new_candles = [c for c in new_data if c[0] not in existing_timestamps]

    # Update candle_data and push to Firebase
    candle_data.extend(new_candles)
    for c in new_candles:
        push_candle_to_firebase(c)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

# Run WebSocket in background thread
def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://ws.binaryws.com/websockets/v3?app_id=1089",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    print("📡 Streaming candles and pushing to Firebase...")
    threading.Thread(target=run_websocket).start()

    # Keep process alive
    while True:
        time.sleep(60)
