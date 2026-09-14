"""FASE-P2 — O1-cuarentena: el ZIP se escribe antes de decidir y el rename es la decisión.

Todos los tests corren contra un ZIP real generado por ``DeliveryPackager`` y contra
un directorio de entregas real (L-V.1: un fixture sobre un directorio inventado no
certifica el enforcement del pipeline).
"""

import json
import zipfile
from pathlib import Path

import pytest

from modules.delivery.delivery_packager import (
    DeliveryPackager,
    QuarantineSuppressionError,
)
from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.asset_reviewer import AssetReviewer
from modules.quality_gates.tribunal.judge import TribunalJudge
from modules.quality_gates.tribunal.outcome import EXPECTED_REVIEWERS

HOTEL_ID = "hoteltest"


@pytest.fixture
def hotel_layout(tmp_path):
    """output/<hotel>/v4_audit/ con assets y un acta ya escrita en disco."""
    output = tmp_path / "v4_complete"
    output.mkdir()
    hotel_dir = output / HOTEL_ID
    hotel_dir.mkdir()
    (hotel_dir / "boton_whatsapp.html").write_text("<button>WA</button>", encoding="utf-8")
    (hotel_dir / "geo_playbook.md").write_text("# GEO\n\ncontenido real por hotel", encoding="utf-8")

    audit_dir = hotel_dir / "v4_audit"
    audit_dir.mkdir()
    (audit_dir / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": 2, "generated": 2, "failed": 0}}),
        encoding="utf-8",
    )
    # Acta de una corrida anterior: si viajara en el ZIP, fijaría un veredicto viejo.
    (audit_dir / "acta_revision.json").write_text(
        json.dumps({"verdict": "APROBADO-PARA-ENTREGA", "hotel_id": HOTEL_ID}),
        encoding="utf-8",
    )
    (audit_dir / "acta_revision.md").write_text("# Acta vieja\n", encoding="utf-8")

    deliveries = output / "deliveries"
    deliveries.mkdir()
    return {"output": output, "hotel": hotel_dir, "audit": audit_dir, "deliveries": deliveries}


@pytest.fixture
def packager(hotel_layout):
    return DeliveryPackager(
        base_output_dir=str(hotel_layout["output"]),
        deliveries_dir=str(hotel_layout["deliveries"]),
    )


def write_quarantine(packager, hotel_layout):
    return packager.write(
        hotel_id=HOTEL_ID,
        output_dir=str(hotel_layout["hotel"]),
        hotel_name="Hotel Test",
        core_assets=["boton_whatsapp.html"],
        geo_assets=["geo_playbook.md"],
    )


def published_zips(deliveries):
    """El glob que exige AC-E5: ningún ``*.zip`` publicado para este hotel."""
    return sorted(p.name for p in deliveries.glob(f"{HOTEL_ID}_*.zip"))


# ── AC-E2 / AC-E5: la cuarentena y su supresión ──────────────────────────────


def test_write_deja_cuarentena_sin_publicar(packager, hotel_layout):
    """El ZIP existe como ``.zip.tmp`` y no hay nombre definitivo todavía."""
    tmp_path_str = write_quarantine(packager, hotel_layout)
    tmp = Path(tmp_path_str)

    assert tmp.name.endswith(".zip.tmp")
    assert tmp.exists()
    assert zipfile.ZipFile(tmp).read("MANIFEST.json")
    assert published_zips(hotel_layout["deliveries"]) == []


def test_suprimir_la_cuarentena_no_deja_ningun_zip(packager, hotel_layout):
    """AC-E5: con veredicto bloqueante no queda ningún ``*.zip`` del hotel."""
    tmp = Path(write_quarantine(packager, hotel_layout))
    packager.suppress(tmp)

    assert not tmp.exists()
    assert published_zips(hotel_layout["deliveries"]) == []
    assert list(hotel_layout["deliveries"].glob(f"{HOTEL_ID}_*")) == []


def test_publicar_otorga_el_nombre_definitivo_y_validate_zip_pasa(packager, hotel_layout):
    """Veredicto no bloqueante: el ZIP queda publicado y sigue siendo consistente."""
    tmp = Path(write_quarantine(packager, hotel_layout))
    published = Path(packager.publish(tmp))

    assert published.exists()
    assert published.suffix == ".zip"
    assert not tmp.exists()
    assert published_zips(hotel_layout["deliveries"]) == [published.name]

    with zipfile.ZipFile(published) as z:
        manifest = json.loads(z.read("MANIFEST.json"))
        names = set(z.namelist())
    assert names == {f["name"] for f in manifest["files"]}
    assert manifest["total_size_bytes"] == sum(f["size_bytes"] for f in manifest["files"])


def test_borrado_que_falla_es_error_de_infraestructura(packager, hotel_layout, monkeypatch):
    """Contrato §3.4: un ``unlink`` fallido no puede reportarse como supresión lograda."""
    tmp = Path(write_quarantine(packager, hotel_layout))

    def _fallar(self):
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "unlink", _fallar)
    with pytest.raises(QuarantineSuppressionError):
        packager.suppress(tmp)

    assert tmp.exists(), "la cuarentena sigue en disco: no se suprimió nada"


