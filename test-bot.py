import asyncio
from telegram import Bot

BOT_TOKEN = "8341222978:AAGBVcZpUBflaiU3cS0g8XlmMir_q1GeNxs"
CHANNEL_ID = "-1003571934893"

async def main():
    print("🚀 Script started")
    bot = Bot(token=BOT_TOKEN)
    print("🤖 Bot object created")
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text="✅ Test message from bot"
    )
    print("📨 Message sent call executed")

asyncio.run(main())

