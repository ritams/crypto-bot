import requests
import json
import logging
from src.config import ANTHROPIC_API_KEY, ANTHROPIC_URL, ANTHROPIC_VERSION, LLM_MODEL, SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_transcript(transcript_text):
    """
    Sends the transcript to Anthropic Claude for analysis.
    """
    logger.info(f"Sending transcript to AI ({LLM_MODEL}) for analysis...")
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    
    data = {
        "model": LLM_MODEL,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Here is the transcript:\n\n{transcript_text[:100000]}"}  # Truncate if too long
        ],
    }
    
    try:
        response = requests.post(ANTHROPIC_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['content'][0]['text']
        
        # Parse JSON content
        try:
            # Strip markdown code fences if present
            clean = content.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            analysis = json.loads(clean.strip())
            return analysis
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON.")
            return {"error": "Invalid JSON response from AI", "raw": content}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed: {e}")
        return None
