"""Contrafactual AC6 medido, no afirmado (recuperacion 2026-10-07).

Lado PRE : lineas `wa.me` del miembro producido en la corrida del 2026-10-07.
Lado POST: el MISMO archivo, producido offline por el MISMO handler de produccion
           (`ConditionalGenerator._generate_content('local_content_page', ...)`)
           con las MISMAS entradas de esa corrida.

Comando:
    python -X utf8 evidence/AC6-AC10-RECUPERACION-2026-10-07/contrafactual_wa_me.py
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.asset_generation.conditional_generator import ConditionalGenerator  # noqa: E402

ZIP_CERTIFICADO = (
    ROOT / "output" / "REFACTOR-WHATSAPP-ENTREGA-2026-09-18" / "v4_complete"
    / "deliveries" / "hotel_don_alfonso_20261007.zip"
)
MIEMBRO = "ASSETS/local_content_page/contenido_local__20261007_093402.md"

# Entradas de la corrida, leidas del paquete certificado (solo lectura):
#   audit_report_20261007_093348.json -> validation.gbp_phone / phone_web / whatsapp_status
#   site_presence_snapshot.json       -> whatsapp_button.presence_evidence_kind
ENTRADAS_DE_LA_CORRIDA = {
    "hotel_data": {
        "name": "Hotel Don Alfonso",
        "city": "Santa Rosa de Cabal",
        "state": "Risaralda",
        "phone": "(606) 3146139",       # gbp.phone, que el orquestador escribe en hotel_data
        "website": "https://www.donalfonsohotel.com/",
    },
    "whatsapp_presence_evidence_kind": "plugin_fingerprint",
    "whatsapp_status": "estimated",
    "whatsapp_href_number": None,
}


def contar(cuerpo: str):
    lineas = [(i, l.strip()) for i, l in enumerate(cuerpo.splitlines(), 1) if "wa.me" in l]
    return lineas


def main() -> int:
    with zipfile.ZipFile(ZIP_CERTIFICADO) as z:
        pre = z.read(MIEMBRO).decode("utf-8")
    lineas_pre = contar(pre)

    # POST: mismo handler de produccion, mismas entradas, codigo corregido.
    contenido = ConditionalGenerator()._generate_content(
        "local_content_page",
        ENTRADAS_DE_LA_CORRIDA,
        "Hotel Don Alfonso",
        "hotel_don_alfonso",
    )
    lineas_post = contar(contenido)

    print(f"archivo PRE  : {ZIP_CERTIFICADO.name} :: {MIEMBRO}")
    print(f"lineas wa.me PRE : {len(lineas_pre)}  -> numeros de linea "
          f"{[i for i, _ in lineas_pre]}")
    print(f"ejemplo PRE      : {lineas_pre[0][1] if lineas_pre else '(ninguna)'}")
    print()
    print("archivo POST : contenido producido offline por el handler de produccion")
    print(f"lineas wa.me POST: {len(lineas_post)}  -> {[i for i, _ in lineas_post]}")
    print(f"pagina(s) en el POST: {contenido.count('# ')} cabeceras, "
          f"{contenido.count('Para reservar:')} frases de reserva")
    print()
    print(f"CONTRAFACTUAL: {len(lineas_pre)} -> {len(lineas_post)}")
    return 0 if (len(lineas_pre) == 5 and len(lineas_post) == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
