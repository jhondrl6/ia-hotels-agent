"""FASE-E — snapshot interno de insumos, resolvedor unico del Tribunal y ZIP real.

Gobierna AC9, AC10, AC11 y AC12 del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18.

Criterios que hacen de dientes, no de decoracion:

* AC11 se mide contra `review_inputs` y contra los cuatro revisores reales: un documento
  que existe pero que el resolvedor no alcanza es NO_LEIDO, jamas lista vacia.
* AC10 lee IMPLEMENTATION_ORDER.md del ZIP que escribio `DeliveryPackager.write()`, no de
  un markdown fabricado en el test (L-V.1), y revalida el writer vigente por mutacion en
  lugar de reimplementar el fix de P6/P6-R (L-VUP-5).
* La no-exportabilidad del snapshot se comprueba con el writer real (`namelist()`), no
  leyendo el codigo.
* AC12 usa `ActaWriter` y `TribunalJudge.finalize`, y el par permitir/bloquear sale del
  `publish()`/`suppress()` del packager.

Ninguna prueba ejecuta `main.py v4complete` (§Corrida unica del contrato).
"""

import json
import shutil
import zipfile
from pathlib import Path

import pytest

from main import _compute_package_evidence, _record_published_package_evidence
from modules.data_validation.whatsapp_contract import (
    READ_ABSENT,
    READ_ERROR,
    READ_NOT_READ,
    READ_OK,
)
from modules.delivery.delivery_packager import DeliveryPackager
from modules.quality_gates.tribunal.alignment_reviewer import AlignmentReviewer
from modules.quality_gates.tribunal.asset_reviewer import AssetReviewer
from modules.quality_gates.tribunal.diagnosis_reviewer import (
    FINDING_REVIEW_INPUT_ABSENT,
    FINDING_REVIEW_INPUT_UNREAD,
    FINDING_UNTRACEABLE_PAIN,
    DiagnosisReviewer,
)
from modules.quality_gates.tribunal.honesty_reviewer import HonestyReviewer
from modules.quality_gates.tribunal.judge import TribunalJudge
from modules.quality_gates.tribunal.review_inputs import (
    DISPOSITION_INTERNAL_COPY,
    DISPOSITION_RETAINED_BY_GATE,
    KIND_DIAGNOSTICO,
    KIND_PROPUESTA,
    MANIFEST_NAME,
    SNAPSHOT_DIRNAME,
    ReviewInputs,
    capture_review_inputs,
    manifest_path_for,
    run_root_for,
    sha256_bytes,
    snapshot_root_for,
)
from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.artifact_paths import resolve_latest

RUN_ID = "run_20261006T120000"
CATALOGO_ASSETS = ("hotel_schema.json", "faq_schema.json", "whatsapp_setup_guide.md")

DIAGNOSTICO_TEXT = (
    "# Diagnostico\n\n"
    "Brecha con pain_id: whatsapp_conflict y otra con pain_id: cobertura_geo_faltante\n"
)
PROPUESTA_TEXT = "# Propuesta comercial\n\nSe promete la guia de configuracion de WhatsApp.\n"
LEDGER = {
    "entries": [
        {
            "pain_id": "otra_cosa",
            "source_module": "modules/analyzers",
            "source_file": "gaps.py",
            "severity": "INFO",
            "confidence": 0.9,
        }
    ]
}
MATRIX = {"entries": [], "services": []}
SCENARIOS = {"breakdown": {"evidence_tier": "B"}, "scenarios": {}}


class _ExtractoraVacia:
    """Extractor determinista: no hay LLM en esta bateria y no hace falta."""

    def extract_verbal_promises(self, text):
        return []


