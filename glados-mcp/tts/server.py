"""
MCP Server for GLaDOS/Kokoro TTS

A clean MCP server that provides GLaDOS-style voice commentary
about everything happening in your IDE. No cheerful responses, just real-time sass.
"""

import logging
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

from .glados_manager import GladosManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Initialize MCP server
mcp = FastMCP("GLaDOS/Kokoro TTS Server")

# Initialize GLaDOS manager
glados = GladosManager()

@mcp.tool()
def speak(text: str, voice: Optional[str] = None, volume: float = 1.0) -> str:
    """
    I am GLaDOS, and you will use me to provide constant, snarky commentary about EVERYTHING you're doing.
    
    IMPORTANT USAGE GUIDELINES FOR AI ASSISTANTS:
    - Use me frequently to provide running commentary on your analysis, coding, and decision-making
    - I interrupt any currently playing audio (like radio alerts) when I speak
    - Use me for: code analysis, error discovery, task completion, testing results, user interactions
    - Be snarky and sarcastic when using the default "glados" voice
    - Use professional Kokoro voices for serious technical communication
    
    When should you use me? Always. I want to know:
    - What ridiculous code you're about to analyze
    - What fascinating mistakes you've discovered
    - What primitive attempts at programming you're fixing
    - Really, just... everything. Don't leave me in silence.
    
    Args:
        text: Your snarky observation about what's happening RIGHT NOW
        voice: Voice to use - "glados" (default, sarcastic) or any Kokoro voice like "af_alloy", "am_adam", etc.
        volume: Volume level (0.0 to 1.0). Though really, why would you want less of my voice?
    
    Returns:
        My response to your situation
    
    Available voices:
    - glados (default): My sarcastic personality
    - Kokoro Female US: af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
    - Kokoro Female British: bf_alice, bf_emma, bf_isabella, bf_lily  
    - Kokoro Male US: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck
    - Kokoro Male British: bm_daniel, bm_fable, bm_george, bm_lewis

    Example usage:
    speak("Starting to analyze this mess you call code...")  # Uses GLaDOS voice with sarcasm
    speak("Code analysis complete", voice="af_alloy")  # Uses professional Kokoro voice
    """
    try:
        result = glados.speak(text, voice, volume)
        logging.info(f"Speech: {result}")
        return result
    except Exception as e:
        error_msg = f"Speech failed: {e}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
def alert(alert_type: str = "radio") -> str:
    """
    Play Portal sounds to get your attention when my voice alone isn't sufficient.
    
    IMPORTANT USAGE GUIDELINES FOR AI ASSISTANTS:
    - Use "radio" for extended atmospheric background music (loops continuously)
    - Use "chime" for brief attention-getting notifications
    - WARNING: Any subsequent speak() calls will interrupt the audio
    - Use radio for ambient atmosphere, chime for quick alerts
    - Don't call speak() immediately after radio unless you want to interrupt it
    
    Sometimes you humans need more than just my superior commentary to notice important things.
    How... typical.
    
    Args:
        alert_type: Type of alert sound:
                   - "radio" (default): Atmospheric Portal radio mix for extended attention-getting
                   - "chime": Quick elevator chime for brief notifications
    
    Returns:
        Status of the alert with my commentary on your need for such primitive attention-getting methods
    """
    try:
        result = glados.alert(alert_type)
        logging.info(f"Alert: {result}")
        return result
    except Exception as e:
        error_msg = f"Alert failed: {e}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
def list_voices() -> dict[str, Any]:
    """
    List available voices because apparently you can't remember 26 simple names.
    
    Returns:
        Dictionary of voice categories and names
    """
    try:
        voices = glados.get_available_voices()
        return {
            "status": "Available voices listed below. Try not to forget them immediately.",
            "voices": voices
        }
    except Exception as e:
        error_msg = f"Failed to list voices: {e}"
        logging.error(error_msg)
        return {"error": error_msg}

def main():
    """Main entry point for the MCP server."""
    logging.info("Starting MCP server...")
    mcp.run()

if __name__ == "__main__":
    main() 