from bs4 import BeautifulSoup


def obtener_html(pagina, url):
    pagina.goto(url, wait_until="load")
    return pagina.content()


def extraer_texto(html, selector):
    sopa = BeautifulSoup(html, "html.parser")
    elemento = sopa.select_one(selector)

    if elemento is None:
        return None

    return elemento.get_text(strip=True)
