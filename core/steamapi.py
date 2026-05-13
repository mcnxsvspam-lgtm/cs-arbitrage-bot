import requests

STEAM_FEE_MULTIPLIER = 0.8697


class SteamAPI:
    def __init__(self, currency="EUR"):
        self.currency = currency

    def _priceoverview(self, appid, market_hash_name):
        url = "[steamcommunity.com](https://steamcommunity.com/market/priceoverview/)"
        params = {
            "currency": 3,
            "appid": appid,
            "market_hash_name": market_hash_name
        }
        r = requests.get(url, params=params, timeout=8)
        return r.json()

    def _extract_item_nameid(self, appid, market_hash_name):
        url = f"[steamcommunity.com](https://steamcommunity.com/market/listings/{appid}/{market_hash_name})"
        html = requests.get(url, timeout=8).text

        marker = "Market_LoadOrderSpread("
        pos = html.find(marker)
        if pos == -1:
            return None

        start = pos + len(marker)
        end = html.find(")", start)
        raw = html[start:end].strip()
        return raw.split(",")[0]

    def _histogram(self, item_nameid):
        if not item_nameid:
            return {}

        url = "[steamcommunity.com](https://steamcommunity.com/market/itemordershistogram)"
        params = {
            "currency": 3,
            "language": "en",
            "item_nameid": item_nameid
        }
        r = requests.get(url, params=params, timeout=8)
        return r.json()

    def get_item(self, appid, market_hash_name):
        po = self._priceoverview(appid, market_hash_name)

        def parse_price(s):
            if not s:
                return None
            s = s.replace("€", "").replace("$", "").replace(" ", "").replace(",", ".")
            try:
                return float(s)
            except:
                return None

        lowest_sell = parse_price(po.get("lowest_price"))

        nameid = self._extract_item_nameid(appid, market_hash_name)
        hist = self._histogram(nameid)

        def parse_hist(s):
            if not s:
                return None
            s = s.replace("€", "").replace("$", "").replace(" ", "").replace(",", ".")
            try:
                return float(s)
            except:
                return None

        highest_buy = parse_hist(hist.get("buy_order_price"))
        buy_count = int(hist.get("buy_order_count", 0))
        sell_count = int(hist.get("sell_order_count", 0))

        if highest_buy and lowest_sell:
            spread = ((lowest_sell - highest_buy) / lowest_sell) * 100
        else:
            spread = None

        steam_after = highest_buy * STEAM_FEE_MULTIPLIER if highest_buy else None

        return {
            "name": market_hash_name,
            "highest_buy_order": highest_buy,
            "lowest_sell_listing": lowest_sell,
            "buy_order_count": buy_count,
            "sell_order_count": sell_count,
            "spread_pct": spread,
            "steam_after_fee": steam_after
        }
