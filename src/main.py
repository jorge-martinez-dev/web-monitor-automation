import time

from playwright.sync_api import sync_playwright

from config import (
    MONITORES,
    INTERVALO_SEGUNDOS,
    MAX_REINTENTOS,
    ESPERA_REINTENTO,
)
from monitor import detectar_cambio
from notifier import notificar_cambio
from scraper import obtener_html, extraer_texto
from storage import guardar_estado, leer_estado


def revisar_monitor(pagina, configuracion):
    nombre = configuracion["nombre"]
    url = configuracion["url"]
    selector = configuracion["selector"]

    print(f"\nRevisando monitor: {nombre}")

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            html = obtener_html(pagina, url)
            valor_actual = extraer_texto(html, selector)

            if valor_actual is None:
                print(f"No se encontró el selector: {selector}")
                return

            valor_anterior = leer_estado(nombre)

            print("Valor actual:", valor_actual)
            print("Valor anterior:", valor_anterior)

            if detectar_cambio(valor_actual, valor_anterior):
                notificar_cambio(valor_anterior, valor_actual)
            else:
                print("No hubo cambios")

            guardar_estado(nombre, valor_actual)
            return

        except Exception as error:
            print(f"Intento {intento} de {MAX_REINTENTOS} falló:")
            print(error)

            if intento < MAX_REINTENTOS:
                print(
                    f"Reintentando en "
                    f"{ESPERA_REINTENTO} segundos..."
                )
                time.sleep(ESPERA_REINTENTO)
            else:
                print("No fue posible completar esta revisión.")


def ejecutar_monitores(pagina):
    for configuracion in MONITORES:
        revisar_monitor(pagina, configuracion)


def iniciar_aplicacion():
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=False)
        contexto = navegador.new_context()
        pagina = contexto.new_page()

        print("Monitor iniciado. Presiona Ctrl + C para detenerlo.")

        try:
            while True:
                ejecutar_monitores(pagina)

                print(
                    f"\nPróxima revisión en "
                    f"{INTERVALO_SEGUNDOS} segundos.\n"
                )

                time.sleep(INTERVALO_SEGUNDOS)

        except KeyboardInterrupt:
            print("\nMonitor detenido por el usuario.")

        finally:
            contexto.close()
            navegador.close()


if __name__ == "__main__":
    iniciar_aplicacion()