def _run(tmp_path, *, diagnostico=True, propuesta=True, assets=("whatsapp_setup_guide.md",)):
    """Monta la forma real del pipeline: run_root/hotel/v4_audit + run_root/deliveries."""
    root = tmp_path / "output"
    hotel = root / "hotel_x"
    audit = hotel / "v4_audit"
    deliveries = root / "deliveries"
    assets_dir = hotel / "ASSETS"
    for path in (audit, deliveries, assets_dir):
        path.mkdir(parents=True, exist_ok=True)

    diag_path = root / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20261006.md"
    prop_path = root / "02_PROPUESTA_COMERCIAL_20261006.md"
    # write_bytes y no write_text: bajo Windows el modo texto traduce \n a \r\n y el
    # cotejo "la copia interna es el byte a byte del original" fallaria por el
    # instrumento, no por el producto.
    if diagnostico:
        diag_path.write_bytes(DIAGNOSTICO_TEXT.encode("utf-8"))
    if propuesta:
        prop_path.write_bytes(PROPUESTA_TEXT.encode("utf-8"))

    (audit / "pain_ledger.json").write_text(json.dumps(LEDGER), encoding="utf-8")
    (audit / "proposal_asset_matrix.json").write_text(json.dumps(MATRIX), encoding="utf-8")
    (audit / "financial_scenarios_2026100612.json").write_text(
        json.dumps(SCENARIOS), encoding="utf-8"
    )
    (audit / "gate_report_2026100612.json").write_text(
        json.dumps({"gate_results": []}), encoding="utf-8"
    )
    (audit / "coherence_validation.json").write_text(
        json.dumps({"is_coherent": True}), encoding="utf-8"
    )
    for name in assets:
        # en la RAIZ del source_dir: _collect_files asigna ASSETS/<nombre> a los .md/.json
        # .csv/.html de raiz, y ASSETS/<rel> a lo que ya vive subdirectorios abajo.
        (hotel / name).write_bytes(f"<!-- {name} -->\n".encode("utf-8"))

    return {
        "root": root,
        "hotel": hotel,
        "audit": audit,
        "deliveries": deliveries,
        "diag": diag_path,
        "prop": prop_path,
    }


def _captura(tree, **kwargs):
    retained = kwargs.pop("retained_by_gate", True)
    return capture_review_inputs(
        run_root=tree["root"],
        run_id=RUN_ID,
        v4_audit_dir=tree["audit"],
        documents={"diagnostico": tree["diag"], "propuesta": tree["prop"]},
        retained_by_gate=retained,
        **kwargs,
    )


# ── AC11 · snapshot y manifiesto ──────────────────────────────────────


def test_copia_interna_vive_fuera_del_directorio_del_hotel(tmp_path):
    tree = _run(tmp_path)
    manifest = _captura(tree)

    snapshot_root = snapshot_root_for(tree["root"], RUN_ID)
    copia = snapshot_root / KIND_DIAGNOSTICO / tree["diag"].name
    assert copia.is_file()
    assert copia.read_text(encoding="utf-8") == DIAGNOSTICO_TEXT
    # hermano del hotel, no dentro de lo que el packager recurre
    assert tree["hotel"] not in copia.parents
    assert manifest["snapshot_root"] == f"{SNAPSHOT_DIRNAME}/{RUN_ID}"


def test_manifest_declara_run_id_fuente_hash_ruta_interna_y_disposition(tmp_path):
    tree = _run(tmp_path)
    manifest = _captura(tree)

    entry = next(d for d in manifest["documents"] if d["kind"] == KIND_DIAGNOSTICO)
    assert entry["run_id"] == RUN_ID
    assert entry["original_path"] == str(tree["diag"])
    assert entry["internal_path"] == (
        f"{SNAPSHOT_DIRNAME}/{RUN_ID}/{KIND_DIAGNOSTICO}/{tree['diag'].name}"
    )
    raw = tree["diag"].read_bytes()
    assert entry["sha256"] == sha256_bytes(raw)
    assert entry["size_bytes"] == len(raw)
    assert entry["read_status"] == READ_OK
    assert entry["disposition"] == DISPOSITION_RETAINED_BY_GATE
    assert entry["captured_at"]
    assert manifest_path_for(tree["audit"]).is_file()
    assert run_root_for(tree["audit"]) == tree["root"]


