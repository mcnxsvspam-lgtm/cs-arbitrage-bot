from flask import Flask, render_template
        "name": "AK-47 Redline",
        "wear": "Field-Tested",
        "float": 0.21,
        "steam_price": 58,
        "steam_fastsell": 55,
        "cs_price": 41,
        "volume": 284,
        "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530139/360fx360f"
    },
    {
        "name": "AWP Asiimov",
        "wear": "Battle-Scarred",
        "float": 0.68,
        "steam_price": 91,
        "steam_fastsell": 87,
        "cs_price": 69,
        "volume": 163,
        "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530170/360fx360f"
    },
    {
        "name": "M4A1-S Printstream",
        "wear": "Field-Tested",
        "float": 0.18,
        "steam_price": 144,
        "steam_fastsell": 139,
        "cs_price": 118,
        "volume": 82,
        "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530208/360fx360f"
    }
]


def calculate_profit(item):

    steam_after_fee = item["steam_fastsell"] * STEAM_FEE

    profit = round(steam_after_fee - item["cs_price"], 2)

    roi = round((profit / item["cs_price"]) * 100, 2)

    item["profit"] = profit
    item["roi"] = roi

    return item


@app.route("/")
def dashboard():

    processed = []

    for skin in skins:
        processed.append(calculate_profit(skin))

    processed.sort(key=lambda x: x["profit"], reverse=True)

    return render_template("index.html", skins=processed)


if __name__ == "__main__":
    app.run(debug=True)
