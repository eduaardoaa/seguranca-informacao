from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


def gerar_par_chaves(bits: int = 2048):
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
    )
    return chave_privada, chave_privada.public_key()


def assinar(mensagem: bytes, chave_privada) -> bytes:
    return chave_privada.sign(
        mensagem,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verificar(mensagem: bytes, assinatura: bytes, chave_publica) -> bool:
    try:
        chave_publica.verify(
            assinatura,
            mensagem,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
