from playwright.sync_api import (
    Browser,
    Error as PlaywrightError,
    Page,
    sync_playwright,
)


CDP_URL = "http://127.0.0.1:9222"
DOMINIO_SICT = "citas.sct.gob.mx"


def buscar_pagina_sict(
    navegador: Browser,
) -> Page | None:
    for contexto in navegador.contexts:
        for pagina in contexto.pages:
            if DOMINIO_SICT in pagina.url:
                return pagina

    return None


def verificar_sesion_manual() -> bool:
    try:
        with sync_playwright() as playwright:
            navegador = (
                playwright.chromium.connect_over_cdp(
                    CDP_URL,
                    timeout=10_000,
                )
            )

            pagina = buscar_pagina_sict(navegador)

            if pagina is None:
                print(
                    "Chrome está conectado, pero no se "
                    "encontró una pestaña de la SICT."
                )
                return False

            titulo = pagina.title()
            url = pagina.url

            print("Conexión de solo lectura establecida.")
            print("Título:", titulo)
            print("URL:", url)

            if "/login" in url:
                print(
                    "La pestaña existe, pero la sesión "
                    "todavía no está iniciada."
                )
                return False

            print(
                "Sesión manual de la SICT detectada "
                "correctamente."
            )
            return True

    except PlaywrightError as error:
        print("No fue posible conectar con Chrome:")
        print(error)
        return False


if __name__ == "__main__":
    verificar_sesion_manual()