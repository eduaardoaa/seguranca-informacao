"""Cadastro e verificação local com primitivas da biblioteca padrão."""

import hashlib
import hmac
from pathlib import Path
import re
import secrets
import sqlite3


RAIZ = Path(__file__).resolve().parents[1]
ITERACOES = 600_000
TAMANHO_SALT = 16
TAMANHO_HASH = 32
MIN_SENHA = 8
MAX_SENHA = 128


def _etapa(acompanhar, mensagem):
    if acompanhar is not None:
        acompanhar(mensagem)


def derivar(senha: str, salt: bytes, iteracoes: int = ITERACOES) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, iteracoes, dklen=TAMANHO_HASH
    )


class Autenticacao:
    def __init__(self, banco=None):
        caminho = Path(banco) if banco is not None else RAIZ / "dados" / "usuarios.sqlite3"
        bloqueadas = set()
        for nome in ("senhas_comuns.txt", "senhas_vazadas.txt"):
            linhas = (RAIZ / "recursos" / nome).read_text(encoding="utf-8").splitlines()
            if not linhas or not any(linhas):
                raise ValueError("Base de senhas bloqueadas vazia.")
            bloqueadas.update(linha.casefold() for linha in linhas if linha)
        self.bloqueadas = frozenset(bloqueadas)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.conexao = sqlite3.connect(caminho)
        self.conexao.row_factory = sqlite3.Row
        self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                algoritmo TEXT NOT NULL CHECK (algoritmo = 'pbkdf2-sha256'),
                iteracoes INTEGER NOT NULL CHECK (iteracoes = 600000),
                salt BLOB NOT NULL CHECK (length(salt) = 16),
                hash BLOB NOT NULL CHECK (length(hash) = 32)
            )
        """)
        self.conexao.commit()
        self.salt_ficticio = secrets.token_bytes(TAMANHO_SALT)
        self.hash_ficticio = derivar(secrets.token_urlsafe(32), self.salt_ficticio)

    def fechar(self):
        self.conexao.close()

    @staticmethod
    def normalizar_usuario(usuario: str) -> str:
        usuario = usuario.strip().lower()
        if not re.fullmatch(r"[a-z0-9_.-]{3,40}", usuario):
            raise ValueError("Usuário: 3 a 40 letras sem acento, números, ponto, _ ou -.")
        return usuario

    def cadastrar(self, usuario: str, senha: str, acompanhar=None):
        _etapa(acompanhar, "[1/7] Validando e normalizando o identificador do usuário...")
        usuario = self.normalizar_usuario(usuario)
        _etapa(acompanhar, f"[2/7] Conferindo o tamanho da senha: {MIN_SENHA} a {MAX_SENHA} caracteres...")
        if not MIN_SENHA <= len(senha) <= MAX_SENHA:
            raise ValueError(f"A senha deve ter entre {MIN_SENHA} e {MAX_SENHA} caracteres.")
        _etapa(acompanhar, "[3/7] Consultando as bases locais de senhas comuns e vazadas...")
        if senha.casefold() in self.bloqueadas:
            raise ValueError("Senha presente na base local de senhas expostas/comuns.")
        _etapa(acompanhar, "[4/7] Gerando salt aleatório individual de 16 bytes...")
        salt = secrets.token_bytes(TAMANHO_SALT)
        _etapa(acompanhar, f"      Salt gerado (hex): {salt.hex()}")
        _etapa(acompanhar, f"[5/7] Derivando hash com PBKDF2-HMAC-SHA256 ({ITERACOES:,} iterações)...")
        resumo = derivar(senha, salt)
        _etapa(acompanhar, f"      Hash derivado (hex): {resumo.hex()}")
        _etapa(acompanhar, "[6/7] Gravando usuário, algoritmo, iterações, salt e hash no SQLite...")
        try:
            with self.conexao:
                self.conexao.execute(
                    "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)",
                    (usuario, "pbkdf2-sha256", ITERACOES, salt, resumo),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Usuário já cadastrado.") from exc
        _etapa(acompanhar, "[7/7] Transação confirmada. A senha original não foi gravada.")

    def autenticar(self, usuario: str, senha: str, acompanhar=None) -> bool:
        _etapa(acompanhar, "[1/5] Validando os dados informados para o login...")
        if not 1 <= len(senha) <= MAX_SENHA:
            return False
        try:
            usuario = self.normalizar_usuario(usuario)
        except ValueError:
            usuario = ""  
        _etapa(acompanhar, "[2/5] Consultando o registro pelo usuário com SQL parametrizado...")
        registro = self.conexao.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()
        _etapa(acompanhar, "[3/5] Preparando salt e parâmetros; sem cadastro, usar registro fictício...")
        salt = self.salt_ficticio
        esperado = self.hash_ficticio
        if registro is not None:
            if (registro["algoritmo"] != "pbkdf2-sha256"
                    or registro["iteracoes"] != ITERACOES
                    or not isinstance(registro["salt"], bytes)
                    or not isinstance(registro["hash"], bytes)
                    or len(registro["salt"]) != TAMANHO_SALT
                    or len(registro["hash"]) != TAMANHO_HASH):
                return False
            salt, esperado = registro["salt"], registro["hash"]
        _etapa(acompanhar, f"[4/5] Derivando o candidato com PBKDF2-HMAC-SHA256 ({ITERACOES:,} iterações)...")
        candidato = derivar(senha, salt)
        _etapa(acompanhar, "[5/5] Comparando os valores de 32 bytes com hmac.compare_digest...")
        coincide = hmac.compare_digest(candidato, esperado)
        return coincide and registro is not None
