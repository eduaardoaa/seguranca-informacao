"""Entrada com asteriscos no console Windows, sem dependências externas."""

from getpass import getpass
import os
import sys


def _teclas_windows():
    import ctypes
    from ctypes import wintypes

    class Tecla(ctypes.Structure):
        _fields_ = [("pressionada", wintypes.BOOL), ("repeticoes", wintypes.WORD),
                    ("virtual", wintypes.WORD), ("scan", wintypes.WORD),
                    ("caractere", wintypes.WCHAR), ("controle", wintypes.DWORD)]

    class Evento(ctypes.Union):
        _fields_ = [("tecla", Tecla), ("reserva", ctypes.c_byte * 16)]

    class Registro(ctypes.Structure):
        _fields_ = [("tipo", wintypes.WORD), ("evento", Evento)]

    console = ctypes.WinDLL("kernel32", use_last_error=True)
    console.GetStdHandle.argtypes = [wintypes.DWORD]
    console.GetStdHandle.restype = wintypes.HANDLE
    console.ReadConsoleInputW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Registro),
                                        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    console.ReadConsoleInputW.restype = wintypes.BOOL
    entrada = console.GetStdHandle(-10)
    registro, quantidade = Registro(), wintypes.DWORD()
    primeira = ""
    while True:
        if not console.ReadConsoleInputW(entrada, ctypes.byref(registro), 1,
                                         ctypes.byref(quantidade)):
            raise ctypes.WinError(ctypes.get_last_error())
        if registro.tipo != 1 or not registro.evento.tecla.pressionada:
            continue
        tecla = registro.evento.tecla
        caractere = tecla.caractere
        if caractere == "\x00":
            continue
        for _ in range(tecla.repeticoes):
            if "\ud800" <= caractere <= "\udbff":
                primeira = caractere
                continue
            if primeira and "\udc00" <= caractere <= "\udfff":
                caractere = (primeira + caractere).encode(
                    "utf-16-le", "surrogatepass"
                ).decode("utf-16-le")
            primeira = ""
            yield caractere


def ler_senha(mensagem: str) -> str:
    if os.name != "nt" or not sys.stdin.isatty() or not sys.stdout.isatty():
        return getpass(mensagem)

    caracteres = []
    print(mensagem, end="", flush=True)
    try:
        for tecla in _teclas_windows():
            if tecla in ("\r", "\n"):
                return "".join(caracteres)
            if tecla == "\x03":
                raise KeyboardInterrupt
            if tecla in ("\x04", "\x1a"):
                raise EOFError
            if tecla in ("\b", "\x7f"):
                if caracteres:
                    caracteres.pop()
                    print("\b \b", end="", flush=True)
            elif tecla and tecla.isprintable():
                caracteres.append(tecla)
                print("*", end="", flush=True)
    finally:
        print(flush=True)
