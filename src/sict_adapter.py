import json
from datetime import date
from typing import Any


CLAVE_FECHAS = "disabledDaysFilter"


def convertir_a_diccionario(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return valor

    if isinstance(valor, str):
        try:
            contenido = json.loads(valor)
        except json.JSONDecodeError as error:
            raise ValueError(
                "El contenido recibido no es un JSON válido."
            ) from error

        if isinstance(contenido, dict):
            return contenido

    raise ValueError(
        "El contenido recibido no tiene formato de diccionario."
    )


def extraer_lista_livewire(valor: Any) -> list[str]:
    if not isinstance(valor, list):
        raise ValueError(
            "disabledDaysFilter no contiene una lista."
        )

    if valor and isinstance(valor[0], list):
        elementos = valor[0]
    else:
        elementos = valor

    fechas = []

    for elemento in elementos:
        if not isinstance(elemento, str):
            continue

        try:
            fecha = date.fromisoformat(elemento)
        except ValueError:
            continue

        fechas.append(fecha.isoformat())

    return sorted(set(fechas))


def extraer_fechas_candidatas(
    respuesta_livewire: str | dict[str, Any],
) -> list[str]:
    respuesta = convertir_a_diccionario(
        respuesta_livewire
    )

    componentes = respuesta.get("components")

    if not isinstance(componentes, list):
        raise ValueError(
            "La respuesta no contiene componentes Livewire."
        )

    for componente in componentes:
        if not isinstance(componente, dict):
            continue

        snapshot_original = componente.get("snapshot")

        if snapshot_original is None:
            continue

        try:
            snapshot = convertir_a_diccionario(
                snapshot_original
            )
        except ValueError:
            continue

        datos = snapshot.get("data")

        if not isinstance(datos, dict):
            continue

        if CLAVE_FECHAS not in datos:
            continue

        return extraer_lista_livewire(
            datos[CLAVE_FECHAS]
        )

    raise ValueError(
        "No se encontró disabledDaysFilter "
        "en la respuesta Livewire."
    )


def filtrar_fechas_disponibles(
    fechas_candidatas: list[str],
    fecha_minima: date | None = None,
) -> list[str]:
    limite = fecha_minima or date.today()
    fechas_disponibles = set()

    for texto_fecha in fechas_candidatas:
        try:
            fecha = date.fromisoformat(texto_fecha)
        except ValueError:
            continue

        if fecha < limite:
            continue

        if fecha.weekday() >= 5:
            continue

        fechas_disponibles.add(fecha.isoformat())

    return sorted(fechas_disponibles)


def extraer_fechas_disponibles(
    respuesta_livewire: str | dict[str, Any],
    fecha_minima: date | None = None,
) -> list[str]:
    fechas_candidatas = extraer_fechas_candidatas(
        respuesta_livewire
    )

    return filtrar_fechas_disponibles(
        fechas_candidatas,
        fecha_minima,
    )