def test_documento_nunca_generado_se_registra_como_ABSENT_sin_copia(tmp_path):
    tree = _run(tmp_path, propuesta=False)
    manifest = _captura(tree)

    entry = next(d for d in manifest["documents"] if d["kind"] == KIND_PROPUESTA)
    assert entry["read_status"] == READ_ABSENT
    assert entry["internal_path"] is None
    assert entry["sha256"] is None
    assert "no generado" in entry["cause"]

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    read = ri.read_document(KIND_PROPUESTA)
    assert read.read_status == READ_ABSENT
    assert read.content is None


def test_tras_el_borrado_el_revisor_lee_la_copia_interna(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tree["diag"].unlink()

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    read = ri.read_document(KIND_DIAGNOSTICO)
    assert read.read_status == READ_OK
    assert read.content == DIAGNOSTICO_TEXT
    assert read.source == "snapshot"
    assert read.disposition == DISPOSITION_RETAINED_BY_GATE


def test_borrado_sin_copia_interna_es_NO_LEIDO_y_no_OK_vacio(tmp_path):
    tree = _run(tmp_path)
    manifest = _captura(tree)
    tree["diag"].unlink()
    shutil.rmtree(snapshot_root_for(tree["root"], RUN_ID))

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID, manifest=manifest)
    read = ri.read_document(KIND_DIAGNOSTICO)
    assert read.read_status == READ_NOT_READ
    assert read.content is None
    assert "copia interna" in read.cause
    assert read.disposition == DISPOSITION_RETAINED_BY_GATE


