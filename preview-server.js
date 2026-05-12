async function fetchJson(url) {
  const res = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9" } });
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}

function parsePrice(value) {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value === "number") return value;
  let text = String(value).replace(/\u00a0/g, " ").replace(/[^\d,.-]/g, "");
  if (!text) return null;
  if (text.includes(",") && !text.includes(".")) text = text.replace(",", ".");
  if (text.includes(",") && text.includes(".")) text = text.replace(/,/g, "");
  const parsed = Number(text);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseIntValue(value) {
  const digits = String(value || "").replace(/[^\d]/g, "");
  return digits ? Number(digits) : 0;
}

const money = (value) => (value === null || value === undefined ? null : Number(value.toFixed(2)));
const pct = (value) => (value === null || value === undefined ? null : Number(value.toFixed(2)));
const eur = (value) => (value === null || value === undefined ? "-" : `€${Number(value).toFixed(2)}`);
const pc = (value) => (value === null || value === undefined ? "-" : `${Number(value).toFixed(2)}%`);
const spread = (lowest, buy) => (!lowest || !buy ? null : pct(Math.max(((lowest - buy) / lowest) * 100, 0)));

async function steamMeta(name) {
  return cached(`steam-meta:${name}`, async () => {
    let nameid = null;
    let icon = null;

    try {
      const index = await cached("steam-nameid-index", () => fetchJson(STEAM_NAMEID_INDEX_URL), 86400000);
      nameid = index[name] ? String(index[name]) : null;
    } catch {
      nameid = null;
    }

    if (!nameid) {
      try {
        const page = await fetchText(`https://steamcommunity.com/market/listings/${STEAM_APP_ID}/${encodeURIComponent(name)}`);
        nameid = page.match(/Market_LoadOrderSpread\(\s*['"]?(\d+)['"]?\s*\)/)?.[1] || null;
        icon = page.match(/"icon_url"\s*:\s*"([^"]+)"/)?.[1]?.replace(/\\\//g, "/") || null;
      } catch {
        nameid = null;
      }
    }
    if (!icon) {
      try {
        const url = new URL(`https://steamcommunity.com/market/listings/${STEAM_APP_ID}/${encodeURIComponent(name)}/render`);
        url.searchParams.set("start", "0");
        url.searchParams.set("count", "1");
        url.searchParams.set("currency", String(STEAM_CURRENCY));
        url.searchParams.set("language", "english");
        url.searchParams.set("format", "json");
        const render = await fetchJson(url);
        const assets = render.assets || {};
        for (const appAssets of Object.values(assets)) {
          for (const contextAssets of Object.values(appAssets)) {
            for (const asset of Object.values(contextAssets)) {
              if (asset.icon_url) {
                icon = asset.icon_url;
                break;
              }
            }
            if (icon) break;
          }
          if (icon) break;
        }
      } catch {
        icon = null;
      }
    }
    return {
      itemNameId: nameid,
      image: icon ? `https://community.cloudflare.steamstatic.com/economy/image/${icon}/96fx96f` : null,
    };
  }, 86400000);
}

async function steamOverview(name) {
  return cached(`steam-price:${name}`, async () => {
    const url = new URL("https://steamcommunity.com/market/priceoverview/");
    url.searchParams.set("appid", STEAM_APP_ID);
    url.searchParams.set("currency", STEAM_CURRENCY);
    url.searchParams.set("market_hash_name", name);
    const data = await fetchJson(url);
    return {
      lowest: parsePrice(data.lowest_price),
      median: parsePrice(data.median_price),
      volume: parseIntValue(data.volume),
    };
  });
}

function depthNear(graph, target, side) {
  if (!graph?.length || !target) return 0;
  let qty = 0;
  for (const point of graph) {
    const price = parsePrice(point[0]);
    const amount = parseIntValue(point[1]);
    if (price === null) continue;
    if (side === "sell" && price <= target * 1.02) qty = Math.max(qty, amount);
    if (side === "buy" && price >= target * 0.98) qty = Math.max(qty, amount);
  }
  return qty;
}

async function steamOrders(itemNameId) {
  if (!itemNameId) return { lowestSell: null, highestBuy: null, buyDepth: 0, sellDepth: 0 };
  return cached(`steam-orders:${itemNameId}`, async () => {
    const url = new URL("https://steamcommunity.com/market/itemordershistogram");
    url.searchParams.set("country", STEAM_COUNTRY);
    url.searchParams.set("language", "english");
    url.searchParams.set("currency", STEAM_CURRENCY);
    url.searchParams.set("item_nameid", itemNameId);
    url.searchParams.set("two_factor", "0");
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://steamcommunity.com/market/",
      },
    });
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    const data = await res.json();
    const sell = data.sell_order_graph || [];
    const buy = data.buy_order_graph || [];
    const lowestSell = sell.length ? parsePrice(sell[0][0]) : null;
    const highestBuy = buy.length ? parsePrice(buy[0][0]) : null;
    return {
      lowestSell,
      highestBuy,
      sellDepth: depthNear(sell, lowestSell, "sell"),
      buyDepth: depthNear(buy, highestBuy, "buy"),
    };
  });
}

