import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_SRC = RUTA_PROYECTO / "src"

sys.path.insert(0, str(RUTA_SRC))


from sict_processor import (  # noqa: E402
    procesar_disponibilidad_sict,
)
from sict_state import ResultadoEstadoSict  # noqa: E402


class TestSictProcessor(unittest.TestCase):
    def crear_resultado(
        self,
        *,
        fechas_anteriores=("2026-08-06",),
        fechas_actuales=("2026-08-06", "2026-08-10"),
        fechas_nuevas=("2026-08-10",),
        cambio_detectado=True,
    ):
        return ResultadoEstadoSict(
            clave_estado="sict_u_m_bombas",
            fechas_anteriores=fechas_anteriores,
            fechas_actuales=fechas_actuales,
            fechas_nuevas=fechas_nuevas,
            cambio_detectado=cambio_detectado,
        )

    @patch("sict_processor.confirmar_estado_sict")
    @patch(
        "sict_processor.notificar_fechas_sict",
        return_value=True,
    )
    @patch("sict_processor.analizar_estado_sict")
    def test_notifica_antes_de_confirmar_el_estado(
        self,
        analizar_mock,
        notificar_mock,
        confirmar_mock,
    ):
        resultado_estado = self.crear_resultado()
        analizar_mock.return_value = resultado_estado

        eventos = Mock()
        eventos.attach_mock(notificar_mock, "notificar")
        eventos.attach_mock(confirmar_mock, "confirmar")

        procesado = procesar_disponibilidad_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            ["2026-08-06", "2026-08-10"],
        )

        self.assertTrue(procesado)
        self.assertEqual(
            eventos.mock_calls,
            [
                call.notificar(
                    "U.M. BOMBAS",
                    "https://citas.sct.gob.mx/",
                    ("2026-08-10",),
                ),
                call.confirmar(resultado_estado),
            ],
        )

    @patch("sict_processor.confirmar_estado_sict")
    @patch(
        "sict_processor.notificar_fechas_sict",
        return_value=False,
    )
    @patch("sict_processor.analizar_estado_sict")
    def test_no_confirma_si_telegram_falla(
        self,
        analizar_mock,
        notificar_mock,
        confirmar_mock,
    ):
        analizar_mock.return_value = self.crear_resultado()

        procesado = procesar_disponibilidad_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            ["2026-08-06", "2026-08-10"],
        )

        self.assertFalse(procesado)
        notificar_mock.assert_called_once()
        confirmar_mock.assert_not_called()

    @patch("sict_processor.confirmar_estado_sict")
    @patch("sict_processor.notificar_fechas_sict")
    @patch("sict_processor.analizar_estado_sict")
    def test_confirma_cambios_sin_fechas_nuevas(
        self,
        analizar_mock,
        notificar_mock,
        confirmar_mock,
    ):
        resultado_estado = self.crear_resultado(
            fechas_actuales=("2026-08-06",),
            fechas_nuevas=(),
        )
        analizar_mock.return_value = resultado_estado

        procesado = procesar_disponibilidad_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            ["2026-08-06"],
        )

        self.assertTrue(procesado)
        notificar_mock.assert_not_called()
        confirmar_mock.assert_called_once_with(resultado_estado)

    @patch("sict_processor.confirmar_estado_sict")
    @patch("sict_processor.notificar_fechas_sict")
    @patch("sict_processor.analizar_estado_sict")
    def test_no_notifica_ni_confirma_sin_cambios(
        self,
        analizar_mock,
        notificar_mock,
        confirmar_mock,
    ):
        analizar_mock.return_value = self.crear_resultado(
            fechas_actuales=("2026-08-06",),
            fechas_nuevas=(),
            cambio_detectado=False,
        )

        procesado = procesar_disponibilidad_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            ["2026-08-06"],
        )

        self.assertTrue(procesado)
        notificar_mock.assert_not_called()
        confirmar_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()