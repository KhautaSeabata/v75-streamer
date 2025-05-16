import websocket
import json
import time
import requests
from datetime import datetime

# Telegram credentials
BOT_TOKEN = "7819951392:AAFkYd9-sblexjXNqgIfhbWAIC1Lr6NmPpo"
CHAT_ID = "6734231237"

# Send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Telegram error:", e)

# WebSocket event handlers
def on_open(ws):
    print("✅ WebSocket connected.")
    subscribe_message = {
        "ticks": "R_10",  # Replace with your symbol if needed
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
        msg = f"📈 Tick @ {readable_time} UTC\n💰 Price: {price}"
        print(msg)
        send_telegram_message(msg)

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
