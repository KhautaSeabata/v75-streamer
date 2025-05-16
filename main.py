import requests

# Firebase Realtime Database URL
FIREBASE_URL = "https://data-364f1-default-rtdb.firebaseio.com"

# Initial data for Vix25
initial_data = {
    "initialized": True,
    "created_at": "from_script"
}

# Full path to Vix25 node
url = f"{FIREBASE_URL}/Vix25.json"

# Send data
response = requests.put(url, json=initial_data)

if response.status_code == 200:
    print("✅ Vix25 node created successfully in Firebase!")
else:
    print(f"❌ Failed to create node: {response.status_code} - {response.text}")
