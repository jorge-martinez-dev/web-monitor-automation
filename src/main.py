from scraper import abrir_pagina, extraer_texto, leer_estado, guardar_estado
from monitor import detectar_cambio
from notifier import notificar_cambio
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