import os
import sys
import json

try:
    from gtts import gTTS
except ImportError:
    print("Instale o gTTS: pip install gtts")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("Instale o pydub: pip install pydub")
    sys.exit(1)

PASTA_SAIDA = os.path.join(os.path.dirname(__file__), "audio_tests")
CAMINHO_CONFIG = os.path.join(os.path.dirname(__file__), "config", "commands.json")


def gerar_audio(id_comando: str, texto: str, pasta_saida: str):
    caminho_mp3 = os.path.join(pasta_saida, f"{id_comando}.mp3")
    caminho_wav = os.path.join(pasta_saida, f"{id_comando}.wav")

    print(f"  Gerando: '{texto}' → {caminho_wav}")

    tts = gTTS(text=texto, lang="pt", tld="com.br")
    tts.save(caminho_mp3)

    audio = AudioSegment.from_mp3(caminho_mp3)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(caminho_wav, format="wav")

    os.remove(caminho_mp3)
    print(f"  ✓ Salvo: {caminho_wav}")


def main():
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)

    print("\n=== Gerando arquivos de áudio para testes ===\n")

    for comando in config["commands"]:
        frase_teste = comando["keywords"][0]
        gerar_audio(comando["id"], frase_teste, PASTA_SAIDA)

    print(f"\n✓ Todos os áudios gerados em: {PASTA_SAIDA}/")


if __name__ == "__main__":
    main()
