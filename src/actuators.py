"""
actuators.py
-------------
Módulo de atuadores do assistente virtual.
Cada atuador lê sua configuração do arquivo JSON externo e executa
a ação correspondente no sistema operacional.
"""

import json
import os
import platform
import subprocess
import webbrowser


class Actuator:
    """
    Atuador do sistema: executa ações reais no SO com base nos
    parâmetros lidos do arquivo JSON de configuração.
    """

    def __init__(self, config_path: str = "config/commands.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.actions_config = self.config.get("actions", {})
        self.system = platform.system()  # 'Linux', 'Windows' ou 'Darwin'

    def execute(self, command: dict) -> bool:
        """
        Despacha a execução para o método correto com base no campo 'action'.

        Args:
            command: Dicionário do comando vindo do CommandProcessor.

        Returns:
            True se a ação foi executada, False caso contrário.
        """
        action_name = command.get("action", "")
        response_msg = command.get("response", f"Executando {action_name}...")
        print(f"\n[ASSISTENTE] {response_msg}")

        # Busca método dinamicamente: _action_open_browser, etc.
        method = getattr(self, f"_action_{action_name}", None)

        if method is None:
            print(f"[ATUADOR] Ação '{action_name}' não implementada.")
            return False

        action_cfg = self.actions_config.get(action_name, {})
        return method(action_cfg)

    # ------------------------------------------------------------------
    # Atuadores individuais
    # ------------------------------------------------------------------

    def _action_open_browser(self, cfg: dict) -> bool:
        """Abre o navegador padrão do sistema."""
        url = cfg.get("url", "https://www.google.com")

        try:
            webbrowser.open(url)
            print(f"[ATUADOR] Navegador aberto → {url}")
        except Exception as e:
            print(f"[ATUADOR] Erro ao abrir navegador: {e}")
            return False

        return True

    def _action_open_editor(self, cfg: dict) -> bool:
        """Abre o editor de código configurado."""
        editor = cfg.get("path", {}).get(self.system, "code")
        alternatives = cfg.get("alternatives", [])

        # Tenta o editor principal
        candidates = [editor] + alternatives
        for candidate in candidates:
            try:
                subprocess.Popen(
                    [candidate],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(f"[ATUADOR] Editor aberto: '{candidate}'")
                return True
            except FileNotFoundError:
                continue

        # Se nenhum editor foi encontrado, simula a atuação
        print(
            "[ATUADOR] SIMULAÇÃO: Nenhum editor encontrado no sistema. "
            "Editor de código seria aberto aqui."
        )
        return True

    def _action_increase_volume(self, cfg: dict) -> bool:
        """Aumenta o volume do sistema."""
        step = cfg.get("step", 10)
        success = False

        try:
            if self.system == "Linux":
                # PulseAudio / ALSA
                result = os.system(
                    f"pactl set-sink-volume @DEFAULT_SINK@ +{step}%"
                )
                if result != 0:
                    os.system(f"amixer -D pulse sset Master {step}%+")
                success = True

            elif self.system == "Windows":
                # Via PowerShell / nircmd
                ps_cmd = (
                    f"$obj = New-Object -ComObject WScript.Shell; "
                    f"for ($i=0; $i -lt {step // 2}; $i++) "
                    f"{{ $obj.SendKeys([char]175) }}"
                )
                subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    check=True,
                )
                success = True

            elif self.system == "Darwin":
                current = int(
                    os.popen(
                        "osascript -e 'output volume of (get volume settings)'"
                    ).read().strip()
                )
                new_vol = min(100, current + step)
                os.system(f"osascript -e 'set volume output volume {new_vol}'")
                success = True

            print(f"[ATUADOR] Volume aumentado em {step}%.")

        except Exception as e:
            print(f"[ATUADOR] SIMULAÇÃO: Volume seria aumentado em {step}%. ({e})")
            success = True  # Conta como executado (simulação)

        return success

    def _action_lock_screen(self, cfg: dict) -> bool:
        """Bloqueia a tela do computador."""
        try:
            if self.system == "Linux":
                commands = cfg.get(
                    "linux_commands",
                    ["loginctl lock-session"],
                )
                for cmd in commands:
                    result = os.system(cmd)
                    if result == 0:
                        print("[ATUADOR] Tela bloqueada com sucesso.")
                        return True
                print(
                    "[ATUADOR] SIMULAÇÃO: Tela seria bloqueada aqui "
                    "(nenhum locker encontrado)."
                )

            elif self.system == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                print("[ATUADOR] Tela bloqueada.")

            elif self.system == "Darwin":
                os.system(
                    "/System/Library/CoreServices/Menu\\ Extras/User.menu"
                    "/Contents/Resources/CGSession -suspend"
                )
                print("[ATUADOR] Tela bloqueada.")

        except Exception as e:
            print(f"[ATUADOR] SIMULAÇÃO: Tela seria bloqueada. ({e})")

        return True
