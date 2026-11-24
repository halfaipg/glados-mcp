"""Voice manager: loads the GLaDOS and Kokoro synthesizers and plays audio."""

from __future__ import annotations

import logging
import os
import re
import threading
from typing import Any

import numpy as np

from .utils.resources import ensure_models, missing_models, sound_path
from .utils.spoken_text_converter import SpokenTextConverter

logger = logging.getLogger(__name__)

GLADOS_VOICE = "glados"
# The GLaDOS model is noticeably louder than the Kokoro voices.
DEFAULT_VOLUME = {"glados": 0.55, "kokoro": 1.0}
# Kokoro rejects inputs over 510 phonemes, so long text is synthesized in pieces.
MAX_CHUNK_CHARS = 250

ALERTS = {
    "radio": "looping_radio_mix.wav",
    "chime": "portal_elevator_chime.wav",
}


class NotReadyError(RuntimeError):
    """The voices cannot be used (yet)."""


def _split_text(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split text into chunks of whole sentences no longer than `limit`."""
    chunks: list[str] = []
    current = ""
    for sentence in re.split(r"(?<=[.!?;:])\s+", text.strip()):
        while len(sentence) > limit:  # one very long sentence: break on a space
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                chunks.append(current)
                current = ""
            chunks.append(sentence[:cut])
            sentence = sentence[cut:].strip()
        if current and len(current) + 1 + len(sentence) > limit:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


class GladosManager:
    """Owns the synthesizers and the audio device.

    Loading is done on a background thread so the MCP handshake is not held up
    by the first-run model download.
    """

    def __init__(self) -> None:
        self.default_voice = os.environ.get("GLADOS_MCP_DEFAULT_VOICE", GLADOS_VOICE).strip()
        self.converter = SpokenTextConverter()
        self.kokoro_voices: list[str] = []
        self._glados: Any = None
        self._kokoro: Any = None
        self._ready = threading.Event()
        self._error: str | None = None
        self._status = "starting"
        self._init_thread: threading.Thread | None = None
        self._speech_lock = threading.Lock()

    # -- startup ---------------------------------------------------------

    def start(self) -> None:
        """Begin downloading/loading models in the background (idempotent)."""
        if self._init_thread is None:
            self._init_thread = threading.Thread(target=self._initialize, name="glados-init", daemon=True)
            self._init_thread.start()

    def _initialize(self) -> None:
        try:
            if missing_models():
                self._status = "downloading voice models (first run, about 300 MB)"
                ensure_models(self._on_download_progress)
            self._status = "loading voice models"
            from .synth.tts_glados import SpeechSynthesizer as GladosSynthesizer
            from .synth.tts_kokoro import SpeechSynthesizer as KokoroSynthesizer

            self._glados = GladosSynthesizer()
            self._kokoro = KokoroSynthesizer()
            self.kokoro_voices = sorted(self._kokoro.voices.keys())
            self._status = "ready"
            logger.info("GLaDOS and %d Kokoro voices ready.", len(self.kokoro_voices))
        except Exception as e:  # reported to the client on the next tool call
            self._error = f"Voice models failed to load: {e}"
            logger.exception("Initialization failed")
        finally:
            self._ready.set()

    def _on_download_progress(self, done: int, total: int) -> None:
        percent = min(99, done * 100 // total)
        self._status = f"downloading voice models (first run, about 300 MB): {percent}% done"

    def _require_ready(self, timeout: float = 20.0) -> None:
        self.start()
        if not self._ready.wait(timeout):
            raise NotReadyError(f"Not ready yet, still {self._status}. Try again shortly.")
        if self._error:
            raise NotReadyError(self._error)

    # -- audio -----------------------------------------------------------

    @staticmethod
    def _sounddevice() -> Any:
        try:
            import sounddevice
        except OSError as e:  # PortAudio shared library missing (Linux)
            raise NotReadyError(
                f"Audio output is unavailable: {e}. On Linux, install PortAudio "
                "(e.g. `sudo apt install libportaudio2`)."
            ) from e
        return sounddevice

    def stop(self) -> None:
        """Stop whatever is currently playing."""
        self._sounddevice().stop()

    def alert(self, alert_type: str = "chime") -> str:
        """Start playing an alert sound and return immediately."""
        if alert_type not in ALERTS:
            raise ValueError(f"Unknown alert type '{alert_type}'. Use one of: {', '.join(ALERTS)}.")
        import soundfile

        sd = self._sounddevice()
        audio, sample_rate = soundfile.read(str(sound_path(ALERTS[alert_type])), dtype="float32")
        sd.play(audio, sample_rate)
        return f"Playing '{alert_type}' ({len(audio) / sample_rate:.0f} seconds)."

    def speak(self, text: str, voice: str | None = None, volume: float | None = None) -> str:
        """Speak text and block until playback has finished."""
        text = text.strip()
        if not text:
            raise ValueError("Nothing to say: text is empty.")
        self._require_ready()
        sd = self._sounddevice()

        voice = (voice or self.default_voice or GLADOS_VOICE).strip()
        is_glados = voice.lower() == GLADOS_VOICE
        if not is_glados and voice not in self.kokoro_voices:
            raise ValueError(
                f"Unknown voice '{voice}'. Use '{GLADOS_VOICE}' or one of: {', '.join(self.kokoro_voices)}."
            )
        if volume is None:
            volume = DEFAULT_VOLUME["glados" if is_glados else "kokoro"]
        volume = max(0.0, min(1.0, volume))

        # One utterance at a time: the Kokoro voice is state on a shared synthesizer.
        with self._speech_lock:
            if is_glados:
                synth = self._glados
            else:
                synth = self._kokoro
                synth.set_voice(voice)
            pieces = []
            for chunk in _split_text(text):
                samples = synth.generate_speech_audio(self.converter.text_to_spoken(chunk))
                pieces.append(np.asarray(samples, dtype=np.float32).reshape(-1))
            audio = np.concatenate(pieces) * volume
            sd.play(audio, synth.sample_rate)
            sd.wait()

        return f"Spoke {len(audio) / synth.sample_rate:.1f} seconds of audio with voice '{voice}'."

    def get_available_voices(self) -> dict[str, Any]:
        """Voices grouped by accent and gender."""
        self._require_ready()
        groups = {
            "kokoro_female_us": "af_",
            "kokoro_male_us": "am_",
            "kokoro_female_british": "bf_",
            "kokoro_male_british": "bm_",
        }
        result: dict[str, Any] = {"default": self.default_voice, "glados": [GLADOS_VOICE]}
        for name, prefix in groups.items():
            result[name] = [v for v in self.kokoro_voices if v.startswith(prefix)]
        grouped = {v for name in groups for v in result[name]}
        other = [v for v in self.kokoro_voices if v not in grouped]
        if other:
            result["kokoro_other"] = other
        return result
