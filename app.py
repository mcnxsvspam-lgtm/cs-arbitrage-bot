from flask import Flask, render_template
import requests
import re
import os

app = Flask(__name__)

SEARCH_ITEMS = [

    "AK-47 Redline (Field-Tested)",

    "AWP Asiimov (Battle-Scarred)",

    "M4A1-S Printstream (Field-Tested)",

    "USP-S Kill Confirmed (Minimal Wear)"
]


def get_item_nameid(item_name):

    try:

        url = (
            f"https://steamcommunity.com/market/listings/730/{item_name}"
        )

        headers = {

            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

        r = requests.get(

            url,

            headers=headers,

            timeout=15
        )

        match = re.search(

            r"Market_LoadOrderSpread\(\s?(\d+)\s?\)",

            r.text
        )

        if match:

            return match.group(1)

        print("NO ITEM_NAMEID:", item_name)

        return None

    except Exception as e:

        print("ITEM_NAMEID ERROR:", e)

        return None


def get_steam_data(item_name):

    try:

        item_nameid = get_item_nameid(item_name)

        if not item_nameid:

            return None

        url = (
            "https://steamcommunity.com/"
            "market/itemordershistogram"
        )

        params = {

            "country": "DE",

            "language": "english",

            "currency": 3,

            "item_nameid": item_nameid,

            "two_factor": 0
        }

        headers = {

            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),

            "Accept": "*/*",

            "Referer": (
                f"https://steamcommunity.com/"
                f"market/listings/730/{item_name}"
            )
        }

        r = requests.get(

            url,

            params=params,

            headers=headers,

            timeout=15
        )

        print("STATUS:", r.status_code)

        print("TEXT:", r.text[:300])

        if r.status_code != 200:

            return None

        data = r.json()

        return data

    except Exception as e:

        print("STEAM ERROR:", e)

        return None


def parse_price(price):

    if not price:

        return 0

    price = (
        str(price)
        .replace("€", "")
        .replace(",", ".")
        .strip()
    )

    try:

        return float(price)

    except:

        return 0


@app.route("/")
def dashboard():

    skins = []

    for item in SEARCH_ITEMS:

        try:

            steam = get_steam_data(item)

            if not steam:

                continue

            lowest_sell = (
                parse_price(
                    steam.get("lowest_sell_order")
                ) / 100
            )

            highest_buy = (
                parse_price(
                    steam.get("highest_buy_order")
                ) / 100
            )

            spread = 0

            if lowest_sell > 0:

                spread = round(

                    (
                        (
                            lowest_sell
                            - highest_buy
                        )
                        / lowest_sell
                    ) * 100,

                    2
                )

            steam_after_fee = round(

                highest_buy * 0.8697,

                2
            )

            liquidity_score = max(

                0,

                round(100 - spread)
            )

            skins.append({

                "name": item,

                "lowest_sell": lowest_sell,

                "highest_buy": highest_buy,

                "steam_after_fee": steam_after_fee,

                "spread": spread,

                "liquidity": liquidity_score,

                "image": (
                    "https://community.cloudflare."
                    "steamstatic.com/economy/"
                    "image/class/730/188530139/360fx360f"
                )
            })

        except Exception as e:

            print("DASHBOARD ERROR:", e)

    skins.sort(

        key=lambda x: x["spread"]
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
