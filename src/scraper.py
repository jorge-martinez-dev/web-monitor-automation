from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def abrir_pagina(url):
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=False)
        pagina = navegador.new_page()
        pagina.goto(url)

        html = pagina.content()

        pagina.wait_for_timeout(5000)
        navegador.close()

        return html


def extraer_texto_principal(html):
    sopa = BeautifulSoup(html, "html.parser")
    elemento = sopa.find("h1")

    if elemento is None:
        return None

    return elemento.get_text(strip=True)


contenido = abrir_pagina("https://example.com")
texto_principal = extraer_texto_principal(contenido)

print(texto_principal)