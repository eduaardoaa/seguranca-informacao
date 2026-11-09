import os
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_CHAVES_DIR = os.path.join(_SRC_DIR, "..", "chaves")
sys.path.insert(0, _SRC_DIR)

import cifragem_hibrida as ch
import assinatura_digital as ad


def linha(titulo: str):
    print(f"\n{'=' * 65}")
    print(f"  {titulo}")
    print(f"{'=' * 65}")


def demo_cifragem_hibrida():
    linha("CENÁRIO 1 — CIFRAGEM HÍBRIDA (RSA-OAEP + AES-256-GCM)")

    print("\n[1/5] Gerando par de chaves RSA-2048...")
    chave_privada, chave_publica = ch.gerar_par_chaves(bits=2048)
    ch.salvar_chaves(chave_privada, chave_publica, pasta=_CHAVES_DIR)
    print("      OK — par gerado e salvo em chaves/")

    mensagem_original = b"Dados confidenciais: saldo = R$ 12.500,00 | conta = 00123-4"
    print(f"\n[2/5] Mensagem original:\n      \"{mensagem_original.decode()}\"")

    print("\n[3/5] Cifrando mensagem...")
    pacote = ch.cifrar(mensagem_original, chave_publica)
    print(f"      Chave AES cifrada (RSA-OAEP): {len(pacote['chave_aes_cifrada'])} bytes")
    print(f"      Nonce GCM (96 bits):           {pacote['nonce'].hex()}")
    print(f"      Texto cifrado + tag GCM:       {len(pacote['texto_cifrado'])} bytes")

    print("\n[4/5] TESTE A — Decifragem sem adulteração (esperado: SUCESSO)")
    try:
        resultado = ch.decifrar(pacote, chave_privada)
        print(f"      [SUCESSO] Mensagem recuperada:\n      \"{resultado.decode()}\"")
    except Exception as e:
        print(f"      [FALHA INESPERADA] {type(e).__name__}: {e}")

    print("\n[5/5] TESTE B — 1 byte adulterado no texto cifrado (esperado: FALHA)")
    pacote_adulterado = dict(pacote)
    ciphertext_adulterado = bytearray(pacote["texto_cifrado"])
    ciphertext_adulterado[0] ^= 0xFF         
    pacote_adulterado["texto_cifrado"] = bytes(ciphertext_adulterado)

    try:
        resultado = ch.decifrar(pacote_adulterado, chave_privada)
        print(f"      [ALERTA — FALHA GRAVE] Adulteração não detectada: \"{resultado.decode()}\"")
    except Exception as e:
        print(f"      [CORRETO] Adulteração detectada e rejeitada!")
        print(f"      Exceção: {type(e).__name__} — {e}")


def demo_assinatura_digital():
    linha("CENÁRIO 2 — ASSINATURA DIGITAL (RSA-PSS + SHA-256)")

    print("\n[1/6] Gerando par de chaves RSA-2048 para assinatura...")
    chave_privada, chave_publica = ad.gerar_par_chaves(bits=2048)
    print("      OK — par gerado")

    mensagem = b"Termo de aceite: Eduardo Andrade aprova versao 3.1 do contrato em 2026-11-02."
    print(f"\n[2/6] Mensagem a assinar:\n      \"{mensagem.decode()}\"")

    print("\n[3/6] Assinando com RSA-PSS (SHA-256)...")
    assinatura = ad.assinar(mensagem, chave_privada)
    print(f"      Assinatura gerada: {len(assinatura)} bytes")
    print(f"      Primeiros 24 bytes (hex): {assinatura[:24].hex()}...")

    print("\n[4/6] TESTE A — Verificação da mensagem original (esperado: SUCESSO)")
    valido = ad.verificar(mensagem, assinatura, chave_publica)
    print(f"      [{'SUCESSO' if valido else 'FALHA INESPERADA'}] "
          f"Assinatura {'VÁLIDA' if valido else 'inválida'}")

    print("\n[5/6] TESTE B — Mensagem adulterada (esperado: FALHA)")
    mensagem_adulterada = mensagem.replace(b"aprova", b"REJEITA")
    valido = ad.verificar(mensagem_adulterada, assinatura, chave_publica)
    if not valido:
        print("      [CORRETO] Adulteração da mensagem detectada — assinatura INVÁLIDA")
    else:
        print("      [ALERTA — FALHA GRAVE] Mensagem adulterada passou na verificação!")

    print("\n[6/6] TESTE C — Assinatura forjada com bytes aleatórios (esperado: FALHA)")
    assinatura_forjada = os.urandom(len(assinatura))
    valido = ad.verificar(mensagem, assinatura_forjada, chave_publica)
    if not valido:
        print("      [CORRETO] Assinatura forjada rejeitada corretamente")
    else:
        print("      [ALERTA — FALHA GRAVE] Assinatura forjada aceita!")


if __name__ == "__main__":
    print("=" * 65)
    print("  PROJETO INTEGRADOR — SEGURANÇA DA INFORMAÇÃO")
    print("  Entrega 1: Criptografia Assimétrica e Confiança")
    print("  Disciplina: Segurança da Informação | Unit")
    print("=" * 65)

    demo_cifragem_hibrida()
    demo_assinatura_digital()

    print("\n" + "=" * 65)
    print("  DEMONSTRAÇÃO CONCLUÍDA — todos os cenários executados")
    print("=" * 65 + "\n")
