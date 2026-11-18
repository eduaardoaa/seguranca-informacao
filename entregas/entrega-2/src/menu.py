"""Execute da raiz: python entregas/entrega-2/src/menu.py."""

import sqlite3

from autenticacao import Autenticacao, MIN_SENHA, MAX_SENHA
from demonstracoes import NOMES, demonstrar, demonstrar_todos
from entrada_senha import ler_senha
from interface import (AMAR, BOLD, CINZA, VERDE, CIANO, texto, cabecalho, limpar, pausar,
                       titulo, info, ok, erro, aviso, resultado)


def menu_principal():
    cabecalho()
    print(texto("  Escolha uma operação ou demonstração:\n", BOLD))
    opcoes = {"1": "Cadastrar usuário → PASSO A PASSO",
              "2": "Entrar com usuário → PASSO A PASSO", **NOMES,
              "9": "Rodar todos os 6 cenários em sequência"}
    for numero, descricao in opcoes.items():
        cor = AMAR if numero in {"4", "5", "7", "8"} else VERDE if numero == "3" else CIANO
        print(f"  {texto('[' + numero + ']', AMAR)}  {texto(descricao, cor)}")
    print(texto("\n  [0]  Sair\n", CINZA))
    return input(texto("  Opção: ", BOLD)).strip()


def cadastrar(app):
    titulo("CADASTRO — PASSO A PASSO")
    info("O cadastro será salvo no banco local da Entrega 2.")
    usuario = input("  Usuário: ")
    senha = ler_senha(f"  Senha ({MIN_SENHA} a {MAX_SENHA} caracteres): ")
    if senha != ler_senha("  Confirme a senha: "):
        erro("As senhas não coincidem. Nenhum cadastro foi realizado.")
        return
    try:
        app.cadastrar(usuario, senha, acompanhar=info)
    except ValueError as exc:
        erro(str(exc))
        aviso("Cadastro interrompido; nenhum registro novo foi confirmado.")
        return
    ok("Cadastro realizado!")
    resultado("SUCESSO — somente os dados protegidos foram persistidos.")


def entrar(app):
    titulo("LOGIN — PASSO A PASSO")
    usuario = input("  Usuário: ")
    senha = ler_senha("  Senha: ")
    if app.autenticar(usuario, senha, acompanhar=info):
        ok("Login realizado com sucesso.")
        resultado("SUCESSO — credenciais verificadas.")
    else:
        erro("Usuário ou senha inválidos.")


def main():
    app = None
    try:
        while True:
            opcao = menu_principal()
            if opcao == "0":
                print(texto("\n  Até logo!\n", CINZA))
                break
            if opcao not in {"1", "2", *NOMES, "9"}:
                aviso("Opção inválida.")
                pausar()
                continue
            limpar()
            if opcao in {"1", "2"}:
                if app is None:
                    app = Autenticacao()
                (cadastrar if opcao == "1" else entrar)(app)
            else:
                try:
                    demonstrar_todos() if opcao == "9" else demonstrar(opcao)
                except AssertionError as exc:
                    resultado(f"FALHA INESPERADA: {exc}", sucesso=False)
            pausar()
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrado.")
    except (OSError, sqlite3.Error, ValueError):
        erro("Não foi possível acessar os dados locais. Verifique o banco e a base de senhas.")
    finally:
        if app is not None:
            app.fechar()


if __name__ == "__main__":
    main()
