"""AC6 (sesión de recuperación 2026-10-07): el bloque CONTACTO no publica el teléfono del hotel.

Hallazgo V-5 de FASE-VERIFY: `propuesta_v6_template.md:253` llevaba
`WhatsApp: ${hotel_phone}`, y `hotel_phone` se alimentaba con
`audit_result.gbp.phone` — el teléfono del HOTEL, en el bloque de contacto de
IA Hoteles. La propuesta del 2026-10-07 lo imprimió como canal de la agencia
misma.

Configuración medida: `config/` no tiene número de la agencia (ninguna clave de
`config/*.yaml` declara contacto propio), así que el mandato aplica la segunda
rama: se retira la línea `WhatsApp:` y se conserva el email.
"""

import re
from pathlib import Path

import pytest

from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

PLANTILLA = (
    Path(__file__).resolve().parents[2]
    / "modules" / "commercial_documents" / "templates" / "propuesta_v6_template.md"
)

TELEFONO_HOTEL_GBP = "(606) 3146139"
EMAIL_AGENCIA = "contacto@iahoteles.co"


@pytest.fixture
def generador():
    return V4ProposalGenerator()


def bloque_contacto(renderizado: str) -> str:
    """El bloque CONTACTO recortado por su propio título, no por adyacencia."""
    match = re.search(r"^##\s.*CONTACTO\s*$", renderizado, re.MULTILINE)
    assert match is not None, "la propuesta debe conservar su bloque CONTACTO"
    resto = renderizado[match.end():]
    siguiente = re.search(r"^##\s", resto, re.MULTILINE)
    return resto[:siguiente.start()] if siguiente else resto


def _render(generador, contexto):
    return generador._render_template(PLANTILLA.read_text(encoding="utf-8"), contexto)


def test_bloque_contacto_no_emite_whatsapp_del_hotel(generador):
    """Con el mismo contexto que produjo la propuesta del 2026-10-07: 0 `WhatsApp:`."""
    contexto = {"hotel_phone": TELEFONO_HOTEL_GBP, "hotel_name": "Hotel Don Alfonso"}

    contacto = bloque_contacto(_render(generador, contexto))

    assert "WhatsApp:" not in contacto
    assert TELEFONO_HOTEL_GBP not in contacto
    assert "6063146139" not in contacto


def test_bloque_contacto_conserva_el_email(generador):
    """Retirar el canal no retira el contacto: el email de la agencia sigue."""
    contacto = bloque_contacto(_render(generador, {"hotel_name": "Hotel Don Alfonso"}))

    assert EMAIL_AGENCIA in contacto
    assert "IA Hoteles Agent" in contacto


def test_plantilla_no_declara_el_placeholder(generador):
    """La plantilla no puede volver a publicar el teléfono: el placeholder se fue."""
    crudo = PLANTILLA.read_text(encoding="utf-8")

    assert "${hotel_phone}" not in crudo
    assert not re.search(r"^WhatsApp:", crudo, re.MULTILINE)


def test_el_contexto_ya_no_extrae_el_telefono(generador):
    """PATCH-6 se retiro con su unico lector: el generador no extrae gbp.phone para el contacto.

    Se verifica por fuente porque el dato muerto es la otra mitad del defecto:
    una clave de contexto sin lector caduca y alguien la re-conecta.
    """
    import inspect

    fuente = inspect.getsource(generador.__class__)

    assert "hotel_phone" not in fuente
