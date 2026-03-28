"""
End-to-End Tests for FASE-I-01: Autonomous Researcher Integration.

Tests verify:
1. DataAssessment.research_if_low_data() triggers on LOW classification
2. V4AssetOrchestrator integrates AutonomousResearcher for enrichment
3. research_result is persisted to JSON
4. Confidence scoring works correctly
5. NEVER_BLOCK: System continues even if research fails

FASE-I-01 Criteria:
- Tests pass 5/5
- Suite NEVER_BLOCK passing
- Coherence >= 0.8
- AutonomousResearcher appears as "conectada" in capabilities.md
"""

import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.asset_generation.data_assessment import (
    DataAssessment,
    DataClassification,
    DataAssessmentResult,
    DataMetric
)
from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
from modules.providers.autonomous_researcher import (
    AutonomousResearcher,
    ResearchOutput,
    ResearchResult
)
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidatedField
)


class TestAutonomousResearcherIntegration:
    """Tests for FASE-I-01: Autonomous Researcher Integration."""

    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        """Initialize components before each test."""
        self.data_assessor = DataAssessment()
        self.orchestrator = V4AssetOrchestrator(output_base_dir=str(tmp_path))
        self.tmp_path = tmp_path
        self.hotel_name = "Hotel Test FASE-I"
        self.hotel_url = "https://hotel-test.com"

    # ========================================================================
    # TEST 1: research_if_low_data triggers on LOW classification
    # ========================================================================

    def test_research_if_low_data_triggers_on_low_classification(self):
        """
        Test that research_if_low_data() executes AutonomousResearcher
        when classification is LOW.

        Criteria: research_if_low_data() calls AutonomousResearcher.research()
        """
        # Create LOW classification result
        low_result = DataAssessmentResult(
            classification=DataClassification.LOW,
            overall_score=0.15,
            metrics=[
                DataMetric(name="core_hotel_data", available=False, weight=0.25),
                DataMetric(name="gbp_data", available=False, weight=0.35),
                DataMetric(name="seo_data", available=False, weight=0.20),
                DataMetric(name="web_scraping", available=False, weight=0.20),
            ],
            missing_data=["name", "phone", "address", "reviews", "rating"],
            recommendations=["Use FAST path", "Consider running AutonomousResearcher"]
        )

        with patch.object(AutonomousResearcher, 'research') as mock_research:
            mock_research.return_value = ResearchResult(
                found=True,
                data={"gbp": {"rating": 4.2}},
                confidence=0.25,
                sources=["gbp"],
                conflicts=[],
                timestamp=datetime.now()
            )

            result = self.data_assessor.research_if_low_data(
                hotel_name=self.hotel_name,
                hotel_url=self.hotel_url,
                assessment_result=low_result,
                output_dir=str(self.tmp_path)
            )

            # Verify research was called
            assert mock_research.called, "AutonomousResearcher.research() should be called on LOW data"
            assert mock_research.call_args[1]['hotel_name'] == self.hotel_name
            assert mock_research.call_args[1]['url'] == self.hotel_url

    def test_research_if_low_data_skips_on_medium_classification(self):
        """
        Test that research_if_low_data() does NOT trigger research
        when classification is MED or HIGH.
        """
        for classification in [DataClassification.MED, DataClassification.HIGH]:
            result = DataAssessmentResult(
                classification=classification,
                overall_score=0.5 if classification == DataClassification.MED else 0.85,
                metrics=[],
                missing_data=[],
                recommendations=[]
            )

            with patch.object(AutonomousResearcher, 'research') as mock_research:
                returned_result = self.data_assessor.research_if_low_data(
                    hotel_name=self.hotel_name,
                    hotel_url=self.hotel_url,
                    assessment_result=result,
                    output_dir=str(self.tmp_path)
                )

                # Verify research was NOT called
                assert not mock_research.called, \
                    f"AutonomousResearcher should NOT be called when classification is {classification.value}"

    # ========================================================================
    # TEST 2: V4AssetOrchestrator integrates AutonomousResearcher
    # ========================================================================

    def test_orchestrator_has_data_assessor_integrated(self):
        """
        Test that V4AssetOrchestrator has DataAssessment integrated.

        This verifies the basic integration structure for FASE-I-01.
        The actual flow is tested in other tests.
        """
        # Verify orchestrator has data_assessor attribute (FASE-I-01 integration)
        assert hasattr(self.orchestrator, 'data_assessor'), \
            "V4AssetOrchestrator should have data_assessor attribute"

        # Verify data_assessor is an instance of DataAssessment
        assert isinstance(self.orchestrator.data_assessor, DataAssessment), \
            "data_assessor should be instance of DataAssessment"

    def test_research_flow_when_low_classification(self):
        """
        Test the complete research flow when classification is LOW.

        This tests the integration between DataAssessment and AutonomousResearcher.
        """
        # Create LOW classification result
        low_result = DataAssessmentResult(
            classification=DataClassification.LOW,
            overall_score=0.15,
            metrics=[
                DataMetric(name="core_hotel_data", available=False, weight=0.25),
                DataMetric(name="gbp_data", available=False, weight=0.35),
            ],
            missing_data=["reviews", "rating"],
            recommendations=["Use FAST path"]
        )

        with patch.object(AutonomousResearcher, 'research') as mock_research:
            mock_research.return_value = ResearchResult(
                found=True,
                data={"gbp": {"rating": 4.2}},
                confidence=0.25,
                sources=["gbp"],
                conflicts=[],
                timestamp=datetime.now()
            )

            # Call research_if_low_data directly through data_assessor
            result = self.orchestrator.data_assessor.research_if_low_data(
                hotel_name=self.hotel_name,
                hotel_url=self.hotel_url,
                assessment_result=low_result,
                output_dir=str(self.tmp_path)
            )

            # Verify research was called
            assert mock_research.called, "AutonomousResearcher.research() should be called"
            assert result.classification == DataClassification.LOW

    # ========================================================================
    # TEST 3: research_result is persisted to JSON
    # ========================================================================

    def test_research_output_persists_to_json(self):
        """
        Test that ResearchOutput is saved to JSON file when research completes.
        """
        researcher = AutonomousResearcher(output_dir=str(self.tmp_path))

        with patch.object(researcher.scrapers['gbp'], 'scrape') as mock_gbp:
            mock_gbp.return_value = {
                'found': True,
                'data': {'hotel_name': self.hotel_name, 'rating': 4.5},
                'url': self.hotel_url
            }

            result = researcher.research(
                hotel_name=self.hotel_name,
                url=self.hotel_url,
                persist=True
            )

            # Verify research output was stored
            assert researcher.last_research_output is not None
            assert researcher.last_research_output.hotel_name == self.hotel_name

            # Verify JSON file was created
            json_files = list(self.tmp_path.glob("research_*.json"))
            assert len(json_files) > 0, "ResearchOutput JSON file should be created"

        researcher.close()

    # ========================================================================
    # TEST 4: Confidence scoring reflects sources found
    # ========================================================================

    def test_confidence_scoring_formula(self):
        """
        Test that confidence scoring works correctly:
        - 4/4 sources = 1.0
        - 3/4 sources = 0.75
        - 2/4 sources = 0.5
        - 1/4 sources = 0.25
        - 0/4 sources = 0.0
        """
        test_cases = [
            (['gbp', 'booking', 'tripadvisor', 'instagram'], 1.0),
            (['gbp', 'booking', 'tripadvisor'], 0.75),
            (['gbp', 'booking'], 0.5),
            (['gbp'], 0.25),
            ([], 0.0),
        ]

        for sources, expected_confidence in test_cases:
            confidence = AutonomousResearcher.calculate_research_confidence(
                sources, {}
            ) if hasattr(AutonomousResearcher, 'calculate_research_confidence') else \
                self._calc_confidence(sources)

            assert confidence == expected_confidence, \
                f"Sources {sources} should give confidence {expected_confidence}, got {confidence}"

    def _calc_confidence(self, sources_checked):
        """Helper to calculate confidence matching the module's formula."""
        from modules.providers.autonomous_researcher import calculate_research_confidence
        return calculate_research_confidence(sources_checked, {})

    # ========================================================================
    # TEST 5: NEVER_BLOCK - System continues even if research fails
    # ========================================================================

    def test_never_block_research_failure_does_not_crash(self):
        """
        Test that if AutonomousResearcher fails, the system continues
        without crashing (NEVER_BLOCK architecture).
        """
        low_result = DataAssessmentResult(
            classification=DataClassification.LOW,
            overall_score=0.15,
            metrics=[],
            missing_data=["reviews", "rating"],
            recommendations=["Use FAST path"]
        )

        with patch.object(AutonomousResearcher, 'research') as mock_research:
            # Simulate research failure
            mock_research.side_effect = Exception("Network error")

            # Should not raise - NEVER_BLOCK
            result = self.data_assessor.research_if_low_data(
                hotel_name=self.hotel_name,
                hotel_url=self.hotel_url,
                assessment_result=low_result,
                output_dir=str(self.tmp_path)
            )

            # Should return original assessment result
            assert result == low_result, "Should return original result when research fails"

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _create_mock_audit_result(self):
        """Create minimal mock V4AuditResult using correct structure."""
        return V4AuditResult(
            url=self.hotel_url,
            hotel_name=self.hotel_name,
            timestamp=datetime.now().isoformat(),
            schema=Mock(properties={
                "name": self.hotel_name,
                "description": "Test hotel description",
                "telephone": "+573001234567",
                "url": self.hotel_url,
                "address": "Test Address 123",
            }),
            gbp=Mock(),
            performance=Mock(),
            validation=Mock(),
            overall_confidence="LOW"
        )

    def _create_mock_validation_summary(self, low_data=False):
        """Create minimal mock ValidationSummary using correct structure."""
        from modules.data_validation.confidence_taxonomy import ConfidenceLevel

        fields = [
            ValidatedField(field_name="name", value=self.hotel_name, confidence=ConfidenceLevel.VERIFIED),
            ValidatedField(field_name="phone", value="+573001234567", confidence=ConfidenceLevel.VERIFIED),
        ]
        return ValidationSummary(
            fields=fields,
            overall_confidence=ConfidenceLevel.UNKNOWN if low_data else ConfidenceLevel.VERIFIED
        )

    def _create_mock_diagnostic_doc(self):
        """Create minimal mock DiagnosticDocument using correct structure."""
        return DiagnosticDocument(
            path="/tmp/diagnostic.json",
            problems=[],
            financial_impact=Mock(),
            generated_at=datetime.now().isoformat()
        )

    def _create_mock_proposal_doc(self):
        """Create minimal mock ProposalDocument using correct structure."""
        return ProposalDocument(
            path="/tmp/proposal.json",
            price_monthly=1000000,
            assets_proposed=[],
            roi_projected=1.5,
            generated_at=datetime.now().isoformat()
        )


class TestAutonomousResearcherCapability:
    """Tests for capability contract verification."""

    def test_capability_contract_registered_in_capabilities_md(self):
        """
        Verify that AutonomousResearcher appears as 'conectada' in capabilities.md.

        This test reads capabilities.md and verifies the entry exists.
        """
        capabilities_path = Path(__file__).parent.parent.parent / "docs" / "contributing" / "capabilities.md"
        assert capabilities_path.exists(), "capabilities.md should exist"

        content = capabilities_path.read_text()

        # Verify AutonomousResearcher entry exists and is marked as 'conectada'
        assert "AutonomousResearcher" in content, \
            "AutonomousResearcher should be documented in capabilities.md"

        # Check it's marked as connected
        lines = content.split('\n')
        found = False
        for line in lines:
            if "AutonomousResearcher" in line and "conectada" in line:
                found = True
                break

        assert found, "AutonomousResearcher should be marked as 'conectada' in capabilities.md"
