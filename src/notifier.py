import logging
import asyncio
from telegram import Bot
from src.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_telegram_message(message):
    """
    Sends a message to the configured Telegram chat.
    """
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
        logger.info("Telegram message sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

def format_analysis_for_telegram(analysis_json):
    """
    Formats the JSON analysis into a readable Telegram message.
    """
    if not analysis_json or "error" in analysis_json:
        return f"⚠️ *Analysis Error*: {analysis_json.get('error', 'Unknown error')}"

    summary = analysis_json.get("summary", "No summary available.")
    risk = analysis_json.get("risk_status", "UNKNOWN")
    
    levels = "\n".join([f"• {lvl}" for lvl in analysis_json.get("key_levels", [])])
    trades = "\n".join([f"• {trade}" for trade in analysis_json.get("trade_recommendations", [])])
    
    message = (
        f"📊 *Crypto Analysis Bot*\n\n"
        f"**Risk Status:** `{risk}`\n\n"
        f"**Summary:**\n{summary}\n\n"
        f"**Key Levels:**\n{levels}\n\n"
        f"**Trade Ideas:**\n{trades}"
    )
    return message
