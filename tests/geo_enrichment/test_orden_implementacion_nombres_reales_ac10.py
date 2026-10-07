"""AC10 (sesión de recuperación 2026-10-07): IMPLEMENTATION_ORDER con tareas reales.

Hallazgo V-2 de FASE-VERIFY: en el ZIP publicado del 2026-10-07
`IMPLEMENTATION_ORDER.md` (2.586 chars) tenía vacías las tres secciones de tarea
—ORDEN DE IMPLEMENTACIÓN, GUÍA DE RELACIONES y CHECKLIST— y las 13 rutas reales
viajaban solo como "ASSETS ADICIONALES sin par conocido". La causa era
`get_implementation_order`, que casaba por igualdad exacta seis nombres
canónicos contra basenames con `ESTIMATED_` y marca de tiempo: dos poblaciones
distintas, 0 coincidencias.

Estos tests corren offline: el writer real (`DeliveryPackager.write`) sobre un
directorio de prueba alimentado con los 13 nombres leídos en solo lectura del
paquete certificado. No se ejecuta `v4complete` (contador 1/1 consumido).
"""

import json
import posixpath
import re
import zipfile
from pathlib import Path

import pytest

from modules.delivery.delivery_packager import DeliveryPackager
from modules.geo_enrichment.asset_responsibility_contract import (
    AssetResponsibilityContract,
    AssetType,
    despojer_nombre_real,
)

PAQUETE_CERTIFICADO = (
    Path(__file__).resolve().parents[2]
    / "output" / "REFACTOR-WHATSAPP-ENTREGA-2026-09-18" / "v4_complete" / "deliveries"
    / "hotel_don_alfonso_20261007.zip"
)

ORDEN_RE = re.compile(r"^###\s*\d+\.", re.MULTILINE)


@pytest.fixture(scope="module")
def paquete_real():
    """Los 13 basenames y su ruta dentro del ZIP, leídos del paquete certificado."""
    if not PAQUETE_CERTIFICADO.exists():
        pytest.skip(f"paquete certificado ausente: {PAQUETE_CERTIFICADO}")
    with zipfile.ZipFile(PAQUETE_CERTIFICADO) as z:
        reporte = json.loads(z.read("ASSETS/v4_audit/asset_generation_report.json"))
        nombres = [a["filename"] for a in reporte["generated_assets"]]
        por_nombre = {posixpath.basename(m): m for m in z.namelist() if m.startswith("ASSETS/")}
    dest = {n: por_nombre[n] for n in nombres if n in por_nombre}
    assert len(nombres) == 13, f"se esperaban 13 assets, la corrida trajo {len(nombres)}"
    return {"nombres": nombres, "dest": dest, "geo_score": 63}


@pytest.fixture
def contrato():
    return AssetResponsibilityContract()


# ══ la regla de despojo, en solitario ════════════════════════════════════════

@pytest.mark.parametrize(
    "nombre,esperado",
    [
        ("hotel_schema_20261007_093402.json", "hotel_schema.json"),
        ("ESTIMATED_boton_whatsapp_20261007_093402.html", "boton_whatsapp.html"),
        ("boton_whatsapp.html", "boton_whatsapp.html"),           # canonico intacto
        ("hotel_schema_rich.json", "hotel_schema_rich.json"),     # GEO, sin marca
        ("hotel_schema_20261007_093402_metadata.json", "hotel_schema_20261007_093402_metadata.json"),
    ],
)
def test_despojer_nombre_real(nombre, esperado):
    assert despojer_nombre_real(nombre) == esperado


@pytest.mark.parametrize("basura", [None, "", 12, ["x"]])
def test_despojer_no_adivina(basura):
    assert despojer_nombre_real(basura) is None


# ══ sin fabricar pares: solo casa lo que es exactamente catálogo ═════════════

