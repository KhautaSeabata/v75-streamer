import asyncio
import json
import datetime
import firebase_admin
from firebase_admin import credentials, db
import websockets

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://data-364f1-default-rtdb.firebaseio.com/'
})

# Firebase refs
candles_ref = db.reference("Vix25/minute_candles")

# Deriv WS URL
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# Keep track of ticks for current minute candle
current_minute = None
open_price = None
high_price = None
low_price = None
close_price = None

async def subscribe_ticks():
    global current_minute, open_price, high_price, low_price, close_price

    async with websockets.connect(DERIV_WS_URL) as ws:
        # Subscribe to tick stream for R_25 (Volatility 25)
        subscribe_msg = {
            "ticks": "R_25"
        }
        await ws.send(json.dumps(subscribe_msg))

        async for message in ws:
            data = json.loads(message)

            if "tick" in data:
                tick = data["tick"]
                tick_time = datetime.datetime.utcfromtimestamp(tick["epoch"]).replace(second=0, microsecond=0)
                tick_price = float(tick["quote"])

                if current_minute is None:
                    # First tick received
                    current_minute = tick_time
                    open_price = high_price = low_price = close_price = tick_price

                elif tick_time > current_minute:
                    # New minute - store previous candle
                    candle_data = {
                        "timestamp": current_minute.isoformat(),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                    }
                    print(f"Storing candle: {candle_data}")
                    candles_ref.push(candle_data)

                    # Reset for new candle
                    current_minute = tick_time
                    open_price = high_price = low_price = close_price = tick_price

                else:
                    # Same minute - update high, low, close
                    if tick_price > high_price:
                        high_price = tick_price
                    if tick_price < low_price:
                        low_price = tick_price
                    close_price = tick_price

            elif "error" in data:
                print("Error from server:", data["error"])

async def main():
    while True:
        try:
            await subscribe_ticks()
        except Exception as e:
            print("WebSocket error:", e)
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
