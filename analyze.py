import requests

FIREBASE = "https://fir-8908c-default-rtdb.firebaseio.com"

def fetch_ticks():
    r = requests.get(f"{FIREBASE}/ticks/R_25.json")
    data = r.json()
    if not data:
        return []
    ticks = sorted(data.values(), key=lambda x: x["epoch"])
    return ticks[-600:]

def detect_extremes(ticks):
    hh, ll = [], []

    for i in range(2, len(ticks) - 2):
        prev, curr, nxt = ticks[i - 1], ticks[i], ticks[i + 1]
        if curr["quote"] > prev["quote"] and curr["quote"] > nxt["quote"]:
            hh.append((i, curr["quote"]))
        if curr["quote"] < prev["quote"] and curr["quote"] < nxt["quote"]:
            ll.append((i, curr["quote"]))

    return hh, ll

def make_trendline(points):
    if len(points) < 2:
        return []

    (x1, y1), (x2, y2) = points[0], points[-1]
    m = (y2 - y1) / (x2 - x1 + 1e-6)
    b = y1 - m * x1
    return [m * x + b for x in range(x1, x2 + 1)]

def push_line(label, values):
    requests.patch(f"{FIREBASE}/analysis/R_25.json", json={
        label: {"points": values}
    })

def main():
    ticks = fetch_ticks()
    hh, ll = detect_extremes(ticks)

    if len(hh) >= 2:
        upper = make_trendline(hh)
        push_line("upper_trendline", upper)

    if len(ll) >= 2:
        lower = make_trendline(ll)
        push_line("lower_trendline", lower)

if __name__ == "__main__":
    main()
