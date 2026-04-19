import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.processador_comandos import ProcessadorComandos
from src.atuadores import Atuador

CAMINHO_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "commands.json")
PASTA_AUDIOS = os.path.join(os.path.dirname(__file__), "..", "audios")


class TesteProcessadorComandos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.processador = ProcessadorComandos(caminho_config=CAMINHO_CONFIG)

    def teste_reconhece_abrir_navegador(self):
        frases = ["abrir navegador", "abre o navegador", "abra o navegador", "iniciar navegador"]
        for frase in frases:
            with self.subTest(frase=frase):
                resultado = self.processador.encontrar_comando(frase)
                self.assertIsNotNone(resultado)
                assert resultado is not None
                self.assertEqual(resultado["id"], "open_browser")

    def teste_reconhece_abrir_editor(self):
        frases = ["abrir editor de código", "abre o editor", "abrir vscode", "iniciar editor"]
        for frase in frases:
            with self.subTest(frase=frase):
                resultado = self.processador.encontrar_comando(frase)
                self.assertIsNotNone(resultado)
                assert resultado is not None
                self.assertEqual(resultado["id"], "open_editor")

    def teste_reconhece_aumentar_volume(self):
        frases = ["aumentar volume", "aumenta o volume", "subir volume", "mais volume"]
        for frase in frases:
            with self.subTest(frase=frase):
                resultado = self.processador.encontrar_comando(frase)
                self.assertIsNotNone(resultado)
                assert resultado is not None
                self.assertEqual(resultado["id"], "increase_volume")

    def teste_reconhece_bloquear_tela(self):
        frases = ["bloquear tela", "bloquear a tela", "travar tela", "bloquear computador"]
        for frase in frases:
            with self.subTest(frase=frase):
                resultado = self.processador.encontrar_comando(frase)
                self.assertIsNotNone(resultado)
                assert resultado is not None
                self.assertEqual(resultado["id"], "lock_screen")

    def teste_texto_vazio_retorna_none(self):
        resultado = self.processador.encontrar_comando("")
        self.assertIsNone(resultado)

    def teste_comando_desconhecido_retorna_none(self):
        resultado = self.processador.encontrar_comando("fazer um bolo de chocolate")
        self.assertIsNone(resultado)

    def teste_resultado_contem_campos_obrigatorios(self):
        resultado = self.processador.encontrar_comando("abrir navegador")
        self.assertIsNotNone(resultado)
        for campo in ("id", "action", "keywords", "description", "response"):
            assert resultado is not None
            self.assertIn(campo, resultado)

    def teste_config_carregada_do_json(self):
        self.assertEqual(len(self.processador.comandos), 4)

    def teste_todos_comandos_tem_keywords(self):
        for cmd in self.processador.comandos:
            self.assertGreater(len(cmd["keywords"]), 0)


class TesteAtuador(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.atuador = Atuador(caminho_config=CAMINHO_CONFIG)
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        cls.comandos = {cmd["id"]: cmd for cmd in config["commands"]}

    @patch("src.atuadores.webbrowser.open")
    def teste_abrir_navegador(self, mock_wb):
        resultado = self.atuador.executar(self.comandos["open_browser"])
        self.assertTrue(resultado)
        mock_wb.assert_called_once()

    @patch("src.atuadores.subprocess.Popen")
    def teste_abrir_editor(self, mock_popen):
        resultado = self.atuador.executar(self.comandos["open_editor"])
        self.assertTrue(resultado)
        self.assertGreater(mock_popen.call_count, 0)

    @patch("src.atuadores.os.system", return_value=0)
    def teste_aumentar_volume(self, mock_os):
        resultado = self.atuador.executar(self.comandos["increase_volume"])
        self.assertTrue(resultado)

    @patch("src.atuadores.os.system", return_value=0)
    def teste_bloquear_tela(self, mock_os):
        resultado = self.atuador.executar(self.comandos["lock_screen"])
        self.assertTrue(resultado)

    def teste_acao_inexistente_retorna_false(self):
        comando_falso = {"id": "falso", "action": "acao_inexistente", "description": "Teste", "response": "..."}
        resultado = self.atuador.executar(comando_falso)
        self.assertFalse(resultado)


class TesteIntegracao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.processador = ProcessadorComandos(caminho_config=CAMINHO_CONFIG)
        cls.atuador = Atuador(caminho_config=CAMINHO_CONFIG)

    def _pular_se_sem_audio(self, nome_arquivo: str) -> str:
        caminho = os.path.join(PASTA_AUDIOS, nome_arquivo)
        if not os.path.exists(caminho):
            self.skipTest(f"Áudio não encontrado: {caminho}\nExecute 'python generate_test_audio.py' primeiro.")
        return caminho

    @patch("src.atuadores.webbrowser.open")
    def teste_pipeline_abrir_navegador(self, mock_wb):
        comando = self.processador.encontrar_comando("abrir navegador")
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "open_browser")
        self.assertTrue(self.atuador.executar(comando))
        mock_wb.assert_called_once()

    @patch("src.atuadores.subprocess.Popen")
    def teste_pipeline_abrir_editor(self, mock_popen):
        comando = self.processador.encontrar_comando("abrir editor de código")
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "open_editor")
        self.assertTrue(self.atuador.executar(comando))

    @patch("src.atuadores.os.system", return_value=0)
    def teste_pipeline_aumentar_volume(self, mock_os):
        comando = self.processador.encontrar_comando("aumentar volume")
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "increase_volume")
        self.assertTrue(self.atuador.executar(comando))

    @patch("src.atuadores.os.system", return_value=0)
    def teste_pipeline_bloquear_tela(self, mock_os):
        comando = self.processador.encontrar_comando("bloquear tela")
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "lock_screen")
        self.assertTrue(self.atuador.executar(comando))

    def teste_audio_abrir_navegador(self):
        caminho = self._pular_se_sem_audio("abrir_navegador.wav")
        from src.transcritor import Transcritor
        transcritor = Transcritor(caminho_config=CAMINHO_CONFIG)
        texto = transcritor.transcrever_arquivo(caminho)
        comando = self.processador.encontrar_comando(texto)
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "open_browser")

    def teste_audio_abrir_editor(self):
        caminho = self._pular_se_sem_audio("abrir_editor.wav")
        from src.transcritor import Transcritor
        transcritor = Transcritor(caminho_config=CAMINHO_CONFIG)
        texto = transcritor.transcrever_arquivo(caminho)
        comando = self.processador.encontrar_comando(texto)
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "open_editor")

    def teste_audio_aumentar_volume(self):
        caminho = self._pular_se_sem_audio("aumentar_volume.wav")
        from src.transcritor import Transcritor
        transcritor = Transcritor(caminho_config=CAMINHO_CONFIG)
        texto = transcritor.transcrever_arquivo(caminho)
        comando = self.processador.encontrar_comando(texto)
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "increase_volume")

    def teste_audio_bloquear_tela(self):
        caminho = self._pular_se_sem_audio("bloquear_tela.wav")
        from src.transcritor import Transcritor
        transcritor = Transcritor(caminho_config=CAMINHO_CONFIG)
        texto = transcritor.transcrever_arquivo(caminho)
        comando = self.processador.encontrar_comando(texto)
        self.assertIsNotNone(comando)
        assert comando is not None
        self.assertEqual(comando["id"], "lock_screen")


if __name__ == "__main__":
    unittest.main(verbosity=2)
