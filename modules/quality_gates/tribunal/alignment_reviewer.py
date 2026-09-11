"""AlignmentReviewer — Bot 2 del tribunal de certificación.

Revisor híbrido que extrae promesas verbales de la propuesta y las verifica
deterministamente contra la matriz. Produce revision_alineacion.json.

Flujo:
1. LLM extrae promesas verbales de 02_PROPUESTA_COMERCIAL.md
2. Capa determinista cruza en ambas direcciones: cada promesa contra la matriz
   y cada entrada de matriz sin promesa también se clasifica
3. Clasifica: ALINEADO / SIN-BRECHA-ASOCIADA / PROMESA-SIN-MATRIZ
4. Detecta S-C4: tabla de assets técnicos como tercera superficie de promesa
5. NO_BREACH: si el servicio NO fue prometido, es info legítima (no hallazgo);
   si una promesa cae en una entrada NO_BREACH, es SIN-BRECHA-ASOCIADA (§5.2)
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
        proposal_text = self._load_proposal()
        matrix = self._load_proposal_matrix()
        pain_ledger_resolved = self._load_pain_ledger_resolved()

        if proposal_text is None:
            return self._error_report("No se encontró 02_PROPUESTA_COMERCIAL*.md")
        if matrix is None:
            return self._error_report("No se encontró proposal_asset_matrix.json")

        if extractor is None:
            extractor = LLMPromiseExtractor()

        verbal_promises = extractor.extract_verbal_promises(proposal_text)
        matrix_entries = self._build_matrix_lookup(matrix)

        service_matrix = []
        findings = []
        matched_entry_keys = set()

        for promise in verbal_promises:
            entry_key, entry = self._find_matrix_entry(promise, matrix_entries)
            if entry_key is not None:
                matched_entry_keys.add(entry_key)
            row = self._classify_promise(promise, entry)
            service_matrix.append(row)
            if row["status"] == STATUS_PROMESA_SIN_MATRIZ:
                findings.append(self._make_finding(
                    "PROMESA_SIN_MATRIZ",
                    f"Promesa verbal '{row['promise_text'][:80]}' sin entrada en matriz",
                    promise.location,
                ))
            elif row["status"] == STATUS_SIN_BRECHA:
                findings.append(self._make_finding(
                    "SIN_BRECHA_ASOCIADA",
                    row["finding"],
                    promise.location,
                ))

        no_breach_info = self._cover_unmatched_entries(
            matrix_entries, matched_entry_keys, service_matrix, findings
        )

        s_c4_finding = self._detect_technical_assets_table(proposal_text)
        if s_c4_finding:
            findings.append(s_c4_finding)

        summary = self._compute_summary(service_matrix)
        summary["no_breach_info"] = no_breach_info
        verdict = self._compute_verdict(findings)

        return {
            "reviewer": "alignment_reviewer",
            "clause": "P6.2",
            "service_matrix": service_matrix,
            "findings": findings,
            "summary": summary,
            "verdict_recommendation": verdict,
            "info": {"brechas_en_ledger": self._count_ledger_brechas(pain_ledger_resolved)},
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

    def _find_matrix_entry(self, promise: VerbalPromise, matrix_lookup: dict):
        """Busca (entry_key, entry) correspondiente a una promesa verbal.

        Normaliza guiones bajos y guiones a espacios en ambos lados antes de
        substring matching; si no hay match, intenta intersección de palabras.
        """
        hint = self._normalize(promise.service_hint)
        if not hint:
            return None, None

        for key, entry in matrix_lookup.items():
            name = self._normalize(key)
            if hint in name or name in hint:
                return key, entry

        hint_words = set(hint.split())
        for key, entry in matrix_lookup.items():
            name_words = set(self._normalize(key).split())
            if name_words & hint_words:
                return key, entry

        return None, None

    @staticmethod
    def _normalize(value: str) -> str:
        return value.lower().replace("_", " ").replace("-", " ").strip()

    def _classify_promise(self, promise: VerbalPromise, entry: Optional[dict]) -> dict:
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
            result["finding"] = "Servicio vendido sin brecha asociada (NO_BREACH)"
        else:
            result["status"] = STATUS_SIN_BRECHA
            result["finding"] = f"Estado no estándar: {status}"

        return result

    def _detect_technical_assets_table(self, proposal_text: str) -> Optional[dict]:
        """Detecta S-C4: tabla de assets técnicos como tercera superficie de promesa.

        La tabla la genera incondicionalmente
        ``v4_proposal_generator._generate_technical_assets_table()`` y se inyecta
        en el template vía ``${technical_assets_table}``. Es una superficie de
        promesa adicional que Bot 2 debe señalar al Juez sin alterar el veredicto.
        """
        pattern = r"\|\s*Asset Técnico\s*\|\s*Estado\s*\|\s*Descripción\s*\|"
        if re.search(pattern, proposal_text, re.IGNORECASE):
            return {
                "finding_type": "S_C4_TECHNICAL_ASSETS_TABLE",
                "clause": "P6.2",
                "severity": "INFO",
                "description": "Tabla de assets técnicos detectada como tercera superficie de promesa (S-C4)",
                "source_artifact": "02_PROPUESTA_COMERCIAL.md",
            }
        return None

    def _cover_unmatched_entries(
        self,
        matrix_entries: dict,
        matched_entry_keys: set,
        service_matrix: list,
        findings: list,
    ) -> int:
        """Clasifica entradas de matriz sin promesa verbal (cruce inverso).

        Una entrada LINKED con pain_ids sin promesa sigue siendo ALINEADO
        (responden a una brecha diagnosticada). Una entrada NO_BREACH sin
        promesa es un servicio legítimamente no prometido: se cuenta como
        info, no como hallazgo.

        Retorna el conteo de entradas NO_BREACH no prometidas.
        """
        no_breach_info = 0
        for key, entry in matrix_entries.items():
            if key in matched_entry_keys:
                continue
            status = entry.get("status", "")
            pain_ids = entry.get("pain_ids") or []

            if status == "NO_BREACH":
                no_breach_info += 1
                continue

            row = {
                "service": entry.get("service_name") or key,
                "status": None,
                "verbal_promise_found": False,
                "promise_text": None,
                "matrix_entry_found": True,
                "pain_id": pain_ids[0] if pain_ids else None,
                "finding": None,
            }

            if status == "LINKED" and pain_ids:
                row["status"] = STATUS_ALINEADO
            elif status == "LINKED":
                row["status"] = STATUS_SIN_BRECHA
                row["finding"] = "Servicio LINKED en matriz sin pain_id asociado"
            elif status == "PRESENT_IN_PRODUCTION":
                row["status"] = STATUS_ALINEADO
                row["finding"] = "Presente en producción"
            else:
                row["status"] = STATUS_SIN_BRECHA
                row["finding"] = f"Estado no estándar en matriz: {status}"

            if row["status"] == STATUS_SIN_BRECHA:
                findings.append(self._make_finding(
                    "SIN_BRECHA_ASOCIADA",
                    row["finding"],
                    "proposal_asset_matrix.json",
                ))
            service_matrix.append(row)

        return no_breach_info

    @staticmethod
    def _count_ledger_brechas(ledger) -> int:
        """Brechas registradas en pain_ledger_resolved (divulgación informativa)."""
        if not isinstance(ledger, dict):
            return 0
        return len(ledger.get("entries") or [])

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
        """Veredicto recomendado: BLOQUEAR por artefacto faltante (CRITICAL),
        DEVOLVER-PRUEBAS por hallazgo sustantivo (promesa sin matriz o servicio
        sin brecha), APROBADO en otro caso. Los hallazgos INFO (S-C4) se
        divulgan pero no alteran la recomendación.
        """
        if any(f.get("severity") == "CRITICAL" for f in findings):
            return VERDICT_BLOQUEAR
        escalate = {
            "PROMESA_SIN_MATRIZ": True,
            "SIN_BRECHA_ASOCIADA": True,
        }
        if any(f.get("finding_type") in escalate for f in findings):
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
            "summary": {"aligned": 0, "no_breach": 0, "promise_without_matrix": 0, "total": 0, "no_breach_info": 0},
            "verdict_recommendation": VERDICT_BLOQUEAR,
            "info": {"brechas_en_ledger": 0},
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
