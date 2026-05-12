from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)


@app.template_filter("eur")
def eur(value):
    try:
        return f"€{float(value):.2f}"
    except:
        return "€0.00"


@app.template_filter("pc")
def pc(value):
    try:
        return f"{float(value):.2f}%"
    except:
        return "0%"


@app.route("/")
def dashboard():

    mode = request.args.get("mode", "cashout")

    cashout_rows = [
        {
            "name": "AK-47 Redline (Field-Tested)",
            "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530139/330fx330f",
            "steam_buy": 36.30,
            "steam_spread": 1.62,
            "steam_after_fee": 31.57,
            "csmarket_lowest": 35.24,
            "fastsell": 34.80,
            "final_cash": 31.40,
            "kept_pct": 86.2,
            "steam_volume": 139,
            "liquidity": "HIGH",
            "liquidity_score": 77,
        }
    ]

    profit_rows = [
        {
            "name": "AK-47 Nightwish (Field-Tested)",
            "image": "https://community.cloudflare.steamstatic.com/economy/image/class/730/188530139/330fx330f",
            "csmarket_lowest": 55.66,
            "steam_buy": 73.17,
            "steam_after_fee": 63.73,
            "profit": 8.07,
            "profit_roi": 14.5,
            "steam_spread": 0.15,
            "steam_volume": 119,
            "risk": "OK",
            "liquidity": "MID",
            "liquidity_score": 71,
        }
    ]

    actionable_routes = [
        {
            "net_profit": 3.12,
            "net_profit_pct": 3.12,
            "entry_name": "AK-47 Nightwish (FT)",
            "entry_csmarket_buy": 82,
            "entry_steam_sell": 101,
            "entry_steam_after_fee": 87.83,
            "exit_qty": 2,
            "exit_name": "AK-47 Redline (FT)",
            "final_cash": 103.12,
            "confidence": "MEDIUM",
            "liquidity": "HIGH",
        }
    ]

    return render_template(
        "index.html",
        mode=mode,
        cashout_rows=cashout_rows,
        profit_rows=profit_rows,
        actionable_routes=actionable_routes,
        scan_count=len(cashout_rows),
        updated_at=datetime.now().strftime("%H:%M:%S")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
