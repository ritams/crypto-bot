import asyncio
from telegram import Bot
from src.config import TELEGRAM_TOKEN

async def get_chat_id():
    if not TELEGRAM_TOKEN or "your_" in TELEGRAM_TOKEN:
        print("Please set your TELEGRAM_TOKEN in .env first!")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    print(f"Checking updates for bot: {(await bot.get_me()).username}")
    print("Please send a message to your bot on Telegram now...")
    
    # Simple polling loop to get the first update
    offset = None
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                if update.message:
                    chat_id = update.message.chat_id
                    username = update.message.from_user.username
                    print(f"\nSUCCESS! Found message from @{username}")
                    print(f"Your Chat ID is: {chat_id}")
                    print("\nCopy this ID to your .env file as TELEGRAM_CHAT_ID")
                    return
                offset = update.update_id + 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(get_chat_id())
