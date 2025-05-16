import websocket
import json
import pandas as pd
import threading
import time
import requests

BOT_TOKEN = "7819951392:AAFkYd9-sblexjXNqgIfhbWAIC1Lr6NmPpo"
CHAT_ID = "6734231237"

candle_data = []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

def detect_patterns(df):
    detected = []
    if len(df) < 20:
        return detected

    last = df.iloc[-1]
    recent_high = df['high'][-10:].max()
    recent_low = df['low'][-10:].min()

    if last['high'] > recent_high * 0.99:
        entry = last['close']
        sl = recent_low
        tp = entry + (entry - sl) * 1.5
        detected.append(("🚩 Bullish Flag", entry, sl, tp))

    return detected

def analyze_data():
    if len(candle_data) < 20:
        return

    df = pd.DataFrame(candle_data[-500:], columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    detected = detect_patterns(df)

    for name, entry, sl, tp in detected:
        last_close = df["close"].iloc[-1]

        if sl * 0.99 < last_close < sl * 1.01:
            advice = "⚠️ Risky – Consider Exit"
        elif last_close > tp * 0.97:
            advice = "✅ Approaching TP – Watch"
        else:
            advice = "⏳ Hold"

        message = (
            f"📈 *{name}* detected on *Volatility 10 Index*\n"
            f"💰 Entry: `{entry:.2f}`\n"
            f"🛑 Stop Loss: `{sl:.2f}`\n"
            f"🎯 Take Profit: `{tp:.2f}`\n"
            f"🔁 Break Even: `{entry:.2f}`\n"
            f"{advice}"
        )
        send_telegram_message(message)

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

    candle_data = [
        [c["epoch"], c["open"], c["high"], c["low"], c["close"]]
        for c in candles
    ]
    analyze_data()

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, code, msg):
    print("WebSocket closed")

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
    print("📊 Analyzer started")
    threading.Thread(target=run_websocket).start()

    while True:
        time.sleep(60)
        analyze_data()
