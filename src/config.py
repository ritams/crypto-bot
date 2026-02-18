import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# OAuth2 Credentials
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TARGET_SENDER = "ritam4jnu@gmail.com"  # Or whatever the actual sender is
SAVE_TRANSCRIPTS = True # Set to False to disable saving transcripts
LLM_MODEL = "claude-sonnet-4-6"
PROCESSED_IDS_FILE = "processed_videos.json"
POLL_INTERVAL = 60 # Seconds between polling checks (fallback for IDLE)

SYSTEM_PROMPT = """
You are an expert Crypto Trader and Analyst. 
Your task is to analyze the provided YouTube video transcript and extract actionable intelligence.

Please structure your response in the following JSON format:
{
  "summary": "A brief 2-3 sentence summary of the video's main point.",
  "risk_status": "RISK-ON | RISK-OFF | NEUTRAL",
  "key_levels": [
    "BTC Support: $60k",
    "ETH Resistance: $3k"
  ],
  "trade_recommendations": [
    "Buy BTC if it holds $60k",
    "Short ETH at $3.2k"
  ]
}

If the transcript is not about crypto trading, return: {"error": "Not a crypto/trading video."}
"""
