import requests
import json

TEST_ITEM = "AK-47 | Redline (Field-Tested)"

ENDPOINTS = [
    # NEW Domain (2026)
    "[market.csgo.com](https://market.csgo.com/api/v2/search-list-items-by-hash-name-all)",
    "[market.csgo.com](https://market.csgo.com/api/v2/search-item-by-hash-name)",
    "[market.csgo.com](https://market.csgo.com/api/v2/items)",
    "[market.csgo.com](https://market.csgo.com/api/v2/get-list-items-info)",

    # OLD Domain
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/search-list-items-by-hash-name-all)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/search-item-by-hash-name)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/items)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/get-list-items-info)",
]


def test_endpoint(url, params):
    print("=" * 70)
    print("TESTING:", url)
    try:
        r = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print("REQUEST FAILED:", e)
        return

    print("STATUS:", r.status_code)

    try:
        data = r.json()
        print("JSON RESPONSE:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print("NON-JSON RESPONSE:")
        print(r.text[:2000])  # prevent huge spam


def main():
    print("=== CSMarket Endpoint Debugger ===")
    print("Testing item:", TEST_ITEM)
    print()

    params = {
        "key": "",  # optional unless using authenticated buy/sell
        "hash_name": TEST_ITEM
    }

    for url in ENDPOINTS:
        test_endpoint(url, params)


if __name__ == "__main__":
    main()
