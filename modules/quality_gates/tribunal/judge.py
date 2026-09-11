"""TribunalJudge — Juez determinista del tribunal de certificación.

Lee outputs de gates y artefactos existentes; NUNCA reimplementa lógica de gates.
Produce un veredicto determinista sobre las 6 cláusulas P6 + regla de primer piso.
"""

import json
import glob
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


VERDICT_APPROVED = "APROBADO-PARA-ENTREGA"
VERDICT_CONDITIONAL = "APROBADO-CONDICIONAL-PENDING-ONBOARDING"
VERDICT_RETURN = "DEVOLVER-CORRECCIONES"
VERDICT_BLOCKED = "BLOQUEADO"

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_ADVISORY = "ADVISORY"
STATUS_NOT_EVALUABLE = "NOT_EVALUABLE"

FIRST_FLOOR_TIERS = {"B", "C"}

# Cláusulas que el Juez puede certificar en T1. P6.2 se excluye porque el plan
# la difiere a T4-A (requiere LLM). P6.5 se excluye porque D-T1.3 (opción a)
# la libera para Bot 4 (honestidad NL); el primer piso vive en first_floor_rule.
T1_CERTIFIABLE_CLAUSES = ("P6.1", "P6.3", "P6.4", "P6.6")

# Veredictos que impiden emitir el ZIP. Un solo punto de decisión para main.py.
BLOCKING_VERDICTS = frozenset({VERDICT_BLOCKED, VERDICT_RETURN})


def blocks_delivery_zip(acta: Optional[dict]) -> bool:
    """True si el veredicto del acta impide el ZIP. Sin acta no bloquea (never-block)."""
    return acta is not None and acta.get("verdict") in BLOCKING_VERDICTS


