import os
import glob
import logging
import subprocess
import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from src.config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_DURATION_SECS = 600  # 10 minutes per chunk


def get_transcript(video_id):
    """
    Fetches the transcript for a YouTube video.
    Tries YouTube captions first, falls back to Whisper API if unavailable.
    """
    logger.info(f"Fetching transcript for video: {video_id}")

    # 1. Try YouTube captions
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = ' '.join([entry.text for entry in transcript])
        logger.info(f"YouTube transcript fetched ({len(text)} chars)")
        return text
    except Exception as e:
        logger.warning(f"YouTube transcript unavailable: {e}")

    # 2. Fallback: download audio and transcribe with Whisper
    logger.info("Falling back to Whisper API transcription...")
    return transcribe_with_whisper(video_id)


def transcribe_with_whisper(video_id):
    """
    Downloads low-quality audio from YouTube, splits into 10-min chunks,
    transcribes each chunk with OpenAI Whisper API, and aggregates the results.
    """
    audio_dir = f"data/audio/{video_id}"
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, "full.m4a")

    try:
        # Download lowest quality audio
        ydl_opts = {
            'format': 'worstaudio[ext=m4a]/worstaudio/worst',
            'outtmpl': audio_path,
            'quiet': True,
            'no_warnings': True,
        }
        logger.info(f"Downloading audio for {video_id} (low quality)...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        # Split into 10-minute chunks using ffmpeg
        chunk_pattern = os.path.join(audio_dir, "chunk_%03d.m4a")
        logger.info(f"Splitting audio into {CHUNK_DURATION_SECS // 60}-min chunks...")
        subprocess.run(
            [
                "ffmpeg", "-i", audio_path,
                "-f", "segment",
                "-segment_time", str(CHUNK_DURATION_SECS),
                "-c", "copy",
                "-reset_timestamps", "1",
                chunk_pattern,
            ],
            capture_output=True,
            check=True,
        )

        # Find all chunk files sorted by name
        chunk_files = sorted(glob.glob(os.path.join(audio_dir, "chunk_*.m4a")))
        if not chunk_files:
            logger.error("No audio chunks produced after splitting.")
            return None

        logger.info(f"Transcribing {len(chunk_files)} chunk(s) with Whisper API...")

        # Transcribe each chunk and aggregate
        transcript_parts = []
        for i, chunk_path in enumerate(chunk_files):
            logger.info(f"  Transcribing chunk {i + 1}/{len(chunk_files)}...")
            with open(chunk_path, "rb") as audio_file:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    files={"file": (os.path.basename(chunk_path), audio_file, "audio/mp4")},
                    data={"model": "whisper-1"},
                )
                response.raise_for_status()
            transcript_parts.append(response.json()["text"])

        text = " ".join(transcript_parts)
        logger.info(f"Whisper transcript fetched ({len(text)} chars, {len(chunk_files)} chunks)")
        return text

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return None

    finally:
        # Clean up audio directory
        if os.path.exists(audio_dir):
            for f in os.listdir(audio_dir):
                os.remove(os.path.join(audio_dir, f))
            os.rmdir(audio_dir)
            logger.info(f"Cleaned up {audio_dir}")
