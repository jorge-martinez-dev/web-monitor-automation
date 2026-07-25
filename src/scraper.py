from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from monitor import detectar_cambio
from notifier import notificar_cambio
def abrir_pagina(url):
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=False)
        pagina = navegador.new_page()
        pagina.goto(url)

        html = pagina.content()

        pagina.wait_for_timeout(5000)
        navegador.close()

        return html


def extraer_texto(html, selector):
    sopa = BeautifulSoup(html, "html.parser")
    elemento = sopa.select_one(selector)

    if elemento is None:
        return None

    return elemento.get_text(strip=True)

def guardar_estado(valor):
    with open("estado.txt", "w", encoding="utf-8") as archivo:
        archivo.write(valor)

def leer_estado():
    try:
        with open("estado.txt", "r", encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return "" 

contenido = abrir_pagina("https://example.com")

titulo = extraer_texto(contenido, "h1")
parrafo = extraer_texto(contenido, "p")
enlace = extraer_texto(contenido, "a")

print("Título:", titulo)
print("Párrafo:", parrafo)
print("Enlace:", enlace)
estado_anterior = leer_estado()
print("Estado anterior:", estado_anterior)
if detectar_cambio(titulo, estado_anterior):
    notificar_cambio(estado_anterior, titulo)
else:
    print("No hubo cambios")

guardar_estado(titulo)