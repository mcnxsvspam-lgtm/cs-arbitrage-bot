from flask import Flask, render_template
import os

app = Flask(__name__)

skins = [
    {
        "name": "AK-47 Redline",
        "wear": "Field-Tested",
        "float": 0.21,
        "steam_price": 58,
        "steam_fastsell": 55,
        "cs_price": 41,
        "volume": 284,
        "profit": 6.85,
        "roi": 16.7,
        "image": "https://cdn.cloudflare.steamstatic.com/apps/730/icons/econ/default_generated/weapon_ak47_cu_redline_light_large.png"
    },
    {
        "name": "AWP Asiimov",
        "wear": "Battle-Scarred",
        "float": 0.68,
        "steam_price": 91,
        "steam_fastsell": 87,
        "cs_price": 69,
        "volume": 163,
        "profit": 6.69,
        "roi": 9.7,
        "image": "https://cdn.cloudflare.steamstatic.com/apps/730/icons/econ/default_generated/weapon_awp_cu_awp_asiimov_light_large.png"
    }
]

@app.route("/")
def dashboard():
    return render_template("index.html", skins=skins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
