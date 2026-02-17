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

def load_processed_ids():
    """Loads processed video IDs from the JSON file."""
    if os.path.exists(PROCESSED_IDS_FILE):
        try:
            with open(PROCESSED_IDS_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load processed IDs: {e}")
    return set()

def save_processed_id(video_id):
    """Saves a new video ID to the JSON file."""
    ids = load_processed_ids()
    ids.add(video_id)
    try:
        with open(PROCESSED_IDS_FILE, "w") as f:
            json.dump(list(ids), f)
        logger.info(f"Video ID {video_id} marked as processed.")
    except Exception as e:
        logger.error(f"Failed to save processed ID: {e}")

def save_transcript_to_file(video_id, text):
    # ... existing save_transcript_to_file ...
    try:
        os.makedirs("transcripts", exist_ok=True)
        filename = f"transcripts/{video_id}.txt"
        with open(filename, "w") as f:
            f.write(text)
        logger.info(f"Transcript saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save transcript: {e}")

def process_video(video_id):
    """
    Orchestrates the pipeline for a single video.
    """
    logger.info(f"Processing Video ID: {video_id}")

    # 0. Deduplication Check
    processed_ids = load_processed_ids()
    if video_id in processed_ids:
        logger.info(f"Skipping {video_id}: Already processed.")
        return
    
    # 1. Get Transcript
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
    message = format_analysis_for_telegram(analysis)
    logger.info(f"Telegram message: {message}")
    
    # Run async function in sync context
    try:
        asyncio.run(send_telegram_message(message))
        # 4. Mark as complete only if successful
        save_processed_id(video_id)
    except Exception as e:
        logger.error(f"Error in notification loop: {e}")

def main():
    logger.info("Starting Crypto Bot...")
    try:
        # Blocks here until an email arrives
        listen_for_emails(callback=process_video)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
