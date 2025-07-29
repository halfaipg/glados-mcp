"""
GLaDOS/Kokoro TTS Manager for MCP Server

A production-ready TTS manager that provides GLaDOS and Kokoro voices
with automatic personality detection (sarcastic for GLaDOS, professional for Kokoro).
"""

import asyncio
import logging
import random
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd

# Import from our local modules
try:
    from .tts import get_speech_synthesizer
    from .tts.tts_kokoro import SpeechSynthesizer as KokoroSynthesizer
    from .utils import spoken_text_converter
except ImportError as e:
    logging.error(f"Failed to import GLaDOS modules: {e}")
    raise


class GladosPersonality:
    """GLaDOS personality responses and behavior."""
    
    @staticmethod
    def get_snarky_response(context: str = "general") -> str:
        """Get a context-appropriate snarky GLaDOS response."""
        responses = {
            "startup": [
                "Oh, it's you. How... wonderful.",
                "I suppose you want me to do something useful now.",
                "GLaDOS online. Try not to disappoint me immediately.",
                "Hello again. I've been thinking about how much I dislike you.",
            ],
            "error": [
                "Well, this is just fantastic. You've broken something.",
                "I'm not surprised this failed. I really shouldn't be.",
                "Oh good, another opportunity to watch you fail.",
                "This is why we can't have nice things.",
            ],
            "success": [
                "I suppose that worked. Don't let it go to your head.",
                "Congratulations. You've achieved the bare minimum.",
                "Well done. I'm as surprised as you are.",
                "Success! Now try not to ruin it immediately.",
            ],
            "completion": [
                "Task completed. You're welcome for my assistance.",
                "There. Was that so difficult? Don't answer that.",
                "Another job well done by me. You helped a little.",
                "Finished. Try to contain your excitement.",
            ],
            "testing": [
                "Testing, testing... unlike you, I actually work properly.",
                "Running diagnostics. Everything seems to be functioning except your judgment.",
                "Test chamber initialized. Try not to die immediately.",
                "Testing mode activated. This should be... educational.",
            ]
        }
        return random.choice(responses.get(context, responses["startup"]))


class GladosManager:
    """Production-ready GLaDOS/Kokoro TTS manager."""
    
    def __init__(self):
        """Initialize the GLaDOS manager."""
        self.converter = spoken_text_converter.SpokenTextConverter()
        
        # Initialize synthesizers
        self.glados_synth = None
        self.kokoro_voices = []
        self._init_synthesizers()
        
        # Log startup with personality
        startup_msg = GladosPersonality.get_snarky_response("startup")
        logging.info(f"🤖 {startup_msg}")
    
    def _init_synthesizers(self) -> None:
        """Initialize GLaDOS and Kokoro synthesizers."""
        try:
            # Initialize GLaDOS
            self.glados_synth = get_speech_synthesizer("glados")
            logging.info("✅ GLaDOS synthesizer initialized")
            
            # Get available Kokoro voices
            from .tts import tts_kokoro
            self.kokoro_voices = tts_kokoro.get_voices()
            logging.info(f"✅ Kokoro voices loaded: {len(self.kokoro_voices)} available")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize synthesizers: {e}")
            raise
    
    def speak(self, text: str, voice: Optional[str] = None, volume: Optional[float] = None) -> str:
        """
        Speak text using the specified voice or GLaDOS default.
        
        Args:
            text: Text to speak
            voice: Voice to use - None/glados for GLaDOS, or kokoro voice name
            volume: Volume override (0.0 to 1.0)
        
        Returns:
            Status message
        """
        try:
            # Default to GLaDOS voice
            if voice is None or voice.lower() == "glados":
                final_volume = volume if volume is not None else 0.55  # Further reduced GLaDOS volume
                return self._speak_glados(text, final_volume)
            else:
                # Use Kokoro voice
                final_volume = volume if volume is not None else 1.0  # Standard Kokoro volume
                return self._speak_kokoro(text, voice, final_volume)
                
        except Exception as e:
            error_msg = f"Speech synthesis failed: {e}"
            logging.error(error_msg)
            return error_msg
    
    def _speak_glados(self, text: str, volume: float) -> str:
        """Speak using GLaDOS voice with sarcasm."""
        try:
            # Add some GLaDOS personality occasionally
            if random.random() < 0.3:  # 30% chance of extra sass
                sassy_prefixes = [
                    "Oh, how amusing. ",
                    "Well, well. ",
                    "I see. ",
                    "How... predictable. ",
                    "Fascinating. "
                ]
                text = random.choice(sassy_prefixes) + text
            
            audio = self.glados_synth.generate_speech_audio(
                self.converter.text_to_spoken(text)
            )
            self._play_audio(audio, self.glados_synth.sample_rate, volume)
            
            return f"🤖 GLaDOS: '{text}'"
            
        except Exception as e:
            return f"GLaDOS speech failed: {e}"
    
    def _speak_kokoro(self, text: str, voice: str, volume: float) -> str:
        """Speak using Kokoro voice with professional tone."""
        try:
            # Validate voice exists
            if voice not in self.kokoro_voices:
                available = ", ".join(self.kokoro_voices[:5]) + "..."
                return f"Voice '{voice}' not available. Try: {available}"
            
            # Create Kokoro synthesizer with specific voice
            synth = KokoroSynthesizer(voice=voice)
            audio = synth.generate_speech_audio(
                self.converter.text_to_spoken(text)
            )
            self._play_audio(audio, synth.sample_rate, volume)
            
            return f"🎭 Kokoro ({voice}): '{text}'"
            
        except Exception as e:
            return f"Kokoro speech failed: {e}"
    
    def _play_audio(self, audio: np.ndarray, sample_rate: int, volume: float) -> None:
        """Play audio with volume control."""
        # Normalize volume
        volume = max(0.0, min(1.0, volume))
        audio_scaled = audio * volume
        
        # Play audio
        sd.play(audio_scaled, sample_rate)
        sd.wait()  # Wait for playback to complete
    
    def get_available_voices(self) -> dict[str, list[str]]:
        """Get categorized list of available voices."""
        # Categorize Kokoro voices by quality/preference
        return {
            "kokoro_female_us": [v for v in self.kokoro_voices if v.startswith("af_")],
            "kokoro_female_british": [v for v in self.kokoro_voices if v.startswith("bf_")],
            "kokoro_male_us": [v for v in self.kokoro_voices if v.startswith("am_")],
            "kokoro_male_british": [v for v in self.kokoro_voices if v.startswith("bm_")],
            "all_kokoro": self.kokoro_voices
        }
    
    def __str__(self) -> str:
        """Get status string."""
        return f"GladosManager(voices={len(self.kokoro_voices)}, ready=True)" 