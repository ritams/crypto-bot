import requests
import json
import logging
from src.config import OPENROUTER_API_KEY, OPENROUTER_URL, LLM_MODEL, SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_transcript(transcript_text):
    """
    Sends the transcript to OpenRouter for analysis.
    """
    logger.info(f"Sending transcript to AI ({LLM_MODEL}) for analysis...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional: Add site URL and name as per OpenRouter docs for rankings
        "HTTP-Referer": "https://github.com/ritam/crypto-bot", 
        "X-Title": "Crypto Analysis Bot"
    }
    
    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the transcript:\n\n{transcript_text[:100000]}"} # Truncate if too long
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse JSON content
        try:
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON.")
            return {"error": "Invalid JSON response from AI", "raw": content}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed: {e}")
        return None
