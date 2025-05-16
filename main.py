import asyncio
import httpx
import time
from datetime import datetime
import json

FIREBASE_TICK_URL = "https://data-364f1-default-rtdb.firebaseio.com/Vix25.json"
FIREBASE_CANDLE_URL = "https://data-364f1-default-rtdb.firebaseio.com/Vix25_1min"

async def fetch_ticks():
    """Fetch all Vix25 ticks from Firebase."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(FIREBASE_TICK_URL)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return []
        return sorted(data.values(), key=lambda x: x["timestamp"])

def group_ticks_by_minute(ticks):
    """Group tick data into 1-minute buckets."""
    candles = {}
    for tick in ticks:
        ts = int(tick["timestamp"])
        minute_key = ts - (ts % 60)  # align to minute start
        price = float(tick["price"])

        if minute_key not in candles:
            candles[minute_key] = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "timestamp": minute_key
            }
        else:
            candle = candles[minute_key]
            candle["high"] = max(candle["high"], price)
            candle["low"] = min(candle["low"], price)
            candle["close"] = price

    return list(candles.values())

async def store_candles(candles):
    """Store generated candles in Firebase."""
    async with httpx.AsyncClient() as client:
        updates = {str(c["timestamp"]): c for c in candles}
        resp = await client.patch(f"{FIREBASE_CANDLE_URL}.json", data=json.dumps(updates))
        resp.raise_for_status()
        print("Stored", len(candles), "candles")

async def run():
    while True:
        ticks = await fetch_ticks()
        if not ticks:
            print("No tick data found.")
            await asyncio.sleep(10)
            continue

        candles = group_ticks_by_minute(ticks)
        await store_candles(candles)

        await asyncio.sleep(60)  # wait 1 minute to process again

if __name__ == "__main__":
    asyncio.run(run())
