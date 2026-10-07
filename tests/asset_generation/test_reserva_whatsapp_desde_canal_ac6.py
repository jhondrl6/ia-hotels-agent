"""AC6 (sesión de recuperación 2026-10-07): el destino `wa.me` sale del canal, no del teléfono.

La certificación de FASE-VERIFY dejó AC6 en FALLA (hallazgo V-1): el paquete
publicado del 2026-10-07 emitía `https://wa.me/6063146139` en 5 líneas de
`ASSETS/local_content_page/contenido_local__20261007_093402.md`, y ese número
era `gbp.phone` — `(606) 3146139` — con `validation.phone_web=null`,
`whatsapp_status='estimated'` y presencia `plugin_fingerprint` sin href. Es
decir: un teléfono de OTRO canal viajaba como destino de WhatsApp.

Estos tests corren offline sobre las mismas entradas medidas en esa corrida.
"""

import pytest

from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.local_content_generator import LocalContentGenerator
from modules.data_validation.whatsapp_contract import (
    CLAVE_CANAL_WHATSAPP,
    EVIDENCE_PLUGIN_FINGERPRINT,
    EVIDENCE_WA_ME_HREF,
    destino_whatsapp_verificado,
)

# ── Entradas medidas en la corrida certificada (solo lectura del ZIP) ─────────
TELEFONO_GBP_REAL = "(606) 3146139"
DIGITOS_GBP_REAL = "6063146139"

CANAL_REAL_DEL_2026_10_07 = {
    # site_presence_snapshot.json -> whatsapp_button.presence_evidence_kind
    "presence_evidence_kind": EVIDENCE_PLUGIN_FINGERPRINT,
    # audit_report_20261007_093348.json -> validation.whatsapp_status
    "whatsapp_status": "estimated",
    # audit_report -> validation.whatsapp_href_number (ausente en la corrida)
    "whatsapp_href_number": None,
}


def hotel_real(**extra):
    hotel = {
        "name": "Hotel Don Alfonso",
        "city": "Santa Rosa de Cabal",
        "state": "Risaralda",
        "phone": TELEFONO_GBP_REAL,
    }
    hotel.update(extra)
    return hotel


def todas_las_paginas(generador, hotel):
    return generador.generate_content_set(hotel, hotel_type="boutique").pages


def contar_wa_me(pages):
    """Ocurrencias de `wa.me` en cuerpo y enlaces internos de todas las páginas."""
    total = sum(p.content_md.count("wa.me") for p in pages)
    total += sum(len([l for l in p.internal_links if "wa.me" in l]) for p in pages)
    return total


# ══ el caso real medido: 0 wa.me ═════════════════════════════════════════════

def test_caso_real_plugin_fingerprint_no_emite_wa_me():
    """Presencia `plugin_fingerprint` sin href: la huella declara presencia, jamás número."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(**{CLAVE_CANAL_WHATSAPP: dict(CANAL_REAL_DEL_2026_10_07)}),
    )

    assert len(pages) >= 2, "la corrida real produjo 5 páginas; el fixture debe ser no vacío"
    assert contar_wa_me(pages) == 0
    assert f"wa.me/{DIGITOS_GBP_REAL}" not in "\n".join(p.content_md for p in pages)


def test_caso_real_conserva_texto_sin_fabricar_destino():
    """Sin canal verificado no hay frase de reserva con enlace, pero la página se produce."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(**{CLAVE_CANAL_WHATSAPP: dict(CANAL_REAL_DEL_2026_10_07)}),
    )

    for page in pages:
        assert "Para reservar:" not in page.content_md
        assert "Reservar: contactar al hotel" in page.internal_links


def test_canal_ausente_no_emite_wa_me():
    """Un hotel sin observación de canal (clave ausente) tampoco fabrica destino."""
    assert contar_wa_me(todas_las_paginas(LocalContentGenerator(), hotel_real())) == 0


# ══ el canal verificado sí habilita destino, y es el del canal ═══════════════

def test_href_verificado_destino_igual_al_canal_normalizado():
    """`wa.me_href` + canal VERIFIED: el destino es el número del href normalizado."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(
            phone="+57 300 123 4567",
            **{
                CLAVE_CANAL_WHATSAPP: {
                    "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
                    "whatsapp_status": "verified",
                    "whatsapp_href_number": "573001234567",
                }
            },
        ),
    )

    cuerpo = "\n".join(p.content_md for p in pages)
    assert "https://wa.me/573001234567" in cuerpo
    assert contar_wa_me(pages) == len(pages) * 2  # una línea y un enlace por página
    for page in pages:
        assert any(l.endswith("https://wa.me/573001234567") for l in page.internal_links)


def test_destino_sale_del_canal_aunque_no_haya_telefono():
    """El destino se construye con el número del canal, no con `hotel_data["phone"]`."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        {
            "name": "Hotel Sin Telefono",
            "city": "Manizales",
            "state": "Caldas",
            CLAVE_CANAL_WHATSAPP: {
                "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
                "whatsapp_status": "verified",
                "whatsapp_href_number": "573001234567",
            },
        },
    )

    assert "https://wa.me/573001234567" in "\n".join(p.content_md for p in pages)


