import time
import threading
from flask import Flask, render_template, request
from core.steamapi import SteamAPI
from core.csmarketapi import CSMarketAPI
from core.scanners import cashout_scan, profit_scan, routes_scan

app = Flask(__name__)

START_CASH = 100.0

SCAN_ITEMS = [
    "AK-47 | Redline (Field-Tested)",
    "AK-47 | Nightwish (Field-Tested)",
    "M4A1-S | Printstream (Field-Tested)",
    "Desert Eagle | Printstream (Field-Tested)",
    "USP-S | Printstream (Field-Tested)",
    "AWP | Asiimov (Field-Tested)"
]

steam = SteamAPI()
cs = CSMarketAPI()

CACHE = {}
CACHE_TTL = 90
LOCK = threading.Lock()


def cache_get(key):
    with LOCK:
        item = CACHE.get(key)
        if not item:
            return None
        if time.time() - item["time"] > CACHE_TTL:
            return None
        return item["value"]


def cache_set(key, value):
    with LOCK:
        CACHE[key] = {"value": value, "time": time.time()}


def fetch_item_data(name):
    key = f"item:{name}"
    cached = cache_get(key)
    if cached:
        return cached
    data = {
        "name": name,
        "steam": steam.get_item(730, name),
        "cs": cs.get_item(name)
    }
    cache_set(key, data)
    return data


@app.template_filter("eur")
def fmt_eur(v):
    if v is None:
        return "-"
    return f"€{v:,.2f}"


@app.template_filter("pc")
def fmt_pc(v):
    if v is None:
        return "-"
    return f"{v:.2f}%"


@app.route("/")
def index():
    mode = request.args.get("mode", "cashout")
    rows = [fetch_item_data(i) for i in SCAN_ITEMS]

    if mode == "cashout":
        data = cashout_scan(rows)
        return render_template("index.html", mode=mode, cashout=data)

    if mode == "profit":
        data = profit_scan(rows)
        return render_template("index.html", mode=mode, profit=data)

    if mode == "routes":
        data = routes_scan(rows, START_CASH)
        return render_template("index.html", mode=mode, routes=data)

    data = cashout_scan(rows)
    return render_template("index.html", mode="cashout", cashout=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
