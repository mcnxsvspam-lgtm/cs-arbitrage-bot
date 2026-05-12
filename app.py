from flask import Flask, render_template
import os
import random

app = Flask(__name__)

MIN_PRICE = 10
MAX_PRICE = 150

MAX_SPREAD = 15

MIN_VOLUME = 20

CSMARKET_SELL_FEE = 0.95
CSMARKET_WITHDRAW_FEE = 0.95

ITEMS = [

    "AK-47 Redline (Field-Tested)",

    "AK-47 Neon Rider (Field-Tested)",

    "AK-47 Bloodsport (Well-Worn)",

    "M4A1-S Printstream (Battle-Scarred)",

    "M4A4 Temukau (Field-Tested)",

    "AWP Asiimov (Battle-Scarred)",

    "USP-S Kill Confirmed (Field-Tested)",

    "Desert Eagle Printstream (Field-Tested)",

    "Glock-18 Vogue (Field-Tested)",

    "Driver Gloves Imperial Plaid (Battle-Scarred)"
]


def generate_market_data(item):

    steam_lowest = round(
        random.uniform(10, 150),
        2
    )

    spread_percent = round(
        random.uniform(2, 14),
        2
    )

    highest_buy = round(

        steam_lowest
        * (1 - spread_percent / 100),

        2
    )

    steam_after_fee = round(

        highest_buy * 0.8697,

        2
    )

    csmarket_sell = round(

        steam_after_fee
        * random.uniform(1.01, 1.12),

        2
    )

    csmarket_after_fees = round(

        csmarket_sell
        * CSMARKET_SELL_FEE
        * CSMARKET_WITHDRAW_FEE,

        2
    )

    final_profit = round(

        csmarket_after_fees
        - steam_lowest,

        2
    )

    roi = round(

        (
            final_profit
            / steam_lowest
        ) * 100,

        2
    )

    volume = random.randint(20, 500)

    liquidity_score = round(
        100 - spread_percent
    )

    return {

        "name": item,

        "steam_lowest": steam_lowest,

        "highest_buy": highest_buy,

        "steam_after_fee": steam_after_fee,

        "csmarket_sell": csmarket_sell,

        "cashout": csmarket_after_fees,

        "profit": final_profit,

        "roi": roi,

        "spread": spread_percent,

        "volume": volume,

        "liquidity": liquidity_score,

        "image": (
            "https://community.cloudflare."
            "steamstatic.com/economy/"
            "image/class/730/188530139/360fx360f"
        )
    }


@app.route("/")
def dashboard():

    skins = []

    for item in ITEMS:

        skin = generate_market_data(item)

        if (
            skin["steam_lowest"] >= MIN_PRICE
            and skin["steam_lowest"] <= MAX_PRICE
            and skin["spread"] <= MAX_SPREAD
            and skin["volume"] >= MIN_VOLUME
        ):

            skins.append(skin)

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
