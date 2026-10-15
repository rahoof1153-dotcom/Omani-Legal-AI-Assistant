"""Speech-to-text interface.

Security Phase 1: voice transcription is disabled until the correct Whisper
dependency, a validated local model and safe temporary-file lifecycle exist.
No audio is written to disk or transmitted to third-party providers here.
"""
from __future__ import annotations

class SpeechToText:
    def __init__(self, language="en"):
        self.language = language
        self.model = None

    def load_model(self, model_size="base"):
        # Fail closed, without automatically downloading a model.
        return False

    def transcribe_audio(self, audio_data, detect_language=True):
        # Never expose the audio or filesystem paths as exception text.
        raise RuntimeError("Offline voice transcription is disabled pending dependency validation.")


def preprocess_audio(audio_bytes):
    """Refuse unattended audio processing while speech pipeline is disabled."""
    raise RuntimeError("Audio preprocessing is disabled pending privacy validation.")
