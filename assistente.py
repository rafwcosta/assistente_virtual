import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.transcritor import Transcritor
from src.processador_comandos import ProcessadorComandos
from src.atuadores import Atuador

CAMINHO_CONFIG = os.path.join(os.path.dirname(__file__), "config", "commands.json")


def executar_via_microfone(transcritor, processador, atuador):
    print("\n" + "=" * 55)
    print("  ASSISTENTE VIRTUAL  |  Automação por Voz")
    print("=" * 55)
    print("Pressione Ctrl+C para sair.\n")

    while True:
        try:
            print("\n[ASSISTENTE] Aguardando comando...")
            texto = transcritor.gravar_e_transcrever()

            if not texto:
                print("[ASSISTENTE] Não entendi. Tente novamente.")
                continue

            comando = processador.encontrar_comando(texto)

            if comando:
                atuador.executar(comando)
            else:
                print(f"[ASSISTENTE] Comando não reconhecido para: '{texto}'")
                listar_comandos(processador)

        except KeyboardInterrupt:
            print("\n[ASSISTENTE] Encerrando. Até logo!")
            break


def executar_via_arquivo(caminho_audio, transcritor, processador, atuador):
    print(f"\n[ASSISTENTE] Processando arquivo: {caminho_audio}")
    texto = transcritor.transcrever_arquivo(caminho_audio)
    comando = processador.encontrar_comando(texto)

    if comando:
        atuador.executar(comando)
    else:
        print("[ASSISTENTE] Nenhum comando reconhecido.")

    return comando


def listar_comandos(processador):
    for cmd in processador.comandos:
        print(f"  • {cmd['description']} → ex: '{cmd['keywords'][0]}'")


def main():
    analisador = argparse.ArgumentParser(description="Assistente Virtual por Voz")
    analisador.add_argument("--arquivo", "-a", type=str, default=None)
    args = analisador.parse_args()

    transcritor = Transcritor(caminho_config=CAMINHO_CONFIG)
    processador = ProcessadorComandos(caminho_config=CAMINHO_CONFIG)
    atuador = Atuador(caminho_config=CAMINHO_CONFIG)

    if args.arquivo:
        executar_via_arquivo(args.arquivo, transcritor, processador, atuador)
    else:
        executar_via_microfone(transcritor, processador, atuador)


if __name__ == "__main__":
    main()
