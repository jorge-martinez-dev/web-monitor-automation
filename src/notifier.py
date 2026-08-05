import os
from collections.abc import Iterable
from pathlib import Path

import requests
from dotenv import load_dotenv


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_ENV = RUTA_PROYECTO / ".env"

load_dotenv(RUTA_ENV)


def enviar_mensaje_telegram(mensaje: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("No se configuraron las variables de Telegram.")
        return False

    try:
        respuesta = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": mensaje,
            },
            timeout=15,
        )

        respuesta.raise_for_status()
        print("Notificación enviada a Telegram.")
        return True

    except requests.RequestException as error:
        print("No se pudo enviar la notificación a Telegram:")
        print(error)
        return False


def crear_mensaje_cambio(
    nombre: str,
    url: str,
    valor_anterior: str,
    valor_actual: str,
) -> str:
    return (
        "🚨 Cambio detectado por el monitor\n\n"
        f"Monitor: {nombre}\n"
        f"URL: {url}\n\n"
        f"Valor anterior: {valor_anterior or '(vacío)'}\n"
        f"Valor actual: {valor_actual}"
    )


def crear_mensaje_fechas_sict(
    sede: str,
    url: str,
    fechas_nuevas: Iterable[str],
) -> str:
    fechas_limpias = []

    for fecha in fechas_nuevas:
        if not isinstance(fecha, str):
            continue

        fecha_limpia = fecha.strip()

        if (
            fecha_limpia
            and fecha_limpia not in fechas_limpias
        ):
            fechas_limpias.append(fecha_limpia)

    if not fechas_limpias:
        raise ValueError(
            "Se necesita al menos una fecha nueva."
        )

    lista_fechas = "\n".join(
        f"• {fecha}"
        for fecha in fechas_limpias
    )

    return (
        "📅 Nuevas fechas disponibles en la SICT\n\n"
        f"Sede: {sede}\n\n"
        f"Fechas nuevas:\n{lista_fechas}\n\n"
        f"Consulta manual:\n{url}"
    )


def notificar_cambio(
    nombre: str,
    url: str,
    valor_anterior: str,
    valor_actual: str,
) -> bool:
    print("Cambio detectado")
    print("Monitor:", nombre)
    print("URL:", url)
    print("Valor anterior:", valor_anterior)
    print("Valor actual:", valor_actual)

    mensaje = crear_mensaje_cambio(
        nombre,
        url,
        valor_anterior,
        valor_actual,
    )

    return enviar_mensaje_telegram(mensaje)


def notificar_fechas_sict(
    sede: str,
    url: str,
    fechas_nuevas: Iterable[str],
) -> bool:
    try:
        mensaje = crear_mensaje_fechas_sict(
            sede,
            url,
            fechas_nuevas,
        )
    except ValueError as error:
        print("No se envió la alerta de la SICT:")
        print(error)
        return False

    print("Nuevas fechas de la SICT detectadas.")
    print("Sede:", sede)

    return enviar_mensaje_telegram(mensaje)