import websocket
import json
import requests
from datetime import datetime

# Firebase base URL (replace with your own database URL if needed)
FIREBASE_BASE_URL = "https://data-364f1-default-rtdb.firebaseio.com/"

# Map each symbol to its respective Firebase node
symbol_to_node = {
    "R_10": "Vix10",
    "R_25": "Vix25",
    "R_100": "Vix100",
    "Volatiliti 10 (1s)": "Vix10s",
    "Volatility 75 (1s)": "Vix75s"
}

def on_open(ws):
    print("✅ WebSocket connected.")
    # Subscribe to each symbol by sending separate subscription requests
    for symbol in symbol_to_node.keys():
        subscribe_message = {
            "ticks": symbol,
            "subscribe": 1
        }
        ws.send(json.dumps(subscribe_message))
        print(f"Subscribed to {symbol}")

def on_message(ws, message):
    data = json.loads(message)

    if "tick" in data:
        tick = data["tick"]
        price = tick.get("quote")
        timestamp = tick.get("epoch")
        if timestamp is None:
            # In some messages the tick may not include a timestamp
            return
        readable_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        tick_data = {
            "time": readable_time,
            "timestamp": timestamp,
            "price": price
        }

        # Identify which symbol this tick is for using the echoed subscription request
        symbol = data.get("echo_req", {}).get("ticks")
        if symbol in symbol_to_node:
            node = symbol_to_node[symbol]
            firebase_url = f"{FIREBASE_BASE_URL}{node}.json"
            print(f"Sending tick for {symbol} to Firebase node {node}: {tick_data}")
            try:
                response = requests.post(firebase_url, json=tick_data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Firebase Error for {symbol}:", e)
        else:
            print("Received tick for unknown symbol:", symbol)

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
