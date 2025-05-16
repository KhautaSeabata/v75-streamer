import websocket
import json
import time
import requests
from datetime import datetime

# Firebase config
FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com/ticks.json"  # <- Replace with your Firebase URL

# WebSocket handlers
def on_open(ws):
    print("✅ WebSocket connected.")
    subscribe_message = {
        "ticks": "R_10",  # Replace with your desired symbol
        "subscribe": 1
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    data = json.loads(message)

    if "tick" in data:
        tick = data["tick"]
        price = tick["quote"]
        timestamp = tick["epoch"]
        readable_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        tick_data = {
            "time": readable_time,
            "timestamp": timestamp,
            "price": price
        }

        print("Sending tick to Firebase:", tick_data)
        try:
            response = requests.post(FIREBASE_URL, json=tick_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Firebase Error:", e)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

if __name__ == "__main__":
    ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    ws = websocket.WebSocketApp(ws_url,
                                 on_open=on_open,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.run_forever()
