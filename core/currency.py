USD_TO_EUR = 0.85
RUB_TO_EUR = 0.011
EUR_TO_EUR = 1.0


def normalize_to_eur(price, currency):
    if price is None:
        return None

    c = currency.upper()

    if c == "USD":
        return round(price * USD_TO_EUR, 4)

    if c == "RUB":
        return round(price * RUB_TO_EUR, 4)

    return round(price * EUR_TO_EUR, 4)
