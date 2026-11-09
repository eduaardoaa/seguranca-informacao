import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def gerar_par_chaves(bits: int = 2048):
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
    )
    return chave_privada, chave_privada.public_key()


def cifrar(mensagem: bytes, chave_publica) -> dict:
    chave_aes = os.urandom(32)
    nonce = os.urandom(12)

    aesgcm = AESGCM(chave_aes)
    texto_cifrado = aesgcm.encrypt(nonce, mensagem, None)

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
    chave_aes = chave_privada.decrypt(
        pacote["chave_aes_cifrada"],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aesgcm = AESGCM(chave_aes)
    return aesgcm.decrypt(pacote["nonce"], pacote["texto_cifrado"], None)


def salvar_chaves(chave_privada, chave_publica, pasta: str = "chaves"):
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
