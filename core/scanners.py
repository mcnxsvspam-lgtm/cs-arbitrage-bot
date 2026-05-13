import math

STEAM_FEE = 0.8697
WITHDRAW_FEE = 0.95


def cashout_scan(rows):
    results = []
    for r in rows:
        hb = r.get("steam", {}).get("highest_buy_order")
        ls = r.get("steam", {}).get("lowest_sell_listing")
        cs = r.get("cs", {}).get("cheapest_listing")
        fs = r.get("cs", {}).get("fastsell")

        if not hb or not ls or not cs or not fs:
            continue

        steam_after = hb * STEAM_FEE
        final_cash = fs * WITHDRAW_FEE
        kept_pct = (final_cash / steam_after) * 100 if steam_after > 0 else None
        spread = ((ls - hb) / ls) * 100 if ls > 0 else None

        results.append({
            "item": r["name"],
            "highest_buy": hb,
            "lowest_sell": ls,
            "spread_pct": spread,
            "steam_after_fee": steam_after,
            "cs_cheapest": cs,
            "fastsell": fs,
            "final_cash": final_cash,
            "kept_pct": kept_pct
        })

    return results


def profit_scan(rows):
    results = []
    for r in rows:
        hb = r.get("steam", {}).get("highest_buy_order")
        cs = r.get("cs", {}).get("cheapest_listing")

        if not hb or not cs:
            continue

        steam_after = hb * STEAM_FEE
        profit = steam_after - cs
        roi = (profit / cs) * 100 if cs > 0 else None

        results.append({
            "item": r["name"],
            "cs_price": cs,
            "steam_after_fee": steam_after,
            "profit": profit,
            "roi_pct": roi
        })

    return results


def routes_scan(rows, start_cash):
    results = []
    for entry in rows:
        for exit_item in rows:
            if entry["name"] == exit_item["name"]:
                continue

            entry_cs = entry.get("cs", {}).get("cheapest_listing")
            exit_price = exit_item.get("steam", {}).get("highest_buy_order")
            exit_cs_fast = exit_item.get("cs", {}).get("fastsell")

            if not entry_cs or not exit_price or not exit_cs_fast:
                continue

            # Buy entry item using start_cash
            qty_entry = math.floor(start_cash / entry_cs)
            if qty_entry < 1:
                continue

            cash_after_entry_buy = start_cash - (qty_entry * entry_cs)

            # Sell entry item instantly on Steam
            steam_after = exit_price * STEAM_FEE
            steam_balance = qty_entry * steam_after

            # Buy exit items on Steam
            exit_item_price = exit_price
            qty_exit = math.floor(steam_balance / exit_item_price)
            if qty_exit < 1:
                continue

            remaining_steam = steam_balance - (qty_exit * exit_item_price)

            # FastSell exit items on CSMarket
            fastsell_cash = qty_exit * exit_cs_fast
            final_cash = fastsell_cash * WITHDRAW_FEE

            profit = final_cash - start_cash
            kept_pct = (final_cash / start_cash) * 100 if start_cash > 0 else None

            if final_cash <= start_cash:
                continue

            results.append({
                "entry_item": entry["name"],
                "exit_item": exit_item["name"],
                "start_cash": start_cash,
                "entry_cs_price": entry_cs,
                "qty_entry": qty_entry,
                "steam_after_fee_per_item": steam_after,
                "steam_balance": steam_balance,
                "exit_item_price": exit_item_price,
                "qty_exit": qty_exit,
                "fastsell_price": exit_cs_fast,
                "final_cash": final_cash,
                "profit": profit,
                "kept_pct": kept_pct,
                "remaining_steam": remaining_steam
            })

    return results
