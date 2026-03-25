"""
Tests for DeliveryPackager - FASE-7-DELIVERY-V2.

Tests the automated packaging pipeline:
- test_package_creates_zip: ZIP exists with all assets
- test_manifest_complete: Manifest includes all assets
- test_readme_generated: README exists with instructions
"""

import json
import zipfile
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from modules.delivery.delivery_packager import DeliveryPackager


class TestDeliveryPackager:
    """Tests for DeliveryPackager class."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_dir = base_dir / "output"
            output_dir.mkdir()
            deliveries_dir = base_dir / "deliveries"
            deliveries_dir.mkdir()

            yield {
                "base": base_dir,
                "output": output_dir,
                "deliveries": deliveries_dir
            }

    @pytest.fixture
    def sample_hotel_output(self, temp_dirs):
        """Create a sample hotel output structure."""
        hotel_id = "hotel_test"
        hotel_dir = temp_dirs["output"] / hotel_id
        hotel_dir.mkdir()

        # Create sample files
        (hotel_dir / "hotel-schema.json").write_text('{"@type": "Hotel"}', encoding='utf-8')
        (hotel_dir / "geo_playbook.md").write_text("# GEO Playbook\n\nTest content", encoding='utf-8')
        (hotel_dir / "faq_page.md").write_text("# FAQs\n\nTest FAQs", encoding='utf-8')
        (hotel_dir / "boton_whatsapp.html").write_text("<button>WA</button>", encoding='utf-8')

        # Create subdirectory with assets
        assets_dir = hotel_dir / "assets"
        assets_dir.mkdir()
        (assets_dir / "readme.txt").write_text("readme", encoding='utf-8')

        return temp_dirs

    def test_package_creates_zip(self, sample_hotel_output):
        """ZIP file should be created with all assets."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        zip_path = packager.package(
            hotel_id="hotel_test",
            output_dir=str(sample_hotel_output["output"] / "hotel_test")
        )

        # Verify ZIP was created
        assert Path(zip_path).exists(), "ZIP file should exist"
        assert zip_path.endswith(".zip"), "File should be a ZIP"

        # Verify ZIP is valid and contains files
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) > 0, "ZIP should contain files"
            assert any("hotel-schema.json" in n for n in names), "Should contain schema"
            assert any("geo_playbook.md" in n for n in names), "Should contain geo_playbook"

    def test_manifest_complete(self, sample_hotel_output):
        """Manifest should include metadata for all assets."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        zip_path = packager.package(
            hotel_id="hotel_test",
            output_dir=str(sample_hotel_output["output"] / "hotel_test")
        )

        # Extract and verify manifest
        with zipfile.ZipFile(zip_path, 'r') as zf:
            manifest_content = zf.read("MANIFEST.json")
            manifest = json.loads(manifest_content)

            assert manifest["version"] == "1.0.0", "Should have version"
            assert manifest["hotel_id"] == "hotel_test", "Should have hotel_id"
            assert "files" in manifest, "Should have files array"
            assert len(manifest["files"]) > 0, "Should have at least one file"
            assert manifest["total_files"] > 0, "Should count files"

            # Check each file has required fields
            for f in manifest["files"]:
                assert "name" in f, "File should have name"
                assert "size_bytes" in f, "File should have size_bytes"
                assert "type" in f, "File should have type"

    def test_readme_generated(self, sample_hotel_output):
        """README should exist with implementation instructions."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        zip_path = packager.package(
            hotel_id="hotel_test",
            output_dir=str(sample_hotel_output["output"] / "hotel_test")
        )

        # README should be in ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any("README_DELIVERY.md" in n for n in names), "Should contain README"

            # Verify README has key sections
            readme_content = zf.read("README_DELIVERY.md").decode('utf-8')
            assert "Overview" in readme_content or "overview" in readme_content.lower(), "Should have overview section"
            assert "Implementation" in readme_content or "Timeline" in readme_content, "Should have implementation instructions"

    def test_package_with_diagnostic_and_proposal(self, temp_dirs):
        """Should include DIAGNOSTICO.md and PROPUESTA_COMERCIAL.md when provided."""
        # Setup hotel output
        hotel_dir = temp_dirs["output"] / "hotel_with_docs"
        hotel_dir.mkdir()
        (hotel_dir / "geo_playbook.md").write_text("# GEO", encoding='utf-8')

        # Create diagnostic and proposal
        diag_path = temp_dirs["output"] / "DIAGNOSTICO.md"
        diag_path.write_text("# Diagnostic Document", encoding='utf-8')
        prop_path = temp_dirs["output"] / "PROPUESTA_COMERCIAL.md"
        prop_path.write_text("# Proposal Document", encoding='utf-8')

        packager = DeliveryPackager(
            base_output_dir=str(temp_dirs["output"]),
            deliveries_dir=str(temp_dirs["deliveries"])
        )

        zip_path = packager.package(
            hotel_id="hotel_with_docs",
            output_dir=str(hotel_dir),
            diagnostic_path=str(diag_path),
            proposal_path=str(prop_path)
        )

        # Verify docs are in ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any("DIAGNOSTICO.md" in n for n in names), "Should contain DIAGNOSTICO"
            assert any("PROPUESTA_COMERCIAL.md" in n for n in names), "Should contain PROPUESTA"

    def test_collect_files_excludes_manifest(self, sample_hotel_output):
        """Should not include manifest.json from source in packaged files."""
        # Create a manifest.json in source
        hotel_dir = sample_hotel_output["output"] / "hotel_test"
        manifest = hotel_dir / "manifest.json"
        manifest.write_text('{"test": "manifest"}', encoding='utf-8')

        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        zip_path = packager.package(hotel_id="hotel_test", output_dir=str(hotel_dir))

        # Verify manifest.json is not duplicated in ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            # Should only have one MANIFEST.json (the one we generate)
            manifest_count = sum(1 for n in names if "manifest.json" in n.lower())
            assert manifest_count == 1, "Should only have one manifest (the generated one)"

    def test_create_manifest(self, sample_hotel_output):
        """Manifest should contain correct metadata."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        files = [
            {"source": str(sample_hotel_output["output"] / "hotel_test" / "geo_playbook.md"), "dest": "ASSETS/geo_playbook.md"}
        ]

        manifest = packager.create_manifest("hotel_test", files)

        assert manifest["hotel_id"] == "hotel_test"
        assert "generated_at" in manifest
        assert manifest["package_type"] == "automated_delivery"
        assert len(manifest["files"]) == 1
        assert manifest["files"][0]["name"] == "ASSETS/geo_playbook.md"

    def test_create_readme_file(self, sample_hotel_output):
        """README should be created in delivery directory."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        manifest = {
            "total_files": 5,
            "total_size_bytes": 1024
        }

        packager.create_readme(
            sample_hotel_output["deliveries"],
            "hotel_test",
            manifest
        )

        readme_path = sample_hotel_output["deliveries"] / "README_DELIVERY.md"
        assert readme_path.exists(), "README should be created"

        content = readme_path.read_text(encoding='utf-8')
        assert "hotel_test" in content, "Should contain hotel_id"
        assert "Overview" in content, "Should have overview section"

    def test_zip_path_naming(self, sample_hotel_output):
        """ZIP should be named {hotel_id}_{date}.zip."""
        packager = DeliveryPackager(
            base_output_dir=str(sample_hotel_output["output"]),
            deliveries_dir=str(sample_hotel_output["deliveries"])
        )

        zip_path = packager.package(
            hotel_id="mi_hotel_test",
            output_dir=str(sample_hotel_output["output"] / "hotel_test")
        )

        zip_name = Path(zip_path).name
        # Should contain hotel_id and date pattern
        assert "mi_hotel_test" in zip_name, "Should contain hotel_id"
        assert zip_name.endswith(".zip"), "Should end with .zip"


