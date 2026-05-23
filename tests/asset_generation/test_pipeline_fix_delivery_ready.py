"""
Tests para PIPELINE-FIX (FASE-PF-2): delivery_ready_percentage con confidence_score.

Fórmula correcta: assets con confidence_score >= 0.65 son "delivery ready".
No se usa preflight_status (WARNING) para esta métrica.

Verifica:
1. Asset con confidence=0.8 + preflight=WARNING → cuenta como "ready"
2. Asset con confidence=0.5 → NO cuenta como "ready"
3. Asset con confidence=0.65 → cuenta como "ready" (boundary)
4. Asset con confidence=0.64 → NO cuenta como "ready" (boundary)
5. Escenario: 11/12 >=0.65 → 91.67%
6. Edge case: 0 assets → 0.0%
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.asset_generation.v4_asset_orchestrator import (
    AssetGenerationResult,
    GeneratedAsset,
    FailedAsset,
    SkippedAsset,
)
from modules.commercial_documents.coherence_validator import CoherenceReport


def make_coherence_report():
    from modules.commercial_documents.coherence_validator import CoherenceCheck
    return CoherenceReport(
        is_coherent=True,
        overall_score=0.85,
        checks=[],
    )


def test_confidence_08_warning_ready():
    """Asset con confidence=0.8 y preflight=WARNING → cuenta como 'ready'."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="test_asset",
                filename="test.md",
                path="/tmp/test.md",
                metadata_path="/tmp/test_meta.json",
                preflight_status="WARNING",
                confidence_score=0.80,
                pain_ids_resolved=["pain_1"],
                can_use=True,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 100.0, \
        f"Expected 100.0%, got {d['summary']['delivery_ready_percentage']}"


def test_confidence_05_not_ready():
    """Asset con confidence=0.5 → NO cuenta como 'ready'."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="test_asset",
                filename="test.md",
                path="/tmp/test.md",
                metadata_path="/tmp/test_meta.json",
                preflight_status="PASSED",
                confidence_score=0.50,
                pain_ids_resolved=[],
                can_use=False,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 0.0, \
        f"Expected 0.0%, got {d['summary']['delivery_ready_percentage']}"


def test_confidence_065_boundary_ready():
    """Asset con confidence=0.65 → cuenta como 'ready' (boundary inclusive)."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="test_asset",
                filename="test.md",
                path="/tmp/test.md",
                metadata_path="/tmp/test_meta.json",
                preflight_status="PASSED",
                confidence_score=0.65,
                pain_ids_resolved=["pain_1"],
                can_use=True,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 100.0, \
        f"Expected 100.0%, got {d['summary']['delivery_ready_percentage']}"


def test_confidence_064_boundary_not_ready():
    """Asset con confidence=0.64 → NO cuenta como 'ready' (boundary exclusive)."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="test_asset",
                filename="test.md",
                path="/tmp/test.md",
                metadata_path="/tmp/test_meta.json",
                preflight_status="PASSED",
                confidence_score=0.64,
                pain_ids_resolved=[],
                can_use=True,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 0.0, \
        f"Expected 0.0%, got {d['summary']['delivery_ready_percentage']}"


def test_11_of_12_ready_917():
    """Escenario: 11/12 assets >= 0.65 → 91.67%."""
    assets = []
    for i in range(12):
        if i < 11:
            assets.append(
                GeneratedAsset(
                    asset_type=f"asset_{i}",
                    filename=f"asset_{i}.md",
                    path=f"/tmp/asset_{i}.md",
                    metadata_path=f"/tmp/asset_{i}_meta.json",
                    preflight_status="WARNING",
                    confidence_score=0.80,
                    pain_ids_resolved=[f"pain_{i}"],
                    can_use=True,
                )
            )
        else:
            assets.append(
                GeneratedAsset(
                    asset_type=f"asset_{i}",
                    filename=f"asset_{i}.md",
                    path=f"/tmp/asset_{i}.md",
                    metadata_path=f"/tmp/asset_{i}_meta.json",
                    preflight_status="WARNING",
                    confidence_score=0.50,
                    pain_ids_resolved=[],
                    can_use=False,
                )
            )
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Hotel Castilla Real",
        generated_assets=assets,
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    expected = round((11 / 12) * 100, 2)
    assert d["summary"]["delivery_ready_percentage"] == expected, \
        f"Expected {expected}%, got {d['summary']['delivery_ready_percentage']}"


def test_zero_assets_zero_percent():
    """Edge case: 0 generated_assets → 0.0%."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 0.0, \
        f"Expected 0.0%, got {d['summary']['delivery_ready_percentage']}"


def test_estimated_field_preserved():
    """Campo 'estimated' se preserva para backward compat."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="test_asset",
                filename="test.md",
                path="/tmp/test.md",
                metadata_path="/tmp/test_meta.json",
                preflight_status="WARNING",
                confidence_score=0.80,
                pain_ids_resolved=["pain_1"],
                can_use=True,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert "estimated" in d["summary"], "'estimated' field missing from summary"
    assert d["summary"]["estimated"] == 1, \
        f"Expected estimated=1 (1 WARNING), got {d['summary']['estimated']}"


def test_all_confident_ready():
    """Todos los assets con confidence >= 0.65 → 100%."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="asset_a",
                filename="a.md",
                path="/tmp/a.md",
                metadata_path="/tmp/a_meta.json",
                preflight_status="WARNING",
                confidence_score=0.90,
                pain_ids_resolved=["p1"],
                can_use=True,
            ),
            GeneratedAsset(
                asset_type="asset_b",
                filename="b.md",
                path="/tmp/b.md",
                metadata_path="/tmp/b_meta.json",
                preflight_status="PASSED",
                confidence_score=0.65,
                pain_ids_resolved=["p2"],
                can_use=True,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 100.0


def test_none_confident_ready():
    """Ningún asset con confidence >= 0.65 → 0%."""
    result = AssetGenerationResult(
        hotel_id="test_001",
        hotel_name="Test Hotel",
        generated_assets=[
            GeneratedAsset(
                asset_type="asset_a",
                filename="a.md",
                path="/tmp/a.md",
                metadata_path="/tmp/a_meta.json",
                preflight_status="WARNING",
                confidence_score=0.30,
                pain_ids_resolved=[],
                can_use=False,
            ),
            GeneratedAsset(
                asset_type="asset_b",
                filename="b.md",
                path="/tmp/b.md",
                metadata_path="/tmp/b_meta.json",
                preflight_status="WARNING",
                confidence_score=0.64,
                pain_ids_resolved=[],
                can_use=False,
            ),
        ],
        failed_assets=[],
        coherence_report=make_coherence_report(),
    )
    d = result.to_dict()
    assert d["summary"]["delivery_ready_percentage"] == 0.0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])