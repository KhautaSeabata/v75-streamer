import asyncio
import websockets
import json
import requests
import time

# === Configuration ===
FIREBASE_URL = "https://company-bdb78-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_150"  # Volatility 150 (1s)
MAX_RECORDS = 999

# === State ===
ohlc_minute = None
ohlc_data = {}

def get_minute(epoch):
    return epoch - (epoch % 60)

# === Store 1-minute OHLC to Firebase ===
def push_ohlc_to_firebase(ohlc):
    url = f"{FIREBASE_URL}/1minVix150.json"
    response = requests.post(url, json=ohlc)
    if response.status_code == 200:
        print("[1MIN OHLC] Pushed:", ohlc)
    else:
        print("[1MIN OHLC] Failed to push:", response.text)

# === Prune old ticks if > MAX_RECORDS ===
def prune_old_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json()
        if not data:
            return

        # Sort by epoch
        sorted_ticks = sorted(data.items(), key=lambda item: item[1]["epoch"])
        total = len(sorted_ticks)

        if total <= MAX_RECORDS:
            return

        to_delete = sorted_ticks[:total - MAX_RECORDS]
        delete_payload = {key: None for key, _ in to_delete}

        # Delete old keys
        delete_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        del_response = requests.patch(delete_url, json=delete_payload)
        if del_response.status_code == 200:
            print(f"[PRUNE] Deleted {len(to_delete)} old ticks")
        else:
            print("[PRUNE] Failed:", del_response.text)
    except Exception as e:
        print("[PRUNE] Exception:", e)

# === Main WebSocket Tick Stream ===
async def stream_ticks():
    global ohlc_minute, ohlc_data

    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                await ws.send(json.dumps({
                    "ticks": SYMBOL,
                    "subscribe": 1
                }))
                print(f"[STARTED] Subscribed to {SYMBOL}...")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if "tick" in data:
                        tick = data["tick"]
                        epoch = tick["epoch"]
                        quote = tick["quote"]
                        tick_data = {
                            "symbol": tick["symbol"],
                            "epoch": epoch,
                            "quote": quote
                        }

                        # Store tick in Firebase
                        tick_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
                        requests.post(tick_url, json=tick_data)

                        # Prune every ~50 ticks
                        if epoch % 50 == 0:
                            prune_old_ticks()

                        # Build OHLC per minute
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
                            # Store completed candle
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
            print("[ERROR] Reconnecting in 5s:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
