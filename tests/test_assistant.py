"""
tests/test_assistant.py
------------------------
Testes automatizados com unittest.

Estrutura dos testes:
  - TestCommandProcessor : testa o NLP (NLTK) isoladamente com mocks
  - TestActuator         : testa cada atuador isoladamente (sem SO real)
  - TestIntegration      : testa o pipeline completo usando os arquivos
                           de áudio gerados por generate_test_audio.py
                           (requer os arquivos em audio_tests/)

Execute:
    python -m unittest tests/test_assistant.py -v
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.command_processor import CommandProcessor
from src.actuators import Actuator

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "commands.json"
)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_tests")


# ===========================================================================
# Suite 1: CommandProcessor (NLP / NLTK)
# ===========================================================================

class TestCommandProcessor(unittest.TestCase):
    """
    Testa o módulo de NLP (CommandProcessor) de forma isolada.
    Verifica se o texto transcrito é corretamente mapeado ao comando certo.
    """

    @classmethod
    def setUpClass(cls):
        """Instancia o CommandProcessor uma única vez para todos os testes."""
        cls.processor = CommandProcessor(config_path=CONFIG_PATH)

    # --- Testes de reconhecimento correto ---

    def test_reconhece_abrir_navegador(self):
        """Deve reconhecer variações do comando 'abrir navegador'."""
        frases = [
            "abrir navegador",
            "abre o navegador",
            "abra o navegador",
            "iniciar navegador",
        ]
        for frase in frases:
            with self.subTest(frase=frase):
                result = self.processor.find_command(frase)
                self.assertIsNotNone(result, f"Não reconheceu: '{frase}'")
                self.assertEqual(result["id"], "open_browser")

    def test_reconhece_abrir_editor(self):
        """Deve reconhecer variações do comando 'abrir editor'."""
        frases = [
            "abrir editor de código",
            "abre o editor",
            "abrir vscode",
            "iniciar editor",
        ]
        for frase in frases:
            with self.subTest(frase=frase):
                result = self.processor.find_command(frase)
                self.assertIsNotNone(result, f"Não reconheceu: '{frase}'")
                self.assertEqual(result["id"], "open_editor")

    def test_reconhece_aumentar_volume(self):
        """Deve reconhecer variações do comando 'aumentar volume'."""
        frases = [
            "aumentar volume",
            "aumenta o volume",
            "subir volume",
            "mais volume",
        ]
        for frase in frases:
            with self.subTest(frase=frase):
                result = self.processor.find_command(frase)
                self.assertIsNotNone(result, f"Não reconheceu: '{frase}'")
                self.assertEqual(result["id"], "increase_volume")

    def test_reconhece_bloquear_tela(self):
        """Deve reconhecer variações do comando 'bloquear tela'."""
        frases = [
            "bloquear tela",
            "bloquear a tela",
            "travar tela",
            "bloquear computador",
        ]
        for frase in frases:
            with self.subTest(frase=frase):
                result = self.processor.find_command(frase)
                self.assertIsNotNone(result, f"Não reconheceu: '{frase}'")
                self.assertEqual(result["id"], "lock_screen")

    # --- Testes de casos-limite ---

    def test_texto_vazio_retorna_none(self):
        """Texto vazio não deve retornar nenhum comando."""
        result = self.processor.find_command("")
        self.assertIsNone(result)

    def test_comando_desconhecido_retorna_none(self):
        """Texto sem relação com os comandos deve retornar None."""
        result = self.processor.find_command("fazer um bolo de chocolate")
        self.assertIsNone(result)

    def test_resultado_contem_campos_obrigatorios(self):
        """O comando retornado deve ter os campos exigidos pelo atuador."""
        result = self.processor.find_command("abrir navegador")
        self.assertIsNotNone(result)
        for campo in ("id", "action", "keywords", "description", "response"):
            self.assertIn(campo, result, f"Campo ausente: '{campo}'")

    # --- Testa leitura do JSON externo ---

    def test_config_carregada_do_json(self):
        """Deve ter exatamente 4 comandos conforme o JSON."""
        self.assertEqual(len(self.processor.commands), 4)

    def test_todos_comandos_tem_keywords(self):
        """Todos os comandos do JSON devem ter pelo menos 1 keyword."""
        for cmd in self.processor.commands:
            self.assertGreater(
                len(cmd["keywords"]), 0,
                f"Comando '{cmd['id']}' sem keywords."
            )


# ===========================================================================
# Suite 2: Actuator (atuadores isolados com mocks)
# ===========================================================================

class TestActuator(unittest.TestCase):
    """
    Testa cada atuador de forma isolada, sem executar comandos reais no SO.
    Usa unittest.mock para substituir subprocess, os.system e webbrowser.
    """

    @classmethod
    def setUpClass(cls):
        cls.actuator = Actuator(config_path=CONFIG_PATH)

        # Lê os comandos do JSON para usar nos testes
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        cls.commands = {cmd["id"]: cmd for cmd in config["commands"]}

    @patch("webbrowser.open")
    def test_open_browser_chama_webbrowser(self, mock_wb):
        """Atuador open_browser deve chamar webbrowser.open."""
        command = self.commands["open_browser"]
        result = self.actuator.execute(command)

        self.assertTrue(result)
        mock_wb.assert_called_once()
        # Verifica que a URL foi passada
        called_url = mock_wb.call_args[0][0]
        self.assertIn("http", called_url)

    @patch("subprocess.Popen")
    def test_open_editor_chama_subprocess(self, mock_popen):
        """Atuador open_editor deve tentar abrir um editor via subprocess."""
        command = self.commands["open_editor"]
        result = self.actuator.execute(command)

        self.assertTrue(result)
        # Popen deve ter sido chamado ao menos uma vez
        self.assertGreater(mock_popen.call_count, 0)

    @patch("os.system", return_value=0)
    def test_increase_volume_executa_comando(self, mock_os):
        """Atuador increase_volume deve chamar os.system."""
        command = self.commands["increase_volume"]
        result = self.actuator.execute(command)
        self.assertTrue(result)

    @patch("os.system", return_value=0)
    def test_lock_screen_executa_comando(self, mock_os):
        """Atuador lock_screen deve chamar os.system."""
        command = self.commands["lock_screen"]
        result = self.actuator.execute(command)
        self.assertTrue(result)

    def test_execute_retorna_false_para_acao_inexistente(self):
        """execute() deve retornar False se a ação não existir."""
        fake_command = {
            "id": "fake",
            "action": "acao_inexistente",
            "description": "Teste",
            "response": "Testando...",
        }
        result = self.actuator.execute(fake_command)
        self.assertFalse(result)


# ===========================================================================
# Suite 3: Integração — pipeline completo com arquivos de áudio
# ===========================================================================

class TestIntegration(unittest.TestCase):
    """
    Testa o pipeline completo: Transcrição (Whisper) → NLP → Atuação.

    REQUER:
      1. Arquivos de áudio em audio_tests/ (gerados por generate_test_audio.py)
      2. Conexão com a internet na primeira execução (download do modelo Whisper)

    Se os áudios não existirem, os testes são pulados automaticamente.
    """

    AUDIO_FILES = {
        "open_browser": "open_browser.wav",
        "open_editor": "open_editor.wav",
        "increase_volume": "increase_volume.wav",
        "lock_screen": "lock_screen.wav",
    }

    @classmethod
    def setUpClass(cls):
        """Verifica se os arquivos de áudio existem antes de rodar."""
        cls.processor = CommandProcessor(config_path=CONFIG_PATH)
        cls.actuator = Actuator(config_path=CONFIG_PATH)
        cls.audio_available = os.path.isdir(AUDIO_DIR) and any(
            os.path.exists(os.path.join(AUDIO_DIR, f))
            for f in cls.AUDIO_FILES.values()
        )

    def _get_audio_path(self, filename: str) -> str:
        return os.path.join(AUDIO_DIR, filename)

    def _skip_if_no_audio(self, audio_file: str):
        path = self._get_audio_path(audio_file)
        if not os.path.exists(path):
            self.skipTest(
                f"Arquivo de áudio não encontrado: {path}\n"
                "Execute 'python generate_test_audio.py' primeiro."
            )
        return path

    # --- Testes com mock do Transcriber (pipeline completo sem modelo) ---

    def _run_pipeline_with_mock_transcription(self, text: str, expected_id: str):
        """Auxiliar: roda o pipeline com transcrição mockada."""
        command = self.processor.find_command(text)
        self.assertIsNotNone(command, f"Pipeline não reconheceu: '{text}'")
        self.assertEqual(command["id"], expected_id)
        return command

    @patch("webbrowser.open")
    def test_pipeline_open_browser(self, mock_wb):
        """Pipeline completo: 'abrir navegador' → open_browser → webbrowser."""
        cmd = self._run_pipeline_with_mock_transcription(
            "abrir navegador", "open_browser"
        )
        result = self.actuator.execute(cmd)
        self.assertTrue(result)
        mock_wb.assert_called_once()

    @patch("subprocess.Popen")
    def test_pipeline_open_editor(self, mock_popen):
        """Pipeline completo: 'editor de código' → open_editor → Popen."""
        cmd = self._run_pipeline_with_mock_transcription(
            "abrir editor de código", "open_editor"
        )
        result = self.actuator.execute(cmd)
        self.assertTrue(result)

    @patch("os.system", return_value=0)
    def test_pipeline_increase_volume(self, mock_os):
        """Pipeline completo: 'aumentar volume' → increase_volume → os.system."""
        cmd = self._run_pipeline_with_mock_transcription(
            "aumentar volume", "increase_volume"
        )
        result = self.actuator.execute(cmd)
        self.assertTrue(result)

    @patch("os.system", return_value=0)
    def test_pipeline_lock_screen(self, mock_os):
        """Pipeline completo: 'bloquear tela' → lock_screen → os.system."""
        cmd = self._run_pipeline_with_mock_transcription(
            "bloquear tela", "lock_screen"
        )
        result = self.actuator.execute(cmd)
        self.assertTrue(result)

    # --- Testes com áudio REAL (Whisper + arquivo de áudio) ---

    def test_audio_open_browser(self):
        """Testa transcrição + NLP com arquivo de áudio real."""
        audio_path = self._skip_if_no_audio("open_browser.wav")
        from src.transcriber import Transcriber
        transcriber = Transcriber(config_path=CONFIG_PATH)
        text = transcriber.transcribe_file(audio_path)
        command = self.processor.find_command(text)
        self.assertIsNotNone(command)
        self.assertEqual(command["id"], "open_browser")

    def test_audio_open_editor(self):
        """Testa transcrição + NLP com arquivo de áudio real."""
        audio_path = self._skip_if_no_audio("open_editor.wav")
        from src.transcriber import Transcriber
        transcriber = Transcriber(config_path=CONFIG_PATH)
        text = transcriber.transcribe_file(audio_path)
        command = self.processor.find_command(text)
        self.assertIsNotNone(command)
        self.assertEqual(command["id"], "open_editor")

    def test_audio_increase_volume(self):
        """Testa transcrição + NLP com arquivo de áudio real."""
        audio_path = self._skip_if_no_audio("increase_volume.wav")
        from src.transcriber import Transcriber
        transcriber = Transcriber(config_path=CONFIG_PATH)
        text = transcriber.transcribe_file(audio_path)
        command = self.processor.find_command(text)
        self.assertIsNotNone(command)
        self.assertEqual(command["id"], "increase_volume")

    def test_audio_lock_screen(self):
        """Testa transcrição + NLP com arquivo de áudio real."""
        audio_path = self._skip_if_no_audio("lock_screen.wav")
        from src.transcriber import Transcriber
        transcriber = Transcriber(config_path=CONFIG_PATH)
        text = transcriber.transcribe_file(audio_path)
        command = self.processor.find_command(text)
        self.assertIsNotNone(command)
        self.assertEqual(command["id"], "lock_screen")


# ===========================================================================
# Ponto de entrada
# ===========================================================================

if __name__ == "__main__":
    # Executa com saída detalhada
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCommandProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestActuator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
