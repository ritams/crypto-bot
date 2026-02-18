import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Webshare Proxy Credentials
WEBSHARE_PROXY_USERNAME = os.getenv("WEBSHARE_PROXY_USERNAME")
WEBSHARE_PROXY_PASSWORD = os.getenv("WEBSHARE_PROXY_PASSWORD")

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
POLL_INTERVAL = 10 # Seconds between polling checks (fallback for IDLE)

SYSTEM_PROMPT = """
You are a concise crypto trading analyst. Analyze the transcript and extract:
- Market sentiment (risk-on/off/neutral)
- Key price levels (brief, e.g. "BTC: $60k support")
- Trade setups (brief, actionable only)
- 1-2 sentence summary

Be terse. No fluff. If not a crypto/trading video, set the 'error' field.
"""