def test_copia_interna_alterada_es_READ_ERROR_por_el_sha(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    copia = snapshot_root_for(tree["root"], RUN_ID) / KIND_DIAGNOSTICO / tree["diag"].name
    copia.write_text("otro contenido", encoding="utf-8")

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    read = ri.read_document(KIND_DIAGNOSTICO)
    assert read.read_status == READ_ERROR
    assert "sha256" in read.cause


def test_sin_manifiesto_el_fallback_declara_que_no_esta_ancorado_al_run(tmp_path):
    tree = _run(tmp_path)
    ri = ReviewInputs.for_run(tree["audit"], run_id="")
    read = ri.read_document(KIND_DIAGNOSTICO)
    assert read.read_status == READ_OK
    assert read.source == "legacy-ancestor-walk"
    assert "run_id" in read.cause


def test_ruta_explitica_gana_a_un_archivo_mas_reciente_de_otro_hotel(tmp_path):
    """`resolve_latest(explicit=)` cierra el hueco de F-P4.2: nada de mtime entre hoteles."""
    tree = _run(tmp_path)
    ri = ReviewInputs.for_run(tree["audit"], run_id="")
    pinned = tree["diag"]

    otro = tree["root"] / "02_PROPUESTA_COMERCIAL_OTRO.md"
    otro.write_text("propuesta de otro hotel", encoding="utf-8")
    import os

    os.utime(pinned, ns=(1_000_000_000, 1_000_000_000))
    os.utime(otro, ns=(9_000_000_000_000_000_000, 9_000_000_000_000_000_000))

    assert resolve_latest(
        "01_DIAGNOSTICO_Y_OPORTUNIDAD*.md", tree["audit"], explicit=pinned
    ) == pinned

    borrada = tree["root"] / "01_DIAGNOSTICO_Y_OPORTUNIDAD_NOESTA.md"
    assert resolve_latest(
        "01_DIAGNOSTICO_Y_OPORTUNIDAD*.md", tree["audit"], explicit=borrada
    ) is None


# ── AC11 · los cuatro revisores consumen el resolvedor ────────────────


def test_bot1_traza_las_brechas_desde_la_copia_interna(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tree["diag"].unlink()

    report = DiagnosisReviewer(
        tree["audit"], review_inputs=ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    ).review()

    tipos = [f["finding_type"] for f in report["findings"]]
    assert FINDING_UNTRACEABLE_PAIN in tipos, "el contenido del snapshot no llego al check"
    assert report["review_inputs"]["documents"]
    doc = next(d for d in report["review_inputs"]["documents"] if d["kind"] == KIND_DIAGNOSTICO)
    assert doc["read_status"] == READ_OK
    assert doc["source"] == "snapshot"


def test_bot1_insumo_no_leido_no_es_lista_vacia(tmp_path):
    tree = _run(tmp_path)
    manifest = _captura(tree)
    tree["diag"].unlink()
    shutil.rmtree(snapshot_root_for(tree["root"], RUN_ID))

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID, manifest=manifest)
    report = DiagnosisReviewer(tree["audit"], review_inputs=ri).review()

    tipos = [f["finding_type"] for f in report["findings"]]
    assert tipos.count(FINDING_REVIEW_INPUT_UNREAD) == 1
    assert FINDING_UNTRACEABLE_PAIN not in tipos
    unread = next(f for f in report["findings"] if f["finding_type"] == FINDING_REVIEW_INPUT_UNREAD)
    assert "NO_LEIDO" in unread["description"]
    assert unread["severity"] == "WARNING"


def test_bot1_ausencia_original_se_declara_info_sin_inflar_severidad(tmp_path):
    tree = _run(tmp_path, diagnostico=False)
    _captura(tree)

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    report = DiagnosisReviewer(tree["audit"], review_inputs=ri).review()

    tipos = [f["finding_type"] for f in report["findings"]]
    assert FINDING_REVIEW_INPUT_ABSENT in tipos
    absent = next(f for f in report["findings"] if f["finding_type"] == FINDING_REVIEW_INPUT_ABSENT)
    assert absent["severity"] == "INFO"
    assert report["summary"]["critical"] == 0


def test_bot1_retencion_leida_no_suma_hallazgo_nuevo(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tree["diag"].unlink()

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    report = DiagnosisReviewer(tree["audit"], review_inputs=ri).review()

    tipos = [f["finding_type"] for f in report["findings"]]
    assert FINDING_REVIEW_INPUT_UNREAD not in tipos
    assert FINDING_REVIEW_INPUT_ABSENT not in tipos


def test_bot2_lee_la_propuesta_del_run_y_la_declara_en_su_reporte(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tree["prop"].unlink()

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID)
    report = AlignmentReviewer(tree["audit"], review_inputs=ri).review(_ExtractoraVacia())

    doc = next(d for d in report["review_inputs"]["documents"] if d["kind"] == KIND_PROPUESTA)
    assert doc["read_status"] == READ_OK
    assert doc["source"] == "snapshot"


def test_bot2_error_report_nombras_el_estado_de_lectura(tmp_path):
    tree = _run(tmp_path)
    manifest = _captura(tree)
    tree["prop"].unlink()
    shutil.rmtree(snapshot_root_for(tree["root"], RUN_ID))

    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID, manifest=manifest)
    report = AlignmentReviewer(tree["audit"], review_inputs=ri).review(_ExtractoraVacia())

    assert "NO_LEIDO" in json.dumps(report, ensure_ascii=False)


def test_bot4_manifiesto_del_paquete_por_el_resolvedor(tmp_path):
    tree = _run(tmp_path)
    zip_path = tree["deliveries"] / "hotel_x_20261006.zip.tmp"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("MANIFEST.json", json.dumps({"files": [], "quality_metadata": {"evidence_tier": "A"}}))
        zf.writestr("IMPLEMENTATION_ORDER.md", PROPUESTA_TEXT)

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=zip_path
    )
    report = HonestyReviewer(
        tree["audit"], tree["deliveries"], review_inputs=ri
    ).review(_ExtractoraVacia())

    doc = next(d for d in report["review_inputs"]["documents"] if d["kind"] == "manifest")
    assert doc["read_status"] == READ_OK
    assert doc["source"] == "zip"


