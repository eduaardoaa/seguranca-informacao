"""
Cifragem Híbrida: RSA-OAEP (2048-bit) + AES-256-GCM
- A chave AES é gerada aleatoriamente por mensagem e cifrada com RSA-OAEP.
- O conteúdo é cifrado com AES-256-GCM, que garante sigilo E integridade.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def gerar_par_chaves(bits: int = 2048):
    """Gera par de chaves RSA. Expoente público 65537 (F4), recomendado pelo NIST."""
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
    )
    return chave_privada, chave_privada.public_key()


def cifrar(mensagem: bytes, chave_publica) -> dict:
    """
    Cifra a mensagem com cifragem híbrida.
    Retorna dicionário com: chave_aes_cifrada, nonce, texto_cifrado (inclui tag GCM).
    """
    # Chave AES-256 efêmera (32 bytes = 256 bits), única por mensagem
    chave_aes = os.urandom(32)
    # Nonce de 96 bits — tamanho recomendado para GCM (evita colisões)
    nonce = os.urandom(12)

    # Cifra conteúdo com AES-256-GCM (sigilo + autenticidade do conteúdo)
    aesgcm = AESGCM(chave_aes)
    texto_cifrado = aesgcm.encrypt(nonce, mensagem, None)  # inclui tag de 16 bytes ao final

    # Encapsula chave AES com RSA-OAEP + SHA-256
    chave_aes_cifrada = chave_publica.encrypt(
        chave_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return {
        "chave_aes_cifrada": chave_aes_cifrada,
        "nonce": nonce,
        "texto_cifrado": texto_cifrado,
    }


def decifrar(pacote: dict, chave_privada) -> bytes:
    """
    Decifra o pacote. Lança InvalidTag se o conteúdo foi adulterado,
    ou ValueError se a chave RSA não corresponde.
    """
    # Recupera chave AES usando RSA-OAEP
    chave_aes = chave_privada.decrypt(
        pacote["chave_aes_cifrada"],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Decifra e verifica integridade pelo tag GCM
    aesgcm = AESGCM(chave_aes)
    return aesgcm.decrypt(pacote["nonce"], pacote["texto_cifrado"], None)


def salvar_chaves(chave_privada, chave_publica, pasta: str = "chaves"):
    """Salva as chaves em formato PEM."""
    os.makedirs(pasta, exist_ok=True)

    pem_priv = chave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_pub = chave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(f"{pasta}/chave_privada.pem", "wb") as f:
        f.write(pem_priv)
    with open(f"{pasta}/chave_publica.pem", "wb") as f:
        f.write(pem_pub)

    print(f"    Chaves salvas em: {pasta}/")
