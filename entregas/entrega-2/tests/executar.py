"""Executa a suíte e registra o resultado real, retornando erro se algum teste falhar."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import contextlib
import platform
import re
import sys
from time import perf_counter
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from interface import (VERDE, VERM, AMAR, CINZA, texto, titulo, info, resultado)


NOMES = {
    "test_login_correto": "Login com senha correta",
    "test_login_incorreto_e_usuario_inexistente": "Rejeição de credenciais incorretas",
    "test_persistencia_apos_reabrir": "Persistência após reabrir o banco",
    "test_mesma_senha_produz_salts_e_hashes_distintos": "Salts e hashes individuais",
    "test_banco_nao_armazena_senha_em_texto": "Ausência de senha em texto puro",
    "test_comparacao_segura_da_biblioteca": "Comparação segura com compare_digest",
    "test_limites_da_senha": "Limites de tamanho da senha",
    "test_frase_sem_regra_de_composicao_e_espacos_preservados": "Frases e espaços preservados",
    "test_base_bloqueia_senha_comprida": "Bloqueio de senha da base vazada",
    "test_duplicidade_preserva_cadastro_original": "Duplicidade sem sobrescrever cadastro",
    "test_usuario_invalido_e_injecao_sql": "Usuário inválido e tentativa de SQL",
    "test_hash_adulterado_impede_login": "Rejeição de hash adulterado",
    "test_parametros_invalidos_rejeitados_no_banco": "Rejeição de parâmetros inválidos",
    "test_base_ausente_interrompe_inicializacao": "Base ausente interrompe inicialização",
    "test_base_vazia_interrompe_inicializacao": "Base vazia interrompe inicialização",
}


class ResultadoVisual(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.inicio = perf_counter()
        self.marcado = False
        nome = NOMES.get(test._testMethodName, test.shortDescription() or test._testMethodName)
        self.stream.write(f"  {self.testsRun:02d}  {nome:<43} ")
        self.stream.flush()

    def marcar(self, status, cor):
        if not self.marcado:
            tempo = perf_counter() - self.inicio
            self.stream.writeln(texto(f"[{status}]", cor) + texto(f"  {tempo:.2f}s", CINZA))
            self.stream.flush()
            self.marcado = True

    def addSuccess(self, test):
        super().addSuccess(test)
        self.marcar("APROVADO", VERDE)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.marcar("FALHOU", VERM)

    def addError(self, test, err):
        super().addError(test, err)
        self.marcar("ERRO", VERM)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.marcar("IGNORADO", AMAR)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.marcar("FALHOU", VERM)


class Espelho:
    """Mostra cores no terminal e grava a mesma execução sem ANSI no arquivo."""

    def __init__(self, terminal, arquivo):
        self.terminal, self.arquivo = terminal, arquivo

    def write(self, mensagem):
        self.terminal.write(mensagem)
        self.arquivo.write(re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", mensagem))
        return len(mensagem)

    def flush(self):
        self.terminal.flush()
        self.arquivo.flush()

    def isatty(self):
        return self.terminal.isatty()


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    destino = raiz / "evidencias" / "testes.txt"
    destino.parent.mkdir(exist_ok=True)
    suite = unittest.defaultTestLoader.discover(str(raiz / "tests"), pattern="test_*.py")
    with destino.open("w", encoding="utf-8") as arquivo, contextlib.redirect_stdout(Espelho(sys.stdout, arquivo)):
        titulo("ENTREGA 2 — TESTES AUTOMATIZADOS")
        info(f"Data: {datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')}")
        info(f"Python {platform.python_version()} | {platform.system()}")
        info("Bancos temporários; 600.000 iterações reais; cadastros do menu preservados.")
        info("Verde: aprovado | Vermelho: falha/erro | Amarelo: ignorado")
        print()
        testes = unittest.TextTestRunner(stream=sys.stdout, resultclass=ResultadoVisual, verbosity=0).run(suite)
        info(f"Executados: {testes.testsRun} | Falhas: {len(testes.failures)} | Erros: {len(testes.errors)} | Ignorados: {len(testes.skipped)}")
        resultado("TODOS OS TESTES APROVADOS." if testes.wasSuccessful() else "HÁ TESTES COM FALHA.", sucesso=testes.wasSuccessful())
    print(f"\n  Evidência salva em: {destino}")
    raise SystemExit(0 if testes.wasSuccessful() else 1)
