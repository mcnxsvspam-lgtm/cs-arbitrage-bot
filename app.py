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
        "image": "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdt7d-JmIGZnOHLP7LWnn8fuMhzj7GXodT22QbnqBVqZWj6xYbYwQvlr0s6fA/360fx360f"
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
        "image": "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdt7d-JmIGZnOHLO77QgHIfuMhzj7GXodT22QbnqBVqZWj6xYbYwQvlr0s6fA/360fx360f"
    }
]

@app.route("/")
def dashboard():
    return render_template("index.html", skins=skins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
