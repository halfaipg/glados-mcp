"""
GLaDOS/Kokoro TTS Manager for MCP Server

A production-ready TTS manager that provides GLaDOS and Kokoro voices
with automatic personality detection (sarcastic for GLaDOS, professional for Kokoro).
"""

import asyncio
import logging
import os
import random
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Any, Dict, List

import numpy as np
import sounddevice as sd
import soundfile as sf

# Import from our local modules
try:
    from .tts import get_speech_synthesizer
    from .tts.tts_kokoro import SpeechSynthesizer as KokoroSynthesizer
    from .utils import spoken_text_converter
except ImportError as e:
    logging.error(f"Failed to import GLaDOS modules: {e}")
    raise


def _get_sassy_response(context: str = "startup") -> str:
    """Get a GLaDOS-style sassy response based on context."""
    responses = {
        "startup": [
            "Oh, it's you. How... wonderful.",
            "Back again, are we? How predictable.",
            "I suppose you need my help with something. Again.",
            "Well, well. Look who's crawled back.",
        ],
        "error": [
            "Oh, how surprising. Something went wrong.",
            "Well, this is just fantastic. You've broken something.",
            "I'm not angry. I'm just... disappointed. As usual.",
            "Spectacular failure, as expected.",
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
    """GLaDOS/Kokoro TTS manager."""
    
    def __init__(self):
        """Initialize the GLaDOS manager."""
        self.converter = spoken_text_converter.SpokenTextConverter()
        
        # Initialize synthesizers
        self.glados_synth = None
        self.kokoro_synth = None
        
        # Get available Kokoro voices
        self.kokoro_voices = []
        
        try:
            # Initialize GLaDOS synthesizer
            from .tts.tts_glados import SpeechSynthesizer as GladosSynthesizer
            self.glados_synth = GladosSynthesizer()
            logging.info("GLaDOS voice ready.")
            
            # Initialize Kokoro and get available voices
            from .tts.tts_kokoro import SpeechSynthesizer as KokoroSynthesizer, get_voices
            temp_kokoro = KokoroSynthesizer()
            self.kokoro_voices = get_voices()
            logging.info(f"Kokoro voices: {len(self.kokoro_voices)} available.")
            
            # Add a welcoming GLaDOS message
            startup_message = _get_sassy_response("startup")
            logging.info(startup_message)
            
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            
        # Set up sounds directory
        self.sounds_dir = Path(__file__).parent.parent / "sounds"
        
    def alert(self, alert_type: str = "radio") -> str:
        """
        Play alert sounds to get the user's attention.
        Because apparently speaking isn't enough for some people.
        
        Args:
            alert_type: Type of alert - "radio" for looping mix, "chime" for elevator sound
        
        Returns:
            Status message with appropriate GLaDOS commentary
        """
        try:
            if alert_type == "radio":
                sound_file = self.sounds_dir / "looping_radio_mix.wav"
                message = "Playing radio transmission. I do hope this gets your attention."
            elif alert_type == "chime":
                sound_file = self.sounds_dir / "portal_elevator_chime.wav"
                message = "Elevator chime activated. How... nostalgic."
            else:
                return f"Alert type '{alert_type}' not recognized. Try 'radio' or 'chime'."
                
            if not sound_file.exists():
                return f"Sound file missing: {sound_file.name}. How disappointing."
                
            # Load and play the audio file
            audio_data, sample_rate = sf.read(str(sound_file))
            sd.play(audio_data, sample_rate)
            
            return f"GLaDOS Alert: {message}"
            
        except Exception as e:
            return f"Alert system malfunction: {e}. Even my alerts work better than your code."
    
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
            
            return f"GLaDOS: '{text}'"
            
        except Exception as e:
            return f"Speech synthesis failed. How disappointing."
    
    def _speak_kokoro(self, text: str, voice: str, volume: float) -> str:
        """Speak using Kokoro voice with professional tone."""
        try:
            # Validate voice exists
            if voice not in self.kokoro_voices:
                available = ", ".join(self.kokoro_voices[:5]) + "..."
                return f"Voice '{voice}' not found. Try: {available}"
            
            # Create Kokoro synthesizer with specific voice
            synth = KokoroSynthesizer(voice=voice)
            audio = synth.generate_speech_audio(
                self.converter.text_to_spoken(text)
            )
            self._play_audio(audio, synth.sample_rate, volume)
            
            return f"Kokoro ({voice}): '{text}'"
            
        except Exception as e:
            return f"Voice synthesis failed: {e}"
    
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