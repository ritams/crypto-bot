import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID.
    Returns the concatenated text.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    try:
        # Instantiate the API class
        yt = YouTubeTranscriptApi()
        
        # fetch() gets the transcript directly (defaults to 'en')
        transcript_list = yt.fetch(video_id)
        
        # Concatenate all text parts
        full_text = " ".join([entry.text for entry in transcript_list])
        
        # Clean up whitespace
        full_text = " ".join(full_text.split())
        
        return full_text
        
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"Transcript not available for {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        return None