def test_publicar_sin_cuarentena_no_inventa_un_zip(packager, hotel_layout):
    """No se publica lo que no existe: error explícito, no un ZIP vacío."""
    missing = hotel_layout["deliveries"] / f"{HOTEL_ID}_20260914.zip.tmp"
    with pytest.raises(Exception):
        packager.publish(missing)
    assert published_zips(hotel_layout["deliveries"]) == []


# ── Verificación obligatoria de la Tarea 1: ¿el ZIP empaqueta el acta? ───────


def test_el_paquete_no_contiene_el_acta(packager, hotel_layout):
    """Medición: el acta viajaría pre-veredicto dentro del ZIP → excluida.

    Bajo O1-cuarentena los bytes del ZIP se serializan antes de que los revisores
    lean el paquete, así que un acta dentro del ZIP sería necesariamente la
    versión pre-veredicto: el ZIP se contradeciría a sí mismo (DA-P1.1).
    """
    published = Path(packager.publish(write_quarantine(packager, hotel_layout)))

    with zipfile.ZipFile(published) as z:
        names = z.namelist()
        manifest = json.loads(z.read("MANIFEST.json"))

    assert [n for n in names if "acta_revision" in n] == []
    assert [f["name"] for f in manifest["files"] if "acta_revision" in f["name"]] == []


def test_los_revisores_leen_el_paquete_en_cuarentena(packager, hotel_layout):
    """El cableado O1: Bot 3 lee IMPLEMENTATION_ORDER.md desde el ``.zip.tmp``.

    Si el resolutor solo viera ``*.zip``, el artefacto que sí está en disco se
    publicaría como ARTIFACT_MISSING y el veredicto se degradaría por un fallo de
    wiring, no por una objeción verificada.
    """
    tmp_str = write_quarantine(packager, hotel_layout)
    assert published_zips(hotel_layout["deliveries"]) == []

    review = AssetReviewer(hotel_layout["audit"], hotel_layout["deliveries"]).review()

    assert Path(tmp_str).exists(), "la cuarentena debe seguir intacta para el decisor"
    assert review["implementation_order_check"]["status"] == "OK"
    assert review["implementation_order_check"]["source"] == "zip"


# ── El cierre del círculo: veredicto bloqueante sobre ZIP real ───────────────


def _informe_bloqueante(audit_dir):
    """Diagnóstico del Bot 1 con un CRITICAL, como en la corrida real."""
    for spec in EXPECTED_REVIEWERS:
        payload = {"reviewer": spec.reviewer, "findings": [], "verdict_recommendation": "APROBADO"}
        if spec.reviewer == "diagnosis_reviewer":
            payload["findings"] = [{
                "severity": "CRITICAL",
                "clause": "P6.1",
                "finding_type": "VACUOUS_RECALL",
                "source_artifact": "gate_report_*.json",
                "description": "critical_recall=1.0 sin critical_issues_count",
            }]
            payload["verdict_recommendation"] = "BLOQUEAR"
        (audit_dir / spec.report_filename).write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
    return {spec.reviewer: audit_dir / spec.report_filename for spec in EXPECTED_REVIEWERS}


def test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real(hotel_layout, packager):
    """AC-E2 contra ZIP real: el rename no ocurre y no queda paquete publicado."""
    tmp = Path(write_quarantine(packager, hotel_layout))
    written = _informe_bloqueante(hotel_layout["audit"])

    judge = TribunalJudge(
        v4_audit_dir=hotel_layout["audit"],
        deliveries_dir=hotel_layout["deliveries"],
        hotel_id=HOTEL_ID,
    )
    reports = judge.collect_reviewer_reports(written)
    acta = judge.enrich(judge.evaluate(), reports)
    outcome = judge.finalize(
        acta, reports, blocks=True, gate_blocking_enabled=True
    )

    assert acta["verdict"] == "BLOQUEADO"
    assert outcome.blocks_publish is True
    assert outcome.corrective_actions

    ActaWriter(hotel_layout["audit"]).write(acta)
    packager.suppress(tmp)

    assert published_zips(hotel_layout["deliveries"]) == []
    escrito = json.loads(
        (hotel_layout["audit"] / "acta_revision.json").read_text(encoding="utf-8")
    )
    assert escrito["verdict"] == "BLOQUEADO", "el acta publicada debe ser la enriquecida"
    assert escrito["corrective_actions"]


def test_veredicto_no_bloqueante_publica_el_zip_real(hotel_layout, packager):
    """El camino aprobado: sin objeciones verificadas el rename sí ocurre."""
    tmp = Path(write_quarantine(packager, hotel_layout))
    for spec in EXPECTED_REVIEWERS:
        (hotel_layout["audit"] / spec.report_filename).write_text(
            json.dumps({"reviewer": spec.reviewer, "findings": [], "verdict_recommendation": "APROBADO"}),
            encoding="utf-8",
        )
    written = {spec.reviewer: hotel_layout["audit"] / spec.report_filename for spec in EXPECTED_REVIEWERS}

    judge = TribunalJudge(
        v4_audit_dir=hotel_layout["audit"],
        deliveries_dir=hotel_layout["deliveries"],
        hotel_id=HOTEL_ID,
    )
    reports = judge.collect_reviewer_reports(written)
    acta = judge.enrich(judge.evaluate(), reports)
    outcome = judge.finalize(acta, reports, blocks=False, gate_blocking_enabled=True)

    assert outcome.blocks_publish is False
    published = Path(packager.publish(tmp))
    assert published_zips(hotel_layout["deliveries"]) == [published.name]
