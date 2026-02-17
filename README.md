# Crypto Analysis Bot

A Python bot that monitors your Gmail for "Into the Cryptoverse" emails, extracts the YouTube transcript, analyzes it with AI (OpenRouter), and sends a summary to Telegram.

## Setup Instructions

### 1. Install Dependencies
Make sure you have `uv` installed.
```bash
uv sync
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (if not done already) and fill in the values:

```bash
# Your full Gmail address
EMAIL_USER=your_email@gmail.com

# ⚠️ DO NOT USE YOUR REAL PASSWORD if you have 2FA enabled!
# Generate an App Password:
# 1. Go to Google Account > Security > 2-Step Verification
# 2. Scroll to the bottom and select "App passwords"
# 3. Create a new one (e.g. name it "CryptoBot")
# 4. Use that 16-character code here.
EMAIL_PASS=xxxx xxxx xxxx xxxx

# Your OpenRouter API Key for AI analysis
OPENROUTER_API_KEY=sk-or-...

# Telegram Bot Token (from @BotFather)
TELEGRAM_TOKEN=123456:ABC-DEF...

# Your Chat ID (get it from running `uv run python get_id.py`)
TELEGRAM_CHAT_ID=123456789
```

### 3. Telegram Setup (Detailed)

1.  **Create a New Bot**:
    *   Open Telegram and search for **@BotFather**.
    *   Send the command `/newbot`.
    *   Follow the prompts to name your bot (e.g., "MyCryptoAnalyst") and give it a username (e.g., "my_crypto_analyst_bot").
    *   BotFather will give you a **Token** (looks like `123456:ABC-DEF...`).
    *   Copy this token to `TELEGRAM_TOKEN` in your `.env` file.

2.  **Get Your Chat ID**:

    **Option A: The Easy Way (@userinfobot)**
    *   Open Telegram and search for **@userinfobot**.
    *   Click **Start**.
    *   It will reply with your details. Copy the `Id` line.
    *   Paste it into `TELEGRAM_CHAT_ID` in your `.env` file.

    **Option B: Using the Python Script**
    *   Start a chat with your new bot and say "hello".
    *   Run the helper script included in this project:
        ```bash
        uv run python get_id.py
        ```
    *   It will print your Chat ID. Copy it to `TELEGRAM_CHAT_ID` in your `.env` file.

### 4. Run the Bot
```bash
uv run python main.py
```

## Features
- **Real-time Monitoring**: Uses IMAP IDLE to detect emails instantly.
- **No Audio Download**: Uses `youtube-transcript-api` to fetch captions directly.
- **AI Analysis**: Extracts Risk Status, Key Levels, and Trade Ideas.
