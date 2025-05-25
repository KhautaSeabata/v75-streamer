import asyncio
import websockets
import json
import requests
import time

FIREBASE_URL = "https://company-bdb78-default-rtdb.firebaseio.com"
DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"
SYMBOL = "R_150"

ohlc_minute = None
ohlc_data = {}
MAX_RECORDS = 999  # keep only latest 999 records

def get_minute(epoch):
    return epoch - (epoch % 60)

def push_ohlc_to_firebase(ohlc):
    url = f"{FIREBASE_URL}/Vix150_1min.json"
    response = requests.post(url, json=ohlc)
    if response.status_code == 200:
        print("[1MIN OHLC] Pushed:", ohlc)
    else:
        print("[1MIN OHLC] Failed to push:", response.text)

def prune_old_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json()
        if not data:
            return

        # Sort ticks by epoch (ascending: oldest first)
        sorted_ticks = sorted(data.items(), key=lambda item: item[1]["epoch"])
        total = len(sorted_ticks)

        if total <= MAX_RECORDS:
            return  # nothing to prune

        to_delete_count = total - MAX_RECORDS
        keys_to_delete = [key for key, _ in sorted_ticks[:to_delete_count]]

        delete_payload = {key: None for key in keys_to_delete}

        # Use PATCH to delete keys by setting them to null
        patch_url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        delete_response = requests.patch(patch_url, json=delete_payload)
        if delete_response.status_code == 200:
            print(f"[PRUNE] Deleted {to_delete_count} old tick records")
        else:
            print("[PRUNE] Failed to delete old ticks:", delete_response.text)
    except Exception as e:
        print("[PRUNE] Exception during pruning:", e)

async def stream_ticks():
    global ohlc_minute, ohlc_data

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

                        # Prune old ticks every 50 ticks approx to reduce load
                        if epoch % 50 == 0:
                            prune_old_ticks()

                        # OHLC candle logic
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
                            push_ohlc_to_firebase(ohlc_data)
                            ohlc_minute = minute
                            ohlc_data = {
                                "open": quote,
                                "high": quote,
                                "low": quote,
                                "close": quote,
                                "epoch": minute
                            }
        except Exception as e:
            print("[ERROR] Retrying in 5 seconds:", e)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_ticks())
