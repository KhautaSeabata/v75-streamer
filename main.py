import requests
import websocket
import json
import pandas as pd

# Telegram bot token and chat ID (replace with your actual chat ID)
BOT_TOKEN = "7819951392:AAFkYd9-sblexjXNqgIfhbWAIC1Lr6NmPpo"
CHAT_ID = "6734231237"  # Replace this with your actual Telegram chat ID

# Function to send Telegram message
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # This will raise an error for non-200 status codes
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
        raise  # Re-raise the exception so it's logged by Flask

# WebSocket callback handlers
def on_message(ws, message):
    data = json.loads(message)
    if "candles" in data:
        candles = data["candles"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Simple breakout check
        if latest["high"] > previous["high"]:
            send_telegram_message("🚀 Breakout UP Confirmed!")
        elif latest["low"] < previous["low"]:
            send_telegram_message("📉 Breakout DOWN Confirmed!")

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")
    subscribe_message = {
        "ticks_history": "R_100",
        "style": "candles",
        "granularity": 60,
        "count": 100,
        "subscribe": 1
    }
    ws.send(json.dumps(subscribe_message))

# Example function to get signals
def get_signals():
    # Example signals data (this can be replaced with real-time data)
    signals = [
        {"symbol": "BTCUSDT", "action": "BUY", "price": 27500},
        {"symbol": "ETHUSDT", "action": "SELL", "price": 1850}
    ]
    return signals

# Run WebSocket
if __name__ == "__main__":
    socket = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    ws = websocket.WebSocketApp(socket,
                                 on_open=on_open,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.run_forever()
