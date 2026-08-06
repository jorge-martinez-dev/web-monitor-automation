from collections.abc import Iterable

from notifier import notificar_fechas_sict
from sict_state import (
    analizar_estado_sict,
    confirmar_estado_sict,
)


def procesar_disponibilidad_sict(
    sede: str,
    url: str,
    fechas: Iterable[str],
) -> bool:
    try:
        resultado_estado = analizar_estado_sict(
            sede,
            fechas,
        )
    except (OSError, ValueError) as error:
        print("No fue posible analizar el estado de la sede:")
        print(error)
        return False

    print("Estado:", resultado_estado.clave_estado)

    if not resultado_estado.cambio_detectado:
        if not resultado_estado.fechas_actuales:
            print("SICT: no hay fechas disponibles.")
        else:
            print("SICT: disponibilidad sin cambios.")

        return True

    if not resultado_estado.fechas_nuevas:
        try:
            confirmar_estado_sict(resultado_estado)
        except OSError as error:
            print("No fue posible guardar el estado de la sede:")
            print(error)
            return False

        if not resultado_estado.fechas_actuales:
            print("SICT: no hay fechas disponibles.")
        else:
            print("SICT: disponibilidad actualizada.")
            print("No aparecieron fechas nuevas.")

        return True

    print("SICT: fechas nuevas detectadas:")

    for fecha in resultado_estado.fechas_nuevas:
        print(f"- {fecha}")

    alerta_enviada = notificar_fechas_sict(
        sede,
        url,
        resultado_estado.fechas_nuevas,
    )

    if not alerta_enviada:
        print(
            "SICT: alerta pendiente; el estado no fue "
            "confirmado."
        )
        return False

    try:
        confirmar_estado_sict(resultado_estado)
    except OSError as error:
        print(
            "Telegram fue enviado, pero no se pudo guardar "
            "el estado:"
        )
        print(error)
        return False

    print("SICT: alerta enviada y estado confirmado.")
    return True