def test_juez_y_bot3_resuelven_MANIFEST_desde_el_zip_en_regimen_zip_only(tmp_path):
    """L-E2E.1: `deliveries/<hotel>/MANIFEST.json` no existe; el ZIP del run si."""
    tree = _run(tmp_path)
    zip_path = tree["deliveries"] / "hotel_x_20261006.zip.tmp"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("MANIFEST.json", json.dumps({"files": [], "quality_metadata": {"evidence_tier": "A"}}))

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=zip_path
    )
    judge = TribunalJudge(tree["audit"], tree["deliveries"], hotel_id="hotel_x", review_inputs=ri)
    assert judge._resolve_manifest()["quality_metadata"]["evidence_tier"] == "A"

    ri_bots = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=zip_path
    )
    assert AssetReviewer(tree["audit"], tree["deliveries"], review_inputs=ri_bots)._load_manifest()


def test_zip_de_otro_hotel_mas_nuevo_no_suplanta_la_ruta_explitica(tmp_path):
    tree = _run(tmp_path)
    own = tree["deliveries"] / "hotel_x_20261006.zip.tmp"
    with zipfile.ZipFile(own, "w") as zf:
        zf.writestr("MANIFEST.json", json.dumps({"files": [], "quality_metadata": {"evidence_tier": "A"}}))
    ajeno = tree["deliveries"] / "hotel_otro_20261007.zip.tmp"
    with zipfile.ZipFile(ajeno, "w") as zf:
        zf.writestr("MANIFEST.json", json.dumps({"files": [], "quality_metadata": {"evidence_tier": "C"}}))
    import os

    os.utime(ajeno, ns=(9_000_000_000_000_000_000, 9_000_000_000_000_000_000))

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=own
    )
    assert AssetReviewer(tree["audit"], tree["deliveries"], review_inputs=ri)._resolve_delivery_zip() == own


# ── AC10 · ZIP real escrito por DeliveryPackager ──────────────────────


def _write_paquete(tree, core_assets=CATALOGO_ASSETS):
    packager = DeliveryPackager(base_output_dir=str(tree["root"]), deliveries_dir=str(tree["deliveries"]))
    packager._quality_metadata = {"evidence_tier": "B", "precision_tier": "B"}
    tmp = packager.write(
        hotel_id="hotel_x",
        output_dir=str(tree["hotel"]),
        diagnostic_path=str(tree["diag"]) if tree["diag"].exists() else None,
        proposal_path=str(tree["prop"]) if tree["prop"].exists() else None,
        hotel_name="Hotel X",
        geo_score=50,
        core_assets=list(core_assets) if core_assets else None,
        geo_assets=None,
    )
    return Path(tmp)


def test_zip_real_lleva_implementation_order_con_tareas_no_vacias(tmp_path):
    tree = _run(tmp_path, assets=CATALOGO_ASSETS)
    tmp = _write_paquete(tree, core_assets=list(CATALOGO_ASSETS))

    with zipfile.ZipFile(tmp) as zf:
        texto = zf.read("IMPLEMENTATION_ORDER.md").decode("utf-8")

    assert len(texto.encode("utf-8")) > 800, "no certificar por tamano: se exige estructura"
    assert "### 1." in texto
    assert "Hotel X" in texto
    assert "ASSETS/whatsapp_setup_guide.md" in texto, (
        "el orden publico sigue mostrando el basename en vez de la ruta real del ZIP"
    )


def test_estado_real_de_f_p4_1_sin_assets_planificados_no_hay_orden(tmp_path):
    """Revalidacion del writer vigente (L-VUP-5), medido y no citado del contexto.

    Medido con el writer real: si el pipeline no planifico assets, el paquete NO lleva
    IMPLEMENTATION_ORDER.md. Por eso AC10 no puede certificar por tamano ni por
    presencia de un string: la evidencia es el miembro y su coherencia con el manifiesto.
    """
    tree = _run(tmp_path, assets=())
    tmp = _write_paquete(tree, core_assets=None)

    with zipfile.ZipFile(tmp) as zf:
        miembros = set(zf.namelist())
        manifest = json.loads(zf.read("MANIFEST.json"))

    assert "IMPLEMENTATION_ORDER.md" not in miembros
    assert "README_DELIVERY.md" in miembros
    assert {e["name"] for e in manifest["files"]} == miembros


