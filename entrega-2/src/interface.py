"""Apresentação no terminal, no mesmo estilo da Entrega 1."""

import os
import re
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
VERDE = "\033[92m"
VERM = "\033[91m"
AZUL = "\033[94m"
CIANO = "\033[96m"
AMAR = "\033[93m"
CINZA = "\033[90m"
BRANCO = "\033[97m"


def texto(mensagem, cor=""):
    return f"{cor}{mensagem}{RESET}" if sys.stdout.isatty() else mensagem


def limpar():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input(texto("\n  Pressione ENTER para voltar ao menu...", CINZA))


def titulo(mensagem):
    print(texto(f"\n  {'─' * 62}\n  {mensagem}\n  {'─' * 62}\n", AZUL + BOLD))


def secao(mensagem):
    print(texto(f"\n  {mensagem.upper()}\n  {'─' * 62}", AZUL + BOLD))


def info(mensagem):
    etapa = re.match(r"(\[\d+/\d+\]) (.*)", mensagem)
    if etapa:
        print(f"\n  {texto(etapa[1], AZUL + BOLD)} {etapa[2]}")
    elif mensagem.startswith("      "):
        print(texto(f"        {mensagem.strip()}", CINZA))
    else:
        print(texto(f"  → {mensagem}", CIANO))


def ok(mensagem):
    print(texto(f"  ✔ {mensagem}", VERDE + BOLD))


def erro(mensagem):
    print(texto(f"  ✘ {mensagem}", VERM + BOLD))


def aviso(mensagem):
    print(texto(f"  ⚠ {mensagem}", AMAR))


def rejeicao(mensagem):
    print(texto(f"  [BLOQUEIO ESPERADO] {mensagem}", AMAR + BOLD))


def resultado(mensagem, sucesso=True):
    cor = VERDE if sucesso else VERM
    print(texto(f"\n  {'─' * 62}\n  RESULTADO: {mensagem}\n  {'─' * 62}", cor + BOLD))


def resumo(cenarios, duracao):
    secao("Resumo das demonstrações")
    for nome, passou in cenarios:
        status = texto("APROVADO" if passou else "FALHOU", VERDE if passou else VERM)
        print(f"  [{status}] {nome}")
    aprovados = sum(passou for _, passou in cenarios)
    print(f"\n  Total: {len(cenarios)}  |  Aprovados: {aprovados}  |  Falhas: {len(cenarios) - aprovados}")
    print(texto(f"  Duração: {duracao:.2f}s", CINZA))
    print(texto("  Uma rejeição esperada indica que a proteção funcionou.", CINZA))


def cabecalho():
    limpar()
    linhas = ["╔" + "═" * 62 + "╗",
              "║" + "SEGURANÇA DA INFORMAÇÃO — Entrega 2".center(62) + "║",
              "║" + "Hash e autenticação segura".center(62) + "║",
              "╚" + "═" * 62 + "╝"]
    print(texto("\n  " + "\n  ".join(linhas) + "\n", BRANCO + BOLD))
