
MIN_PRICE = float(os.environ.get("MIN_SCAN_PRICE", "10"))
MAX_PRICE = float(os.environ.get("MAX_SCAN_PRICE", "150"))
MIN_VOLUME = int(os.environ.get("MIN_SCAN_VOLUME", "20"))
MIN_ROUTE_PROFIT = float(os.environ.get("MIN_ROUTE_PROFIT", "0.25"))
CACHE_TTL = int(os.environ.get("CACHE_TTL_SECONDS", "300"))

SESSION = requests.Session()
    return "1 day"


def sale_time_minutes(label):
    return {
        "5 min": 5,
        "30 min": 30,
        "2 hours": 120,
        "1 day": 1440,
    }.get(label, 1440)


def format_duration(minutes):
    if minutes < 60:
        return f"{minutes} min"
    if minutes < 1440:
        hours = round(minutes / 60, 1)
        return f"{hours:g}h"
    days = round(minutes / 1440, 1)
    return f"{days:g}d"


def route_confidence(entry, exit_item, net_profit_pct):
    min_liquidity = min(entry["liquidity_score"], exit_item["liquidity_score"])
    entry_spread = entry["steam_spread"] if entry["steam_spread"] is not None else 99
    exit_spread = exit_item["steam_spread"] if exit_item["steam_spread"] is not None else 99
    max_spread = max(entry_spread, exit_spread)
    min_depth = min(entry["steam_buy_depth"], exit_item["steam_buy_depth"])

    if net_profit_pct >= 3 and min_liquidity >= 75 and max_spread <= 6 and min_depth >= 20:
        return "HIGH"
    if net_profit_pct >= 1 and min_liquidity >= 55 and max_spread <= 10:
        return "MEDIUM"
    return "LOW"


def actionable_route_score(route):
    confidence_score = {"HIGH": 30, "MEDIUM": 18, "LOW": 6}[route["confidence"]]
    liquidity_score_part = min(route["liquidity_score"] / 100 * 30, 30)
    profit_score = min(route["net_profit_pct"] * 8, 30)
    speed_score = max(10 - route["estimated_minutes"] / 180, 0)
    return round(profit_score + liquidity_score_part + confidence_score + speed_score, 2)


def build_market_rows():
    rows = []
    errors = []
    return routes


def build_actionable_routes(rows):
    routes = []
    entries = [
        row for row in rows
        if row["profit"] is not None
        and row["profit"] > 0
        and row["risk"] == "OK"
        and row["liquidity_score"] >= 50
        and row["steam_spread"] is not None
        and row["steam_spread"] <= 12
        and row["steam_buy_depth"] >= 5
    ]
    exits = [
        row for row in rows
        if row["risk"] == "OK"
        and row["liquidity_score"] >= 50
        and row["steam_spread"] is not None
        and row["steam_spread"] <= 12
        and row["fastsell"] is not None
        and row["final_cash"] is not None
        and row["steam_buy_depth"] >= 5
    ]

    for entry in entries:
        start_cash = entry["csmarket_lowest"]
        steam_balance = entry["steam_after_fee"]

        for exit_item in exits:
            if exit_item["name"] == entry["name"]:
                continue
            if exit_item["steam_lowest"] <= 0:
                continue

            exit_qty = int(steam_balance // exit_item["steam_lowest"])
            if exit_qty < 1:
                continue

            steam_spent = money(exit_qty * exit_item["steam_lowest"])
            steam_leftover = money(steam_balance - steam_spent)
            final_cash = money(exit_qty * exit_item["final_cash"])
            net_profit = money(final_cash - start_cash)

            if net_profit <= MIN_ROUTE_PROFIT:
