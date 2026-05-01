import os
import json
import tempfile
import numpy as np

try:
    import sounddevice as sd
    import scipy.io.wavfile as wav_io
    _AUDIO_DISPONIVEL = True
except (OSError, ImportError):
    _AUDIO_DISPONIVEL = False

from transformers import pipeline


class Transcritor:

    def __init__(self, caminho_config: str = "config/commands.json"):
        with open(caminho_config, "r", encoding="utf-8") as f:
            config = json.load(f)

        configuracoes = config.get("settings", {})
        self.nome_modelo = configuracoes.get("model", "openai/whisper-small")
        self.idioma = configuracoes.get("language", "portuguese")
        self.taxa_amostragem = configuracoes.get("sample_rate", 16000)
        self.duracao_gravacao = configuracoes.get("recording_duration", 5)
        self._pipeline = None

    def _carregar_modelo(self):
        if self._pipeline is None:
            print(f"[TRANSCRITOR] Carregando modelo '{self.nome_modelo}'...")
            self._pipeline = pipeline(
                "automatic-speech-recognition",
                model=self.nome_modelo,
            )
            print("[TRANSCRITOR] Modelo carregado com sucesso.")

    def _converter_para_wav(self, caminho_audio: str) -> str:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(caminho_audio)
        audio = audio.set_frame_rate(16000).set_channels(1)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio.export(tmp.name, format="wav")
        return tmp.name

    def transcrever_arquivo(self, caminho_audio: str) -> str:
        self._carregar_modelo()

        extensao = os.path.splitext(caminho_audio)[1].lower()
        arquivo_temporario = None

        if extensao not in (".wav", ".flac", ".mp3"):
            print(f"[TRANSCRITOR] Convertendo '{extensao}' para WAV...")
            arquivo_temporario = self._converter_para_wav(caminho_audio)
            caminho_para_transcrever = arquivo_temporario
        else:
            caminho_para_transcrever = caminho_audio

        resultado = self._pipeline(
            caminho_para_transcrever,
            generate_kwargs={"language": self.idioma},
        )

        if arquivo_temporario:
            os.unlink(arquivo_temporario)

        texto = resultado["text"].lower().strip()
        print(f"[TRANSCRITOR] Transcrição: '{texto}'")
        return texto

    def gravar_e_transcrever(self, duracao: int = None) -> str:
        if duracao is None:
            duracao = self.duracao_gravacao

        if not _AUDIO_DISPONIVEL:
            raise RuntimeError("sounddevice/PortAudio não disponível. Instale portaudio19-dev.")

        print(f"[TRANSCRITOR] Gravando por {duracao} segundo(s)... Fale agora!")
        audio = sd.rec(
            int(duracao * self.taxa_amostragem),
            samplerate=self.taxa_amostragem,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        print("[TRANSCRITOR] Gravação finalizada.")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_int16 = (audio * 32767).astype(np.int16)
            wav_io.write(tmp.name, self.taxa_amostragem, audio_int16)
            transcricao = self.transcrever_arquivo(tmp.name)

        os.unlink(tmp.name)
        return transcricao