def test_los_nombres_reales_que_casan(contrato, paquete_real):
    """De los 13 nombres reales, UNO está catalogado; los otros doce no se inventan."""
    resueltos = {n: contrato.resolver_nombre_real(n) for n in paquete_real["nombres"]}

    assert resueltos["hotel_schema_20261007_093402.json"] == ("hotel_schema.json", AssetType.CORE)
    assert resueltos["ESTIMATED_faqs_20261007_093402.json"] is None, (
        "`faqs` no es `faq_schema.json`: emparejarlos sería fabricar el par"
    )
    assert resueltos["ESTIMATED_org_schema_20261007_093402.json"] is None
    assert sum(1 for v in resueltos.values() if v is not None) == 1


def test_orden_no_vacio_con_nombres_reales(contrato, paquete_real):
    """La regresión certificada: `get_implementation_order` devolvía []."""
    order = contrato.get_implementation_order(paquete_real["nombres"], [])

    assert len(order) == 1
    assert order[0].filename == "hotel_schema.json"
    assert order[0].type == AssetType.CORE


def test_none_sigue_significando_todos(contrato):
    """`None` no se reinterpreta: sin lista, el catálogo completo (3 CORE + 3 GEO)."""
    assert len(contrato.get_implementation_order(None, None)) == 6


def test_lista_vacia_sigue_significando_nada(contrato):
    """`[]` no revive tareas: un paquete sin assets planificados no inventa orden."""
    assert contrato.get_implementation_order([], []) == []


# ══ el template con rutas que existen como miembros del paquete ══════════════

def test_template_emite_tarea_numerada_con_ruta_real(contrato, paquete_real):
    template = contrato.generate_delivery_template(
        hotel_name="Hotel Don Alfonso",
        core_assets=paquete_real["nombres"],
        geo_assets=[],
        geo_score=paquete_real["geo_score"],
        asset_zip_paths=paquete_real["dest"],
    )

    tareas = ORDEN_RE.findall(template)
    assert len(tareas) == 1
    ruta = re.search(r"^###\s*1\.\s+(\S+)", template, re.MULTILINE).group(1)
    assert ruta.startswith("ASSETS/")
    assert ruta == paquete_real["dest"]["hotel_schema_20261007_093402.json"]


def test_los_no_catalogados_siguen_siendo_adicionales(contrato, paquete_real):
    """Criterio 5: los assets fuera del catálogo siguen listándose como adicionales."""
    template = contrato.generate_delivery_template(
        hotel_name="Hotel Don Alfonso",
        core_assets=paquete_real["nombres"],
        geo_assets=[],
        asset_zip_paths=paquete_real["dest"],
    )

    adicionales = re.findall(r"^- \*\*`(ASSETS/[^`]+)`\*\*", template, re.MULTILINE)
    assert len(adicionales) == 12
    assert "ASSETS/faq_page/ESTIMATED_faqs_20261007_093402.json" in adicionales
    # el que sí está catalogado ya no puede declararse "sin par conocido"
    assert "ASSETS/hotel_schema/hotel_schema_20261007_093402.json" not in adicionales


# ══ el writer real: ZIP de prueba con los nombres de la corrida ══════════════

@pytest.fixture
def entrega(tmp_path, paquete_real):
    """Directorio de salida materializado con los 13 archivos reales, en su ruta real.

    Se reproducen los subdirectorios (`ASSETS/<tipo>/<basename>`) porque
    `DeliveryPackager._collect_files` solo enruta a `ASSETS/` lo que llega en
    subcarpeta o con extension conocida: un fixture plano dejaba un `.txt` fuera
    de `ASSETS/` y mediria otra cosa.
    """
    output = tmp_path / "v4_complete"
    hotel = output / "donalfonso"
    audit = hotel / "v4_audit"
    deliveries = output / "deliveries"
    for d in (hotel, audit, deliveries):
        d.mkdir(parents=True)
    for nombre in paquete_real["nombres"]:
        destino = paquete_real["dest"][nombre]          # ASSETS/<tipo>/<basename>
        relativa = destino.split("/", 1)[1]             # sin el prefijo ASSETS/
        ruta = hotel / relativa
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(f"# {nombre}\n\ncontenido por hotel\n", encoding="utf-8")
    (audit / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": 13, "generated": 13, "failed": 0}}),
        encoding="utf-8",
    )
    packager = DeliveryPackager(
        base_output_dir=str(output), deliveries_dir=str(deliveries)
    )
    quarantine = packager.write(
        hotel_id="donalfonso",
        output_dir=str(hotel),
        hotel_name="Hotel Don Alfonso",
        core_assets=paquete_real["nombres"],
        geo_assets=[],
        geo_score=paquete_real["geo_score"],
    )
    return Path(quarantine), deliveries


