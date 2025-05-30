import asyncio
import websockets
import json
import requests
import time

FIREBASE_URL = "https://fir-8908c-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_25"

ohlc_minute = None
ohlc_data = {}

ohlc_5min_minute = None
ohlc_5min_data = {}

MAX_RECORDS = 999  # keep only latest 999 records


def get_minute(epoch):
    return epoch - (epoch % 60)

def get_5min_start(epoch):
    return epoch - (epoch % 300)

def push_ohlc_to_firebase(ohlc, timeframe):
    url = f"{FIREBASE_URL}/{timeframe}Vix25.json"
    response = requests.post(url, json=ohlc)
    if response.status_code == 200:
        print(f"[{timeframe.upper()} OHLC] Pushed:", ohlc)
    else:
        print(f"[{timeframe.upper()} OHLC] Failed to push:", response.text)

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
    global ohlc_minute, ohlc_data, ohlc_5min_minute, ohlc_5min_data

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

                        # Prune every 50 ticks approx
                        if epoch % 50 == 0:
                            prune_old_ticks()

                        # --- 1MIN OHLC Logic ---
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
                            push_ohlc_to_firebase(ohlc_data, "1min")
                            ohlc_minute = minute
                            ohlc_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }

                        # --- 5MIN OHLC Logic ---
                        m5 = get_5min_start(epoch)
                        if ohlc_5min_minute is None:
                            ohlc_5min_minute = m5
                            ohlc_5min_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": m5
                            }
                        elif m5 == ohlc_5min_minute:
                            ohlc_5min_data["high"] = max(ohlc_5min_data["high"], quote)
                            ohlc_5min_data["low"] = min(ohlc_5min_data["low"], quote)
                            ohlc_5min_data["close"] = quote
                        else:
                            push_ohlc_to_firebase(ohlc_5min_data, "5min")
                            ohlc_5min_minute = m5
                            ohlc_5min_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": m5
                            }

        except Exception as e:
            print("[ERROR] Retrying in 5 seconds:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
