import asyncio
import json
import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# =========================
# ENV VARIABLES (GitHub Secrets)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN or CHANNEL_ID not set")

# =========================
# REQUEST HEADERS
# =========================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# =========================
# HELPER FUNCTIONS
# =========================
def clean_price(text: str) -> float:
    return float(
        text.replace("₹", "")
            .replace(",", "")
            .replace("\n", "")
            .strip()
    )

def fetch_price(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        price_span = soup.select_one("span.a-offscreen")
        if not price_span:
            return None

        return clean_price(price_span.get_text(strip=True))

    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def load_prices():
    if os.path.exists("prices.json"):
        with open("prices.json", "r") as f:
            return json.load(f)
    return {}

def save_prices(data):
    with open("prices.json", "w") as f:
        json.dump(data, f, indent=2)

# =========================
# MAIN LOGIC
# =========================
async def main():
    print("🚀 Bot started")

    bot = Bot(token=BOT_TOKEN)
    old_prices = load_prices()

    with open("products.json", "r") as f:
        products = json.load(f)

    updated_prices = old_prices.copy()

    for product in products:
        pid = product["id"]
        name = product["name"]
        url = product["url"]

        current_price = fetch_price(url)
        if current_price is None:
            print(f"⚠️ Price not found for {name}")
            continue

        old_price = old_prices.get(pid)

        # First run for this product
        if old_price is None:
            print(f"📦 First run — saving price for {name}: ₹{current_price}")
            updated_prices[pid] = current_price
            continue

        # Price drop detected
        if current_price < old_price:
            print(f"🔥 Price drop for {name}: {old_price} → {current_price}")

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=(
                    "🔥 *PRICE DROP ALERT!*\n\n"
                    f"📦 *{name}*\n"
                    f"~~₹{old_price}~~ → *₹{current_price}*\n\n"
                    f"🛒 Buy now:\n{url}"
                ),
                parse_mode="Markdown"
            )

            updated_prices[pid] = current_price

        else:
            print(f"ℹ️ No drop for {name} (₹{current_price})")
            updated_prices[pid] = old_price

    save_prices(updated_prices)
    print("✅ Run completed")

# =========================
# ENTRY POINT
# =========================
asyncio.run(main())
