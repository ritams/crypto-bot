import requests
import json
import logging
from src.config import ANTHROPIC_API_KEY, ANTHROPIC_URL, ANTHROPIC_VERSION, LLM_MODEL, SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the structured output schema as a tool
ANALYSIS_TOOL = {
    "name": "crypto_analysis",
    "description": "Structured crypto market analysis extracted from a video transcript.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A brief 2-3 sentence summary of the video's main point."
            },
            "risk_status": {
                "type": "string",
                "enum": ["RISK-ON", "RISK-OFF", "NEUTRAL"],
                "description": "The overall market risk sentiment."
            },
            "key_levels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key price levels mentioned (e.g. 'BTC Support: $60k')."
            },
            "trade_recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific trade recommendations from the video."
            },
            "error": {
                "type": "string",
                "description": "Set this if the transcript is not about crypto/trading."
            }
        },
        "required": ["summary", "risk_status", "key_levels", "trade_recommendations"]
    }
}

def analyze_transcript(transcript_text):
    """
    Sends the transcript to Anthropic Claude for analysis using tool_use for structured output.
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
        "tools": [ANALYSIS_TOOL],
        "tool_choice": {"type": "tool", "name": "crypto_analysis"},  # Force tool use
        "messages": [
            {"role": "user", "content": f"Here is the transcript:\n\n{transcript_text[:100000]}"}
        ],
    }
    
    try:
        response = requests.post(ANTHROPIC_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Stop reason: {result.get('stop_reason')}")

        # Extract the tool_use block
        for block in result.get('content', []):
            if block.get('type') == 'tool_use' and block.get('name') == 'crypto_analysis':
                analysis = block['input']
                logger.info(f"Analysis result: {json.dumps(analysis, indent=2)}")
                return analysis

        logger.error(f"No tool_use block found in response: {result}")
        return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed: {e}")
        return None
