import requests
import json
import os

TEST_ITEM = "AK-47 | Redline (Field-Tested)"

ENDPOINTS = [
    # New Domain (claimed modern API)
    "[market.csgo.com](https://market.csgo.com/api/v2/search-list-items-by-hash-name-all)",
    "[market.csgo.com](https://market.csgo.com/api/v2/search-item-by-hash-name)",
    "[market.csgo.com](https://market.csgo.com/api/v2/search)",
    "[market.csgo.com](https://market.csgo.com/api/v2/buy-orders-summary)",
    "[market.csgo.com](https://market.csgo.com/api/v2/get-list-items-info)",

    # Old Domain (still works for many developers)
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/search-list-items-by-hash-name-all)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/search-item-by-hash-name)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/search)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/buy-orders-summary)",
    "[market-old.csgo.com](https://market-old.csgo.com/api/v2/get-list-items-info)",
]


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


def save_output(index, data):
    os.makedirs("debug_output", exist_ok=True)
    filename = f"debug_output/endpoint_{index}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to: {filename}")


def test_endpoint(i, url, params):
    print("=" * 80)
    print(f"TEST #{i}: {url}")

    try:
        r = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print("REQUEST FAILED:", e)
        return

    # Print actual requested URL
    print("\nFinal Request URL:")
    print(" ", r.url)

    print("\nHTTP STATUS:", r.status_code)

    print("\nCONTENT-TYPE:", r.headers.get("Content-Type", "UNKNOWN"))

    print("\nHEADERS:")
    for k, v in r.headers.items():
        print(f"  {k}: {v}")

    print("\nBODY:")

    data = safe_json(r)
    if data is not None:
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        print(pretty)

        if r.status_code == 200:
            save_output(i, data)
    else:
        print(r.text[:5000])  # Print up to 5k chars to avoid spam


def main():
    print("=== CSMarket Endpoint Debugger ===")
    print("Testing item:", TEST_ITEM)
    print()

    params = {
        "key": "",           # public data doesn’t need a key
        "hash_name": TEST_ITEM
    }

    for i, url in enumerate(ENDPOINTS, start=1):
        test_endpoint(i, url, params)


if __name__ == "__main__":
    main()