def test_todas_las_rutas_de_orden_existen_como_miembros_del_zip(tmp_path):
    tree = _run(tmp_path, assets=CATALOGO_ASSETS)
    tmp = _write_paquete(tree, core_assets=list(CATALOGO_ASSETS))

    with zipfile.ZipFile(tmp) as zf:
        miembros = set(zf.namelist())
        texto = zf.read("IMPLEMENTATION_ORDER.md").decode("utf-8")

    referenciadas = {
        token for token in texto.replace("(", " ").replace(")", " ").split()
        if token.startswith("ASSETS/")
    }
    assert referenciadas, "IMPLEMENTATION_ORDER no publica ninguna ruta de ASSETS"
    for ruta in referenciadas:
        assert ruta in miembros, f"{ruta} prometido en el orden pero no esta en el paquete"


def test_manifiesto_del_zip_es_coherente_con_sus_miembros(tmp_path):
    tree = _run(tmp_path)
    tmp = _write_paquete(tree)

    with zipfile.ZipFile(tmp) as zf:
        manifest = json.loads(zf.read("MANIFEST.json"))
        miembros = {n for n in zf.namelist()}

    declarados = {e["name"] for e in manifest["files"]}
    assert declarados == miembros, (
        f"manifiesto y paquete divergen: solo-manifiesto={declarados - miembros} "
        f"solo-zip={miembros - declarados}"
    )
    assert manifest["total_files"] == len(manifest["files"])
    assert manifest["hotel_id"] == "hotel_x"


def test_el_asset_nuevo_de_b_viaja_con_su_ruta_real_y_su_orden(tmp_path):
    tree = _run(tmp_path, assets=("whatsapp_setup_guide.md",))
    tmp = _write_paquete(tree, core_assets=("whatsapp_setup_guide.md",))

    with zipfile.ZipFile(tmp) as zf:
        orden = zf.read("IMPLEMENTATION_ORDER.md").decode("utf-8")
        miembros = set(zf.namelist())
        manifest = json.loads(zf.read("MANIFEST.json"))

    assert "ASSETS/whatsapp_setup_guide.md" in miembros
    assert "ASSETS/whatsapp_setup_guide.md" in orden, (
        "el orden publica el basename: la derivacion por dest real (P6-R/R6) se perdio"
    )
    assert "ASSETS/whatsapp_setup_guide.md" in {e["name"] for e in manifest["files"]}


# ── AC11/AC12 · el snapshot no se filtra al paquete ───────────────────


def test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente(tmp_path):
    """Comprobado con el writer real: source_dir apuntando a la raiz de la corrida."""
    tree = _run(tmp_path)
    _captura(tree)

    packager = DeliveryPackager(base_output_dir=str(tree["root"]), deliveries_dir=str(tree["deliveries"]))
    packager._quality_metadata = {"evidence_tier": "B"}
    tmp = Path(packager.write(
        hotel_id="hotel_x",
        output_dir=str(tree["root"]),
        diagnostic_path=None,
        proposal_path=None,
        hotel_name="Hotel X",
        geo_score=50,
        core_assets=["whatsapp_setup_guide.md"],
        geo_assets=None,
    ))

    with zipfile.ZipFile(tmp) as zf:
        miembros = zf.namelist()

    assert not [n for n in miembros if SNAPSHOT_DIRNAME in n], miembros
    # el writer excluye por NOMBRE de archivo, y el miembro lleva el prefijo ASSETS/:
    # cotejar el nombre, no la ruta dentro del ZIP, es lo que le da diente al guard.
    assert not [n for n in miembros if Path(n).name.startswith("review_input_manifest")], miembros
    assert manifest_path_for(tree["audit"]).is_file(), "el manifiesto sigue en v4_audit"


# ── AC12 · par permitir/bloquear sobre el acta real ───────────────────


def _acta_del_run(tree, ri):
    judge = TribunalJudge(tree["audit"], tree["deliveries"], hotel_id="hotel_x", review_inputs=ri)
    return judge, judge.evaluate()


