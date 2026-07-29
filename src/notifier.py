import os
from pathlib import Path

import requests
from dotenv import load_dotenv


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_ENV = RUTA_PROYECTO / ".env"

load_dotenv(RUTA_ENV)


def notificar_cambio(valor_anterior, valor_actual):
    print("Cambio detectado")
    print("Valor anterior:", valor_anterior)
    print("Valor actual:", valor_actual)

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("No se configuraron las variables de Telegram.")
        print(f"Archivo buscado: {RUTA_ENV}")
        return

    mensaje = (
        "🚨 Cambio detectado por el monitor\n\n"
        f"Valor anterior: {valor_anterior or '(vacío)'}\n"
        f"Valor actual: {valor_actual}"
    )

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

    except requests.RequestException as error:
        print("No se pudo enviar la notificación a Telegram:")
        print(error)