async function csmarketIndex() {
  return cached("csmarket-index", async () => {
    const data = await fetchJson("https://market.csgo.com/api/v2/prices/class_instance/EUR.json");
    const raw = data.items || {};
    const index = {};
    for (const [itemKey, item] of Object.entries(raw)) {
      if (!item?.market_hash_name) continue;
      const price = parsePrice(item.price);
      if (!price) continue;
      const classid = String(itemKey).split("_")[0] || item.classid;
      const row = {
        lowest: price,
        buyOrder: parsePrice(item.buy_order),
        avgPrice: parsePrice(item.avg_price),
        popularity: parseIntValue(item.popularity_7d || item.volume),
        image: classid ? `https://community.cloudflare.steamstatic.com/economy/image/class/730/${classid}/96fx96f` : null,
      };
      if (!index[item.market_hash_name] || row.lowest < index[item.market_hash_name].lowest) {
        index[item.market_hash_name] = row;
      }
    }
    return index;
  });
}

function liquidityScore(volume, itemSpread, buyDepth, sellDepth) {
  if (itemSpread === null) return 0;
  const volumeScore = Math.min((volume / 300) * 35, 35);
  const spreadScore = itemSpread < 5 ? 35 : itemSpread < 8 ? 28 : itemSpread < 12 ? 18 : itemSpread <= 15 ? 10 : 0;
  const depthScore = Math.min(((buyDepth + sellDepth) / 80) * 30, 30);
  return Math.round(volumeScore + spreadScore + depthScore);
}

const liquidityLabel = (score) => (score >= 75 ? "HIGH" : score >= 50 ? "MID" : "LOW");
const saleTime = (score, itemSpread, volume) => score >= 80 && itemSpread < 5 ? "5 min" : score >= 65 && volume >= 100 ? "30 min" : score >= 50 ? "2 hours" : "1 day";
const saleTimeMinutes = (label) => ({ "5 min": 5, "30 min": 30, "2 hours": 120, "1 day": 1440 }[label] || 1440);

function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} min`;
  if (minutes < 1440) return `${Number((minutes / 60).toFixed(1))}h`;
  return `${Number((minutes / 1440).toFixed(1))}d`;
}

function routeConfidence(entry, exitItem, netProfitPct) {
  const minLiquidity = Math.min(entry.score, exitItem.score);
  const maxSpread = Math.max(entry.steamSpread ?? 99, exitItem.steamSpread ?? 99);
  const minDepth = Math.min(entry.buyDepth, exitItem.buyDepth);
  if (netProfitPct >= 3 && minLiquidity >= 75 && maxSpread <= 6 && minDepth >= 20) return "HIGH";
  if (netProfitPct >= 1 && minLiquidity >= 55 && maxSpread <= 10) return "MEDIUM";
  return "LOW";
}

function actionableRouteScore(route) {
  const confidenceScore = { HIGH: 30, MEDIUM: 18, LOW: 6 }[route.confidence];
  const liquidityPart = Math.min((route.liquidityScore / 100) * 30, 30);
  const profitPart = Math.min(route.netProfitPct * 8, 30);
  const speedPart = Math.max(10 - route.estimatedMinutes / 180, 0);
  return Number((confidenceScore + liquidityPart + profitPart + speedPart).toFixed(2));
}

function safeUndercut(itemSpread, volume, buyDepth) {
  if (itemSpread === null) return 3.0;
  if (itemSpread < 5 && volume >= 150 && buyDepth >= 20) return 0.7;
  if (itemSpread < 8 && volume >= 80) return 1.2;
  if (itemSpread < 12) return 2.0;
  return 3.5;
}

async function scan() {
  const errors = [];
  let cs = {};
  try {
    cs = await csmarketIndex();
  } catch (error) {
    errors.push(`CSMarket: ${error.message}`);
  }

  const rows = [];
  for (const name of itemPool) {
    try {
      const market = cs[name];
      if (!market) continue;
      const meta = await steamMeta(name);
      const overview = await steamOverview(name);
      const orders = await steamOrders(meta.itemNameId);
      const steamLowest = orders.lowestSell || overview.lowest;
      const steamBuy = orders.highestBuy;
      const volume = overview.volume || market.popularity;
      if (!steamLowest || steamLowest < MIN_PRICE || steamLowest > MAX_PRICE || volume < MIN_VOLUME) continue;
      const itemSpread = spread(steamLowest, steamBuy);
      const score = liquidityScore(volume, itemSpread, orders.buyDepth, orders.sellDepth);
      const undercut = safeUndercut(itemSpread, volume, orders.buyDepth);
      const safeSell = money(market.lowest * (1 - undercut / 100));
      const fastsell = money(Math.max(market.buyOrder || 0, safeSell));
      const panic = money(Math.max(market.buyOrder || 0, market.lowest * 0.92));
      const finalCash = money(fastsell * CSMARKET_CASHOUT);
      const loss = money(steamLowest - finalCash);
      rows.push({
        name,
        image: meta.image || market.image,
        steamLowest: money(steamLowest),
        steamBuy: money(steamBuy),
        steamAfterFee: money(steamLowest * STEAM_FEE),
        steamSpread: itemSpread,
        volume,
        buyDepth: orders.buyDepth,
        sellDepth: orders.sellDepth,
        csLowest: money(market.lowest),
        csBuy: money(market.buyOrder),