def test_bloqueo_suprime_la_cuarentena_y_el_acta_conserva_hash_y_conteo(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tmp = _write_paquete(tree)

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=tmp
    )
    judge, acta = _acta_del_run(tree, ri)
    outcome = judge.finalize(acta, [], blocks=True, gate_blocking_enabled=True)
    assert outcome.blocks_publish is True

    acta["package_evidence"] = {
        "suppressed": True,
        "path": str(tmp),
        **_compute_package_evidence(tmp),
    }
    ActaWriter(tree["audit"]).write(acta)

    DeliveryPackager(base_output_dir=str(tree["root"]), deliveries_dir=str(tree["deliveries"])).suppress(tmp)

    acta_disk = json.loads((tree["audit"] / "acta_revision.json").read_text(encoding="utf-8"))
    assert acta_disk["enforcement"]["enabled"] is True
    assert acta_disk["enforcement"]["suppressed_by_operator"] is False
    assert acta_disk["package_evidence"]["suppressed"] is True
    assert len(acta_disk["package_evidence"]["sha256"]) == 64
    assert acta_disk["package_evidence"]["member_count"] > 0
    assert not tmp.exists()
    assert not list(tree["deliveries"].glob("*.zip"))


def test_capturar_el_contenido_tras_suprimir_es_evidencia_ausente(tmp_path):
    """AC10 (F-P4.9): la evidencia del ZIP se toma DENTRO de la corrida, no despues."""
    tree = _run(tmp_path)
    _captura(tree)
    tmp = _write_paquete(tree)
    with zipfile.ZipFile(tmp) as zf:
        assert zf.read("IMPLEMENTATION_ORDER.md")

    DeliveryPackager(base_output_dir=str(tree["root"]), deliveries_dir=str(tree["deliveries"])).suppress(tmp)

    with pytest.raises(FileNotFoundError):
        zipfile.ZipFile(tmp)

    # F-P4.9: el writer never-block declara la ausencia en vez de inventar el conteo.
    evidencia = _compute_package_evidence(tmp)
    assert evidencia["sha256"] is None
    assert evidencia["member_count"] is None
    assert evidencia["error"]


def test_permitir_publica_y_la_rama_publish_registra_package_evidence(tmp_path):
    tree = _run(tmp_path)
    _captura(tree)
    tmp = _write_paquete(tree)

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=tmp
    )
    judge, acta = _acta_del_run(tree, ri)
    outcome = judge.finalize(acta, [], blocks=False, gate_blocking_enabled=True)
    assert outcome.blocks_publish is False

    published = Path(DeliveryPackager(
        base_output_dir=str(tree["root"]), deliveries_dir=str(tree["deliveries"])
    ).publish(tmp))
    _record_published_package_evidence(acta, published, tree["audit"])

    assert published.is_file() and not tmp.exists()
    assert acta["package_evidence"]["suppressed"] is False
    assert acta["package_evidence"]["sha256"] == sha256_bytes(published.read_bytes())
    assert acta["package_evidence"]["member_count"] > 0

    acta_disk = json.loads((tree["audit"] / "acta_revision.json").read_text(encoding="utf-8"))
    assert acta_disk["package_evidence"]["sha256"] == acta["package_evidence"]["sha256"]


