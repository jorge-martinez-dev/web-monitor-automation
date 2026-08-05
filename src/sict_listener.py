import msvcrt
from datetime import date

from playwright.sync_api import (
    Error as PlaywrightError,
    Page,
    Response,
    sync_playwright,
)

from sict_adapter import extraer_fechas_disponibles
from sict_session import CDP_URL, buscar_pagina_sict


RUTA_LIVEWIRE = "/livewire/update"
ERROR_RESPUESTA_EXPIRADA = "No resource with given identifier found"
ERROR_NAVEGADOR_CERRADO = (
    "Target page, context or browser has been closed"
)


def obtener_sede_seleccionada(pagina: Page) -> str | None:
    sede = pagina.evaluate(
        """
        () => {
            const selects = Array.from(
                document.querySelectorAll("select")
            );

            const obtenerOpcion = (select) =>
                select.options[select.selectedIndex] || null;

            const selectSede = selects.find((select) =>
                Array.from(select.attributes).some((atributo) =>
                    `${atributo.name} ${atributo.value}`
                        .toLowerCase()
                        .includes("headquarter")
                )
            );

            const opcionSede = selectSede
                ? obtenerOpcion(selectSede)
                : null;

            if (opcionSede?.textContent?.trim()) {
                return opcionSede.textContent.trim();
            }

            const opcionUnidad = selects
                .map(obtenerOpcion)
                .find((opcion) =>
                    opcion?.textContent
                        ?.trim()
                        .toUpperCase()
                        .startsWith("U.M.")
                );

            return opcionUnidad?.textContent?.trim() || null;
        }
        """
    )

    if not isinstance(sede, str):
        return None

    sede_limpia = " ".join(sede.split())
    return sede_limpia or None


def escuchar_disponibilidad() -> None:
    ultimo_resultado: tuple[str, ...] | None = None

    def manejar_respuesta(respuesta: Response) -> None:
        nonlocal ultimo_resultado

        if RUTA_LIVEWIRE not in respuesta.url:
            return

        if not respuesta.ok:
            print(f"Livewire respondió con HTTP {respuesta.status}.")
            return

        try:
            fechas = extraer_fechas_disponibles(
                respuesta.text(),
                fecha_minima=date.today(),
            )

        except ValueError:
            # No todas las respuestas Livewire contienen el calendario.
            return

        except PlaywrightError as error:
            mensaje_error = str(error)

            errores_ignorables = (
                ERROR_RESPUESTA_EXPIRADA,
                ERROR_NAVEGADOR_CERRADO,
            )

            if not any(
                texto in mensaje_error
                for texto in errores_ignorables
            ):
                print(
                    "No se pudo leer una respuesta Livewire: "
                    f"{error}"
                )

            return

        resultado_actual = tuple(fechas)

        if resultado_actual == ultimo_resultado:
            return

        ultimo_resultado = resultado_actual

        try:
            sede = obtener_sede_seleccionada(pagina)
        except PlaywrightError:
            sede = None

        print()
        print("Sede detectada:", sede or "(no identificada)")

        if not fechas:
            print("SICT: no hay fechas disponibles.")
            return

        print("SICT: fechas disponibles detectadas:")

        for fecha in fechas:
            print(f"- {fecha}")

    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.connect_over_cdp(
                CDP_URL,
                timeout=10_000,
            )

            pagina = buscar_pagina_sict(navegador)

            if pagina is None:
                print(
                    "Chrome está conectado, pero no se encontró "
                    "una pestaña de la SICT."
                )
                return

            pagina.on("response", manejar_respuesta)

            print("Escucha de solo lectura iniciada.")
            print("Realiza manualmente una consulta de sede en Chrome.")
            print("Presiona Q para detener el programa.")

            while True:
                pagina.wait_for_timeout(500)

                if not msvcrt.kbhit():
                    continue

                tecla = msvcrt.getwch().lower()

                if tecla == "q":
                    break

            try:
                pagina.remove_listener(
                    "response",
                    manejar_respuesta,
                )
                pagina.wait_for_timeout(250)
            except (PlaywrightError, RuntimeError):
                pass

            print("\nEscucha detenida.")

    except PlaywrightError as error:
        if ERROR_NAVEGADOR_CERRADO in str(error):
            print("\nChrome fue cerrado. Escucha finalizada.")
            return

        print("No fue posible mantener la conexión con Chrome:")
        print(error)


if __name__ == "__main__":
    escuchar_disponibilidad()