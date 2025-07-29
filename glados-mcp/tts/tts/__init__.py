"""GLaDOS TTS Implementation - Production Ready"""

from .tts_glados import SpeechSynthesizer as GladosSynthesizer
from .tts_kokoro import SpeechSynthesizer as KokoroSynthesizer, get_voices


def get_speech_synthesizer(model_type: str = "glados"):
    """Get a speech synthesizer instance.
    
    Args:
        model_type: Either 'glados' or 'kokoro'
    
    Returns:
        Synthesizer instance
    """
    if model_type.lower() == "glados":
        return GladosSynthesizer()
    elif model_type.lower() == "kokoro":
        return KokoroSynthesizer()
    else:
        raise ValueError(f"Unknown model type: {model_type}")


__all__ = ["get_speech_synthesizer", "GladosSynthesizer", "KokoroSynthesizer", "get_voices"]
