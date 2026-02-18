import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from src.config import WEBSHARE_PROXY_USERNAME, WEBSHARE_PROXY_PASSWORD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID using youtube-transcript-api
    routed through a Webshare residential proxy.
    """
    logger.info(f"Fetching transcript for video: {video_id}")

    try:
        proxy_config = WebshareProxyConfig(
            proxy_username=WEBSHARE_PROXY_USERNAME,
            proxy_password=WEBSHARE_PROXY_PASSWORD,
        )
        api = YouTubeTranscriptApi(proxy_config=proxy_config)
        transcript = api.fetch(video_id)

        text = ' '.join([entry.text for entry in transcript])
        logger.info(f"Transcript fetched ({len(text)} chars)")
        return text

    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        return None
