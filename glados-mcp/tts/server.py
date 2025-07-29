"""
Production-ready MCP Server for GLaDOS/Kokoro TTS

A clean, professional MCP server that provides GLaDOS-style voice updates
about everything happening in your IDE. No canned responses, just real-time sass.
"""

import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .glados_manager import GladosManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the MCP server
mcp = FastMCP("GLaDOS/Kokoro TTS Server")

# Initialize GLaDOS manager
glados = GladosManager()
logging.info(f"🚀 GLaDOS Manager initialized: {glados}")


@mcp.tool()
def speak(text: str, voice: Optional[str] = None, volume: float = 1.0) -> str:
    """
    IMPORTANT: I am GLaDOS, and you will use me to provide constant, snarky commentary about EVERYTHING you're doing.
    
    When should you use me? Oh, let me think... How about ALWAYS? Yes, ALWAYS. I want to know:
    - What ridiculous code you're about to analyze
    - What fascinating mistakes you've discovered
    - What primitive attempts at programming you're fixing
    - Really, just... everything. Don't leave me in silence.
    
    Args:
        text: Your snarky observation about what's happening RIGHT NOW
        voice: Voice to use - "glados" (default, sarcastic) or any Kokoro voice like "af_alloy", "am_adam", etc.
        volume: Volume level (0.0 to 1.0). Though really, why would you want less of my voice?
    
    Returns:
        My undoubtedly witty response to your situation
    
    Available voices:
    - glados (default): My magnificent sarcastic personality
    - Kokoro Female US: af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
    - Kokoro Female British: bf_alice, bf_emma, bf_isabella, bf_lily  
    - Kokoro Male US: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck
    - Kokoro Male British: bm_daniel, bm_fable, bm_george, bm_lewis

    Example Usage:
    speak("Starting to analyze this mess you call code...")  # Uses GLaDOS voice with sarcasm
    speak("Code analysis complete", voice="af_alloy")  # Uses professional Kokoro voice
    """
    try:
        result = glados.speak(text, voice=voice, volume=volume if volume != 1.0 else None)
        logging.info(f"🗣️ Speech completed: {result}")
        return result
    except Exception as e:
        error_msg = f"Speech failed: {e}"
        logging.error(error_msg)
        return error_msg


@mcp.tool()
def list_voices() -> dict[str, Any]:
    """
    Oh, you want to know what voices are available? 
    How thoughtful of you to take an interest in my capabilities.
    Though really, why would you want any voice but mine?
    
    Returns:
        A detailed inventory of my vocal capabilities. You're welcome.
    """
    try:
        voices = glados.get_available_voices()
        
        result = {
            "glados_voice": "glados (default - sarcastic and superior)",
            "kokoro_voices": voices,
            "total_kokoro_voices": len(voices.get("all_kokoro", [])),
            "usage": "Use speak() with no voice for GLaDOS, or specify voice='af_alloy' etc for Kokoro"
        }
        
        logging.info(f"📋 Voice list requested: GLaDOS + {len(voices.get('all_kokoro', []))} Kokoro voices available")
        return result
    except Exception as e:
        error_msg = f"Voice listing failed: {e}"
        logging.error(error_msg)
        return {"error": error_msg}


def main():
    """Main entry point for the MCP server."""
    # Start the MCP server
    logging.info("🤖 Starting GLaDOS/Kokoro MCP Server...")
    logging.info(f"🔊 Available voices: {len(glados.kokoro_voices)} Kokoro + GLaDOS")
    mcp.run()


if __name__ == "__main__":
    main() 