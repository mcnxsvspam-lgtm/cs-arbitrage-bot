from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

CSMARKET_SELL_FEE = 0.95
CSMARKET_WITHDRAW_FEE = 0.95

SEARCH_ITEMS = [
    {
        "name": "AK-47 Redline (Field-Tested)",
        "cs_price": 52
    },

    {
        "name": "AWP Asiimov (Battle-Scarred)",
        "cs_price": 97
    },

    {
        "name": "M4A1-S Printstream (Field-Tested)",
        "cs_price": 134
    },

    {
        "name": "USP-S Kill Confirmed (Minimal Wear)",
        "cs_price": 118
    }
]


def get_steam_price(item_name):

    url = "https://steamcommunity.com/market/priceoverview/"

    params = {
        "appid": 730,
        "currency": 1,
        "market_hash_name": item_name
    }

    try:

        r = requests.get(url, params=params)

        data = r.json()

        return data

    except:

        return {}


def parse_price(price_string):

    if not price_string:
        return 0

    price_string = (
        price_string
        .replace("$", "")
        .replace("€", "")
        .replace(",", ".")
        .strip()
    )

    try:
        return float(price_string)

    except:
        return 0


@app.route("/")
def dashboard():

    skins = []

    for item in SEARCH_ITEMS:

        steam = get_steam_price(item["name"])

        steam_price = parse_price(
            steam.get("lowest_price")
        )

        volume = steam.get("volume", "0")

        cs_price = item["cs_price"]

        cashout = round(
            cs_price
            * CSMARKET_SELL_FEE
            * CSMARKET_WITHDRAW_FEE,
            2
        )

        profit = round(
            cashout - steam_price,
            2
        )

        roi = 0

        if steam_price > 0:

            roi = round(
                (profit / steam_price) * 100,
                2
            )

        skins.append({

            "name": item["name"],

            "steam_price": steam_price,

            "cs_price": cs_price,

            "cashout": cashout,

            "profit": profit,

            "roi": roi,

            "volume": volume,

            "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530139/360fx360f"
        })

    skins.sort(
        key=lambda x: x["profit"],
        reverse=True
    )

    return render_template(
        "index.html",
        skins=skins
    )


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8080)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