def test_el_veredicto_del_juez_sigue_intacto_con_los_mismos_insumos(tmp_path):
    """Enforcement congelado: E agrega el resolvedor, no cambia la regla de decision."""
    tree = _run(tmp_path)
    ri = ReviewInputs.for_run(tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"])
    judge = TribunalJudge(tree["audit"], tree["deliveries"], hotel_id="hotel_x", review_inputs=ri)
    primer = judge.evaluate()
    segundo = TribunalJudge(tree["audit"], tree["deliveries"], hotel_id="hotel_x").evaluate()
    assert primer["verdict"] == segundo["verdict"]
    assert primer["evidence_tier"] == segundo["evidence_tier"]


# ── AC9 · lector sobre baseline real, con skip visible ────────────────


BASELINE_RUN = Path("output/TAREA7-2026-09-19")


def _baseline_audit_dir():
    if not BASELINE_RUN.is_dir():
        return None
    for candidate in BASELINE_RUN.rglob("v4_audit"):
        if candidate.is_dir():
            return candidate
    return None


def test_lector_de_insumos_sobre_baseline_real():
    audit = _baseline_audit_dir()
    if audit is None:
        pytest.skip("baseline output/TAREA7-2026-09-19 ausente: AC9 sin certificar en esta maquina")

    ri = ReviewInputs.for_run(audit, deliveries_dir=audit.parents[1] / "deliveries")
    propuesta = ri.read_document(KIND_PROPUESTA)
    assert propuesta.read_status in (READ_OK, READ_ABSENT)
    if propuesta.read_status == READ_OK:
        assert propuesta.content.strip()
        assert propuesta.source == "legacy-ancestor-walk"
    else:
        assert propuesta.cause, "ABSENT sin causa declarada"

    manifiesto = ri.read_manifest_json()
    assert manifiesto.read_status in (READ_OK, READ_ABSENT, READ_ERROR)
    if manifiesto.read_status != READ_OK:
        assert manifiesto.cause, "el lector no puede reportar None sin causa"
        assert manifiesto.content is None


def test_lector_nuevo_no_devuelve_favorable_ante_un_paquete_roto(tmp_path):
    tree = _run(tmp_path)
    roto = tree["deliveries"] / "hotel_x_20261006.zip.tmp"
    roto.write_bytes(b"esto no es un zip")

    ri = ReviewInputs.for_run(
        tree["audit"], run_id=RUN_ID, deliveries_dir=tree["deliveries"], package_zip_path=roto
    )
    read = ri.read_manifest_json()
    assert read.read_status == READ_ERROR
    assert read.content is None
    assert "abrir" in read.cause


# ── Cable de produccion (AST): la ruta de `main.py` realmente usa el resolvedor ──
#
# Ninguna prueba de esta bateria ejecuta `main.py v4complete` (§Corrida unica). El cable
# se verifica sobre el AST de la funcion de produccion, como hizo FASE-D con su guard.


def _cuerpo_v4_complete():
    import ast
    import main

    source = Path(main.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_v4_complete_mode":
            return node
    raise AssertionError("run_v4_complete_mode no existe en main.py")


def _calls(node, predicate):
    import ast

    return [n for n in ast.walk(node) if isinstance(n, ast.Call) and predicate(n)]


def test_main_congela_los_insumos_antes_de_borrar_los_documentos():
    """El orden temporal es el contrato: borrar sin captura deja el insumo en NO_LEIDO."""
    import ast

    cuerpo = _cuerpo_v4_complete()
    captura = _calls(cuerpo, lambda n: isinstance(n.func, ast.Name) and n.func.id == "capture_review_inputs")
    borrados = _calls(cuerpo, lambda n: isinstance(n.func, ast.Attribute) and n.func.attr == "unlink")

    assert captura, "main.py ya no congela los insumos del Tribunal antes del borrado"
    assert borrados, "se perdio el borrado: la retencion por gate es parte del contrato"
    assert min(c.lineno for c in captura) < max(b.lineno for b in borrados)
    assert all(c.lineno < max(b.lineno for b in borrados) for c in captura)


def test_main_pasa_el_resolvedor_al_juez_y_a_los_cuatro_bots():
    """AC11: un solo resolvedor consumido por los cinco lectores, no cuatro globs."""
    import ast

    cuerpo = _cuerpo_v4_complete()
    for nombre in (
        "DiagnosisReviewer",
        "AssetReviewer",
        "AlignmentReviewer",
        "HonestyReviewer",
        "TribunalJudge",
    ):
        calls = _calls(cuerpo, lambda n, nb=nombre: isinstance(n.func, ast.Name) and n.func.id == nb)
        assert calls, f"{nombre} ya no se construye en run_v4_complete_mode"
        for call in calls:
            keywords = {k.arg for k in call.keywords}
            assert "review_inputs" in keywords, f"{nombre} recibe rutas propias: perdio el resolvedor"
