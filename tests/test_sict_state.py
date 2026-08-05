import sys
import unittest
from pathlib import Path
from unittest.mock import patch


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_SRC = RUTA_PROYECTO / "src"

sys.path.insert(0, str(RUTA_SRC))


from sict_state import (  # noqa: E402
    actualizar_estado_sict,
    crear_clave_estado,
    normalizar_fechas,
)


class TestSictState(unittest.TestCase):
    def test_crea_clave_independiente_por_sede(self):
        resultado = crear_clave_estado("U.M. BOMBAS")

        self.assertEqual(
            resultado,
            "sict_u_m_bombas",
        )

    def test_elimina_acentos_de_la_clave(self):
        resultado = crear_clave_estado("U.M. MÉRIDA")

        self.assertEqual(
            resultado,
            "sict_u_m_merida",
        )

    def test_normaliza_fechas(self):
        resultado = normalizar_fechas(
            [
                "2026-08-10",
                "2026-08-06",
                "2026-08-10",
                "fecha-invalida",
            ]
        )

        self.assertEqual(
            resultado,
            (
                "2026-08-06",
                "2026-08-10",
            ),
        )

    @patch("sict_state.guardar_estado")
    @patch(
        "sict_state.leer_estado",
        return_value="2026-08-06\n2026-08-07",
    )
    def test_detecta_solamente_fechas_nuevas(
        self,
        leer_estado_mock,
        guardar_estado_mock,
    ):
        resultado = actualizar_estado_sict(
            "U.M. BOMBAS",
            [
                "2026-08-06",
                "2026-08-07",
                "2026-08-10",
            ],
        )

        self.assertTrue(resultado.cambio_detectado)
        self.assertEqual(
            resultado.fechas_nuevas,
            ("2026-08-10",),
        )

        leer_estado_mock.assert_called_once_with(
            "sict_u_m_bombas"
        )

        guardar_estado_mock.assert_called_once_with(
            "sict_u_m_bombas",
            "2026-08-06\n2026-08-07\n2026-08-10",
        )

    @patch("sict_state.guardar_estado")
    @patch(
        "sict_state.leer_estado",
        return_value="2026-08-06\n2026-08-07",
    )
    def test_no_guarda_si_no_hay_cambios(
        self,
        leer_estado_mock,
        guardar_estado_mock,
    ):
        resultado = actualizar_estado_sict(
            "U.M. BOMBAS",
            [
                "2026-08-06",
                "2026-08-07",
            ],
        )

        self.assertFalse(resultado.cambio_detectado)
        self.assertEqual(resultado.fechas_nuevas, ())

        leer_estado_mock.assert_called_once_with(
            "sict_u_m_bombas"
        )

        guardar_estado_mock.assert_not_called()

    @patch("sict_state.guardar_estado")
    @patch(
        "sict_state.leer_estado",
        return_value="2026-08-06\n2026-08-07",
    )
    def test_actualiza_estado_si_desaparece_una_fecha(
        self,
        leer_estado_mock,
        guardar_estado_mock,
    ):
        resultado = actualizar_estado_sict(
            "U.M. BOMBAS",
            ["2026-08-06"],
        )

        self.assertTrue(resultado.cambio_detectado)
        self.assertEqual(resultado.fechas_nuevas, ())

        leer_estado_mock.assert_called_once_with(
            "sict_u_m_bombas"
        )

        guardar_estado_mock.assert_called_once_with(
            "sict_u_m_bombas",
            "2026-08-06",
        )


if __name__ == "__main__":
    unittest.main()