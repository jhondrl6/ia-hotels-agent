"""
Tests for Evidence Ledger - Sistema de Registro Inmutable de Evidencias

Fase 2: Tests completos para el ledger de evidencias con verificación
de integridad mediante hash SHA-256.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from data_validation import EvidenceLedger, Evidence, EvidenceType


@pytest.fixture
def ledger():
    """Fixture que proporciona un EvidenceLedger limpio."""
    return EvidenceLedger()


@pytest.fixture
def sample_evidence():
    """Fixture que proporciona una evidencia de ejemplo."""
    return Evidence(
        evidence_id=uuid4(),
        source_type="whatsapp",
        source_url="https://example.com",
        raw_data={"phone": "+1234567890"},
        extracted_value="+1234567890",
        collector_version="1.0.0"
    )


@pytest.fixture
def sample_claim_id():
    """Fixture que proporciona un UUID de claim de ejemplo."""
    return uuid4()


class TestStoreAndRetrieve:
    """Tests para almacenar y recuperar evidencias."""

    def test_store_and_retrieve_evidence(self, ledger, sample_claim_id, sample_evidence):
        """Almacenar y recuperar evidencia exitosamente."""
        # Store evidence
        evidence_hash = ledger.store(sample_claim_id, sample_evidence)

        # Verify hash was returned
        assert isinstance(evidence_hash, str)
        assert len(evidence_hash) == 64  # SHA-256 hex length

        # Retrieve and verify
        retrieved = ledger.retrieve(sample_claim_id)
        assert retrieved is not None
        assert retrieved.evidence_id == sample_evidence.evidence_id
        assert retrieved.source_type == sample_evidence.source_type
        assert retrieved.extracted_value == sample_evidence.extracted_value


class TestIntegrityVerification:
    """Tests para verificación de integridad."""

    def test_verify_integrity_success(self, ledger, sample_claim_id, sample_evidence):
        """Verificar integridad exitosa sin modificaciones."""
        ledger.store(sample_claim_id, sample_evidence)

        result = ledger.verify_integrity(sample_claim_id)
        assert result is True

    def test_verify_integrity_failure(self, ledger, sample_claim_id, sample_evidence):
        """Verificar integridad fallida después de modificación."""
        ledger.store(sample_claim_id, sample_evidence)

        # Modify the stored evidence directly (simulating tampering)
        stored = ledger._storage[sample_claim_id]
        stored.extracted_value = "modified_value"

        result = ledger.verify_integrity(sample_claim_id)
        assert result is False

    def test_verify_integrity_nonexistent_returns_false(self, ledger):
        """Verificar integridad de claim inexistente retorna False."""
        nonexistent_claim_id = uuid4()
        result = ledger.verify_integrity(nonexistent_claim_id)
        assert result is False


class TestFilteringAndRetrieval:
    """Tests para filtrado y recuperación de evidencias."""

    def test_get_by_source_type(self, ledger):
        """Filtrar por tipo de fuente."""
        claim_id_1 = uuid4()
        claim_id_2 = uuid4()
        claim_id_3 = uuid4()

        evidence_1 = Evidence(source_type="whatsapp", extracted_value="123")
        evidence_2 = Evidence(source_type="whatsapp", extracted_value="456")
        evidence_3 = Evidence(source_type="schema", extracted_value="789")

        ledger.store(claim_id_1, evidence_1)
        ledger.store(claim_id_2, evidence_2)
        ledger.store(claim_id_3, evidence_3)

        whatsapp_evidence = ledger.get_by_source("whatsapp")
        assert len(whatsapp_evidence) == 2
        assert all(e.source_type == "whatsapp" for e in whatsapp_evidence)

        schema_evidence = ledger.get_by_source("schema")
        assert len(schema_evidence) == 1
        assert schema_evidence[0].source_type == "schema"

    def test_get_all_returns_copy(self, ledger, sample_claim_id, sample_evidence):
        """get_all retorna copia, no referencia."""
        ledger.store(sample_claim_id, sample_evidence)

        all_evidence = ledger.get_all()
        original_count = len(all_evidence)

        # Modify the returned dictionary
        all_evidence[uuid4()] = sample_evidence

        # Verify ledger is unchanged
        assert ledger.count() == original_count
        assert len(ledger.get_all()) == original_count

    def test_retrieve_nonexistent_returns_none(self, ledger):
        """Recuperar claim inexistente retorna None."""
        nonexistent_claim_id = uuid4()
        result = ledger.retrieve(nonexistent_claim_id)
        assert result is None

    def test_get_by_claim_ids(self, ledger):
        """Recuperar múltiples evidencias."""
        claim_id_1 = uuid4()
        claim_id_2 = uuid4()
        claim_id_3 = uuid4()

        evidence_1 = Evidence(source_type="whatsapp", extracted_value="value1")
        evidence_2 = Evidence(source_type="schema", extracted_value="value2")
        evidence_3 = Evidence(source_type="gbp", extracted_value="value3")

        ledger.store(claim_id_1, evidence_1)
        ledger.store(claim_id_2, evidence_2)
        ledger.store(claim_id_3, evidence_3)

        # Get subset of evidences
        target_claims = [claim_id_1, claim_id_3, uuid4()]  # One non-existent
        result = ledger.get_by_claim_ids(target_claims)

        assert len(result) == 2
        assert claim_id_1 in result
        assert claim_id_3 in result
        assert result[claim_id_1].extracted_value == "value1"
        assert result[claim_id_3].extracted_value == "value3"


class TestDeletion:
    """Tests para eliminación de evidencias."""

    def test_delete_existing(self, ledger, sample_claim_id, sample_evidence):
        """Eliminar evidencia existente."""
        ledger.store(sample_claim_id, sample_evidence)
        assert ledger.count() == 1

        result = ledger.delete(sample_claim_id)
        assert result is True
        assert ledger.count() == 0
        assert ledger.retrieve(sample_claim_id) is None

    def test_delete_nonexistent(self, ledger):
        """Eliminar evidencia inexistente."""
        nonexistent_claim_id = uuid4()
        result = ledger.delete(nonexistent_claim_id)
        assert result is False


class TestLedgerOperations:
    """Tests para operaciones generales del ledger."""

    def test_count(self, ledger):
        """Contar evidencias."""
        assert ledger.count() == 0

        # Add evidences
        for i in range(5):
            claim_id = uuid4()
            evidence = Evidence(source_type="test", extracted_value=f"value_{i}")
            ledger.store(claim_id, evidence)

        assert ledger.count() == 5

        # Delete one
        some_claim_id = list(ledger._storage.keys())[0]
        ledger.delete(some_claim_id)
        assert ledger.count() == 4

    def test_clear(self, ledger):
        """Limpiar almacenamiento."""
        # Add multiple evidences
        for i in range(3):
            claim_id = uuid4()
            evidence = Evidence(source_type="test", extracted_value=f"value_{i}")
            ledger.store(claim_id, evidence)

        assert ledger.count() == 3

        ledger.clear()

        assert ledger.count() == 0
        assert ledger.get_all() == {}
        assert ledger.retrieve(uuid4()) is None

    def test_store_multiple_evidence(self, ledger):
        """Almacenar múltiples evidencias."""
        evidences = []
        claim_ids = []

        for i in range(10):
            claim_id = uuid4()
            evidence = Evidence(
                source_type="test",
                extracted_value=f"value_{i}",
                raw_data={"index": i}
            )
            claim_ids.append(claim_id)
            evidences.append(evidence)
            ledger.store(claim_id, evidence)

        assert ledger.count() == 10

        # Verify all can be retrieved
        for i, claim_id in enumerate(claim_ids):
            retrieved = ledger.retrieve(claim_id)
            assert retrieved is not None
            assert retrieved.extracted_value == f"value_{i}"


class TestEvidenceModel:
    """Tests para el modelo Evidence."""

    def test_evidence_to_dict(self, sample_evidence):
        """Convertir evidencia a diccionario."""
        evidence_dict = sample_evidence.to_dict()

        assert isinstance(evidence_dict, dict)
        assert "evidence_id" in evidence_dict
        assert "claim_id" in evidence_dict
        assert "source_type" in evidence_dict
        assert "source_url" in evidence_dict
        assert "raw_data" in evidence_dict
        assert "extracted_value" in evidence_dict
        assert "timestamp" in evidence_dict
        assert "collector_version" in evidence_dict

        # Verify values
        assert evidence_dict["source_type"] == sample_evidence.source_type
        assert evidence_dict["extracted_value"] == sample_evidence.extracted_value
        assert evidence_dict["evidence_id"] == str(sample_evidence.evidence_id)

    def test_hash_consistency(self, ledger):
        """Consistencia de hashes - mismos datos = mismo hash."""
        claim_id = uuid4()
        fixed_timestamp = "2024-01-01T00:00:00"  # Fixed timestamp for consistency
        evidence_id = uuid4()

        # Create two identical evidences with same all fields
        evidence_1 = Evidence(
            evidence_id=evidence_id,
            claim_id=claim_id,
            source_type="test",
            extracted_value="consistent_value",
            raw_data={"key": "value"},
            timestamp=fixed_timestamp,
            collector_version="1.0.0"
        )

        evidence_2 = Evidence(
            evidence_id=evidence_id,
            claim_id=claim_id,
            source_type="test",
            extracted_value="consistent_value",
            raw_data={"key": "value"},
            timestamp=fixed_timestamp,
            collector_version="1.0.0"
        )

        # Calculate hashes manually
        hash_1 = ledger._calculate_hash(evidence_1)
        hash_2 = ledger._calculate_hash(evidence_2)

        assert hash_1 == hash_2
        assert len(hash_1) == 64  # SHA-256 hex length

        # Store and verify
        stored_hash = ledger.store(claim_id, evidence_1)
        assert stored_hash == hash_1

        # Verify integrity
        assert ledger.verify_integrity(claim_id) is True
