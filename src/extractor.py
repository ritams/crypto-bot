import os
import re
import logging
import yt_dlp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _parse_vtt(vtt_content):
    """
    Parses a WebVTT subtitle string into plain text, removing timestamps and duplicates.
    """
    # Remove WEBVTT header and metadata
    lines = vtt_content.split('\n')
    text_lines = []
    seen = set()
    
    for line in lines:
        line = line.strip()
        # Skip blank lines, WEBVTT header, NOTE blocks, and timestamp lines
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or '-->' in line:
            continue
        # Skip cue identifiers (pure numbers or timestamps)
        if re.match(r'^[\d:.\s]+$', line):
            continue
        # Remove HTML-like tags (e.g. <c>, </c>, <00:00:00.000>)
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            text_lines.append(clean)
    
    return ' '.join(text_lines)

def get_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID using yt-dlp.
    Downloads auto-generated subtitles and parses them into plain text.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = f"/tmp/{video_id}"
    
    ydl_opts = {
        'skip_download': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'en-US', 'en-GB'],
        'subtitlesformat': 'vtt',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the downloaded subtitle file
        for lang in ['en', 'en-US', 'en-GB']:
            vtt_path = f"{output_template}.{lang}.vtt"
            if os.path.exists(vtt_path):
                with open(vtt_path, 'r', encoding='utf-8') as f:
                    vtt_content = f.read()
                os.remove(vtt_path)  # Clean up
                
                text = _parse_vtt(vtt_content)
                text = ' '.join(text.split())  # Normalize whitespace
                logger.info(f"Transcript fetched ({len(text)} chars)")
                return text
        
        logger.error(f"No subtitle file found for video {video_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching transcript with yt-dlp: {e}")
        # Clean up any partial files
        for lang in ['en', 'en-US', 'en-GB']:
            vtt_path = f"{output_template}.{lang}.vtt"
            if os.path.exists(vtt_path):
                os.remove(vtt_path)
        return None
