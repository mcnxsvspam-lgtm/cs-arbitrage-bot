from flask import Flask, render_template
import os
import random

app = Flask(__name__)

STEAM_FEE = 0.8697

CSMARKET_SELL_FEE = 0.95
WITHDRAW_FEE = 0.95

ITEMS = [

    {
        "name": "AK-47 Redline (Field-Tested)",
        "steam_sell": 39.10,
        "steam_buy": 36.30,
        "csmarket_price": 41.20,
        "volume": 284
    },

    {
        "name": "AWP Asiimov (Battle-Scarred)",
        "steam_sell": 91.55,
        "steam_buy": 87.00,
        "csmarket_price": 96.50,
        "volume": 163
    },

    {
        "name": "M4A1-S Printstream (Battle-Scarred)",
        "steam_sell": 128.33,
        "steam_buy": 121.00,
        "csmarket_price": 135.90,
        "volume": 82
    },

    {
        "name": "USP-S Kill Confirmed (Field-Tested)",
        "steam_sell": 108.00,
        "steam_buy": 102.50,
        "csmarket_price": 115.00,
        "volume": 97
    },

    {
        "name": "Desert Eagle Printstream (Field-Tested)",
        "steam_sell": 44.49,
        "steam_buy": 42.52,
        "csmarket_price": 47.20,
        "volume": 215
    }
]


def get_image():

    return (
        "https://community.cloudflare."
        "steamstatic.com/economy/"
        "image/class/730/188530139/360fx360f"
    )


@app.route("/")
def dashboard():

    profit_routes = []

    cashout_routes = []

    for item in ITEMS:

        steam_after_fee = round(

            item["steam_sell"]
            * STEAM_FEE,

            2
        )

        profit = round(

            steam_after_fee
            - item["csmarket_price"],

            2
        )

        roi = round(

            (
                profit
                / item["csmarket_price"]
            ) * 100,

            2
        )

        profit_routes.append({

            "name": item["name"],

            "buy": item["csmarket_price"],

            "sell": item["steam_sell"],

            "after_fee": steam_after_fee,

            "profit": profit,

            "roi": roi,

            "volume": item["volume"],

            "image": get_image()
        })

        csmarket_after = round(

            item["csmarket_price"]
            * CSMARKET_SELL_FEE
            * WITHDRAW_FEE,

            2
        )

        cashout_loss = round(

            csmarket_after
            - item["steam_sell"],

            2
        )

        cashout_roi = round(

            (
                cashout_loss
                / item["steam_sell"]
            ) * 100,

            2
        )

        cashout_routes.append({

            "name": item["name"],

            "steam_buy": item["steam_sell"],

            "csmarket_sell": item["csmarket_price"],

            "cashout": csmarket_after,

            "profit": cashout_loss,

            "roi": cashout_roi,

            "volume": item["volume"],

            "image": get_image()
        })

    profit_routes.sort(

        key=lambda x: x["profit"],

        reverse=True
    )

    cashout_routes.sort(

        key=lambda x: x["roi"],

        reverse=True
    )

    return render_template(

        "index.html",

        profit_routes=profit_routes,

        cashout_routes=cashout_routes
    )


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8080)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
