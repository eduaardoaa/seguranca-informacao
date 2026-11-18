import hashlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from autenticacao import Autenticacao, ITERACOES, RAIZ


SENHA = "caderno azul junto da janela"


class TestAutenticacao(unittest.TestCase):
    def setUp(self):
        (RAIZ / "dados").mkdir(exist_ok=True)
        self.temporario = tempfile.TemporaryDirectory(dir=RAIZ / "dados")
        self.banco = Path(self.temporario.name) / "teste.sqlite3"
        self.app = Autenticacao(self.banco)
        self.addCleanup(self.temporario.cleanup)
        self.addCleanup(self.app.fechar)

    def test_login_correto(self):
        cadastro, login = [], []
        self.app.cadastrar("aluno", SENHA, acompanhar=cadastro.append)
        self.assertTrue(self.app.autenticar("aluno", SENHA, acompanhar=login.append))
        self.assertTrue(cadastro[-1].startswith("[7/7]"))
        self.assertTrue(login[-1].startswith("[5/5]"))
        self.assertNotIn(SENHA, "\n".join(cadastro + login))

    def test_login_incorreto_e_usuario_inexistente(self):
        self.app.cadastrar("aluno", SENHA)
        incorreto, inexistente = [], []
        self.assertFalse(self.app.autenticar(
            "aluno", "senha incorreta para o teste", acompanhar=incorreto.append))
        self.assertFalse(self.app.autenticar(
            "inexistente", SENHA, acompanhar=inexistente.append))
        self.assertEqual(incorreto, inexistente)

    def test_persistencia_apos_reabrir(self):
        self.app.cadastrar("aluno", SENHA)
        outra = Autenticacao(self.banco)
        try:
            self.assertTrue(outra.autenticar("aluno", SENHA))
        finally:
            outra.fechar()

    def test_mesma_senha_produz_salts_e_hashes_distintos(self):
        self.app.cadastrar("aluno1", SENHA)
        self.app.cadastrar("aluno2", SENHA)
        a, b = self.app.conexao.execute("SELECT * FROM usuarios ORDER BY usuario").fetchall()
        self.assertNotEqual(a["salt"], b["salt"])
        self.assertNotEqual(a["hash"], b["hash"])
        for registro in (a, b):
            self.assertEqual(registro["algoritmo"], "pbkdf2-sha256")
            self.assertEqual(registro["iteracoes"], 600_000)
            self.assertEqual(len(registro["salt"]), 16)
            self.assertEqual(len(registro["hash"]), 32)
            self.assertEqual(registro["hash"], hashlib.pbkdf2_hmac(
                "sha256", SENHA.encode(), registro["salt"], ITERACOES, dklen=32))

    def test_banco_nao_armazena_senha_em_texto(self):
        self.app.cadastrar("aluno", SENHA)
        colunas = [r[1] for r in self.app.conexao.execute("PRAGMA table_info(usuarios)")]
        self.assertEqual(colunas, ["usuario", "algoritmo", "iteracoes", "salt", "hash"])
        self.assertNotIn(SENHA.encode(), self.banco.read_bytes())
        self.assertNotIn(SENHA, "\n".join(self.app.conexao.iterdump()))

    def test_comparacao_segura_da_biblioteca(self):
        self.app.cadastrar("aluno", SENHA)
        import hmac
        with patch("autenticacao.hmac.compare_digest", wraps=hmac.compare_digest) as comparar:
            self.assertTrue(self.app.autenticar("aluno", SENHA))
            self.assertFalse(self.app.autenticar("aluno", "outra senha completamente diferente"))
            self.assertFalse(self.app.autenticar("desconhecido", SENHA))
            self.assertEqual(comparar.call_count, 3)
            for chamada in comparar.call_args_list:
                self.assertEqual([len(v) for v in chamada.args], [32, 32])

    def test_limites_da_senha(self):
        for senha in ("", "a" * 7, "a" * 129):
            with self.subTest(tamanho=len(senha)), self.assertRaises(ValueError):
                self.app.cadastrar("aluno", senha)
        for n in (8, 14, 15, 128):
            self.app.cadastrar(f"aluno{n}", "á" * n)
            self.assertTrue(self.app.autenticar(f"aluno{n}", "á" * n))

    def test_frase_sem_regra_de_composicao_e_espacos_preservados(self):
        senha = "  frase simples com espaços  "
        self.app.cadastrar("aluno", senha)
        self.assertTrue(self.app.autenticar("aluno", senha))
        self.assertFalse(self.app.autenticar("aluno", senha.strip()))

    def test_base_bloqueia_senha_comprida(self):
        # Escolha real da base, com comprimento que passa pela política mínima.
        vazadas = (RAIZ / "recursos" / "senhas_vazadas.txt").read_text(encoding="utf-8").splitlines()
        senha = next(s for s in vazadas if 8 <= len(s) <= 128)
        with self.assertRaisesRegex(ValueError, "base local"):
            self.app.cadastrar("aluno", senha.upper())
        self.assertEqual(self.app.conexao.execute("SELECT count(*) FROM usuarios").fetchone()[0], 0)

    def test_duplicidade_preserva_cadastro_original(self):
        self.app.cadastrar(" Aluno ", SENHA)
        with self.assertRaises(ValueError):
            self.app.cadastrar("ALUNO", "nova senha diferente da original")
        self.assertTrue(self.app.autenticar("ALUNO", SENHA))

    def test_usuario_invalido_e_injecao_sql(self):
        self.app.cadastrar("aluno", SENHA)
        for usuario in ("", "ab", "a" * 41, "' OR 1=1 --"):
            with self.subTest(usuario=usuario):
                with self.assertRaises(ValueError):
                    self.app.cadastrar(usuario, SENHA)
                self.assertFalse(self.app.autenticar(usuario, SENHA))
        self.assertTrue(self.app.autenticar("aluno", SENHA))

    def test_hash_adulterado_impede_login(self):
        self.app.cadastrar("aluno", SENHA)
        with self.app.conexao:
            self.app.conexao.execute("UPDATE usuarios SET hash = ?", (bytes(32),))
        self.assertFalse(self.app.autenticar("aluno", SENHA))

    def test_parametros_invalidos_rejeitados_no_banco(self):
        self.app.cadastrar("aluno", SENHA)
        for campo, valor in (("iteracoes", 1), ("algoritmo", "sha256"),
                             ("salt", b"curto"), ("hash", b"curto")):
            with self.subTest(campo=campo), self.assertRaises(sqlite3.IntegrityError):
                with self.app.conexao:
                    self.app.conexao.execute(f"UPDATE usuarios SET {campo} = ?", (valor,))

    def test_base_ausente_interrompe_inicializacao(self):
        with patch("autenticacao.Path.read_text", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                Autenticacao(self.banco)

    def test_base_vazia_interrompe_inicializacao(self):
        with patch("autenticacao.Path.read_text", return_value=""):
            with self.assertRaisesRegex(ValueError, "vazia"):
                Autenticacao(self.banco)


if __name__ == "__main__":
    unittest.main(verbosity=2)
