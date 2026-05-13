import requests
from .currency import normalize_to_eur


class CSMarketAPI:
    def __init__(self):
        self.api_base = "[market.csgo.com](https://market.csgo.com/api/v2)"

    def _fetch_listings(self, market_hash_name):
        url = f"{self.api_base}/search-list-items-by-hash-name-all"
        params = {"key": "", "hash_name": market_hash_name}
        try:
            r = requests.get(url, params=params, timeout=8)
            return r.json()
        except:
            return {}

    def _fetch_autobuy(self, market_hash_name):
        url = f"{self.api_base}/buy-orders-summary"
        params = {"key": "", "hash_name": market_hash_name}
        try:
            r = requests.get(url, params=params, timeout=8)
            return r.json()
        except:
            return {}

    def get_item(self, market_hash_name):
        listings = self._fetch_listings(market_hash_name)
        autobuy = self._fetch_autobuy(market_hash_name)

        cheapest_raw = None
        currency = "EUR"

        if "data" in listings and listings["data"]:
            first = listings["data"][0]
            cheapest_raw = first.get("price")
            currency = first.get("currency", "EUR")

        autobuy_raw = None
        if "data" in autobuy and autobuy["data"]:
            autobuy_raw = autobuy["data"].get("best_order")

        cheapest = normalize_to_eur(cheapest_raw, currency) if cheapest_raw else None
        autobuy_price = normalize_to_eur(autobuy_raw, currency) if autobuy_raw else None

        if autobuy_price and autobuy_price > 0:
            fastsell = autobuy_price
        else:
            fastsell = cheapest * 0.995 if cheapest else None

        return {
            "name": market_hash_name,
            "cheapest_listing": cheapest,
            "currency": currency,
            "fastsell": fastsell,
            "autobuy_price": autobuy_price
        }
