import time

from scraper import abrir_pagina, extraer_texto, leer_estado, guardar_estado
from monitor import detectar_cambio
from notifier import notificar_cambio
from config import (
    URL,
    SELECTOR,
    INTERVALO_SEGUNDOS,
    MAX_REINTENTOS,
    ESPERA_REINTENTO,
)


def ejecutar_monitor():
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            contenido = abrir_pagina(URL)
            valor_actual = extraer_texto(contenido, SELECTOR)

            if valor_actual is None:
                print(f"No se encontró el selector: {SELECTOR}")
                return

            valor_anterior = leer_estado()

            print("Valor actual:", valor_actual)
            print("Valor anterior:", valor_anterior)

            if detectar_cambio(valor_actual, valor_anterior):
                notificar_cambio(valor_anterior, valor_actual)
            else:
                print("No hubo cambios")

            guardar_estado(valor_actual)
            return

        except Exception as error:
            print(f"Intento {intento} de {MAX_REINTENTOS} falló:")
            print(error)

            if intento < MAX_REINTENTOS:
                print(f"Reintentando en {ESPERA_REINTENTO} segundos...")
                time.sleep(ESPERA_REINTENTO)
            else:
                print("No fue posible completar la revisión.")


if __name__ == "__main__":
    print("Monitor iniciado. Presiona Ctrl + C para detenerlo.")

    try:
        while True:
            ejecutar_monitor()

            print(
                f"Próxima revisión en "
                f"{INTERVALO_SEGUNDOS} segundos.\n"
            )

            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nMonitor detenido por el usuario.")