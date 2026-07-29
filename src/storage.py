from pathlib import Path


CARPETA_ESTADOS = Path("data")


def obtener_ruta_estado(nombre):
    CARPETA_ESTADOS.mkdir(exist_ok=True)
    return CARPETA_ESTADOS / f"{nombre}.txt"


def guardar_estado(nombre, valor):
    ruta = obtener_ruta_estado(nombre)
    ruta.write_text(valor, encoding="utf-8")


def leer_estado(nombre):
    ruta = obtener_ruta_estado(nombre)

    if not ruta.exists():
        return ""

    return ruta.read_text(encoding="utf-8")