import sys
import unittest
from pathlib import Path
from unittest.mock import patch


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_SRC = RUTA_PROYECTO / "src"

sys.path.insert(0, str(RUTA_SRC))


from notifier import (  # noqa: E402
    crear_mensaje_cambio,
    crear_mensaje_fechas_sict,
    enviar_mensaje_telegram,
    notificar_fechas_sict,
)


class TestNotifier(unittest.TestCase):
    def test_crea_mensaje_de_cambio(self):
        mensaje = crear_mensaje_cambio(
            "Monitor de prueba",
            "https://example.com",
            "",
            "Valor nuevo",
        )

        self.assertIn(
            "Monitor: Monitor de prueba",
            mensaje,
        )
        self.assertIn(
            "URL: https://example.com",
            mensaje,
        )
        self.assertIn(
            "Valor anterior: (vacío)",
            mensaje,
        )
        self.assertIn(
            "Valor actual: Valor nuevo",
            mensaje,
        )

    def test_crea_mensaje_de_fechas_sict(self):
        mensaje = crear_mensaje_fechas_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            [
                "2026-08-06",
                "2026-08-07",
            ],
        )

        self.assertIn(
            "Sede: U.M. BOMBAS",
            mensaje,
        )
        self.assertIn(
            "• 2026-08-06",
            mensaje,
        )
        self.assertIn(
            "• 2026-08-07",
            mensaje,
        )
        self.assertIn(
            "https://citas.sct.gob.mx/",
            mensaje,
        )

    @patch("notifier.enviar_mensaje_telegram")
    def test_no_notifica_si_no_hay_fechas(
        self,
        enviar_mensaje_mock,
    ):
        resultado = notificar_fechas_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            [],
        )

        self.assertFalse(resultado)
        enviar_mensaje_mock.assert_not_called()

    @patch(
        "notifier.enviar_mensaje_telegram",
        return_value=True,
    )
    def test_notifica_fechas_nuevas(
        self,
        enviar_mensaje_mock,
    ):
        resultado = notificar_fechas_sict(
            "U.M. BOMBAS",
            "https://citas.sct.gob.mx/",
            ["2026-08-06"],
        )

        self.assertTrue(resultado)
        enviar_mensaje_mock.assert_called_once()

        mensaje = enviar_mensaje_mock.call_args.args[0]

        self.assertIn(
            "Sede: U.M. BOMBAS",
            mensaje,
        )
        self.assertIn(
            "• 2026-08-06",
            mensaje,
        )

    @patch("notifier.requests.post")
    @patch("notifier.os.getenv")
    def test_envia_mensaje_a_telegram(
        self,
        getenv_mock,
        post_mock,
    ):
        variables = {
            "TELEGRAM_BOT_TOKEN": "token-prueba",
            "TELEGRAM_CHAT_ID": "123456",
        }

        getenv_mock.side_effect = variables.get

        resultado = enviar_mensaje_telegram(
            "Mensaje de prueba"
        )

        self.assertTrue(resultado)

        post_mock.assert_called_once_with(
            (
                "https://api.telegram.org/"
                "bottoken-prueba/sendMessage"
            ),
            data={
                "chat_id": "123456",
                "text": "Mensaje de prueba",
            },
            timeout=15,
        )

        post_mock.return_value.raise_for_status.assert_called_once()

    @patch("notifier.requests.post")
    @patch(
        "notifier.os.getenv",
        return_value=None,
    )
    def test_no_envia_sin_variables(
        self,
        getenv_mock,
        post_mock,
    ):
        resultado = enviar_mensaje_telegram(
            "Mensaje de prueba"
        )

        self.assertFalse(resultado)
        self.assertGreaterEqual(
            getenv_mock.call_count,
            1,
        )
        post_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()