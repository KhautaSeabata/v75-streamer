import asyncio
import json
import firebase_admin
from firebase_admin import credentials, db
import websockets

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")  # Your Firebase service account key JSON
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://data-364f1-default-rtdb.firebaseio.com/'
})

# Firebase DB reference to store ticks
ticks_ref = db.reference("Vix25/ticks")

# Deriv WebSocket URL
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

async def subscribe_ticks():
    async with websockets.connect(DERIV_WS_URL) as ws:
        # Subscribe to Volatility 25 ticks
        subscribe_msg = json.dumps({"ticks": "R_25"})
        await ws.send(subscribe_msg)
        print("Subscribed to Volatility 25 ticks")

        async for message in ws:
            data = json.loads(message)
            if "tick" in data:
                tick = data["tick"]
                # Store the tick data to Firebase
                ticks_ref.push(tick)
                print(f"Stored tick: epoch={tick['epoch']} quote={tick['quote']}")
            elif "error" in data:
                print("Error from Deriv:", data["error"])

async def main():
    while True:
        try:
            await subscribe_ticks()
        except Exception as e:
            print(f"WebSocket error: {e}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
