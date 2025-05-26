import requests
import time
from datetime import datetime
import numpy as np
import json

FIREBASE_TICKS_URL = 'https://fir-8908c-default-rtdb.firebaseio.com/ticks/R_25.json'
FIREBASE_ANALYSIS_URL = 'https://fir-8908c-default-rtdb.firebaseio.com/analysis/R_25.json'

def fetch_latest_ticks(limit=100):
    try:
        response = requests.get(FIREBASE_TICKS_URL)
        data = response.json()
        if not data:
            return []

        ticks = sorted(data.values(), key=lambda x: x['epoch'])
        return ticks[-limit:]
    except Exception as e:
        print('Error fetching ticks:', e)
        return []

def find_structure(ticks):
    prices = [float(t['quote']) for t in ticks]
    times = [t['epoch'] for t in ticks]

    HH, HL, LL, LH = [], [], [], []

    for i in range(2, len(prices)-2):
        if prices[i] > prices[i-1] and prices[i] > prices[i+1] and prices[i] > prices[i-2] and prices[i] > prices[i+2]:
            HH.append({'time': times[i], 'price': prices[i]})
        elif prices[i] < prices[i-1] and prices[i] < prices[i+1] and prices[i] < prices[i-2] and prices[i] < prices[i+2]:
            LL.append({'time': times[i], 'price': prices[i]})

    for i in range(1, len(HH)):
        if HH[i]['price'] > HH[i-1]['price']:
            HL.append(HH[i-1])
        else:
            LH.append(HH[i-1])

    return HH, HL, LL, LH

def determine_channel(HH, HL, LL, LH):
    if len(HH) < 2 or len(LL) < 2:
        return 'sideways'

    hh_slope = HH[-1]['price'] - HH[-2]['price']
    ll_slope = LL[-1]['price'] - LL[-2]['price']

    if hh_slope > 0 and ll_slope > 0:
        return 'up'
    elif hh_slope < 0 and ll_slope < 0:
        return 'down'
    else:
        return 'sideways'

def linear_regression(points):
    if len(points) < 2:
        return None

    x = np.array([p['time'] for p in points])
    y = np.array([p['price'] for p in points])
    slope, intercept = np.polyfit(x, y, 1)

    return [{'time': int(t), 'price': float(slope * t + intercept)} for t in x]

def push_analysis(channel_type, upper_line, lower_line):
    data = {
        'channel_type': channel_type,
        'upper_line': upper_line,
        'lower_line': lower_line,
        'timestamp': int(time.time())
    }
    try:
        requests.put(FIREBASE_ANALYSIS_URL, json=data)
    except Exception as e:
        print('Failed to push analysis:', e)

def run_analysis():
    while True:
        ticks = fetch_latest_ticks()
        if len(ticks) < 10:
            time.sleep(2)
            continue

        HH, HL, LL, LH = find_structure(ticks)
        channel_type = determine_channel(HH, HL, LL, LH)

        upper_line = linear_regression(HH if channel_type != 'down' else LH)
        lower_line = linear_regression(HL if channel_type != 'up' else LL)

        if upper_line and lower_line:
            push_analysis(channel_type, upper_line, lower_line)

        time.sleep(5)

if __name__ == '__main__':
    run_analysis()
