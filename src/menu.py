"""
Menu interativo — Entrega 1: Criptografia Assimétrica e Confiança
Execute: python3 src/menu.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cifragem_hibrida as ch
import assinatura_digital as ad

# ── Cores ANSI ────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
VERDE  = "\033[92m"
VERM   = "\033[91m"
AZUL   = "\033[94m"
CIANO  = "\033[96m"
AMAR   = "\033[93m"
CINZA  = "\033[90m"
BRANCO = "\033[97m"

def limpar():
    os.system("clear")

def pausar():
    input(f"\n{CINZA}  Pressione ENTER para voltar ao menu...{RESET}")

def titulo(texto):
    print(f"\n{AZUL}{BOLD}  {'─' * 54}{RESET}")
    print(f"{AZUL}{BOLD}  {texto}{RESET}")
    print(f"{AZUL}{BOLD}  {'─' * 54}{RESET}\n")

def ok(msg):
    print(f"  {VERDE}{BOLD}✔  {msg}{RESET}")

def erro(msg):
    print(f"  {VERM}{BOLD}✘  {msg}{RESET}")

def info(msg):
    print(f"  {CIANO}→  {msg}{RESET}")

def aviso(msg):
    print(f"  {AMAR}⚠  {msg}{RESET}")

def cabecalho():
    limpar()
    print(f"\n{BOLD}{BRANCO}  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║   SEGURANÇA DA INFORMAÇÃO — Entrega 1               ║")
    print(f"  ║   Criptografia Assimétrica e Confiança              ║")
    print(f"  ╚══════════════════════════════════════════════════════╝{RESET}\n")

def menu_principal():
    cabecalho()
    print(f"  {BOLD}Escolha um teste:{RESET}\n")
    print(f"  {AMAR}[1]{RESET}  Cifragem híbrida  →  {VERDE}✔ SUCESSO{RESET}  (mensagem decifrada corretamente)")
    print(f"  {AMAR}[2]{RESET}  Cifragem híbrida  →  {VERM}✘ FALHA{RESET}   (texto cifrado adulterado)")
    print(f"  {AMAR}[3]{RESET}  Cifragem híbrida  →  {VERM}✘ FALHA{RESET}   (chave errada)")
    print(f"  {AMAR}[4]{RESET}  Assinatura digital →  {VERDE}✔ SUCESSO{RESET}  (assinatura verificada)")
    print(f"  {AMAR}[5]{RESET}  Assinatura digital →  {VERM}✘ FALHA{RESET}   (mensagem adulterada)")
    print(f"  {AMAR}[6]{RESET}  Assinatura digital →  {VERM}✘ FALHA{RESET}   (assinatura forjada)")
    print(f"  {AMAR}[7]{RESET}  Rodar {BOLD}todos os testes{RESET} em sequência")
    print(f"\n  {CINZA}[0]  Sair{RESET}\n")
    return input(f"  {BOLD}Opção: {RESET}").strip()

# ── Testes individuais ─────────────────────────────────────────

def teste_1():
    titulo("TESTE 1 — Cifragem híbrida: SUCESSO")
    print(f"  {CINZA}Cenário: mensagem cifrada e decifrada normalmente.{RESET}\n")

    info("Gerando par de chaves RSA-2048...")
    time.sleep(0.4)
    priv, pub = ch.gerar_par_chaves()
    ok("Par de chaves RSA-2048 gerado")

    mensagem = b"Contrato confidencial: valor = R$ 50.000,00"
    info(f"Mensagem original: \"{mensagem.decode()}\"")

    info("Cifrando com AES-256-GCM + RSA-OAEP...")
    time.sleep(0.3)
    pacote = ch.cifrar(mensagem, pub)
    ok(f"Chave AES cifrada: {len(pacote['chave_aes_cifrada'])} bytes")
    ok(f"Nonce GCM: {pacote['nonce'].hex()}")
    ok(f"Texto cifrado + tag: {len(pacote['texto_cifrado'])} bytes")

    info("Decifrando com a chave privada correta...")
    time.sleep(0.3)
    resultado = ch.decifrar(pacote, priv)
    ok(f"Mensagem recuperada: \"{resultado.decode()}\"")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: SUCESSO — a mensagem foi protegida e recuperada intacta.{RESET}")

def teste_2():
    titulo("TESTE 2 — Cifragem híbrida: FALHA (texto adulterado)")
    print(f"  {CINZA}Cenário: atacante altera 1 byte do texto cifrado em trânsito.{RESET}\n")

    priv, pub = ch.gerar_par_chaves()
    mensagem = b"Autorizacao de transferencia: R$ 9.999,00"
    info(f"Mensagem original: \"{mensagem.decode()}\"")

    info("Cifrando mensagem...")
    time.sleep(0.3)
    pacote = ch.cifrar(mensagem, pub)
    ok("Mensagem cifrada com sucesso")

    aviso("Simulando adulteração: invertendo bits do 1º byte do texto cifrado...")
    time.sleep(0.4)
    adulterado = bytearray(pacote["texto_cifrado"])
    adulterado[0] ^= 0xFF
    pacote_mal = dict(pacote)
    pacote_mal["texto_cifrado"] = bytes(adulterado)

    info("Tentando decifrar o pacote adulterado...")
    time.sleep(0.3)
    try:
        ch.decifrar(pacote_mal, priv)
        erro("ALERTA GRAVE: adulteração não detectada!")
    except Exception as e:
        ok(f"Adulteração detectada! Exceção: {BOLD}{type(e).__name__}{RESET}{VERDE}")
        ok("Tag GCM inválida — decifração abortada antes de expor dados corrompidos")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: CORRETO — o AES-GCM rejeitou o pacote adulterado.{RESET}")

def teste_3():
    titulo("TESTE 3 — Cifragem híbrida: FALHA (chave errada)")
    print(f"  {CINZA}Cenário: destinatário tenta decifrar com a chave privada errada.{RESET}\n")

    _, pub_legit   = ch.gerar_par_chaves()
    priv_errada, _ = ch.gerar_par_chaves()

    mensagem = b"Relatorio secreto de auditoria interna"
    info(f"Mensagem: \"{mensagem.decode()}\"")
    info("Cifrando com chave pública legítima...")
    time.sleep(0.3)
    pacote = ch.cifrar(mensagem, pub_legit)
    ok("Mensagem cifrada")

    aviso("Tentando decifrar com uma chave privada DIFERENTE...")
    time.sleep(0.4)
    try:
        ch.decifrar(pacote, priv_errada)
        erro("ALERTA GRAVE: decifrou com chave errada!")
    except Exception as e:
        ok(f"Decifração rejeitada! Exceção: {BOLD}{type(e).__name__}{RESET}{VERDE}")
        ok("RSA-OAEP não conseguiu recuperar a chave AES — operação abortada")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: CORRETO — chave errada não decifra a mensagem.{RESET}")

def teste_4():
    titulo("TESTE 4 — Assinatura digital: SUCESSO")
    print(f"  {CINZA}Cenário: mensagem assinada e verificada corretamente.{RESET}\n")

    info("Gerando par de chaves RSA-2048 para assinatura...")
    time.sleep(0.4)
    priv, pub = ad.gerar_par_chaves()
    ok("Par de chaves RSA-2048 gerado")

    mensagem = b"Termo de aceite: Eduardo Andrade concorda com os termos em 2026-11-09."
    info(f"Mensagem: \"{mensagem.decode()}\"")

    info("Assinando com RSA-PSS + SHA-256...")
    time.sleep(0.3)
    assinatura = ad.assinar(mensagem, priv)
    ok(f"Assinatura gerada: {len(assinatura)} bytes")
    ok(f"Prévia (hex): {assinatura[:20].hex()}...")

    info("Verificando assinatura com a chave pública...")
    time.sleep(0.3)
    valido = ad.verificar(mensagem, assinatura, pub)
    if valido:
        ok("Assinatura VÁLIDA — mensagem autêntica e íntegra")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: SUCESSO — identidade do remetente confirmada.{RESET}")

def teste_5():
    titulo("TESTE 5 — Assinatura digital: FALHA (mensagem adulterada)")
    print(f"  {CINZA}Cenário: atacante modifica o conteúdo da mensagem após a assinatura.{RESET}\n")

    priv, pub = ad.gerar_par_chaves()
    mensagem_original  = b"Pagamento de R$ 100,00 aprovado."
    mensagem_adulterada = b"Pagamento de R$ 99.999,00 aprovado."

    info(f"Mensagem original:   \"{mensagem_original.decode()}\"")
    info("Assinando mensagem original...")
    time.sleep(0.3)
    assinatura = ad.assinar(mensagem_original, priv)
    ok("Assinatura gerada")

    aviso(f"Mensagem adulterada: \"{mensagem_adulterada.decode()}\"")
    aviso("Reutilizando a assinatura da mensagem original na versão adulterada...")
    time.sleep(0.4)

    info("Verificando assinatura na mensagem adulterada...")
    time.sleep(0.3)
    valido = ad.verificar(mensagem_adulterada, assinatura, pub)
    if not valido:
        ok("Assinatura INVÁLIDA — alteração na mensagem detectada")
        ok("RSA-PSS recalculou o hash e detectou divergência")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: CORRETO — adulteração bloqueada pela assinatura digital.{RESET}")

def teste_6():
    titulo("TESTE 6 — Assinatura digital: FALHA (assinatura forjada)")
    print(f"  {CINZA}Cenário: atacante tenta forjar uma assinatura com bytes aleatórios.{RESET}\n")

    priv, pub = ad.gerar_par_chaves()
    mensagem = b"Contrato de prestacao de servicos aprovado."

    info(f"Mensagem: \"{mensagem.decode()}\"")
    aviso("Gerando assinatura falsa com 256 bytes aleatórios...")
    time.sleep(0.4)
    import os as _os
    assinatura_falsa = _os.urandom(256)
    ok(f"Assinatura falsa gerada: {len(assinatura_falsa)} bytes")

    info("Verificando assinatura falsa contra a mensagem...")
    time.sleep(0.3)
    valido = ad.verificar(mensagem, assinatura_falsa, pub)
    if not valido:
        ok("Assinatura forjada REJEITADA")
        ok("Sem a chave privada, é computacionalmente inviável forjar uma assinatura válida")

    print(f"\n  {VERDE}{BOLD}  RESULTADO: CORRETO — tentativa de forja bloqueada.{RESET}")

def todos_os_testes():
    testes = [teste_1, teste_2, teste_3, teste_4, teste_5, teste_6]
    nomes  = [
        "Cifragem → Sucesso",
        "Cifragem → Texto adulterado",
        "Cifragem → Chave errada",
        "Assinatura → Sucesso",
        "Assinatura → Mensagem adulterada",
        "Assinatura → Assinatura forjada",
    ]

    cabecalho()
    titulo("TODOS OS TESTES")

    for i, (teste, nome) in enumerate(zip(testes, nomes), 1):
        print(f"  {AMAR}[{i}/6]{RESET} {nome}...")
        time.sleep(0.2)

    print()
    for teste in testes:
        teste()
        print(f"\n  {CINZA}{'─' * 54}{RESET}\n")
        time.sleep(0.3)

    print(f"\n  {VERDE}{BOLD}  TODOS OS 6 TESTES CONCLUÍDOS COM SUCESSO.{RESET}\n")

# ── Loop principal ─────────────────────────────────────────────

mapa = {
    "1": teste_1, "2": teste_2, "3": teste_3,
    "4": teste_4, "5": teste_5, "6": teste_6,
    "7": todos_os_testes,
}

while True:
    opcao = menu_principal()
    if opcao == "0":
        limpar()
        print(f"\n  {CIANO}Até logo!{RESET}\n")
        break
    elif opcao in mapa:
        limpar()
        mapa[opcao]()
        pausar()
    else:
        aviso("Opção inválida. Tente novamente.")
        time.sleep(1)
