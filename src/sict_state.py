import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from storage import guardar_estado, leer_estado


@dataclass(frozen=True)
class ResultadoEstadoSict:
    clave_estado: str
    fechas_anteriores: tuple[str, ...]
    fechas_actuales: tuple[str, ...]
    fechas_nuevas: tuple[str, ...]
    cambio_detectado: bool


def normalizar_nombre_sede(sede: str) -> str:
    if not isinstance(sede, str) or not sede.strip():
        raise ValueError("La sede no puede estar vacía.")

    texto_normalizado = unicodedata.normalize(
        "NFKD",
        sede.strip(),
    )

    texto_sin_acentos = "".join(
        caracter
        for caracter in texto_normalizado
        if not unicodedata.combining(caracter)
    )

    nombre_normalizado = re.sub(
        r"[^a-z0-9]+",
        "_",
        texto_sin_acentos.lower(),
    ).strip("_")

    if not nombre_normalizado:
        raise ValueError("No fue posible normalizar la sede.")

    return nombre_normalizado


def crear_clave_estado(sede: str) -> str:
    nombre_normalizado = normalizar_nombre_sede(sede)
    return f"sict_{nombre_normalizado}"


def normalizar_fechas(
    fechas: Iterable[str],
) -> tuple[str, ...]:
    fechas_validas = set()

    for valor in fechas:
        if not isinstance(valor, str):
            continue

        try:
            fecha = date.fromisoformat(valor.strip())
        except ValueError:
            continue

        fechas_validas.add(fecha.isoformat())

    return tuple(sorted(fechas_validas))


def serializar_fechas(fechas: Iterable[str]) -> str:
    fechas_normalizadas = normalizar_fechas(fechas)
    return "\n".join(fechas_normalizadas)


def deserializar_fechas(valor: str) -> tuple[str, ...]:
    return normalizar_fechas(valor.splitlines())


def actualizar_estado_sict(
    sede: str,
    fechas: Iterable[str],
) -> ResultadoEstadoSict:
    clave_estado = crear_clave_estado(sede)

    fechas_actuales = normalizar_fechas(fechas)
    valor_anterior = leer_estado(clave_estado)
    fechas_anteriores = deserializar_fechas(valor_anterior)

    conjunto_anterior = set(fechas_anteriores)

    fechas_nuevas = tuple(
        fecha
        for fecha in fechas_actuales
        if fecha not in conjunto_anterior
    )

    cambio_detectado = fechas_actuales != fechas_anteriores

    if cambio_detectado:
        guardar_estado(
            clave_estado,
            serializar_fechas(fechas_actuales),
        )

    return ResultadoEstadoSict(
        clave_estado=clave_estado,
        fechas_anteriores=fechas_anteriores,
        fechas_actuales=fechas_actuales,
        fechas_nuevas=fechas_nuevas,
        cambio_detectado=cambio_detectado,
    )