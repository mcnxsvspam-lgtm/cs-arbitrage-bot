from flask import Flask, render_template, request
from urllib.parse import quote
import html
import json
import os
import re
import time

import requests

app = Flask(__name__)

STEAM_APP_ID = 730
STEAM_FEE_MULTIPLIER = 0.8697
CSMARKET_CASHOUT_MULTIPLIER = 0.9025
STEAM_CURRENCY = int(os.environ.get("STEAM_CURRENCY", "3"))
STEAM_COUNTRY = os.environ.get("STEAM_COUNTRY", "AT")
STEAM_LANGUAGE = os.environ.get("STEAM_LANGUAGE", "english")
CSMARKET_CURRENCY = os.environ.get("CSMARKET_CURRENCY", "EUR")
STEAM_NAMEID_INDEX_URL = os.environ.get(
    "STEAM_NAMEID_INDEX_URL",
    "https://raw.githubusercontent.com/somespecialone/steam-item-name-ids/master/data/cs2.json",
)
MIN_PRICE = float(os.environ.get("MIN_SCAN_PRICE", "10"))
MAX_PRICE = float(os.environ.get("MAX_SCAN_PRICE", "150"))
MIN_VOLUME = int(os.environ.get("MIN_SCAN_VOLUME", "20"))
MIN_ROUTE_PROFIT = float(os.environ.get("MIN_ROUTE_PROFIT", "0.25"))
CACHE_TTL = int(os.environ.get("CACHE_TTL_SECONDS", "300"))

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
})

CACHE = {}

ITEM_POOL = [
    "AK-47 | Redline (Field-Tested)",
    "AK-47 | Legion of Anubis (Field-Tested)",
    "AK-47 | Nightwish (Field-Tested)",
    "M4A1-S | Cyrex (Field-Tested)",
    "M4A1-S | Decimator (Field-Tested)",
    "M4A1-S | Printstream (Battle-Scarred)",
    "M4A4 | The Emperor (Field-Tested)",
    "M4A4 | Desolate Space (Field-Tested)",
    "AWP | Asiimov (Battle-Scarred)",
    "AWP | Neo-Noir (Field-Tested)",
    "USP-S | Kill Confirmed (Field-Tested)",
    "USP-S | The Traitor (Field-Tested)",
    "Glock-18 | Vogue (Field-Tested)",
    "Desert Eagle | Printstream (Field-Tested)",
    "Desert Eagle | Code Red (Field-Tested)",
]

ALLOWED_WEARS = ["Field-Tested", "Well-Worn", "Battle-Scarred"]
IGNORED_WORDS = ["Souvenir", "Sticker", "StatTrak", "Capsule", "Patch", "Music Kit"]


def cached(key, loader, ttl=CACHE_TTL):
    now = time.time()
    hit = CACHE.get(key)
    if hit and now - hit["time"] < ttl:
        return hit["value"]

    value = loader()
    CACHE[key] = {"time": now, "value": value}
    return value


def parse_price(value):
    if value in [None, "", "-"]:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"[^\d,.\-]", "", text)
    if not text:
        return None

    if "," in text and "." not in text:
        text = text.replace(",", ".")
    elif "," in text and "." in text:
        text = text.replace(",", "")

    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value):
    if value in [None, "", "-"]:
        return 0
    digits = re.sub(r"[^\d]", "", str(value))