class TribunalJudge:
    """Juez determinista que certifica las 6 cláusulas P6 + P7.

    Constructor: ``TribunalJudge(v4_audit_dir, deliveries_dir, hotel_id)``.
    ``deliveries_dir`` se resuelve por glob del ``<hotel_id>_<fecha>`` más reciente.
    """

    def __init__(
        self,
        v4_audit_dir: str | Path,
        deliveries_dir: str | Path,
        hotel_id: str = "",
    ):
        self.v4_audit_dir = Path(v4_audit_dir)
        self.deliveries_dir = Path(deliveries_dir)
        self.hotel_id = hotel_id
        self._manifest_cache: Optional[dict] = None

    def evaluate(self) -> dict:
        """Retorna el acta de revisión con veredicto determinista."""
        evidence_tier = self._read_evidence_tier()
        clauses = self._evaluate_clauses()
        first_floor = self._apply_first_floor_rule(evidence_tier)
        verdict = self._compute_verdict(clauses, evidence_tier, first_floor)

        return {
            "verdict": verdict,
            "evidence_tier": evidence_tier,
            "clauses_evaluated": 6,
            "clauses": clauses,
            "reviewer_reports": [],
            "first_floor_rule": first_floor,
            "timestamp": datetime.now().isoformat(),
            "hotel_id": self.hotel_id,
        }

    def _resolve_manifest(self) -> Optional[dict]:
        """Resuelve MANIFEST.json por glob en deliveries_dir (más reciente)."""
        if self._manifest_cache is not None:
            return self._manifest_cache

        if not self.deliveries_dir.exists():
            return None

        hotel_dirs = sorted(
            self.deliveries_dir.glob(f"{self.hotel_id}_*"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )

        for hotel_dir in hotel_dirs:
            manifest_path = hotel_dir / "MANIFEST.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        self._manifest_cache = json.load(f)
                    return self._manifest_cache
                except (json.JSONDecodeError, OSError):
                    continue

        return None

    def _read_evidence_tier(self) -> str:
        """Lee evidence_tier de MANIFEST.json → quality_metadata.evidence_tier."""
        manifest = self._resolve_manifest()
        if manifest is None:
            return "C"
        quality_metadata = manifest.get("quality_metadata", {})
        return quality_metadata.get("evidence_tier", "C")

    def _resolve_artifact(self, pattern: str) -> Optional[Path]:
        """Resuelve artifact timestamped por glob (más reciente)."""
        matches = sorted(
            self.v4_audit_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return matches[0] if matches else None

    def _load_json(self, path: Optional[Path]) -> Optional[dict]:
        """Carga JSON de forma segura (never-block)."""
        if path is None or not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _evaluate_clauses(self) -> dict:
        """Evalúa las 6 cláusulas P6."""
        return {
            "P6.1": self._evaluate_p6_1(),
            "P6.2": self._evaluate_p6_2(),
            "P6.3": self._evaluate_p6_3(),
            "P6.4": self._evaluate_p6_4(),
            "P6.5": {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": None,
                "finding": "Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a",
            },
            "P6.6": self._evaluate_p6_6(),
        }

    def _evaluate_p6_1(self) -> dict:
        """P6.1: Critical recall — gate critical_recall pasó."""
        gate_report = self._load_gate_report()
        if gate_report is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "gate_report_*.json",
                "finding": "gate_report no disponible",
            }

        recall_gate = self._find_gate(gate_report, "critical_recall")
        if recall_gate is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "gate_report_*.json",
                "finding": "gate critical_recall no encontrado en gate_report",
            }

        passed = recall_gate.get("passed", False)
        value = recall_gate.get("value")
        message = recall_gate.get("message", "")

        if passed:
            return {
                "status": STATUS_PASS,
                "source_artifact": "gate_report_*.json",
                "finding": f"critical_recall OK: {message}",
            }
        else:
            return {
                "status": STATUS_FAIL,
                "source_artifact": "gate_report_*.json",
                "finding": f"critical_recall FAIL: {message}",
            }

    def _evaluate_p6_2(self) -> dict:
        """P6.2: Alineación de promesas NL — requiere Bot 2 (futuro).

        En T1, sin el alignment_reviewer implementado, esta cláusula es
        NOT_EVALUABLE. T4-A la implementará con extracción LLM.
        """
        return {
            "status": STATUS_NOT_EVALUABLE,
            "source_artifact": "revision_alineacion.json (T4-A)",
            "finding": "Requiere Bot 2 (alignment_reviewer) — no implementado en T1",
        }

    def _evaluate_p6_3(self) -> dict:
        """P6.3: Completitud de assets — asset_generation_report.

        En T1, lee el asset_generation_report directamente. T2-B implementará
        el asset_reviewer que profundiza en esta cláusula.
        """
        asset_report_path = self._resolve_artifact("asset_generation_report.json")
        asset_report = self._load_json(asset_report_path)

        if asset_report is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "asset_generation_report.json",
                "finding": "asset_generation_report no disponible",
            }

        summary = asset_report.get("summary", {})
        total = summary.get("total_assets", 0)
        generated = summary.get("generated", 0)
        failed = summary.get("failed", 0)

        if total == 0:
            return {
                "status": STATUS_ADVISORY,
                "source_artifact": "asset_generation_report.json",
                "finding": "Sin assets en catálogo",
            }

        if failed > 0:
            return {
                "status": STATUS_FAIL,
                "source_artifact": "asset_generation_report.json",
                "finding": f"{failed}/{total} assets fallidos",
            }

        return {
            "status": STATUS_PASS,
            "source_artifact": "asset_generation_report.json",
            "finding": f"{generated}/{total} assets generados exitosamente",
        }

    def _evaluate_p6_4(self) -> dict:
        """P6.4: Cobertura propuesta→asset — proposal_asset_matrix."""
        matrix_path = self._resolve_artifact("proposal_asset_matrix.json")
        matrix = self._load_json(matrix_path)

        if matrix is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "proposal_asset_matrix.json",
                "finding": "proposal_asset_matrix no disponible",
            }

        delivery_ready = matrix.get("delivery_ready")
        if delivery_ready is not None:
            summary = matrix.get("summary", {})
            promised = summary.get("promised", 0)
            entries = matrix.get("entries", [])
            linked = sum(1 for e in entries if e.get("status") == "LINKED")
            present = sum(1 for e in entries if e.get("status") == "PRESENT_IN_PRODUCTION")

            if delivery_ready:
                return {
                    "status": STATUS_PASS,
                    "source_artifact": "proposal_asset_matrix.json",
                    "finding": f"delivery_ready=true: {promised} servicios prometidos, {linked} linked, {present} en producción",
                }
            else:
                return {
                    "status": STATUS_FAIL,
                    "source_artifact": "proposal_asset_matrix.json",
                    "finding": f"delivery_ready=false: {promised} servicios prometidos, cobertura insuficiente",
                }

        alignment = matrix.get("alignment", {})
        if alignment:
            passed = alignment.get("passed", False)
            coverage = alignment.get("coverage_ratio", 0.0)
            message = alignment.get("message", "")

            if passed:
                return {
                    "status": STATUS_PASS,
                    "source_artifact": "proposal_asset_matrix.json",
                    "finding": f"Cobertura {coverage:.0%}: {message}",
                }
            else:
                return {
                    "status": STATUS_FAIL,
                    "source_artifact": "proposal_asset_matrix.json",
                    "finding": f"Cobertura insuficiente: {message}",
                }

        return {
            "status": STATUS_NOT_EVALUABLE,
            "source_artifact": "proposal_asset_matrix.json",
            "finding": "Formato de proposal_asset_matrix no reconocido",
        }

    def _evaluate_p6_6(self) -> dict:
        """P6.6: Coherencia + contradicciones — gate_report (coherence + hard_contradictions).

        NO lee el flag is_coherent de coherence_validation.json (post-N11/P9,
        el gate coherence ya respeta is_coherent; leer gates es fuente única).
        """
        gate_report = self._load_gate_report()
        if gate_report is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "gate_report_*.json",
                "finding": "gate_report no disponible",
            }

        coherence_gate = self._find_gate(gate_report, "coherence")
        contradictions_gate = self._find_gate(gate_report, "hard_contradictions")

        if coherence_gate is None and contradictions_gate is None:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "gate_report_*.json",
                "finding": "gates coherence y hard_contradictions no encontrados",
            }

        coherence_passed = coherence_gate.get("passed", False) if coherence_gate else None
        contradictions_passed = contradictions_gate.get("passed", False) if contradictions_gate else None

        findings = []
        if coherence_gate:
            coherence_val = coherence_gate.get("value", "N/A")
            findings.append(f"coherence={'PASS' if coherence_passed else 'FAIL'} ({coherence_val})")
        if contradictions_gate:
            contradictions_val = contradictions_gate.get("value", "N/A")
            findings.append(f"hard_contradictions={'PASS' if contradictions_passed else 'FAIL'} ({contradictions_val})")

        all_passed = (coherence_passed is not False) and (contradictions_passed is not False)
        any_fail = (coherence_passed is False) or (contradictions_passed is False)

        if any_fail:
            return {
                "status": STATUS_FAIL,
                "source_artifact": "gate_report_*.json",
                "finding": "; ".join(findings),
            }
        elif all_passed:
            return {
                "status": STATUS_PASS,
                "source_artifact": "gate_report_*.json",
                "finding": "; ".join(findings),
            }
        else:
            return {
                "status": STATUS_NOT_EVALUABLE,
                "source_artifact": "gate_report_*.json",
                "finding": "; ".join(findings),
            }

    def _load_gate_report(self) -> Optional[dict]:
        """Carga gate_report_*.json (resuelve por glob, más reciente)."""
        gate_report_path = self._resolve_artifact("gate_report_*.json")
        return self._load_json(gate_report_path)

    def _find_gate(self, gate_report: dict, gate_name: str) -> Optional[dict]:
        """Busca un gate específico en gate_report → gate_results."""
        gate_results = gate_report.get("gate_results", [])
        for gate in gate_results:
            if gate.get("gate_name") == gate_name:
                return gate
        return None

    def _apply_first_floor_rule(self, evidence_tier: str) -> dict:
        """Regla de primer piso: tier B/C → máximo APROBADO-CONDICIONAL."""
        applied = evidence_tier in FIRST_FLOOR_TIERS
        reason = (
            f"evidence_tier {evidence_tier} → máximo condicional"
            if applied
            else f"evidence_tier {evidence_tier} → sin restricción de primer piso"
        )
        return {"applied": applied, "reason": reason}

    def _compute_verdict(
        self, clauses: dict, evidence_tier: str, first_floor: dict
    ) -> str:
        """Matriz findings → veredicto.

        - Gate blocking fallido → BLOQUEADO
        - Finding CRITICAL de revisores → DEVOLVER-CORRECCIONES
        - Solo WARNING/INFO con gates en verde → primer piso por tier
        - Un WARNING NO degrada por debajo del primer piso
        - APROBADO-PARA-ENTREGA exige Tier A y todas las cláusulas certificables
          de T1 en PASS: sin evidencia evaluable no se certifica la entrega.
        """
        has_blocking_fail = any(
            c.get("status") == STATUS_FAIL
            for key, c in clauses.items()
            if key in ("P6.1", "P6.6")
        )

        if has_blocking_fail:
            return VERDICT_BLOCKED

        has_critical_finding = any(
            c.get("status") == STATUS_FAIL
            for key, c in clauses.items()
            if key in ("P6.3", "P6.4")
        )

        if has_critical_finding:
            return VERDICT_RETURN

        if first_floor["applied"]:
            return VERDICT_CONDITIONAL

        # Sin evidencia certificada no se entrega el veredicto máximo: NOT_EVALUABLE
        # degrada a condicional en lugar de contar como no-bloqueante.
        certifiable = all(
            clauses[key].get("status") == STATUS_PASS for key in T1_CERTIFIABLE_CLAUSES
        )

        if certifiable and evidence_tier == "A":
            return VERDICT_APPROVED

        return VERDICT_CONDITIONAL