def test_telefono_de_otro_canal_no_suplanta_al_canal():
    """Canal verificado con un número y teléfono GBP con otro: no hay enlace."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(
            **{
                CLAVE_CANAL_WHATSAPP: {
                    "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
                    "whatsapp_status": "verified",
                    "whatsapp_href_number": "573111111111",
                }
            }
        ),
    )

    assert contar_wa_me(pages) == 0


# ══ los cuatro estados que el plan enumeró como rechazo ══════════════════════

def _canal(**campo):
    canal = {
        "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
        "whatsapp_status": "verified",
        "whatsapp_href_number": "573001234567",
    }
    canal.update(campo)
    return canal


def test_estado_estimated_con_numero_casado_rechaza_por_estado():
    """Caso discriminante del guard de estado: con numero que casa, solo el estado corta.

    Sin este caso el mutante que apaga el filtro de estado sobrevive, porque el
    contraste de numero (capa siguiente) ya venia cortando el mismo fixture.
    """
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(phone="+57 300 123 4567", **{CLAVE_CANAL_WHATSAPP: _canal(whatsapp_status="estimated")}),
    )

    assert contar_wa_me(pages) == 0


def test_plugin_fingerprint_con_numero_casado_rechaza_por_clase_de_evidencia():
    """Caso discriminante del guard de clase: una huella de plugin jamas habilita destino."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(
            phone="+57 300 123 4567",
            **{CLAVE_CANAL_WHATSAPP: _canal(presence_evidence_kind=EVIDENCE_PLUGIN_FINGERPRINT)},
        ),
    )

    assert contar_wa_me(pages) == 0


@pytest.mark.parametrize(
    "estado",
    ["estimated", "conflict", "unknown", "insufficient", None, ""],
)
def test_estado_no_verified_rechaza_destino(estado):
    """`estimated`, `CONFLICT`, `unknown` o ausente: el canal no habilita destino."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(
            **{
                CLAVE_CANAL_WHATSAPP: {
                    "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
                    "whatsapp_status": estado,
                    "whatsapp_href_number": "573001234567",
                }
            }
        ),
    )

    assert contar_wa_me(pages) == 0


@pytest.mark.parametrize(
    "evidencia",
    [EVIDENCE_PLUGIN_FINGERPRINT, "texto_visible", "ninguna", None, ""],
)
def test_evidencia_que_no_es_href_rechaza_destino(evidencia):
    """Solo `wa.me_href` trae destino, aunque el estado venga verificado."""
    pages = todas_las_paginas(
        LocalContentGenerator(),
        hotel_real(
            **{
                CLAVE_CANAL_WHATSAPP: {
                    "presence_evidence_kind": evidencia,
                    "whatsapp_status": "verified",
                    "whatsapp_href_number": "573001234567",
                }
            }
        ),
    )

    assert contar_wa_me(pages) == 0


# ══ el contrato, en solitario: la regla vive en whatsapp_contract ════════════

def test_contrato_rechaza_entradas_que_no_son_observacion():
    """El guard no adivina: sin dict, o con numero inutilizable, no hay destino."""
    assert destino_whatsapp_verificado(None) is None
    assert destino_whatsapp_verificado("573001234567") is None
    assert destino_whatsapp_verificado({}) is None
    assert destino_whatsapp_verificado(
        {"presence_evidence_kind": EVIDENCE_WA_ME_HREF, "whatsapp_status": "verified",
         "whatsapp_href_number": "detected_via_html"}
    ) is None
    assert destino_whatsapp_verificado(
        {"presence_evidence_kind": EVIDENCE_WA_ME_HREF, "whatsapp_status": "verified",
         "whatsapp_href_number": "12345"}
    ) is None  # LONGITUD_INVALIDA: un recorte no es numero


def test_contrato_normaliza_antes_de_comparar():
    """Mismo numero en dos grafias (`+57 300 123 4567` vs `573001234567`) casa."""
    canal = {
        "presence_evidence_kind": EVIDENCE_WA_ME_HREF,
        "whatsapp_status": "verified",
        "whatsapp_href_number": "573001234567",
    }
    assert destino_whatsapp_verificado(canal, "+57 300 123 4567") == "573001234567"
    assert destino_whatsapp_verificado(canal, "57-300-123-4567") == "573001234567"
    assert destino_whatsapp_verificado(canal, TELEFONO_GBP_REAL) is None


# ══ el cableado: el orquestador entrega la observacion del canal ══════════════

def _contenido_por_el_handler(asset_data):
    return ConditionalGenerator()._generate_content(
        "local_content_page", asset_data, "Hotel Don Alfonso", "donalfonso"
    )


def test_handler_pasa_el_canal_y_sin_href_no_hay_wa_me():
    """Rama de producción: `hotel_data['phone']` llega con el GBP pero el canal no trae href."""
    contenido = _contenido_por_el_handler({
        "hotel_data": {"name": "Hotel Don Alfonso", "city": "Santa Rosa de Cabal",
                       "state": "Risaralda", "phone": TELEFONO_GBP_REAL},
        "whatsapp_presence_evidence_kind": EVIDENCE_PLUGIN_FINGERPRINT,
        "whatsapp_status": "estimated",
        "whatsapp_href_number": None,
    })

    assert contenido.count("wa.me") == 0
    assert f"wa.me/{DIGITOS_GBP_REAL}" not in contenido


def test_handler_pasa_el_canal_y_con_href_verificado_hay_destino():
    """La misma rama, con el canal href verificado: el enlace se emite con el numero del canal."""
    contenido = _contenido_por_el_handler({
        "hotel_data": {"name": "Hotel Don Alfonso", "city": "Santa Rosa de Cabal",
                       "state": "Risaralda", "phone": "+57 300 123 4567"},
        "whatsapp_presence_evidence_kind": EVIDENCE_WA_ME_HREF,
        "whatsapp_status": "verified",
        "whatsapp_href_number": "573001234567",
    })

    assert "https://wa.me/573001234567" in contenido
