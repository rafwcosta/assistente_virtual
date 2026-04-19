import json
import os
import platform
import subprocess
import webbrowser


class Atuador:

    def __init__(self, caminho_config: str = "config/commands.json"):
        with open(caminho_config, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.config_acoes = self.config.get("actions", {})
        self.sistema = platform.system()

    def executar(self, comando: dict) -> bool:
        nome_acao = comando.get("action", "")
        mensagem = comando.get("response", f"Executando {nome_acao}...")
        print(f"\n[ASSISTENTE] {mensagem}")

        metodo = getattr(self, f"_acao_{nome_acao}", None)

        if metodo is None:
            print(f"[ATUADOR] Ação '{nome_acao}' não implementada.")
            return False

        config_acao = self.config_acoes.get(nome_acao, {})
        return metodo(config_acao)

    def _acao_open_browser(self, cfg: dict) -> bool:
        url = cfg.get("url", "https://www.google.com")
        try:
            webbrowser.open(url)
            print(f"[ATUADOR] Navegador aberto → {url}")
        except Exception as erro:
            print(f"[ATUADOR] Erro ao abrir navegador: {erro}")
            return False
        return True

    def _acao_open_editor(self, cfg: dict) -> bool:
        editor = cfg.get("path", {}).get(self.sistema, "code")
        alternativas = cfg.get("alternatives", [])
        candidatos = [editor] + alternativas

        for candidato in candidatos:
            try:
                subprocess.Popen(
                    [candidato],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(f"[ATUADOR] Editor aberto: '{candidato}'")
                return True
            except FileNotFoundError:
                continue

        print("[ATUADOR] SIMULAÇÃO: Nenhum editor encontrado. Editor seria aberto aqui.")
        return True

    def _acao_increase_volume(self, cfg: dict) -> bool:
        passo = cfg.get("step", 10)
        try:
            if self.sistema == "Linux":
                resultado = os.system(f"pactl set-sink-volume @DEFAULT_SINK@ +{passo}%")
                if resultado != 0:
                    os.system(f"amixer -D pulse sset Master {passo}%+")

            elif self.sistema == "Windows":
                comando_ps = (
                    f"$obj = New-Object -ComObject WScript.Shell; "
                    f"for ($i=0; $i -lt {passo // 2}; $i++) "
                    f"{{ $obj.SendKeys([char]175) }}"
                )
                subprocess.run(["powershell", "-Command", comando_ps], check=True)

            elif self.sistema == "Darwin":
                volume_atual = int(
                    os.popen("osascript -e 'output volume of (get volume settings)'").read().strip()
                )
                novo_volume = min(100, volume_atual + passo)
                os.system(f"osascript -e 'set volume output volume {novo_volume}'")

            print(f"[ATUADOR] Volume aumentado em {passo}%.")
        except Exception as erro:
            print(f"[ATUADOR] SIMULAÇÃO: Volume seria aumentado em {passo}%. ({erro})")

        return True

    def _acao_lock_screen(self, cfg: dict) -> bool:
        try:
            if self.sistema == "Linux":
                comandos = cfg.get("linux_commands", ["loginctl lock-session"])
                for cmd in comandos:
                    if os.system(cmd) == 0:
                        print("[ATUADOR] Tela bloqueada com sucesso.")
                        return True
                print("[ATUADOR] SIMULAÇÃO: Tela seria bloqueada aqui.")

            elif self.sistema == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                print("[ATUADOR] Tela bloqueada.")

            elif self.sistema == "Darwin":
                os.system(
                    "/System/Library/CoreServices/Menu\\ Extras/User.menu"
                    "/Contents/Resources/CGSession -suspend"
                )
                print("[ATUADOR] Tela bloqueada.")

        except Exception as erro:
            print(f"[ATUADOR] SIMULAÇÃO: Tela seria bloqueada. ({erro})")

        return True
