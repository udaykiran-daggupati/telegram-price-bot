import asyncio
import json
import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.google.com/"
}

def clean_price(text):
    return float(text.replace("₹", "").replace(",", "").strip())

def fetch_price(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    price_span = soup.select_one("span.a-offscreen")
    return price_span.get_text(strip=True) if price_span else None

def load_prices():
    if os.path.exists("prices.json"):
        with open("prices.json", "r") as f:
            return json.load(f)
    return {}

def save_prices(data):
    with open("prices.json", "w") as f:
        json.dump(data, f)

async def main():
    bot = Bot(token=BOT_TOKEN)
    old_prices = load_prices()

    with open("products.json", "r") as f:
        products = json.load(f)

    updated_prices = old_prices.copy()

    for p in products:
        name = p["name"]
        url = p["url"]

        price_text = fetch_price(url)
        if not price_text:
            continue

        price = clean_price(price_text)
        old_price = old_prices.get(name)

        if old_price is None:
            updated_prices[name] = price
            continue

        if price < old_price:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=(
                    "🔥 PRICE DROP ALERT!\n\n"
                    f"📦 {name}\n"
                    f"Old Price: ₹{old_price}\n"
                    f"New Price: ₹{price}\n\n"
                    f"🛒 Buy now:\n{url}"
                )
            )
            updated_prices[name] = price

    save_prices(updated_prices)

asyncio.run(main())
