import json
import sys
import unittest
from datetime import date
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_SRC = RUTA_PROYECTO / "src"

sys.path.insert(0, str(RUTA_SRC))

from sict_adapter import (
    extraer_fechas_candidatas,
    extraer_fechas_disponibles,
    filtrar_fechas_disponibles,
)


class TestSictAdapter(unittest.TestCase):
    def setUp(self):
        self.fechas_candidatas = [
            "2026-08-03",
            "2026-08-06",
            "2026-08-07",
            "2026-08-08",
            "2026-08-09",
            "2026-08-10",
        ]

        snapshot = {
            "data": {
                "disabledDaysFilter": [
                    self.fechas_candidatas,
                    {"s": "arr"},
                ]
            }
        }

        self.respuesta_livewire = json.dumps(
            {
                "components": [
                    {
                        "snapshot": json.dumps(
                            snapshot
                        )
                    }
                ]
            }
        )

    def test_extrae_fechas_del_snapshot(self):
        resultado = extraer_fechas_candidatas(
            self.respuesta_livewire
        )

        self.assertEqual(
            resultado,
            self.fechas_candidatas,
        )

    def test_descarta_fechas_pasadas_y_fines_de_semana(self):
        resultado = filtrar_fechas_disponibles(
            self.fechas_candidatas,
            fecha_minima=date(2026, 8, 5),
        )

        self.assertEqual(
            resultado,
            [
                "2026-08-06",
                "2026-08-07",
                "2026-08-10",
            ],
        )

    def test_proceso_completo(self):
        resultado = extraer_fechas_disponibles(
            self.respuesta_livewire,
            fecha_minima=date(2026, 8, 5),
        )

        self.assertEqual(
            resultado,
            [
                "2026-08-06",
                "2026-08-07",
                "2026-08-10",
            ],
        )

    def test_rechaza_respuesta_invalida(self):
        with self.assertRaises(ValueError):
            extraer_fechas_candidatas(
                {"respuesta": "incorrecta"}
            )


if __name__ == "__main__":
    unittest.main()