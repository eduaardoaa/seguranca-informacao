"""Cenários didáticos isolados; não alteram os cadastros do menu."""

from pathlib import Path
import tempfile
from time import perf_counter

from autenticacao import Autenticacao, RAIZ, MIN_SENHA, MAX_SENHA
from interface import titulo, secao, info, ok, erro, aviso, rejeicao, resultado, resumo


SENHA_DEMO = "caderno azul junto da janela"
NOMES = {
    "3": "Login correto → SUCESSO",
    "4": "Senha incorreta → REJEIÇÃO",
    "5": "Usuário inexistente → REJEIÇÃO",
    "6": "Mesma senha → SALTS E HASHES DIFERENTES",
    "7": "Senha comum/vazada → CADASTRO REJEITADO",
    "8": "Hash adulterado → LOGIN REJEITADO",
}


def conferir(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)
    ok(mensagem)


def demonstrar(opcao):
    titulo(f"CENÁRIO {int(opcao) - 2} — {NOMES[opcao]}")
    info("Ambiente: banco temporário próprio; somente dados fictícios.")
    expectativas = {
        "3": "Permitir o login com a senha correta.",
        "4": "Bloquear o login com senha incorreta.",
        "5": "Bloquear o login do usuário inexistente.",
        "6": "Gerar salts e hashes distintos para duas contas com a mesma senha.",
        "7": "Bloquear o cadastro antes de gravar a senha da base.",
        "8": "Bloquear o login depois da alteração do hash.",
    }
    info(f"Esperado: {expectativas[opcao]}")
    (RAIZ / "dados").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=RAIZ / "dados") as pasta:
        app = Autenticacao(Path(pasta) / "demo.sqlite3")
        try:
            if opcao == "7":
                secao("Execução — tentativa de cadastro")
                senha = next(s for s in sorted(app.bloqueadas)
                             if MIN_SENHA <= len(s) <= MAX_SENHA)
                aviso("Tentando cadastrar uma senha extraída das bases de bloqueio.")
                try:
                    app.cadastrar("aluno_demo", senha, acompanhar=info)
                except ValueError as exc:
                    conferir("base local" in str(exc), "Senha bloqueada pela base local.")
                    rejeicao(str(exc))
                else:
                    raise AssertionError("Senha da base foi aceita indevidamente.")
                quantidade = app.conexao.execute("SELECT count(*) FROM usuarios").fetchone()[0]
                conferir(quantidade == 0, "Nenhum registro foi gravado.")
            else:
                secao("Preparação — cadastro fictício")
                info("Preparando a conta fictícia aluno_demo:")
                app.cadastrar("aluno_demo", SENHA_DEMO, acompanhar=info)
                if opcao == "6":
                    secao("Execução — segunda conta e comparação")
                    info("Cadastrando colega_demo com a mesma senha, sem expor seu texto:")
                    app.cadastrar("colega_demo", SENHA_DEMO, acompanhar=info)
                    a, b = app.conexao.execute("SELECT * FROM usuarios ORDER BY usuario").fetchall()
                    conferir(a["salt"] != b["salt"], "Cada conta recebeu um salt diferente.")
                    conferir(a["hash"] != b["hash"], "A mesma senha produziu hashes diferentes.")
                else:
                    secao("Execução — verificação do login")
                    usuario, senha = "aluno_demo", SENHA_DEMO
                    if opcao == "4":
                        aviso("Simulando uma tentativa com senha incorreta.")
                        senha = "outra frase para teste"
                    elif opcao == "5":
                        aviso("Simulando uma tentativa para um usuário sem cadastro.")
                        usuario = "nao_existe"
                    elif opcao == "8":
                        aviso("Substituindo o hash da conta fictícia por 32 bytes nulos.")
                        with app.conexao:
                            app.conexao.execute("UPDATE usuarios SET hash = ?", (bytes(32),))
                    info("Executando o login:")
                    aceito = app.autenticar(usuario, senha, acompanhar=info)
                    conferir(aceito == (opcao == "3"), "Resultado observado corresponde ao esperado.")
                    if aceito:
                        ok("Login realizado com sucesso.")
                    else:
                        rejeicao("Usuário ou senha inválidos.")
            resultado("APROVADO — comportamento esperado confirmado.")
        finally:
            app.fechar()
    info("Banco temporário removido; os usuários cadastrados no menu foram preservados.")


def demonstrar_todos():
    titulo("TODOS OS 6 CENÁRIOS")
    info("Verde: teste aprovado  |  Amarelo: bloqueio esperado  |  Vermelho: falha inesperada")
    inicio = perf_counter()
    cenarios = []
    for opcao, nome in NOMES.items():
        try:
            demonstrar(opcao)
        except AssertionError as exc:
            erro(f"Falha inesperada: {exc}")
            cenarios.append((nome, False))
        else:
            cenarios.append((nome, True))
    resumo(cenarios, perf_counter() - inicio)
    passou = all(aprovado for _, aprovado in cenarios)
    resultado("TODOS OS 6 CENÁRIOS APROVADOS." if passou else "HÁ CENÁRIOS COM FALHA.", sucesso=passou)
    if not passou:
        raise AssertionError("Consulte o resumo dos cenários que falharam.")
