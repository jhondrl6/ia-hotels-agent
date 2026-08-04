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

        SINGLE-WRITE strategy: all content (README, MANIFEST) is computed
        in memory first, then the ZIP is written in one atomic pass.
        This eliminates size mismatches caused by multi-write approaches.

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
        # ── NF-5: Single datetime per packaging run ──
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        date_display = now.strftime("%Y-%m-%d")
        timestamp_iso = now.isoformat()

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

        # FASE-5: Generate IMPLEMENTATION_ORDER.md content in memory
        implementation_order_content: Optional[str] = None
        if HAS_ASSET_CONTRACT and (core_assets or geo_assets):
            try:
                contract = AssetResponsibilityContract()
                implementation_order_content = contract.generate_delivery_template(
                    hotel_name=hotel_name or hotel_id,
                    core_assets=core_assets,
                    geo_assets=geo_assets,
                    geo_score=geo_score
                )
            except Exception as e:
                logger.warning(f"[DeliveryPackager] Could not generate implementation order: {e}")

        # ── Compute ZIP filename (NF-5: uses shared date_str) ──
        zip_filename = self._make_zip_filename(hotel_id, date_str)
        zip_path = self.deliveries_dir / zip_filename

        # ── Load DeliveryContext from asset_generation_report ──
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
        except Exception as e:
            logger.warning(f"[DeliveryPackager] DeliveryContext unavailable, using legacy mode: {e}")

        # ═══ SINGLE-WRITE: Compute all content in memory ═══

        # Step 1: Generate README template in memory (with {{TOTAL_FILES}}/{{TOTAL_SIZE}} placeholders)
        preliminary_readme_bytes = self._compute_readme_bytes(
            hotel_id, files_to_package, delivery_context,
            implementation_order_content, date_display
        )

        # Step 2: Build meta file list with preliminary README size
        impl_bytes = (
            implementation_order_content.encode("utf-8")
            if implementation_order_content else None
        )
        meta_entries = [
            {"name": "README_DELIVERY.md", "size_bytes": len(preliminary_readme_bytes), "type": "guide"},
        ]
        if impl_bytes is not None:
            meta_entries.append(
                {"name": "IMPLEMENTATION_ORDER.md", "size_bytes": len(impl_bytes), "type": "guide"}
            )

        # Step 3: Build manifest in memory with real sizes (NF-5: uses shared timestamp)
        manifest = self._build_manifest_in_memory(
            hotel_id, files_to_package, meta_entries, timestamp_iso
        )

        # ── FASE-3 NP6: Enrich manifest with quality metadata ──
        if self._quality_metadata is not None:
            manifest["quality_metadata"] = self._quality_metadata

        # Step 4: Resolve MANIFEST.json self-referencing size via fixed-point
        manifest = self._resolve_manifest_self_size(manifest)

        # Step 5: Finalize README with actual totals from resolved manifest
        readme_bytes = self._finalize_readme_bytes(manifest)

        # Step 5b: If README size changed (placeholder → real values), update manifest
        if len(readme_bytes) != len(preliminary_readme_bytes):
            for entry in manifest["files"]:
                if entry["name"] == "README_DELIVERY.md":
                    entry["size_bytes"] = len(readme_bytes)
                    break
            # Recompute totals and re-resolve self-size
            manifest["total_size_bytes"] = sum(f["size_bytes"] for f in manifest["files"])
            manifest = self._resolve_manifest_self_size(manifest)
            # Finalize README again with updated totals (converges in 1-2 iterations)
            readme_bytes = self._finalize_readme_bytes(manifest)
            # Final size check (extremely unlikely to differ again)
            if len(readme_bytes) != manifest["files"][[f["name"] for f in manifest["files"]].index("README_DELIVERY.md")]["size_bytes"]:
                for entry in manifest["files"]:
                    if entry["name"] == "README_DELIVERY.md":
                        entry["size_bytes"] = len(readme_bytes)
                        break
                manifest["total_size_bytes"] = sum(f["size_bytes"] for f in manifest["files"])
                manifest = self._resolve_manifest_self_size(manifest)
                readme_bytes = self._finalize_readme_bytes(manifest)

        # Step 6: Serialize manifest to bytes (final)
        manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")

        # Step 7: Write ZIP in a single atomic pass
        tmp_zip_path = zip_path.with_suffix(".zip.tmp")
        try:
            self._create_zip_single_write(
                tmp_zip_path, files_to_package, source_dir,
                readme_bytes=readme_bytes,
                implementation_order_bytes=impl_bytes,
                manifest_bytes=manifest_bytes,
            )
            # Atomic rename
            if zip_path.exists():
                zip_path.unlink()
            tmp_zip_path.rename(zip_path)
        except Exception:
            # Cleanup partial ZIP on failure
            if tmp_zip_path.exists():
                tmp_zip_path.unlink()
            raise

        # ── FASE-D T4: Validate ZIP ↔ manifest consistency (blocking gate) ──
        validation_errors = self._validate_zip(zip_path, manifest)
        if validation_errors:
            error_msg = "ZIP validation failed:\n" + "\n".join(f"  - {e}" for e in validation_errors)
            logger.error(f"[DeliveryPackager] {error_msg}")
            # Delete invalid ZIP
            if zip_path.exists():
                zip_path.unlink()
            raise DeliveryValidationError(error_msg)

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
            # FASE-D (N4): umbral de freshness para v4_audit
            # Excluir artefactos con timestamp anterior al run actual
            freshness_cutoff = datetime.now().timestamp() - 86400  # 24 horas
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    # Determine destination path within ZIP
                    rel_path = file_path.relative_to(source_dir)

                    # Skip manifest files
                    if file_path.name == "manifest.json":
                        continue

                    # FASE-D (N4): filtrar v4_audit — solo artefactos del run actual
                    if "v4_audit" in rel_path.parts:
                        file_mtime = file_path.stat().st_mtime
                        if file_mtime < freshness_cutoff:
                            logger.info(
                                f"[DeliveryPackager] Skipping stale v4_audit artifact: {rel_path} "
                                f"(mtime={datetime.fromtimestamp(file_mtime).isoformat()})"
                            )
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
        """Create ZIP file with all collected files (legacy, kept for compat)."""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_info in files:
                source_path = Path(file_info["source"])
                if source_path.exists():
                    # Use the destination name in the ZIP
                    zf.write(source_path, arcname=file_info["dest"])

    # ═══ SINGLE-WRITE: In-memory computation methods ═══

    def _compute_readme_bytes(
        self,
        hotel_id: str,
        files_to_package: List[Dict[str, Any]],
        delivery_context: Optional[Any],
        implementation_order_content: Optional[str],
        date_display: Optional[str] = None,
    ) -> bytes:
        """Generate final README content in memory — no placeholders remain.

        Uses a two-phase approach:
        1. Generate README with placeholder markers for TOTAL_FILES/TOTAL_SIZE
        2. Compute a preliminary manifest to get real totals
        3. Replace placeholders with final values

        Returns UTF-8 encoded bytes of the final README.
        """
        template_path = Path(__file__).parent.parent.parent / "templates" / "delivery_readme_template.md"

        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            content = content.replace("{{HOTEL_ID}}", hotel_id)
            content = content.replace("{{DATE}}", date_display or datetime.now().strftime("%Y-%m-%d"))

            if delivery_context and delivery_context.assets:
                content = content.replace("{{PACKAGE_FILENAME}}", delivery_context.zip_filename)
                # Leave TOTAL_FILES/TOTAL_SIZE as placeholders for now
                # (resolved after manifest is computed)

                # Package Structure from real dest paths
                structure = self._generate_package_structure(
                    delivery_context.files, delivery_context.zip_filename
                )
                content = content.replace("{{PACKAGE_STRUCTURE}}", structure)
                content = content.replace("{{CORE_DOCUMENTS}}", self._generate_core_documents())
                content = content.replace("{{DELIVERABLE_ASSETS}}",
                    self._generate_deliverable_instructions(delivery_context))
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
                content = content.replace("{{TIMELINE}}", self._generate_timeline(delivery_context))
                content = content.replace("{{CHECKLIST}}", self._generate_checklist(delivery_context))
            else:
                # Legacy mode: no DeliveryContext
                content = content.replace("{{PACKAGE_FILENAME}}", f"{hotel_id}_{{DATE}}.zip")
                # Empty all dynamic placeholders for legacy compatibility
                for ph in ["{{PACKAGE_STRUCTURE}}", "{{CORE_DOCUMENTS}}",
                            "{{DELIVERABLE_ASSETS}}", "{{PRESENT_IN_PRODUCTION_SECTION}}",
                            "{{PRESENT_WITH_ISSUES_SECTION}}", "{{ESTIMATED_ASSETS_SECTION}}",
                            "{{ADVISORY_GUIDES_SECTION}}", "{{EVIDENCE_SECTION}}",
                            "{{TIMELINE}}", "{{CHECKLIST}}"]:
                    content = content.replace(ph, "")
        else:
            content = self._default_readme(hotel_id, None, date_display)

        # TOTAL_FILES/TOTAL_SIZE remain as placeholders — they will be
        # resolved by the caller after manifest is finalized.
        # Store content for later fixup.
        self._readme_template_content = content
        # Return preliminary bytes (with placeholders) for size estimation.
        # The caller will invoke _finalize_readme_bytes() after manifest.
        return content.encode("utf-8")

    def _finalize_readme_bytes(self, manifest: Dict[str, Any]) -> bytes:
        """Replace {{TOTAL_FILES}} and {{TOTAL_SIZE}} with final manifest values.

        Called AFTER manifest is fully resolved (including self-size).
        Returns the definitive README bytes that will go into the ZIP.
        """
        content = getattr(self, '_readme_template_content', '') or ''
        content = content.replace("{{TOTAL_FILES}}", str(manifest.get("total_files", "N/A")))
        content = content.replace("{{TOTAL_SIZE}}", self._format_bytes(manifest.get("total_size_bytes", 0)))
        return content.encode("utf-8")

    def _build_manifest_in_memory(
        self,
        hotel_id: str,
        files_to_package: List[Dict[str, Any]],
        meta_entries: List[Dict[str, Any]],
        timestamp_iso: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build manifest dict in memory from real file sizes + meta entries.

        Args:
            hotel_id: Hotel identifier
            files_to_package: List of {source, dest} dicts for real files on disk
            meta_entries: List of {name, size_bytes, type} for in-memory files
            timestamp_iso: NF-5 - pre-computed ISO timestamp (single datetime per run)

        Returns:
            Manifest dict (without MANIFEST.json self-entry yet).
        """
        manifest: Dict[str, Any] = {
            "version": "1.0.0",
            "hotel_id": hotel_id,
            "generated_at": timestamp_iso or datetime.now().isoformat(),
            "package_type": "automated_delivery",
            "files": []
        }

        # Add real files from disk
        for f in files_to_package:
            file_path = Path(f["source"])
            stat = file_path.stat() if file_path.exists() else None
            manifest["files"].append({
                "name": f["dest"],
                "size_bytes": stat.st_size if stat else 0,
                "type": self._classify_file(f["dest"])
            })

        # Add in-memory meta files (README, IMPLEMENTATION_ORDER)
        for entry in meta_entries:
            manifest["files"].append({
                "name": entry["name"],
                "size_bytes": entry["size_bytes"],
                "type": entry["type"]
            })

        manifest["total_files"] = len(manifest["files"])
        manifest["total_size_bytes"] = sum(f["size_bytes"] for f in manifest["files"])
        return manifest

    def _resolve_manifest_self_size(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve MANIFEST.json self-referencing size via fixed-point iteration.

        The manifest includes its own size, but including the size changes
        the file size. We iterate until the serialized size converges.
        Typically converges in 1-2 iterations (digit-count stability).
        """
        # Initial estimate: serialize without self-entry to get base size
        base_json = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
        estimated_size = len(base_json) + 120  # rough overhead for self-entry

        for _ in range(10):  # max iterations (safety)
            # Add/update self-entry
            manifest_copy = {
                "version": manifest["version"],
                "hotel_id": manifest["hotel_id"],
                "generated_at": manifest["generated_at"],
                "package_type": manifest["package_type"],
                "files": [f for f in manifest["files"] if f["name"] != "MANIFEST.json"],
            }
            # Preserve quality_metadata if present
            if "quality_metadata" in manifest:
                manifest_copy["quality_metadata"] = manifest["quality_metadata"]

            # Compute totals without self
            other_total = sum(f["size_bytes"] for f in manifest_copy["files"])

            # Add self-entry with current estimate
            manifest_copy["files"].append({
                "name": "MANIFEST.json",
                "size_bytes": estimated_size,
                "type": "other"
            })
            manifest_copy["total_files"] = len(manifest_copy["files"])
            manifest_copy["total_size_bytes"] = other_total + estimated_size

            # Serialize and measure
            serialized = json.dumps(manifest_copy, indent=2, ensure_ascii=False).encode("utf-8")
            actual_size = len(serialized)

            if actual_size == estimated_size:
                # Converged!
                return manifest_copy

            estimated_size = actual_size
            manifest = manifest_copy

        # If not converged after 10 iterations, use last estimate
        # (extremely unlikely — would require oscillating digit boundaries)
        return manifest_copy  # type: ignore

    def _create_zip_single_write(
        self,
        zip_path: Path,
        files_to_package: List[Dict[str, Any]],
        source_dir: Path,
        readme_bytes: bytes,
        implementation_order_bytes: Optional[bytes],
        manifest_bytes: bytes,
    ):
        """Write ZIP in a single pass: disk files + in-memory content.

        All content is finalized before this call. The ZIP is written
        atomically (caller handles tmp → rename).
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write real files from disk
            for file_info in files_to_package:
                source_path = Path(file_info["source"])
                if source_path.exists():
                    zf.write(source_path, arcname=file_info["dest"])

            # Write in-memory README
            zf.writestr("README_DELIVERY.md", readme_bytes)

            # Write in-memory IMPLEMENTATION_ORDER (if present)
            if implementation_order_bytes is not None:
                zf.writestr("IMPLEMENTATION_ORDER.md", implementation_order_bytes)

            # Write in-memory MANIFEST
            zf.writestr("MANIFEST.json", manifest_bytes)

    # ═══ FASE-B: New methods ═══

    def _make_zip_filename(self, hotel_id: str, date_str: Optional[str] = None) -> str:
        """Compute ZIP filename once, shared by package() and README (FASE-C).

        NF-5: Accepts pre-computed date_str to avoid redundant datetime.now().
        Format: {hotel_id}_{YYYYMMDD}.zip
        """
        if not date_str:
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

    def _default_readme(self, hotel_id: str, manifest: Optional[Dict[str, Any]], date_display: Optional[str] = None) -> str:
        """Generate default README when template is not available."""
        total_files = manifest.get("total_files", "N/A") if manifest else "N/A"

        return f"""# Delivery Package - {hotel_id}

**Generated:** {date_display or datetime.now().strftime("%Y-%m-%d")}
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
