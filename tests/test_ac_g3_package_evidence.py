"""Tests AC-G3: Identidad del paquete suprimido.

Verifica que:
- _compute_package_evidence calcula SHA256 y member_count correctamente
- La evidencia se agrega al acta antes de suprimir el ZIP
- El acta MD renderiza la sección de evidencia del paquete
"""
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
import pytest


def test_compute_package_evidence_basic():
    """AC-G3: _compute_package_evidence calcula SHA256 y member_count."""
    from main import _compute_package_evidence

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / "test.zip"

        # Crear un ZIP con 3 archivos
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
            zf.writestr("dir/file3.txt", "content3")

        evidence = _compute_package_evidence(zip_path)

        assert "sha256" in evidence
        assert "member_count" in evidence
        assert evidence["member_count"] == 3
        assert len(evidence["sha256"]) == 64  # SHA256 hex length

        # Verificar SHA256 manualmente
        sha256_hash = hashlib.sha256()
        with open(zip_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        assert evidence["sha256"] == sha256_hash.hexdigest()


def test_compute_package_evidence_empty_zip():
    """AC-G3: ZIP vacío debe tener member_count=0."""
    from main import _compute_package_evidence

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / "empty.zip"

        with zipfile.ZipFile(zip_path, 'w') as zf:
            pass  # ZIP vacío

        evidence = _compute_package_evidence(zip_path)

        assert evidence["member_count"] == 0
        assert evidence["sha256"] is not None


def test_compute_package_evidence_missing_file():
    """AC-G3: Archivo inexistente debe retornar error."""
    from main import _compute_package_evidence

    evidence = _compute_package_evidence(Path("/nonexistent/file.zip"))

    assert evidence["sha256"] is None
    assert evidence["member_count"] is None
    assert "error" in evidence


def test_acta_writer_renders_package_evidence():
    """AC-G3: ActaWriter renderiza la sección de evidencia del paquete."""
    from modules.quality_gates.tribunal.acta_writer import ActaWriter

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        acta = {
            "verdict": "BLOQUEADO",
            "evidence_tier": "C",
            "hotel_id": "test-hotel",
            "timestamp": "2026-09-15T10:00:00Z",
            "clauses_evaluated": 6,
            "clauses": {},
            "reviewer_reports": [],
            "corrective_actions": [],
            "enforcement": {
                "blocking_env": "TRIBUNAL_BLOCKING",
                "enabled": True,
                "suppressed_by_operator": False,
            },
            "package_evidence": {
                "suppressed": True,
                "path": "/tmp/test.zip.tmp",
                "sha256": "a" * 64,
                "member_count": 15,
            },
        }

        writer = ActaWriter(tmpdir)
        json_path, md_path = writer.write(acta)

        # Leer el MD y verificar que tiene la sección
        md_content = md_path.read_text(encoding="utf-8")
        assert "Evidencia del Paquete Suprimido" in md_content
        assert "a" * 64 in md_content
        assert "15" in md_content
        assert "/tmp/test.zip.tmp" in md_content


def test_acta_writer_no_package_evidence_when_not_suppressed():
    """AC-G3: No renderiza la sección si el paquete no fue suprimido."""
    from modules.quality_gates.tribunal.acta_writer import ActaWriter

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        acta = {
            "verdict": "APROBADO-PARA-ENTREGA",
            "evidence_tier": "A",
            "hotel_id": "test-hotel",
            "timestamp": "2026-09-15T10:00:00Z",
            "clauses_evaluated": 6,
            "clauses": {},
            "reviewer_reports": [],
            "corrective_actions": [],
            "enforcement": {},
            # No package_evidence o suppressed=False
        }

        writer = ActaWriter(tmpdir)
        json_path, md_path = writer.write(acta)

        md_content = md_path.read_text(encoding="utf-8")
        assert "Evidencia del Paquete Suprimido" not in md_content


def test_acta_writer_package_evidence_with_error():
    """AC-G3: Renderiza error si la evidencia no se pudo computar."""
    from modules.quality_gates.tribunal.acta_writer import ActaWriter

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        acta = {
            "verdict": "BLOQUEADO",
            "evidence_tier": "C",
            "hotel_id": "test-hotel",
            "timestamp": "2026-09-15T10:00:00Z",
            "clauses_evaluated": 6,
            "clauses": {},
            "reviewer_reports": [],
            "corrective_actions": [],
            "enforcement": {},
            "package_evidence": {
                "suppressed": True,
                "path": "/tmp/test.zip.tmp",
                "sha256": None,
                "member_count": None,
                "error": "File not found",
            },
        }

        writer = ActaWriter(tmpdir)
        json_path, md_path = writer.write(acta)

        md_content = md_path.read_text(encoding="utf-8")
        assert "Evidencia del Paquete Suprimido" in md_content
        assert "Error al computar evidencia" in md_content
        assert "File not found" in md_content