def test_zip_del_writer_tiene_orden_no_vacio_y_rutas_miembros(entrega):
    """Criterio 6: orden no vacío y cada ruta `ASSETS/...` existe como miembro del ZIP."""
    zip_path, _ = entrega
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        nombres = z.namelist()
        assert "IMPLEMENTATION_ORDER.md" in nombres
        doc = z.read("IMPLEMENTATION_ORDER.md").decode("utf-8")

    assert ORDEN_RE.findall(doc), "el orden volvió a salir vacío"
    for ruta in re.findall(r"^###\s*\d+\.\s+(\S+)", doc, re.MULTILINE):
        assert posixpath.normpath(ruta) in nombres, f"ruta publicada que no es miembro: {ruta}"


def test_zip_del_writer_deja_los_doce_adicionales(entrega):
    """Los doce no catalogados siguen listados y su ruta existe como miembro."""
    zip_path, _ = entrega
    with zipfile.ZipFile(zip_path) as z:
        doc = z.read("IMPLEMENTATION_ORDER.md").decode("utf-8")
        miembros = set(z.namelist())

    adicionales = re.findall(r"^- \*\*`(ASSETS/[^`]+)`\*\*", doc, re.MULTILINE)
    assert len(adicionales) == 12
    assert [a for a in adicionales if posixpath.normpath(a) not in miembros] == []


def test_manifiesto_coherente_contra_el_zip(entrega):
    """Criterio 6: entradas contra `namelist()` y tamaños exactos, sin ausencias."""
    zip_path, _ = entrega
    with zipfile.ZipFile(zip_path) as z:
        miembros = set(z.namelist())
        manifiesto = json.loads(z.read("MANIFEST.json"))
        discrepancias = [
            f["name"] for f in manifiesto["files"]
            if f["name"] in miembros
            and len(z.read(f["name"])) != f.get("size_bytes")
        ]

    declaradas = {f["name"] for f in manifiesto["files"]}
    assert declaradas - miembros == set()
    assert miembros - declaradas == set()
    assert discrepancias == []


def test_sin_assets_planificados_no_hay_archivo(entrega, tmp_path):
    """Criterio 6: el caso sin assets se declara — no se emite IMPLEMENTATION_ORDER.md."""
    zip_path, deliveries = entrega
    with zipfile.ZipFile(zip_path) as z:
        assert "IMPLEMENTATION_ORDER.md" in z.namelist()

    hotel = zip_path.parent.parent / "donalfonso_vacio"
    audit = hotel / "v4_audit"
    audit.mkdir(parents=True)
    (hotel / "algo.md").write_text("# algo\n\ncontenido\n", encoding="utf-8")
    (audit / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": 0, "generated": 0, "failed": 0}}),
        encoding="utf-8",
    )
    vacío = DeliveryPackager(
        base_output_dir=str(deliveries.parent), deliveries_dir=str(deliveries)
    ).write(
        hotel_id="donalfonso_vacio",
        output_dir=str(hotel),
        hotel_name="Hotel Don Alfonso",
        core_assets=None,
        geo_assets=None,
    )
    with zipfile.ZipFile(vacío) as z:
        assert "IMPLEMENTATION_ORDER.md" not in z.namelist()
