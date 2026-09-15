"""Tests AC-G4/AC-G5: Matriz multi-hotel y causalidad.

Verifica los 3 caminos causales con perfiles offline sintéticos:
1. Gates permiten / revisores permiten → publicar
2. Gates permiten / revisores objeta → bloquear
3. Gates ya bloquean → no escribir ZIP

NR7: Cada detección debe tener par green/red (mutación).

[ANOTACIÓN P6-R 2026-09-15 — auditoría forense I1] Este archivo construye el acta
base como dict y puebla `ReviewerReport` a mano: certifica la **lógica del Juez**
(unitario), no el flujo. La prohibición del plan ("no escribir un acta a mano como
sustituto del flujo") aplica a la certificación de AC-G4/G5, que desde P6-R vive
en `tests/test_p6r_full_flow_matrix.py` (packager.write → ZIP real → 4 Bots →
Juez → publish/suppress). Estos tests se conservan como regresión del Juez.
"""
import json
import tempfile
from pathlib import Path
import pytest


def test_causal_path_1_gates_allow_reviewers_allow():
    """AC-G5 Path 1: Gates permiten Y revisores permiten → ZIP se publica.

    Perfil: Hotel con datos completos, sin contradicciones, evidence tier A.
    """
    from modules.quality_gates.tribunal.judge import TribunalJudge, VERDICT_APPROVED
    from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        v4_audit_dir = Path(tmpdir) / "v4_audit"
        deliveries_dir = Path(tmpdir) / "deliveries"
        v4_audit_dir.mkdir(exist_ok=True)
        deliveries_dir.mkdir(exist_ok=True)

        # Simular acta base con todas las cláusulas PASS
        base_acta = {
            "verdict": "PRE-APPROVED",
            "evidence_tier": "A",
            "hotel_id": "hotel-perfil-1",
            "clauses": {
                "P6.1": {"status": "PASS", "finding": "Diagnóstico completo"},
                "P6.2": {"status": "PASS", "finding": "Alineación verificada"},
                "P6.3": {"status": "PASS", "finding": "Assets completos"},
                "P6.4": {"status": "PASS", "finding": "Cobertura completa"},
                "P6.5": {"status": "PASS", "finding": "Honestidad verificada"},
                "P6.6": {"status": "PASS", "finding": "Sin contradicciones"},
            },
            "first_floor_rule": {"applied": False},
        }

        # Simular reports de los 4 revisores sin hallazgos
        reports = [
            ReviewerReport(
                reviewer="diagnosis_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="alignment_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="asset_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="honesty_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
        ]

        judge = TribunalJudge(v4_audit_dir, deliveries_dir)
        enriched_acta = judge.enrich(base_acta, reports)
        outcome = judge.finalize(enriched_acta, reports, blocks=False)

        # Path 1: Debe aprobar
        assert outcome.verdict == VERDICT_APPROVED
        assert not outcome.blocks_publish


def test_causal_path_2_gates_allow_reviewers_object():
    """AC-G5 Path 2: Gates permiten PERO revisores objeta → ZIP se bloquea.

    Perfil: Hotel con datos completos PERO con contradicción crítica detectada
    por honesty_reviewer.
    """
    from modules.quality_gates.tribunal.judge import TribunalJudge, VERDICT_BLOCKED, blocks_delivery_zip
    from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        v4_audit_dir = Path(tmpdir) / "v4_audit"
        deliveries_dir = Path(tmpdir) / "deliveries"
        v4_audit_dir.mkdir(exist_ok=True)
        deliveries_dir.mkdir(exist_ok=True)

        # Acta base con cláusulas PASS (gates permiten)
        base_acta = {
            "verdict": "PRE-APPROVED",
            "evidence_tier": "B",
            "hotel_id": "hotel-perfil-2",
            "clauses": {
                "P6.1": {"status": "PASS", "finding": "Diagnóstico completo"},
                "P6.2": {"status": "PASS", "finding": "Alineación verificada"},
                "P6.3": {"status": "PASS", "finding": "Assets completos"},
                "P6.4": {"status": "PASS", "finding": "Cobertura completa"},
                "P6.5": {"status": "PASS", "finding": "Honestidad verificada"},
                "P6.6": {"status": "PASS", "finding": "Sin contradicciones"},
            },
            "first_floor_rule": {"applied": False},
        }

        # honesty_reviewer detecta hallazgo CRITICAL
        reports = [
            ReviewerReport(
                reviewer="diagnosis_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="alignment_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="asset_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="honesty_reviewer",
                status=ReviewerStatus.OK_WITH_FINDINGS,
                findings_count=1,
                critical_count=1,  # CRITICAL: contradicción de precio
                recommendation="BLOCK",
                findings=[{
                    "type": "pricing_contradiction",
                    "severity": "CRITICAL",
                    "artifact": "PROPUESTA_COMERCIAL.md",
                    "description": "ADR prometido ($500K) vs benchmark regional ($200K)",
                }],
            ),
        ]

        judge = TribunalJudge(v4_audit_dir, deliveries_dir)
        enriched_acta = judge.enrich(base_acta, reports)
        blocks = blocks_delivery_zip(enriched_acta)
        outcome = judge.finalize(enriched_acta, reports, blocks=blocks)

        # Path 2: Debe bloquear (revisor objetó con CRITICAL)
        assert outcome.verdict == VERDICT_BLOCKED
        assert outcome.blocks_publish
        assert len(outcome.corrective_actions) > 0


def test_causal_path_3_gates_already_block():
    """AC-G5 Path 3: Gates ya bloquean → ZIP no se escribe.

    Perfil: Hotel con evidence tier C (sin datos financieros válidos).
    La regla del primer piso aplica y limita a condicional.
    """
    from modules.quality_gates.tribunal.judge import TribunalJudge, VERDICT_CONDITIONAL
    from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        v4_audit_dir = Path(tmpdir) / "v4_audit"
        deliveries_dir = Path(tmpdir) / "deliveries"
        v4_audit_dir.mkdir(exist_ok=True)
        deliveries_dir.mkdir(exist_ok=True)

        # Acta base con evidence tier C (primer piso bloquea)
        base_acta = {
            "verdict": "PRE-APPROVED",
            "evidence_tier": "C",  # Tier C → primer piso aplica
            "hotel_id": "hotel-perfil-3",
            "clauses": {
                "P6.1": {"status": "PASS", "finding": "Diagnóstico completo"},
                "P6.2": {"status": "PASS", "finding": "Alineación verificada"},
                "P6.3": {"status": "PASS", "finding": "Assets completos"},
                "P6.4": {"status": "PASS", "finding": "Cobertura completa"},
                "P6.5": {"status": "PASS", "finding": "Honestidad verificada"},
                "P6.6": {"status": "PASS", "finding": "Sin contradicciones"},
            },
            "first_floor_rule": {
                "applied": True,
                "source_artifact": "financial_scenarios.json",
                "reason": "Evidence tier C requiere onboarding completo",
            },
        }

        # Revisores sin hallazgos (pero el primer piso ya bloquea)
        reports = [
            ReviewerReport(
                reviewer="diagnosis_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="alignment_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="asset_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
            ReviewerReport(
                reviewer="honesty_reviewer",
                status=ReviewerStatus.OK_NO_FINDINGS,
                findings_count=0,
                critical_count=0,
                recommendation="APPROVE",
            ),
        ]

        judge = TribunalJudge(v4_audit_dir, deliveries_dir)
        enriched_acta = judge.enrich(base_acta, reports)
        # blocks=True porque el primer piso ya bloquea
        outcome = judge.finalize(enriched_acta, reports, blocks=True)

        # Path 3: Primer piso limita a condicional (gates ya bloquean)
        assert outcome.verdict == VERDICT_CONDITIONAL
        assert outcome.blocks_publish


def test_nr7_mutation_check_path_1_vs_path_2():
    """NR7: Path 1 (approve) vs Path 2 (reject) deben diferir solo en el input del revisor.

    Mutación: cambiar honesty_reviewer de OK_NO_FINDINGS a OK_WITH_FINDINGS con CRITICAL.
    Expected: verdict cambia de APPROVED a RETURN.
    """
    from modules.quality_gates.tribunal.judge import TribunalJudge, VERDICT_APPROVED, VERDICT_BLOCKED, blocks_delivery_zip
    from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        v4_audit_dir = Path(tmpdir) / "v4_audit"
        deliveries_dir = Path(tmpdir) / "deliveries"
        v4_audit_dir.mkdir(exist_ok=True)
        deliveries_dir.mkdir(exist_ok=True)

        base_acta = {
            "verdict": "PRE-APPROVED",
            "evidence_tier": "A",
            "hotel_id": "hotel-mutation-test",
            "clauses": {
                "P6.1": {"status": "PASS", "finding": "OK"},
                "P6.2": {"status": "PASS", "finding": "OK"},
                "P6.3": {"status": "PASS", "finding": "OK"},
                "P6.4": {"status": "PASS", "finding": "OK"},
                "P6.5": {"status": "PASS", "finding": "OK"},
                "P6.6": {"status": "PASS", "finding": "OK"},
            },
            "first_floor_rule": {"applied": False},
        }

        # Path 1: todos OK
        reports_path1 = [
            ReviewerReport(reviewer="diagnosis_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="alignment_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="asset_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="honesty_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
        ]

        # Path 2: honesty_reviewer con hallazgo CRITICAL (mutación)
        reports_path2 = [
            ReviewerReport(reviewer="diagnosis_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="alignment_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="asset_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ReviewerReport(reviewer="honesty_reviewer", status=ReviewerStatus.OK_WITH_FINDINGS, findings_count=1, critical_count=1, recommendation="RETURN"),
        ]

        judge = TribunalJudge(v4_audit_dir, deliveries_dir)

        # Path 1
        enriched1 = judge.enrich(base_acta, reports_path1)
        outcome1 = judge.finalize(enriched1, reports_path1, blocks=False)
        assert outcome1.verdict == VERDICT_APPROVED
        assert not outcome1.blocks_publish

        # Path 2 (mutación)
        enriched2 = judge.enrich(base_acta, reports_path2)
        blocks2 = blocks_delivery_zip(enriched2)
        outcome2 = judge.finalize(enriched2, reports_path2, blocks=blocks2)
        assert outcome2.verdict == VERDICT_BLOCKED
        assert outcome2.blocks_publish

        # NR7: La única diferencia es el input del revisor → el output cambia
        assert outcome1.verdict != outcome2.verdict


def test_multi_hotel_matrix_three_profiles():
    """AC-G4: Matriz con 3 perfiles offline (Don Alfonso anonimizado + 2 sintéticos).

    Perfil 1: Hotel destino boutique (Don Alfonso anonimizado) - tier A, sin hallazgos
    Perfil 2: Hotel de paso (sintético) - tier B, con hallazgo advisory
    Perfil 3: Hotel sin datos financieros (sintético) - tier C, bloqueado por primer piso
    """
    from modules.quality_gates.tribunal.judge import TribunalJudge
    from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

    profiles = [
        {
            "name": "Hotel Destino Boutique (anonimizado)",
            "tier": "A",
            "expected_verdict": "APROBADO-PARA-ENTREGA",
            "blocks": False,
        },
        {
            "name": "Hotel de Paso (sintético)",
            "tier": "B",
            "expected_verdict": "APROBADO-CONDICIONAL-PENDING-ONBOARDING",
            "blocks": False,
        },
        {
            "name": "Hotel Sin Datos (sintético)",
            "tier": "C",
            "expected_verdict": "APROBADO-CONDICIONAL-PENDING-ONBOARDING",
            "blocks": True,
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        v4_audit_dir = Path(tmpdir) / "v4_audit"
        deliveries_dir = Path(tmpdir) / "deliveries"
        v4_audit_dir.mkdir(exist_ok=True)
        deliveries_dir.mkdir(exist_ok=True)
        judge = TribunalJudge(v4_audit_dir, deliveries_dir)

        for profile in profiles:
            base_acta = {
                "verdict": "PRE-APPROVED",
                "evidence_tier": profile["tier"],
                "hotel_id": profile["name"],
                "clauses": {
                    "P6.1": {"status": "PASS", "finding": "OK"},
                    "P6.2": {"status": "PASS", "finding": "OK"},
                    "P6.3": {"status": "PASS", "finding": "OK"},
                    "P6.4": {"status": "PASS", "finding": "OK"},
                    "P6.5": {"status": "PASS", "finding": "OK"},
                    "P6.6": {"status": "PASS", "finding": "OK"},
                },
                "first_floor_rule": {
                    "applied": profile["tier"] == "C",
                    "source_artifact": "financial_scenarios.json" if profile["tier"] == "C" else None,
                    "reason": "Tier C requiere onboarding" if profile["tier"] == "C" else None,
                },
            }

            reports = [
                ReviewerReport(reviewer="diagnosis_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
                ReviewerReport(reviewer="alignment_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
                ReviewerReport(reviewer="asset_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
                ReviewerReport(reviewer="honesty_reviewer", status=ReviewerStatus.OK_NO_FINDINGS, findings_count=0, critical_count=0, recommendation="APPROVE"),
            ]

            enriched = judge.enrich(base_acta, reports)
            outcome = judge.finalize(enriched, reports, blocks=profile["blocks"])

            assert outcome.verdict == profile["expected_verdict"], f"Perfil {profile['name']}: verdict mismatch"
            assert outcome.blocks_publish == profile["blocks"], f"Perfil {profile['name']}: blocks_publish mismatch"
