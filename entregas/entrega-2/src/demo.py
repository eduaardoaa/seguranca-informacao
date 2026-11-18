"""Evidência reproduzível usando somente identidades e credenciais fictícias."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import platform
import sys
import tempfile

from autenticacao import Autenticacao, RAIZ, MIN_SENHA, MAX_SENHA
from interface import titulo, secao, info, ok, erro, rejeicao, resultado


def executar():
    titulo("ENTREGA 2 — EVIDÊNCIA DE EXECUÇÃO")
    print("Data:", datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds"))
    print("Python:", platform.python_version(), "| Sistema:", platform.system())
    print("Escopo: SQLite temporário local; somente dados fictícios.")
    senha = "caderno azul junto da janela"

    def conferir(descricao, condicao, bloqueio=False):
        if not condicao:
            erro(f"FALHOU: {descricao}")
            raise AssertionError(descricao)
        (rejeicao if bloqueio else ok)(descricao)

    (RAIZ / "dados").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=RAIZ / "dados") as pasta:
        banco = Path(pasta) / "demo.sqlite3"
        app = Autenticacao(banco)
        try:
            print("Entradas na base local:", len(app.bloqueadas))
            secao("1. Cadastro das duas contas fictícias")
            app.cadastrar("aluno_demo", senha, acompanhar=info)
            app.cadastrar("colega_demo", senha, acompanhar=info)
            registros = app.conexao.execute("SELECT * FROM usuarios ORDER BY usuario").fetchall()
            secao("2. Registros protegidos — salt/hash em hexadecimal")
            for r in registros:
                print(f"\n  Usuário: {r['usuario']}  |  {r['algoritmo']}  |  {r['iteracoes']} iterações")
                print(f"  Salt: {r['salt'].hex()}\n  Hash: {r['hash'].hex()}")
            secao("3. Verificação do armazenamento")
            conferir("Não existe coluna de senha em texto puro",
                     registros[0].keys() == ["usuario", "algoritmo", "iteracoes", "salt", "hash"])
            conferir("Senha fictícia ausente do arquivo SQLite", senha.encode() not in banco.read_bytes())
            conferir("Mesma senha possui salts e hashes distintos",
                     registros[0]["salt"] != registros[1]["salt"] and registros[0]["hash"] != registros[1]["hash"])
            secao("4. Login com senha correta — esperado: permitir")
            conferir("Login correto aceito", app.autenticar("aluno_demo", senha, acompanhar=info))
            secao("5. Senha incorreta — esperado: bloquear")
            conferir("Senha incorreta rejeitada", not app.autenticar(
                "aluno_demo", "outra frase para teste", acompanhar=info), bloqueio=True)
            secao("6. Usuário inexistente — esperado: bloquear")
            conferir("Usuário inexistente rejeitado", not app.autenticar(
                "nao_existe", senha, acompanhar=info), bloqueio=True)
            secao("7. Senha das bases locais — esperado: bloquear")
            try:
                app.cadastrar("bloqueado", next(
                    s for s in app.bloqueadas if MIN_SENHA <= len(s) <= MAX_SENHA
                ), acompanhar=info)
            except ValueError as exc:
                rejeicao(f"Senha da base rejeitada: {exc}")
            else:
                raise AssertionError("Senha da base aceita")
            print("\nVerificação usa hashlib.pbkdf2_hmac + hmac.compare_digest.")
            print("Fim: banco temporário será removido; nenhum cadastro real foi utilizado.")
            resultado("TODAS AS VERIFICAÇÕES APROVADAS.")
        finally:
            app.fechar()


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--salvar":
        import contextlib
        destino = Path(sys.argv[2])
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as arquivo, contextlib.redirect_stdout(arquivo):
            executar()
        print("Evidência salva em:", destino)
    elif len(sys.argv) == 1:
        executar()
    else:
        raise SystemExit("Uso: python demo.py [--salvar caminho.txt]")
