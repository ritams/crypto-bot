import os
import json
import asyncio
import logging
from src.config import SAVE_TRANSCRIPTS, PROCESSED_IDS_FILE
from src.monitor import listen_for_emails
from src.extractor import get_transcript
from src.analyst import analyze_transcript
from src.notifier import send_telegram_message, format_analysis_for_telegram

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def load_processed_data():
    """Loads processed email UIDs and video IDs from the JSON file."""
    if os.path.exists(PROCESSED_IDS_FILE):
        try:
            with open(PROCESSED_IDS_FILE, "r") as f:
                data = json.load(f)
            # Migrate from old format (plain list of video IDs)
            if isinstance(data, list):
                return {"emails": [], "videos": data}
            return data
        except Exception as e:
            logger.error(f"Failed to load processed data: {e}")
    return {"emails": [], "videos": []}


def save_processed_data(data):
    """Saves processed data back to the JSON file."""
    try:
        with open(PROCESSED_IDS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save processed data: {e}")


def save_transcript_to_file(video_id, text):
    try:
        os.makedirs("data/transcripts", exist_ok=True)
        filename = f"data/transcripts/{video_id}.txt"
        with open(filename, "w") as f:
            f.write(text)
        logger.info(f"Transcript saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save transcript: {e}")


def process_video(video_id, received_at=None, email_uid=None):
    """
    Orchestrates the pipeline for a single video from an email.
    """
    data = load_processed_data()

    # Check if email was already processed
    if email_uid and email_uid in data["emails"]:
        logger.info(f"Skipping email UID={email_uid}: Already processed.")
        return

    # No video link in email — mark email as processed and skip
    if not video_id:
        logger.info(f"Email UID={email_uid} has no video link, marking as processed.")
        if email_uid:
            data["emails"].append(email_uid)
            save_processed_data(data)
        return

    # Check if video was already processed
    if video_id in data["videos"]:
        logger.info(f"Skipping {video_id}: Already processed.")
        if email_uid and email_uid not in data["emails"]:
            data["emails"].append(email_uid)
            save_processed_data(data)
        return

    logger.info(f"Processing Video ID: {video_id}")

    # 1. Get Transcript (YouTube captions → Whisper fallback)
    transcript = get_transcript(video_id)
    if not transcript:
        logger.error("Aborting: No transcript found.")
        return

    # 1b. Save Transcript if enabled
    if SAVE_TRANSCRIPTS:
        save_transcript_to_file(video_id, transcript)

    # 2. Analyze
    analysis = analyze_transcript(transcript)
    if not analysis:
        logger.error("Aborting: Analysis failed.")
        return

    # 3. Notify
    message = format_analysis_for_telegram(analysis, received_at=received_at)
    logger.info(f"Telegram message: {message}")

    try:
        asyncio.run(send_telegram_message(message))
        # 4. Mark as complete only if successful
        data = load_processed_data()  # Reload in case of concurrent changes
        data["videos"].append(video_id)
        if email_uid and email_uid not in data["emails"]:
            data["emails"].append(email_uid)
        save_processed_data(data)
        logger.info(f"Video {video_id} and email UID={email_uid} marked as processed.")
    except Exception as e:
        logger.error(f"Error in notification loop: {e}")


def main():
    logger.info("Starting Crypto Bot...")
    try:
        listen_for_emails(callback=process_video)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
