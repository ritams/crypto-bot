import logging
import re
import time
import requests
from imap_tools import MailBox, A
from src.config import EMAIL_USER, EMAIL_PASS, TARGET_SENDER, POLL_INTERVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_youtube_link(html_body):
    """
    Extracts the first YouTube video ID from the email body.
    Handles direct links and SendGrid redirects.
    """
    # Regex for common YouTube URL patterns
    youtube_regex = (
        r'(?:https?:\/\/)?(?:www\.)?'
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    
    # 1. Try direct match first (fastest)
    match = re.search(youtube_regex, html_body)
    if match:
        return match.group(1)

    # 2. Look for potential tracking links (e.g. SendGrid)
    # We look for http/https links in hrefs or plain text that aren't obviously other things
    # This regex grabs URLs from href="..." or just raw text URLs
    url_pattern = r'(?:href=["\']|)(https?:\/\/[a-zA-Z0-9.\-]+\.sendgrid\.net\/[^\s"\'<>]+)(?:["\']|)'
    
    urls = re.findall(url_pattern, html_body)
    
    for url in urls:
        try:
            # Clean up the URL if it captured capturing group artifacts
            url = url.strip('"\'')
            logger.info(f"Checking redirect link: {url[:50]}...")
            
            # Resolve the redirect
            response = requests.head(url, allow_redirects=True, timeout=5)
            resolved_url = response.url
            
            # Check resolved URL for YouTube pattern
            match = re.search(youtube_regex, resolved_url)
            if match:
                logger.info(f"Resolved to YouTube ID: {match.group(1)}")
                return match.group(1)
                
        except Exception as e:
            logger.warning(f"Failed to resolve link {url[:30]}...: {e}")
            
    return None

def listen_for_emails(callback, poll_interval=POLL_INTERVAL):
    """
    Connects to Gmail and listens for new emails via IDLE.
    Falls back to polling every `poll_interval` seconds.
    """
    logger.info(f"Connecting to {EMAIL_USER}...")
    
    try:
        # Connect to Gmail
        with MailBox('imap.gmail.com').login(EMAIL_USER, EMAIL_PASS) as mailbox:
            logger.info("Connected. Waiting for new emails...")
            
            # Use the specified folder (Inbox by default)
            mailbox.folder.set('INBOX')
            
            while True:
                try:
                    # wait() blocks until:
                    # 1. An IDLE event occurs (returns list of responses)
                    # 2. The timeout expires (returns empty list)
                    responses = mailbox.idle.wait(timeout=poll_interval)
                    
                    if responses:
                        logger.info(f"IDLE event received: {responses}")
                    else:
                        logger.info(f"Polling check (timeout={poll_interval}s)...")
                    
                    # ALWAYS check for unseen emails after wait returns
                    # This covers both IDLE events and Polling fallbacks
                    for msg in mailbox.fetch(A(seen=False, from_=TARGET_SENDER)):
                        logger.info(f"Received email from {msg.from_}: {msg.subject}")
                        
                        video_id = extract_youtube_link(msg.html or msg.text)
                        if video_id:
                            logger.info(f"Found YouTube Video ID: {video_id}")
                            callback(video_id)
                        else:
                            logger.warning("No YouTube link found in the email.")
                            
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in listener loop: {e}")
                    time.sleep(10) # Prevent tight loop on error
                    
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise
