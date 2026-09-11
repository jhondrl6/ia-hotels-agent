"""AlignmentReviewer — Bot 2 del tribunal de certificación.

Revisor híbrido que extrae promesas verbales de la propuesta y las verifica
deterministamente contra la matriz. Produce revision_alineacion.json.

Flujo:
1. LLM extrae promesas verbales de 02_PROPUESTA_COMERCIAL.md
2. Capa determinista cruza cada promesa contra proposal_asset_matrix.json
3. Clasifica: ALINEADO / SIN-BRECHA-ASOCIADA / PROMESA-SIN-MATRIZ
4. Detecta S-C4: tabla de assets técnicos como tercera superficie de promesa
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from modules.quality_gates.tribunal.llm_extractor import (
    LLMPromiseExtractor,
    PromiseExtractor,
    VerbalPromise,
)


STATUS_ALINEADO = "ALINEADO"
STATUS_SIN_BRECHA = "SIN-BRECHA-ASOCIADA"
STATUS_PROMESA_SIN_MATRIZ = "PROMESA-SIN-MATRIZ"

VERDICT_APROBADO = "APROBADO"
VERDICT_DEVOLVER = "DEVOLVER-PRUEBAS"
VERDICT_BLOQUEAR = "BLOQUEAR"


class AlignmentReviewer:
    """Revisor híbrido de alineación NL (Bot 2).

    Constructor: ``AlignmentReviewer(v4_audit_dir)``.
    Lee propuesta + matriz, extrae promesas verbales (LLM), verifica contra matriz.
    """

    def __init__(self, v4_audit_dir: str | Path):
        self.v4_audit_dir = Path(v4_audit_dir)

    def review(self, extractor: Optional[PromiseExtractor] = None) -> dict:
        """Retorna revision_alineacion.json con service_matrix y findings.

        Args:
            extractor: Extractor de promesas (si es None, usa LLMPromiseExtractor).
        """
        if extractor is None:
            extractor = LLMPromiseExtractor()

        proposal_text = self._load_proposal()
        matrix = self._load_proposal_matrix()
        pain_ledger_resolved = self._load_pain_ledger_resolved()

        if proposal_text is None:
            return self._error_report("No se encontró 02_PROPUESTA_COMERCIAL*.md")
        if matrix is None:
            return self._error_report("No se encontró proposal_asset_matrix.json")

        verbal_promises = extractor.extract_verbal_promises(proposal_text)
        matrix_entries = self._build_matrix_lookup(matrix)

        service_matrix = []
        findings = []

        for promise in verbal_promises:
            entry = self._find_matrix_entry(promise, matrix_entries)
            classification = self._classify_promise(promise, entry, matrix)
            service_matrix.append(classification)
            if classification["status"] == STATUS_PROMESA_SIN_MATRIZ:
                findings.append(self._make_finding(
                    "PROMESA_SIN_MATRIZ",
                    f"Promesa verbal '{promise.text[:50]}...' sin entrada en matriz",
                    promise.location,
                ))

        s_c4_finding = self._detect_technical_assets_table(proposal_text)
        if s_c4_finding:
            findings.append(s_c4_finding)

        summary = self._compute_summary(service_matrix)
        verdict = self._compute_verdict(findings)

        return {
            "reviewer": "alignment_reviewer",
            "clause": "P6.2",
            "service_matrix": service_matrix,
            "findings": findings,
            "summary": summary,
            "verdict_recommendation": verdict,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def write_report(self, extractor: Optional[PromiseExtractor] = None, output_path: Optional[Path] = None) -> Path:
        """Escribe revision_alineacion.json y retorna la ruta."""
        report = self.review(extractor)
        if output_path is None:
            output_path = self.v4_audit_dir / "revision_alineacion.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_path

    def _load_proposal(self) -> Optional[str]:
        """Carga 02_PROPUESTA_COMERCIAL*.md (más reciente)."""
        pattern = "02_PROPUESTA_COMERCIAL*.md"
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None

    def _load_proposal_matrix(self) -> Optional[dict]:
        """Carga proposal_asset_matrix.json."""
        path = self.v4_audit_dir / "proposal_asset_matrix.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_pain_ledger_resolved(self) -> Optional[dict]:
        """Carga pain_ledger_resolved.json (opcional, para contexto)."""
        pattern = "pain_ledger_resolved*.json"
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        if not matches:
            return None
        try:
            with open(matches[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _build_matrix_lookup(self, matrix: dict) -> dict:
        """Construye lookup service_name → entry desde la matriz."""
        entries = matrix.get("entries", [])
        lookup = {}
        for entry in entries:
            service_name = entry.get("service_name", "")
            if service_name:
                lookup[service_name.lower()] = entry
        return lookup

    def _find_matrix_entry(self, promise: VerbalPromise, matrix_lookup: dict) -> Optional[dict]:
        """Busca entrada de matriz correspondiente a una promesa verbal.

        Usa service_hint del LLM para matching. Si no hay match exacto,
        intenta fuzzy match por palabras clave.
        """
        hint = promise.service_hint.lower()
        for service_name, entry in matrix_lookup.items():
            if hint in service_name or service_name in hint:
                return entry

        for service_name, entry in matrix_lookup.items():
            words = set(service_name.split())
            hint_words = set(hint.split())
            if words & hint_words:
                return entry

        return None

    def _classify_promise(self, promise: VerbalPromise, entry: Optional[dict], matrix: dict) -> dict:
        """Clasifica una promesa verbal contra la matriz.

        Retorna dict con: service, status, verbal_promise_found, promise_text,
        matrix_entry_found, pain_id, finding.
        """
        result = {
            "service": promise.service_hint,
            "status": None,
            "verbal_promise_found": True,
            "promise_text": promise.text,
            "matrix_entry_found": entry is not None,
            "pain_id": None,
            "finding": None,
        }

        if entry is None:
            result["status"] = STATUS_PROMESA_SIN_MATRIZ
            result["finding"] = f"Promesa verbal sin entrada en matriz: '{promise.text[:80]}'"
            return result

        status = entry.get("status", "")
        pain_ids = entry.get("pain_ids", [])

        if status == "LINKED":
            if pain_ids:
                result["status"] = STATUS_ALINEADO
                result["pain_id"] = pain_ids[0] if pain_ids else None
            else:
                result["status"] = STATUS_SIN_BRECHA
                result["finding"] = "Servicio LINKED sin pain_id asociado"
        elif status == "PRESENT_IN_PRODUCTION":
            result["status"] = STATUS_ALINEADO
            result["pain_id"] = pain_ids[0] if pain_ids else None
            result["finding"] = "Presente en producción"
        elif status == "NO_BREACH":
            result["status"] = STATUS_SIN_BRECHA
            result["finding"] = "Servicio sin brecha asociada (NO_BREACH)"
        else:
            result["status"] = STATUS_SIN_BRECHA
            result["finding"] = f"Estado no estándar: {status}"

        return result

    def _detect_technical_assets_table(self, proposal_text: str) -> Optional[dict]:
        """Detecta S-C4: tabla de assets técnicos como tercera superficie de promesa.

        La tabla de assets técnicos se imprime incondicionalmente en la propuesta
        (template línea 76: ${technical_assets_table}). Esto es una superficie de
        promesa adicional que Bot 2 debe señalar.
        """
        pattern = r"\|\s*Asset Técnico\s*\|\s*Estado\s*\|\s*Descripción\s*\|"
        if re.search(pattern, proposal_text, re.IGNORECASE):
            return {
                "finding_type": "S_C4_TECHNICAL_ASSETS_TABLE",
                "clause": "P6.2",
                "severity": "WARNING",
                "description": "Tabla de assets técnicos detectada como tercera superficie de promesa (S-C4)",
                "source_artifact": "02_PROPUESTA_COMERCIAL.md",
            }
        return None

    def _compute_summary(self, service_matrix: list) -> dict:
        """Calcula resumen de clasificaciones."""
        aligned = sum(1 for s in service_matrix if s["status"] == STATUS_ALINEADO)
        no_breach = sum(1 for s in service_matrix if s["status"] == STATUS_SIN_BRECHA)
        promise_without_matrix = sum(1 for s in service_matrix if s["status"] == STATUS_PROMESA_SIN_MATRIZ)
        return {
            "aligned": aligned,
            "no_breach": no_breach,
            "promise_without_matrix": promise_without_matrix,
            "total": len(service_matrix),
        }

    def _compute_verdict(self, findings: list) -> str:
        """Calcula veredicto recomendado basado en findings."""
        critical_count = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        warning_count = sum(1 for f in findings if f.get("severity") == "WARNING")

        if critical_count > 0:
            return VERDICT_BLOQUEAR
        if warning_count >= 3:
            return VERDICT_DEVOLVER
        return VERDICT_APROBADO

    def _make_finding(self, finding_type: str, description: str, location: str) -> dict:
        """Construye un finding."""
        return {
            "finding_type": finding_type,
            "clause": "P6.2",
            "severity": "WARNING",
            "description": description,
            "source_artifact": "02_PROPUESTA_COMERCIAL.md",
            "location": location,
        }

    def _error_report(self, message: str) -> dict:
        """Retorna reporte de error cuando faltan artefactos."""
        return {
            "reviewer": "alignment_reviewer",
            "clause": "P6.2",
            "service_matrix": [],
            "findings": [{
                "finding_type": "MISSING_ARTIFACT",
                "clause": "P6.2",
                "severity": "CRITICAL",
                "description": message,
                "source_artifact": "N/A",
            }],
            "summary": {"aligned": 0, "no_breach": 0, "promise_without_matrix": 0, "total": 0},
            "verdict_recommendation": VERDICT_BLOQUEAR,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def _list_artifacts_read(self) -> list:
        """Lista artefactos que este revisor lee."""
        return [
            "02_PROPUESTA_COMERCIAL*.md",
            "proposal_asset_matrix.json",
            "pain_ledger_resolved*.json",
        ]
