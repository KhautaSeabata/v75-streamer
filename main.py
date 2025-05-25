import asyncio
import websockets
import json
import requests
import time

FIREBASE_URL = "https://company-bdb78-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_150"  # Volatility 150 (1s)

ohlc_1min = None
ohlc_5min = None
ohlc_data_1min = {}
ohlc_data_5min = {}
MAX_RECORDS = 999  # keep only latest 999 records

def get_minute(epoch, interval=60):
    return epoch - (epoch % interval)

def push_ohlc_to_firebase(path, ohlc):
    url = f"{FIREBASE_URL}/{path}.json"
    response = requests.post(url, json=ohlc)
    if response.status_code == 200:
        print(f"[{path.upper()}] Pushed:", ohlc)
    else:
        print(f"[{path.upper()}] Failed to push:", response.text)

def prune_old_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json()
        if not data:
            return

        sorted_ticks = sorted(data.items(), key=lambda item: item[1]["epoch"])
        total = len(sorted_ticks)

        if total <= MAX_RECORDS:
            return

        to_delete_count = total - MAX_RECORDS
        keys_to_delete = [key for key, _ in sorted_ticks[:to_delete_count]]
        delete_payload = {key: None for key in keys_to_delete}

        patch_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        delete_response = requests.patch(patch_url, json=delete_payload)
        if delete_response.status_code == 200:
            print(f"[PRUNE] Deleted {to_delete_count} old tick records")
        else:
            print("[PRUNE] Failed to delete old ticks:", delete_response.text)
    except Exception as e:
        print("[PRUNE] Exception during pruning:", e)

async def stream_ticks():
    global ohlc_1min, ohlc_5min, ohlc_data_1min, ohlc_data_5min

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

                        # Push raw tick to Firebase
                        tick_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
                        requests.post(tick_url, json=tick_data)

                        # Prune periodically
                        if epoch % 50 == 0:
                            prune_old_ticks()

                        # 1-minute OHLC logic
                        minute_1 = get_minute(epoch, 60)
                        if ohlc_1min is None:
                            ohlc_1min = minute_1
                            ohlc_data_1min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute_1
                            }
                        elif minute_1 == ohlc_1min:
                            ohlc_data_1min["high"] = max(ohlc_data_1min["high"], quote)
                            ohlc_data_1min["low"] = min(ohlc_data_1min["low"], quote)
                            ohlc_data_1min["close"] = quote
                        else:
                            push_ohlc_to_firebase("1minVix150_1s", ohlc_data_1min)
                            ohlc_1min = minute_1
                            ohlc_data_1min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute_1
                            }

                        # 5-minute OHLC logic
                        minute_5 = get_minute(epoch, 300)
                        if ohlc_5min is None:
                            ohlc_5min = minute_5
                            ohlc_data_5min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute_5
                            }
                        elif minute_5 == ohlc_5min:
                            ohlc_data_5min["high"] = max(ohlc_data_5min["high"], quote)
                            ohlc_data_5min["low"] = min(ohlc_data_5min["low"], quote)
                            ohlc_data_5min["close"] = quote
                        else:
                            push_ohlc_to_firebase("5minVix150_1s", ohlc_data_5min)
                            ohlc_5min = minute_5
                            ohlc_data_5min = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute_5
                            }

        except Exception as e:
            print("[ERROR] Retrying in 5 seconds:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
