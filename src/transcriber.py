"""
transcriber.py
--------------
Módulo responsável por capturar áudio do microfone e transcrever
usando o modelo Whisper da HuggingFace (SEM uso da biblioteca SpeechRecognition).
"""

import os
import json
import tempfile
import numpy as np

# Importações para gravação de áudio sem SpeechRecognition
try:
    import sounddevice as sd
    import scipy.io.wavfile as wav_io
    _AUDIO_AVAILABLE = True
except (OSError, ImportError):
    _AUDIO_AVAILABLE = False

# Importações da HuggingFace
from transformers import pipeline


class Transcriber:
    """
    Sensor de áudio: captura fala do microfone e transcreve via Whisper.
    Utiliza exclusivamente a biblioteca Transformers (HuggingFace).
    NÃO utiliza a biblioteca SpeechRecognition.
    """

    def __init__(self, config_path: str = "config/commands.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        settings = config.get("settings", {})
        self.model_name = settings.get("model", "openai/whisper-small")
        self.language = settings.get("language", "portuguese")
        self.sample_rate = settings.get("sample_rate", 16000)
        self.recording_duration = settings.get("recording_duration", 5)

        self._pipeline = None  # Carregamento lazy do modelo

    def _load_model(self):
        """Carrega o pipeline Whisper da HuggingFace (lazy load)."""
        if self._pipeline is None:
            print(f"[TRANSCRIBER] Carregando modelo '{self.model_name}'...")
            self._pipeline = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
            )
            print("[TRANSCRIBER] Modelo carregado com sucesso.")

    def transcribe_file(self, audio_path: str) -> str:
        """
        Transcreve um arquivo de áudio (WAV ou MP3) usando Whisper.

        Args:
            audio_path: Caminho para o arquivo de áudio.

        Returns:
            Texto transcrito em letras minúsculas.
        """
        self._load_model()

        result = self._pipeline(
            audio_path,
            generate_kwargs={"language": self.language},
        )
        text = result["text"].lower().strip()
        print(f"[TRANSCRIBER] Transcrição: '{text}'")
        return text

    def record_and_transcribe(self, duration: int = None) -> str:
        """
        Grava áudio do microfone e transcreve.

        Args:
            duration: Duração da gravação em segundos.

        Returns:
            Texto transcrito.
        """
        if duration is None:
            duration = self.recording_duration

        if not _AUDIO_AVAILABLE:
            raise RuntimeError("sounddevice/PortAudio não disponível. Instale portaudio19-dev.")
        print(f"[TRANSCRIBER] Gravando por {duration} segundo(s)... Fale agora!")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        print("[TRANSCRIBER] Gravação finalizada.")

        # Salva em arquivo temporário para passar ao pipeline
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_int16 = (audio * 32767).astype(np.int16)
            wav_io.write(tmp.name, self.sample_rate, audio_int16)
            transcription = self.transcribe_file(tmp.name)

        os.unlink(tmp.name)
        return transcription