class TestManifestStructure:
    """Tests for manifest structure and content."""

    def test_manifest_required_fields(self, tmp_path):
        """Manifest should have all required fields per v2.5 spec."""
        packager = DeliveryPackager(deliveries_dir=str(tmp_path))

        files = [
            {"source": str(tmp_path / "test.md"), "dest": "ASSETS/test.md"}
        ]
        # Create the file so stat works
        (tmp_path / "test.md").write_text("test", encoding='utf-8')

        manifest = packager.create_manifest("test_hotel", files)

        required_fields = ["version", "hotel_id", "generated_at", "package_type", "files", "total_files", "total_size_bytes"]
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_file_classification(self, tmp_path):
        """Files should be classified correctly by type."""
        packager = DeliveryPackager(deliveries_dir=str(tmp_path))

        test_cases = [
            ("geo_playbook.md", "guide"),
            ("hotel-schema.json", "schema"),
            ("boton_whatsapp.html", "code"),
            ("50_optimized_faqs.csv", "data"),
            ("DIAGNOSTICO.md", "diagnostic"),
            ("PROPUESTA_COMERCIAL.md", "proposal"),
        ]

        for filename, expected_type in test_cases:
            result = packager._classify_file(filename)
            assert result == expected_type, f"{filename} should be {expected_type}, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
