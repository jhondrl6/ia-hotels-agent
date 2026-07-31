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
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DeliveryValidationError(Exception):
    """Error de validación del delivery package.

    Se lanza cuando _validate_zip() detecta inconsistencias entre
    el ZIP y el manifest después del empaquetado. El ZIP inválido
    se elimina antes de propagar la excepción.
    """
    pass


# FASE-C: Import DeliveryContext for dynamic README generation
try:
    from modules.delivery.delivery_context import DeliveryContext, DeliveryAssetEntry, DeliveryAssetState
    HAS_DELIVERY_CONTEXT = True
except ImportError:
    HAS_DELIVERY_CONTEXT = False

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
        # FASE-3 NP6: quality metadata for MANIFEST enrichment (set by caller before package())
        self._quality_metadata: Optional[Dict[str, Any]] = None

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

        # Collect files to package
        files_to_package = self._collect_files(source_dir, diagnostic_path, proposal_path)

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

        # ── FASE-B T3: Compute ZIP filename once ──
        date_str = datetime.now().strftime("%Y%m%d")
        zip_filename = self._make_zip_filename(hotel_id)
        zip_path = self.deliveries_dir / zip_filename
        manifest_path = self.deliveries_dir / f"{hotel_id}_{date_str}_MANIFEST.json"

        # ── FASE-B T5: Load DeliveryContext from asset_generation_report ──
        delivery_context = None
        try:
            from modules.delivery.delivery_context import DeliveryContext
            report_path = source_dir / "v4_audit" / "asset_generation_report.json"
            if report_path.exists():
                delivery_context = DeliveryContext.from_asset_generation_report(
                    report_path=report_path,
                    hotel_id=hotel_id,
                    zip_filename=zip_filename,
                    files=files_to_package,
                )
        except Exception:
            pass  # Legacy mode: no DeliveryContext available

        # Build meta entries for manifest calculation (NO manifest itself yet — handled in pass 3)
        readme_path = self.deliveries_dir / "README_DELIVERY.md"
        meta_for_manifest = [
            {"source": str(readme_path), "dest": "README_DELIVERY.md"},
        ]
        if implementation_order_path and implementation_order_path.exists():
            meta_for_manifest.append({
                "source": str(implementation_order_path),
                "dest": "IMPLEMENTATION_ORDER.md"
            })

        # ── FASE-B T2: 3-pass manifest with real sizes ──
        # Pass 1: Write README first so it has real size on disk
        self.create_readme(self.deliveries_dir, hotel_id, manifest=None, delivery_context=delivery_context)

        # Pass 2: Build manifest with README now on disk (real size captured)
        files_for_manifest = files_to_package + meta_for_manifest
        manifest = self.create_manifest(hotel_id, files_for_manifest)

        # ── FASE-3 NP6: Enrich manifest with quality metadata ──
        if self._quality_metadata is not None:
            manifest["quality_metadata"] = self._quality_metadata

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Pass 3: Add MANIFEST.json's own size (can only be measured after writing)
        # FASE-B: The self-referencing entry increases the file size. Measure
        # before adding the entry, then correct after the rewrite to account
        # for the entry itself.
        manifest_size_before = manifest_path.stat().st_size
        manifest["total_size_bytes"] += manifest_size_before
        manifest["files"].append({
            "name": "MANIFEST.json",
            "size_bytes": manifest_size_before,
            "type": "other"
        })
        manifest["total_files"] = len(manifest["files"])
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # The added self-entry makes the file larger — correct the size
        manifest_size_after = manifest_path.stat().st_size
        if manifest_size_after != manifest_size_before:
            delta = manifest_size_after - manifest_size_before
            manifest["total_size_bytes"] += delta
            for entry in manifest["files"]:
                if entry["name"] == "MANIFEST.json":
                    entry["size_bytes"] = manifest_size_after
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

        # ── P-01: Post-process README with final manifest totals ──
        # In Pass 1, create_readme() was called with manifest=None, so
        # {{TOTAL_FILES}} and {{TOTAL_SIZE}} were left as placeholders.
        # Now that the manifest is finalized (including MANIFEST.json itself),
        # replace them with the definitive values.
        readme_fixup_path = self.deliveries_dir / "README_DELIVERY.md"
        if readme_fixup_path.exists():
            readme_content = readme_fixup_path.read_text(encoding='utf-8')
            readme_content = readme_content.replace("{{TOTAL_FILES}}", str(manifest["total_files"]))
            readme_content = readme_content.replace("{{TOTAL_SIZE}}",
                                                    self._format_bytes(manifest["total_size_bytes"]))
            readme_fixup_path.write_text(readme_content, encoding='utf-8')

        # Full file list for ZIP (includes manifest now)
        zip_files = files_to_package + meta_for_manifest + [
            {"source": str(manifest_path), "dest": "MANIFEST.json"}
        ]

        # Create ZIP
        self._create_zip(zip_path, zip_files, source_dir)

        # ── FASE-D T4: Validate ZIP ↔ manifest consistency (blocking gate) ──
        validation_errors = self._validate_zip(zip_path, manifest)
        if validation_errors:
            error_msg = "ZIP validation failed:\n" + "\n".join(f"  - {e}" for e in validation_errors)
            logger.error(f"[DeliveryPackager] {error_msg}")
            # Delete invalid ZIP
            if zip_path.exists():
                zip_path.unlink()
            raise DeliveryValidationError(error_msg)

        # Cleanup temp manifest
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
                    # FASE-B: Always use POSIX separators in ZIP paths
                    if len(rel_path.parts) > 1:
                        dest = f"ASSETS/{rel_path.as_posix()}"
                    elif rel_path.suffix in ['.md', '.json', '.csv', '.html']:
                        dest = f"ASSETS/{rel_path.as_posix()}"
                    else:
                        dest = rel_path.as_posix()

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

    # ═══ FASE-B: New methods ═══

    def _make_zip_filename(self, hotel_id: str) -> str:
        """Compute ZIP filename once, shared by package() and README (FASE-C).

        Format: {hotel_id}_{YYYYMMDD}.zip
        """
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{hotel_id}_{date_str}.zip"

    def _validate_zip(self, zip_path: Path, manifest: Dict[str, Any]) -> List[str]:
        """Validate ZIP ↔ manifest consistency after packaging.

        Checks:
        1. Same entries in ZIP and manifest
        2. All paths use POSIX separators (no backslashes)
        3. File sizes match between ZIP and manifest
        4. Total file count and total size match

        Returns list of error messages (empty = valid).
        """
        errors = []

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                zip_names = set(z.namelist())
                manifest_names = {f["name"] for f in manifest.get("files", [])}

                # 1. Same entries
                only_zip = zip_names - manifest_names
                only_manifest = manifest_names - zip_names
                if only_zip:
                    errors.append(f"Entries in ZIP but not in manifest: {only_zip}")
                if only_manifest:
                    errors.append(f"Entries in manifest but not in ZIP: {only_manifest}")

                # 2. POSIX paths
                for name in zip_names:
                    if "\\" in name:
                        errors.append(f"Non-POSIX path in ZIP: {name}")

                # 3. File sizes
                manifest_sizes = {f["name"]: f.get("size_bytes", 0) for f in manifest.get("files", [])}
                for name in zip_names:
                    actual_size = len(z.read(name))
                    declared_size = manifest_sizes.get(name, 0)
                    if actual_size != declared_size:
                        errors.append(
                            f"Size mismatch for '{name}': manifest={declared_size}, actual={actual_size}"
                        )

                # 4. Totals
                declared_total = manifest.get("total_files", 0)
                actual_total = len(zip_names)
                if declared_total != actual_total:
                    errors.append(f"Total files mismatch: manifest={declared_total}, actual={actual_total}")

                declared_size_total = manifest.get("total_size_bytes", 0)
                actual_size_total = sum(len(z.read(n)) for n in zip_names)
                if declared_size_total != actual_size_total:
                    errors.append(
                        f"Total size mismatch: manifest={declared_size_total}, actual={actual_size_total}"
                    )

        except Exception as e:
            errors.append(f"ZIP validation failed: {e}")

        return errors

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
        manifest: Optional[Dict[str, Any]] = None,
        delivery_context: Optional[Any] = None
    ) -> None:
        """
        Generate README_DELIVERY.md with instructions.

        FASE-C: Dynamic README — all sections generated from DeliveryContext
        and real file list. No hardcoded asset names. Backwards-compatible
        with legacy template when delivery_context is None.

        Args:
            delivery_dir: Directory where README will be created
            hotel_id: Hotel identifier
            manifest: Optional manifest data for dynamic content
            delivery_context: Optional DeliveryContext for dynamic sections (FASE-C)
        """
        template_path = Path(__file__).parent.parent.parent / "templates" / "delivery_readme_template.md"

        # Try to load template, fallback to default
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            content = content.replace("{{HOTEL_ID}}", hotel_id)
            content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))

            # ── FASE-C: DeliveryContext available → dynamic sections ──
            if delivery_context and delivery_context.assets:
                content = content.replace("{{PACKAGE_FILENAME}}", delivery_context.zip_filename)
                # TOTAL_FILES/TOTAL_SIZE: when manifest is available, compute; otherwise
                # leave placeholders for post-manifest fixup (P-01: README count mismatch)
                if manifest is not None:
                    content = content.replace("{{TOTAL_FILES}}", str(len(delivery_context.files)))
                    total_size = self._compute_total_size(delivery_context.files, manifest)
                    content = content.replace("{{TOTAL_SIZE}}", self._format_bytes(total_size))

                # Package Structure from real dest paths
                structure = self._generate_package_structure(
                    delivery_context.files, delivery_context.zip_filename
                )
                content = content.replace("{{PACKAGE_STRUCTURE}}", structure)

                # Core Documents section
                content = content.replace("{{CORE_DOCUMENTS}}", self._generate_core_documents())

                # Deliverable Assets section
                content = content.replace("{{DELIVERABLE_ASSETS}}",
                    self._generate_deliverable_instructions(delivery_context))

                # Per-state sections
                content = content.replace(
                    "{{PRESENT_IN_PRODUCTION_SECTION}}",
                    self._generate_present_in_production_section(delivery_context.present_assets)
                )
                content = content.replace(
                    "{{PRESENT_WITH_ISSUES_SECTION}}",
                    self._generate_present_with_issues_section(delivery_context.present_with_issues_assets)
                )
                content = content.replace(
                    "{{ESTIMATED_ASSETS_SECTION}}",
                    self._generate_estimated_section(delivery_context.estimated_assets)
                )
                content = content.replace(
                    "{{ADVISORY_GUIDES_SECTION}}",
                    self._generate_advisory_section(delivery_context.advisory_assets)
                )
                content = content.replace(
                    "{{EVIDENCE_SECTION}}",
                    self._generate_evidence_section(delivery_context)
                )

                # Timeline and Checklist
                content = content.replace("{{TIMELINE}}", self._generate_timeline(delivery_context))
                content = content.replace("{{CHECKLIST}}", self._generate_checklist(delivery_context))
            else:
                # ── Legacy mode: no DeliveryContext ──
                content = content.replace("{{PACKAGE_FILENAME}}", f"{hotel_id}_{{DATE}}.zip")
                if manifest:
                    content = content.replace("{{TOTAL_FILES}}", str(manifest.get("total_files", "N/A")))
                    content = content.replace("{{TOTAL_SIZE}}", self._format_bytes(manifest.get("total_size_bytes", 0)))
                else:
                    content = content.replace("{{TOTAL_FILES}}", "N/A")
                    content = content.replace("{{TOTAL_SIZE}}", "N/A")

                # Empty all dynamic placeholders for legacy compatibility
                for ph in ["{{PACKAGE_STRUCTURE}}", "{{CORE_DOCUMENTS}}",
                            "{{DELIVERABLE_ASSETS}}", "{{PRESENT_IN_PRODUCTION_SECTION}}",
                            "{{PRESENT_WITH_ISSUES_SECTION}}", "{{ESTIMATED_ASSETS_SECTION}}",
                            "{{ADVISORY_GUIDES_SECTION}}", "{{EVIDENCE_SECTION}}",
                            "{{TIMELINE}}", "{{CHECKLIST}}"]:
                    content = content.replace(ph, "")
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

    # ═══ FASE-C: Dynamic README section generators ═══

    def _compute_total_size(
        self, files: List[Dict[str, Any]], manifest: Optional[Dict[str, Any]]
    ) -> int:
        """Compute total size from real files on disk or fallback to manifest."""
        total = 0
        for f in files:
            source = f.get("source", "")
            if source:
                try:
                    total += Path(source).stat().st_size
                except OSError:
                    pass
        if total == 0 and manifest:
            total = manifest.get("total_size_bytes", 0)
        return total

    def _generate_package_structure(
        self, files: List[Dict[str, Any]], zip_filename: str
    ) -> str:
        """Generate tree structure from real ZIP dest paths (T2)."""
        tree: Dict[str, List[str]] = defaultdict(list)
        for f in files:
            dest = f.get("dest", "")
            if "/" in dest:
                parts = dest.split("/")
                if len(parts) >= 2:
                    dir_name = parts[0]
                    file_name = "/".join(parts[1:])
                    tree[dir_name].append(file_name)
                else:
                    tree[""].append(dest)
            else:
                tree[""].append(dest)

        lines = ["```", zip_filename]

        # Root-level documents
        root_files = tree.get("", [])
        for rf in sorted(root_files):
            if rf.endswith(".md") and not rf.startswith("README"):
                lines.append(f"├── {rf}")

        # ASSETS/ directory
        asset_files = tree.get("ASSETS", [])
        subdirs = defaultdict(list)
        for af in asset_files:
            if "/" in af:
                subdir, fname = af.split("/", 1)
                subdirs[subdir].append(fname)
            else:
                subdirs[""].append(af)

        if asset_files:
            lines.append("├── ASSETS/")
            sorted_subdirs = sorted([d for d in subdirs if d])
            for i, sd in enumerate(sorted_subdirs):
                prefix = "│   ├──" if i < len(sorted_subdirs) - 1 else "│   └──"
                lines.append(f"{prefix} {sd}/")

        # Meta-files
        lines.append("├── MANIFEST.json")
        lines.append("└── README_DELIVERY.md")
        lines.append("```")

        return "\n".join(lines)

    def _generate_core_documents(self) -> str:
        """Static instructions for core documents (DIAGNOSTICO + PROPUESTA)."""
        return (
            "### DIAGNOSTICO.md\n"
            "Review your current state analysis, identified gaps, and opportunities.\n\n"
            "### PROPUESTA_COMERCIAL.md\n"
            "Review the commercial proposal with ROI projections and implementation plan.\n"
        )

    def _generate_deliverable_instructions(self, ctx) -> str:
        """Instructions for DELIVERED assets."""
        delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state == DeliveryAssetState.DELIVERED and not getattr(a, 'is_advisory', False)]
        if not delivered:
            return ""
        lines = [
            "The following assets were generated and are ready for implementation:\n",
        ]
        for a in delivered:
            path = a.delivery_path or a.asset_type
            lines.append(f"- **{a.service_name}** (`{path}`): {a.message}")
        lines.append("")
        return "\n".join(lines)

    def _generate_present_in_production_section(self, assets: List[Any]) -> str:
        """Section for assets already present in production (T3)."""
        if not assets:
            return ""
        lines = [
            "## Already Present on Your Website",
            "",
            "The following elements are already present on your site and do NOT require installation:",
            "",
            "| Service | Status |",
            "|---------|--------|",
        ]
        for a in assets:
            lines.append(f"| {a.service_name} | Verified in production |")
        lines.append("")
        return "\n".join(lines)

    def _generate_present_with_issues_section(self, assets: List[Any]) -> str:
        """Section for assets present but requiring review (T3)."""
        if not assets:
            return ""
        lines = [
            "## Present but Requires Review",
            "",
            "These elements exist on your site but need attention before they are fully effective:",
            "",
            "| Service | Issue | Action |",
            "|---------|-------|--------|",
        ]
        for a in assets:
            lines.append(f"| {a.service_name} | {a.message} | Review the accompanying guide |")
        lines.append("")
        return "\n".join(lines)

    def _generate_estimated_section(self, assets: List[Any]) -> str:
        """Section for ESTIMATED assets (T3)."""
        if not assets:
            return ""
        lines = [
            "## Estimated Assets",
            "",
            "The following assets were generated with estimated data. Review before using in production:",
            "",
        ]
        for a in assets:
            path = a.delivery_path or a.asset_type
            lines.append(f"- **{a.service_name}** (`{path}`): {a.message}")
        lines.append("")
        return "\n".join(lines)

    def _generate_advisory_section(self, assets: List[Any]) -> str:
        """Section for advisory guides — NOT installable assets (T3)."""
        if not assets:
            return ""
        lines = [
            "## Advisory Guides",
            "",
            "The following guides are included for review. They are NOT installable assets,",
            "but reference materials to help you resolve specific issues:",
            "",
        ]
        for a in assets:
            path = a.delivery_path or a.asset_type
            lines.append(f"- **{a.service_name}** (`{path}`): {a.message}")
        lines.append("")
        return "\n".join(lines)

    def _generate_evidence_section(self, ctx) -> str:
        """List evidence/audit files (T3)."""
        evidence_files = [
            f for f in ctx.files
            if "v4_audit" in f.get("dest", "").lower()
            or "evidence" in f.get("dest", "").lower()
        ]
        if not evidence_files:
            return ""
        lines = [
            "## Audit Evidence",
            "",
            "The following evidence files document the analysis behind the generated assets:",
            "",
        ]
        for f in evidence_files:
            dest = f.get("dest", "")
            lines.append(f"- `{dest}`")
        lines.append("")
        return "\n".join(lines)

    def _generate_timeline(self, ctx) -> str:
        """Dynamic timeline based on asset states (T3)."""
        has_deliverables = bool([a for a in ctx.assets
            if getattr(a, 'state', None) and a.state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED)])
        has_issues = bool(ctx.present_with_issues_assets)

        lines = []
        if has_deliverables:
            lines.extend([
                "### Week 1: Deploy Generated Assets (1-2 hours)",
                "- [ ] Review DIAGNOSTICO.md for gap analysis",
                "- [ ] Review PROPUESTA_COMERCIAL.md for commercial strategy",
                "- [ ] Deploy Schema markup (JSON-LD)",
                "- [ ] Upload generated assets to your CMS",
                "",
            ])
        if has_issues:
            lines.extend([
                "### Week 2: Review & Fix Issues (2-3 hours)",
                "- [ ] Review assets flagged in 'Present but Requires Review'",
                "- [ ] Resolve configuration conflicts",
                "- [ ] Validate fixes on staging",
                "",
            ])
        lines.extend([
            "### Week 3: Monitor & Validate (1 hour)",
            "- [ ] Verify schema validation at search.google.com/test/rich-results",
            "- [ ] Check Google Search Console for indexing",
            "- [ ] Monitor GBP insights for improvements",
            "",
        ])
        return "\n".join(lines)

    def _generate_checklist(self, ctx) -> str:
        """Dynamic checklist based on asset states (T3)."""
        lines = []
        has_deliverables = bool([a for a in ctx.assets
            if getattr(a, 'state', None) and a.state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED)])

        if has_deliverables:
            lines.extend([
                "### Technical",
                "- [ ] Core documents reviewed",
                "- [ ] Schema markup deployed and validated",
                "- [ ] All generated assets uploaded to production",
                "",
            ])
        if ctx.present_with_issues_assets:
            lines.extend([
                "### Issues to Resolve",
            ])
            for a in ctx.present_with_issues_assets:
                lines.append(f"- [ ] {a.service_name}: {a.message}")
            lines.append("")
        lines.extend([
            "### Monitoring",
            "- [ ] Google Search Console configured",
            "- [ ] Google Business Profile optimized",
            "- [ ] Conversion tracking verified",
            "",
        ])
        return "\n".join(lines)

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
