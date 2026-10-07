"""Verificacion externa de cierre (recuperacion AC6/AC10, 2026-10-07).

Paso aparte de la suite: observa el ZIP que produce el writer real y el contenido
que produce el handler de produccion, y imprime los tres hechos que exige el
atributo de cierre. Comando:

    python -X utf8 evidence/AC6-AC10-RECUPERACION-2026-10-07/verificacion_externa.py
"""

import json
import posixpath
import re
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.asset_generation.conditional_generator import ConditionalGenerator  # noqa: E402
from modules.delivery.delivery_packager import DeliveryPackager  # noqa: E402

ZIP_CERTIFICADO = (ROOT / "output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/v4_complete"
                   / "deliveries/hotel_don_alfonso_20261007.zip")


def nombres_y_destinos():
    with zipfile.ZipFile(ZIP_CERTIFICADO) as z:
        nombres = [a["filename"] for a in
                   json.loads(z.read("ASSETS/v4_audit/asset_generation_report.json"))["generated_assets"]]
        por_nombre = {posixpath.basename(m): m for m in z.namelist() if m.startswith("ASSETS/")}
    return nombres, {n: por_nombre[n] for n in nombres}


def main() -> int:
    nombres, dest = nombres_y_destinos()
    tmp = Path(tempfile.mkdtemp(prefix="verif_ac10_"))
    out = tmp / "v4_complete"
    hotel, audit, deliveries = out / "donalfonso", out / "donalfonso" / "v4_audit", out / "deliveries"
    audit.mkdir(parents=True)
    deliveries.mkdir(parents=True)
    for n in nombres:
        ruta = hotel / dest[n].split("/", 1)[1]
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(f"# {n}\n\ncontenido por hotel\n", encoding="utf-8")
    (audit / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": len(nombres), "generated": len(nombres), "failed": 0}}),
        encoding="utf-8")

    quarantine = Path(DeliveryPackager(base_output_dir=str(out), deliveries_dir=str(deliveries)).write(
        hotel_id="donalfonso", output_dir=str(hotel), hotel_name="Hotel Don Alfonso",
        core_assets=nombres, geo_assets=[], geo_score=63))

    with zipfile.ZipFile(quarantine) as z:
        integridad = z.testzip()
        miembros = set(z.namelist())
        doc = z.read("IMPLEMENTATION_ORDER.md").decode("utf-8")

    tareas = re.findall(r"^###\s*(\d+)\.\s+(\S+)", doc, re.MULTILINE)
    rutas_ok = [(n, r, posixpath.normpath(r) in miembros) for n, r in tareas]

    contenido = ConditionalGenerator()._generate_content(
        "local_content_page",
        {"hotel_data": {"name": "Hotel Don Alfonso", "city": "Santa Rosa de Cabal",
                        "state": "Risaralda", "phone": "(606) 3146139",
                        "website": "https://www.donalfonsohotel.com/"},
         "whatsapp_presence_evidence_kind": "plugin_fingerprint",
         "whatsapp_status": "estimated", "whatsapp_href_number": None},
        "Hotel Don Alfonso", "hotel_don_alfonso")
    wa_me = len([l for l in contenido.splitlines() if "wa.me" in l])

    print(f"1) zipfile.testzip() sobre {quarantine.name} -> {integridad}")
    print(f"2) IMPLEMENTATION_ORDER.md del ZIP de prueba: {len(tareas)} tarea(s) numerada(s)")
    for num, ruta, existe in rutas_ok:
        print(f"   tarea {num}: {ruta} | existe como miembro del ZIP: {existe}")
    print(f"3) contenido local producido tras el fix: {wa_me} linea(s) con `wa.me`")

    return 0 if (integridad is None and rutas_ok and all(e for _, _, e in rutas_ok) and wa_me == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
