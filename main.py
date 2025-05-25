# main.py
import asyncio
import websockets
import json
import requests
import time

FIREBASE_URL = "https://company-bdb78-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_150"
MAX_RECORDS = 999

ohlc_1min = None
ohlc_5min = None
ohlc_data_1min = {}
ohlc_data_5min = {}

def get_minute(epoch):
    return epoch - (epoch % 60)

def get_5min(epoch):
    return epoch - (epoch % 300)

def push_to_firebase(path, data, label="DATA"):
    url = f"{FIREBASE_URL}/{path}.json"
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"[{label}] Pushed:", data)
    else:
        print(f"[{label}] Failed:", response.status_code, response.text)

def prune_old_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json()
        if not data:
            return

        sorted_ticks = sorted(data.items(), key=lambda x: x[1]["epoch"])
        if len(sorted_ticks) <= MAX_RECORDS:
            return

        to_delete = len(sorted_ticks) - MAX_RECORDS
        keys_to_delete = [key for key, _ in sorted_ticks[:to_delete]]
        delete_payload = {key: None for key in keys_to_delete}

        requests.patch(f"{FIREBASE_URL}/ticks/{SYMBOL}.json", json=delete_payload)
        print(f"[PRUNE] Removed {to_delete} old ticks")

    except Exception as e:
        print("[PRUNE] Error:", e)

async def stream_ticks():
    global ohlc_1min, ohlc_5min, ohlc_data_1min, ohlc_data_5min

    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                await ws.send(json.dumps({"ticks": SYMBOL, "subscribe": 1}))
                print(f"[CONNECTED] Streaming {SYMBOL} ticks...")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if "tick" in data:
                        tick = data["tick"]
                        epoch = tick["epoch"]
                        quote = tick["quote"]
                        tick_data = {
                            "symbol": SYMBOL,
                            "epoch": epoch,
                            "quote": quote
                        }

                        # Push tick to Firebase
                        push_to_firebase(f"ticks/{SYMBOL}", tick_data, "TICK")

                        # Prune every 60s
                        if epoch % 60 == 0:
                            prune_old_ticks()

                        # === 1-MIN OHLC ===
                        minute = get_minute(epoch)
                        if ohlc_1min is None:
                            ohlc_1min = minute
                            ohlc_data_1min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }
                        elif minute == ohlc_1min:
                            ohlc_data_1min["high"] = max(ohlc_data_1min["high"], quote)
                            ohlc_data_1min["low"] = min(ohlc_data_1min["low"], quote)
                            ohlc_data_1min["close"] = quote
                        else:
                            push_to_firebase(f"1min/{SYMBOL}", ohlc_data_1min, "1MIN")
                            ohlc_1min = minute
                            ohlc_data_1min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }

                        # === 5-MIN OHLC ===
                        min5 = get_5min(epoch)
                        if ohlc_5min is None:
                            ohlc_5min = min5
                            ohlc_data_5min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": min5
                            }
                        elif min5 == ohlc_5min:
                            ohlc_data_5min["high"] = max(ohlc_data_5min["high"], quote)
                            ohlc_data_5min["low"] = min(ohlc_data_5min["low"], quote)
                            ohlc_data_5min["close"] = quote
                        else:
                            push_to_firebase(f"5min/{SYMBOL}", ohlc_data_5min, "5MIN")
                            ohlc_5min = min5
                            ohlc_data_5min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": min5
                            }

        except Exception as e:
            print("[ERROR] Reconnecting in 5s:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
