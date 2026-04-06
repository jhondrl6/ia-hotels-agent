"""
DeliveryPackager - Automated packaging of hotel assets for delivery.

Creates ZIP packages from generated assets following the FASE-7 specification:
- output/v4_complete/{hotel_id}/ -> deliveries/{hotel_id}_{date}.zip

Creates structured delivery:
    deliveries/{hotel_id}_{date}.zip
        ├── DIAGNOSTICO.md
        ├── PROPUESTA_COMERCIAL.md
        ├── ASSETS/
        │   ├── geo_playbook.md
        │   └── ...
        ├── MANIFEST.json
        ├── IMPLEMENTATION_ORDER.md  (FASE-5)
        └── README_DELIVERY.md

Created as part of FASE-7-DELIVERY-V2: Delivery Pipeline Automation.
FASE-5: Integrated AssetResponsibilityContract for implementation order.
"""

import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# FASE-5: Import for implementation order generation
try:
    from modules.geo_enrichment import AssetResponsibilityContract
    HAS_ASSET_CONTRACT = True
except ImportError:
    HAS_ASSET_CONTRACT = False


class DeliveryPackager:
    """Packages generated assets into deliverable ZIP archives."""

    def __init__(self, base_output_dir: str = "output", deliveries_dir: str = "deliveries"):
        """
        Initialize the DeliveryPackager.

        Args:
            base_output_dir: Base directory for generated assets (default: output)
            deliveries_dir: Directory for final delivery packages (default: deliveries)
        """
        self.base_output_dir = Path(base_output_dir)
        self.deliveries_dir = Path(deliveries_dir)
        self.deliveries_dir.mkdir(parents=True, exist_ok=True)

    def package(
        self,
        hotel_id: str,
        output_dir: Optional[str] = None,
        diagnostic_path: Optional[str] = None,
        proposal_path: Optional[str] = None,
        # FASE-5: Asset Responsibility parameters
        hotel_name: Optional[str] = None,
        geo_score: Optional[int] = None,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None,
    ) -> str:
        """
        Create a ZIP package with all assets for a hotel.

        Args:
            hotel_id: Hotel identifier (used to find output directory)
            output_dir: Override path to output directory (auto-detected if None)
            diagnostic_path: Optional path to DIAGNOSTICO.md
            proposal_path: Optional path to PROPUESTA_COMERCIAL.md
            hotel_name: FASE-5 - Hotel name for implementation order
            geo_score: FASE-5 - GEO score to determine mandatory GEO assets
            core_assets: FASE-5 - List of CORE asset filenames generated
            geo_assets: FASE-5 - List of GEO asset filenames generated

        Returns:
            Path to created ZIP file
        """
        # Resolve output directory
        if output_dir:
            source_dir = Path(output_dir)
        else:
            # Auto-detect: look for output/v4_complete/{hotel_id}
            possible_dirs = [
                self.base_output_dir / "v4_complete" / hotel_id,
                self.base_output_dir / hotel_id,
                self.base_output_dir / f"v4_complete_{hotel_id}",
            ]
            source_dir = None
            for d in possible_dirs:
                if d.exists():
                    source_dir = d
                    break
            if not source_dir:
                source_dir = self.base_output_dir / hotel_id

        if not source_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {source_dir}")

        # Generate delivery filename
        date_str = datetime.now().strftime("%Y%m%d")
        zip_filename = f"{hotel_id}_{date_str}.zip"
        zip_path = self.deliveries_dir / zip_filename

        # Collect files to package
        files_to_package = self._collect_files(source_dir, diagnostic_path, proposal_path)

        # Create ZIP
        self._create_zip(zip_path, files_to_package, source_dir)

        # Create manifest
        manifest = self.create_manifest(hotel_id, files_to_package)
        manifest_path = self.deliveries_dir / f"{hotel_id}_{date_str}_MANIFEST.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # FASE-5: Create IMPLEMENTATION_ORDER.md based on AssetResponsibilityContract
        implementation_order_path = None
        if HAS_ASSET_CONTRACT and (core_assets or geo_assets):
            try:
                contract = AssetResponsibilityContract()
                impl_order_content = contract.generate_delivery_template(
                    hotel_name=hotel_name or hotel_id,
                    core_assets=core_assets,
                    geo_assets=geo_assets,
                    geo_score=geo_score
                )
                implementation_order_path = self.deliveries_dir / "IMPLEMENTATION_ORDER.md"
                implementation_order_path.write_text(impl_order_content, encoding='utf-8')
            except Exception as e:
                logger.warning(f"[DeliveryPackager] Could not generate implementation order: {e}")

        # Create README
        self.create_readme(self.deliveries_dir, hotel_id, manifest)

        # Update ZIP with manifest, README, and IMPLEMENTATION_ORDER
        with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zf:
            zf.write(manifest_path, arcname="MANIFEST.json")
            readme_path = self.deliveries_dir / "README_DELIVERY.md"
            if readme_path.exists():
                zf.write(readme_path, arcname="README_DELIVERY.md")
            # FASE-5: Add implementation order to ZIP
            if implementation_order_path and implementation_order_path.exists():
                zf.write(implementation_order_path, arcname="IMPLEMENTATION_ORDER.md")

        # Remove temp manifest
        if manifest_path.exists():
            manifest_path.unlink()

        return str(zip_path)

    def _collect_files(
        self,
        source_dir: Path,
        diagnostic_path: Optional[str] = None,
        proposal_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect all files to package from source directory."""
        files = []

        # Add DIAGNOSTICO.md if provided
        if diagnostic_path and Path(diagnostic_path).exists():
            files.append({
                "source": diagnostic_path,
                "dest": "DIAGNOSTICO.md"
            })

        # Add PROPUESTA_COMERCIAL.md if provided
        if proposal_path and Path(proposal_path).exists():
            files.append({
                "source": proposal_path,
                "dest": "PROPUESTA_COMERCIAL.md"
            })

        # Collect all files from source directory
        if source_dir.exists():
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    # Determine destination path within ZIP
                    rel_path = file_path.relative_to(source_dir)

                    # Skip manifest files
                    if file_path.name == "manifest.json":
                        continue

                    # For assets in subdirectories, put them under ASSETS/
                    if len(rel_path.parts) > 1:
                        dest = f"ASSETS/{rel_path}"
                    elif rel_path.suffix in ['.md', '.json', '.csv', '.html']:
                        dest = f"ASSETS/{rel_path}"
                    else:
                        dest = str(rel_path)

                    files.append({
                        "source": str(file_path),
                        "dest": dest
                    })

        return files

    def _create_zip(self, zip_path: Path, files: List[Dict[str, Any]], base_dir: Path):
        """Create ZIP file with all collected files."""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_info in files:
                source_path = Path(file_info["source"])
                if source_path.exists():
                    # Use the destination name in the ZIP
                    zf.write(source_path, arcname=file_info["dest"])

    def create_manifest(self, hotel_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate manifest.json with all assets metadata.

        Args:
            hotel_id: Hotel identifier
            files: List of files to include

        Returns:
            Manifest dictionary
        """
        manifest = {
            "version": "1.0.0",
            "hotel_id": hotel_id,
            "generated_at": datetime.now().isoformat(),
            "package_type": "automated_delivery",
            "files": []
        }

        for f in files:
            file_path = Path(f["source"])
            stat = file_path.stat() if file_path.exists() else None

            manifest["files"].append({
                "name": f["dest"],
                "size_bytes": stat.st_size if stat else 0,
                "type": self._classify_file(f["dest"])
            })

        manifest["total_files"] = len(manifest["files"])
        manifest["total_size_bytes"] = sum(f["size_bytes"] for f in manifest["files"])

        return manifest

    def _classify_file(self, filename: str) -> str:
        """Classify file type based on extension and path."""
        if filename.startswith("ASSETS/"):
            name = Path(filename).stem.lower()
            path = Path(filename).suffix.lower()
        else:
            name = Path(filename).stem.lower()
            path = Path(filename).suffix.lower()

        if name in ["diagnostico", "diagnostic"]:
            return "diagnostic"
        elif name in ["propuesta", "proposal", "propuesta_comercial"]:
            return "proposal"
        elif path == ".json":
            return "schema"
        elif path == ".html":
            return "code"
        elif path == ".csv":
            return "data"
        elif path == ".md":
            return "guide"
        else:
            return "other"

    def create_readme(
        self,
        delivery_dir: Path,
        hotel_id: str,
        manifest: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generate README_DELIVERY.md with instructions.

        Args:
            delivery_dir: Directory where README will be created
            hotel_id: Hotel identifier
            manifest: Optional manifest data for dynamic content
        """
        template_path = Path(__file__).parent.parent.parent / "templates" / "delivery_readme_template.md"

        # Try to load template, fallback to default
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            content = content.replace("{{HOTEL_ID}}", hotel_id)
            content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
            if manifest:
                content = content.replace("{{TOTAL_FILES}}", str(manifest.get("total_files", "N/A")))
                content = content.replace("{{TOTAL_SIZE}}", self._format_bytes(manifest.get("total_size_bytes", 0)))
        else:
            content = self._default_readme(hotel_id, manifest)

        readme_path = delivery_dir / "README_DELIVERY.md"
        readme_path.write_text(content, encoding='utf-8')

    def _format_bytes(self, size: int) -> str:
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _default_readme(self, hotel_id: str, manifest: Optional[Dict[str, Any]]) -> str:
        """Generate default README when template is not available."""
        total_files = manifest.get("total_files", "N/A") if manifest else "N/A"

        return f"""# Delivery Package - {hotel_id}

**Generated:** {datetime.now().strftime("%Y-%m-%d")}
**Package ID:** {hotel_id}

## Overview

This package contains {total_files} files ready for implementation.

## Contents

- **DIAGNOSTICO.md** - Diagnostic analysis of current state
- **PROPUESTA_COMERCIAL.md** - Commercial proposal with solutions
- **ASSETS/** - Implementation assets (schemas, guides, code)

## Implementation Timeline

### Week 1: Quick Wins
1. Deploy Schema markup (JSON-LD)
2. Add WhatsApp button code

### Week 2: Content
1. Implement FAQ page
2. Deploy geo-playbook optimizations

### Week 3: Advanced
1. Review monitoring setup
2. Conversion tracking

## Checklist

- [ ] Schema markup deployed
- [ ] FAQ page live
- [ ] WhatsApp button visible
- [ ] GEO optimizations applied
- [ ] Analytics configured

## Support

For questions about implementation, refer to the specific asset guides.
"""
