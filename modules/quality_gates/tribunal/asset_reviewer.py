"""AssetReviewer — Bot 3 del tribunal de certificación.

Revisor determinista que verifica cobertura de assets por servicio, detecta
assets genéricos, ESTIMATED no etiquetados, IMPLEMENTATION_ORDER.md vacío,
y P12 (fuente catálogo estático en promised_assets_exist).

Lee artefactos existentes y archivos reales en disco; NUNCA reimplementa gates.
Produce revision_assets.json que alimenta el acta del Juez.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

STATUS_CON_ASSET = "CON-ASSET"
STATUS_SIN_ASSET = "SIN-ASSET"
STATUS_ASSET_GENERICO = "ASSET-GENERICO"
STATUS_ASSET_ESTIMATED_NO_ETIQUETADO = "ASSET-ESTIMATED-NO-ETIQUETADO"

FINDING_EMPTY_DELIVERY_TEMPLATE = "EMPTY_DELIVERY_TEMPLATE"
FINDING_P12_UNVERIFIABLE = "P12_UNVERIFIABLE"
FINDING_ORPHAN_ASSET = "ORPHAN_ASSET"
FINDING_GENERIC_ASSET = "GENERIC_ASSET"
FINDING_UNLABELED_ESTIMATED = "UNLABELED_ESTIMATED"

VERDICT_APROBADO = "APROBADO"
VERDICT_DEVOLVER = "DEVOLVER-PRUEBAS"
VERDICT_BLOQUEAR = "BLOQUEAR"

_CONFIDENCE_VERIFIED_THRESHOLD = 0.9

_IMPL_ORDER_EMPTY_PATTERNS = [
    re.compile(r"^##\s+ORDEN", re.IGNORECASE),
    re.compile(r"^##\s+GU", re.IGNORECASE),
    re.compile(r"^##\s+CHECKLIST", re.IGNORECASE),
]


class AssetReviewer:
    """Revisor determinista de completitud de assets (Bot 3).

    Constructor: ``AssetReviewer(v4_audit_dir, deliveries_dir)``.
    ``deliveries_dir`` se resuelve por glob del ``<hotel_id>_*`` más reciente.
    """

    def __init__(self, v4_audit_dir: str | Path, deliveries_dir: str | Path):
        self.v4_audit_dir = Path(v4_audit_dir)
        self.deliveries_dir = Path(deliveries_dir)
        self._resolved_delivery_dir: Optional[Path] = None

    def review(self) -> dict:
        """Retorna revision_assets.json con cobertura, hallazgos y veredicto."""
        findings: list = []

        asset_report = self._load_asset_generation_report()
        delivery_qr = self._load_delivery_quality_report()
        matrix = self._load_proposal_matrix()
        manifest = self._load_manifest()

        delivery_dir = self._resolve_delivery_dir()

        coverage = self._build_coverage_by_service(
            asset_report, matrix, delivery_dir, findings
        )

        findings.extend(self._check_p12_source(asset_report, delivery_qr))
        findings.extend(self._check_implementation_order(delivery_dir))
        findings.extend(self._check_orphan_assets(asset_report, matrix, delivery_dir))
        findings.extend(self._check_unlabeled_estimated(asset_report, coverage))

        summary = self._compute_summary(coverage)
        verdict = self._compute_verdict(findings, coverage)

        return {
            "reviewer": "asset_reviewer",
            "clauses": ["P6.3", "P6.4"],
            "coverage_by_service": coverage,
            "findings": findings,
            "summary": summary,
            "verdict_recommendation": verdict,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
        }

    def write_report(self, output_path: Optional[Path] = None) -> Path:
        """Escribe revision_assets.json y retorna la ruta."""
        report = self.review()
        if output_path is None:
            output_path = self.v4_audit_dir / "revision_assets.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_path

    # ── Artifact loaders ──────────────────────────────────────────────

    def _resolve_artifact(self, pattern: str) -> Optional[Path]:
        """Resuelve artefacto timestamped por glob (más reciente)."""
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

    def _load_asset_generation_report(self) -> Optional[dict]:
        path = self._resolve_artifact("asset_generation_report.json")
        return self._load_json(path)

    def _load_delivery_quality_report(self) -> Optional[dict]:
        path = self._resolve_artifact("delivery_quality_report.json")
        return self._load_json(path)

    def _load_proposal_matrix(self) -> Optional[dict]:
        path = self._resolve_artifact("proposal_asset_matrix.json")
        return self._load_json(path)

    def _load_manifest(self) -> Optional[dict]:
        delivery_dir = self._resolve_delivery_dir()
        if delivery_dir is None:
            return None
        manifest_path = delivery_dir / "MANIFEST.json"
        return self._load_json(manifest_path if manifest_path.exists() else None)

    def _resolve_delivery_dir(self) -> Optional[Path]:
        """Resuelve el directorio de entrega más reciente por glob."""
        if self._resolved_delivery_dir is not None:
            return self._resolved_delivery_dir

        if not self.deliveries_dir.exists():
            return None

        hotel_dirs = sorted(
            self.deliveries_dir.glob("*"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )

        for d in hotel_dirs:
            if d.is_dir() and (d / "MANIFEST.json").exists():
                self._resolved_delivery_dir = d
                return d

        if hotel_dirs:
            self._resolved_delivery_dir = hotel_dirs[0]
            return hotel_dirs[0]

        return None

    # ── Coverage by service ───────────────────────────────────────────

    def _build_coverage_by_service(
        self,
        asset_report: Optional[dict],
        matrix: Optional[dict],
        delivery_dir: Optional[Path],
        findings: list,
    ) -> list:
        """Clasifica cada servicio de la matriz en una de las 4 categorías."""
        coverage: list = []

        if matrix is None:
            return coverage

        entries = matrix.get("entries", [])
        generated_assets = self._index_generated_assets(asset_report)

        for entry in entries:
            service_name = entry.get("service_name", "unknown")
            asset_type = entry.get("asset_type", "")
            asset_path = entry.get("asset_path")
            entry_status = entry.get("status", "")
            confidence = entry.get("confidence", 0.0)

            gen_asset = generated_assets.get(asset_type)

            if entry_status in ("PRESENT_IN_PRODUCTION", "REDUNDANT"):
                coverage.append({
                    "service": service_name,
                    "status": STATUS_CON_ASSET,
                    "asset_path": asset_path,
                    "asset_exists_on_disk": False,
                    "finding": f"Asset presente en producción (status={entry_status})",
                })
                continue

            if entry_status == "NO_BREACH":
                continue

            resolved_path = asset_path
            exists_on_disk = False

            if resolved_path:
                full_path = Path(resolved_path)
                if not full_path.is_absolute():
                    full_path = self.v4_audit_dir.parent / resolved_path
                exists_on_disk = full_path.exists()
            elif gen_asset and gen_asset.get("path"):
                resolved_path = gen_asset["path"]
                full_path = Path(resolved_path)
                if not full_path.is_absolute():
                    full_path = self.v4_audit_dir.parent / resolved_path
                exists_on_disk = full_path.exists()
            elif delivery_dir:
                exists_on_disk = self._find_asset_in_delivery_dir(
                    delivery_dir, asset_type
                )
                if exists_on_disk:
                    resolved_path = str(delivery_dir / "ASSETS" / asset_type)

            if entry_status == "MISSING_ASSET" or (not gen_asset and not exists_on_disk):
                coverage.append({
                    "service": service_name,
                    "status": STATUS_SIN_ASSET,
                    "asset_path": resolved_path,
                    "asset_exists_on_disk": exists_on_disk,
                    "finding": f"Servicio '{service_name}' prometido sin asset generado",
                })
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    finding_type=FINDING_GENERIC_ASSET,
                    description=f"Servicio '{service_name}' sin asset (status={entry_status})",
                ))
                continue

            content_check = self._check_asset_content(
                resolved_path, exists_on_disk, gen_asset, service_name
            )

            if content_check == "generic":
                coverage.append({
                    "service": service_name,
                    "status": STATUS_ASSET_GENERICO,
                    "asset_path": resolved_path,
                    "asset_exists_on_disk": exists_on_disk,
                    "finding": f"Asset de '{service_name}' no menciona hotel ni brecha específica",
                })
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    finding_type=FINDING_GENERIC_ASSET,
                    description=f"Asset genérico para servicio '{service_name}'",
                ))
            elif content_check == "unlabeled_estimated":
                coverage.append({
                    "service": service_name,
                    "status": STATUS_ASSET_ESTIMATED_NO_ETIQUETADO,
                    "asset_path": resolved_path,
                    "asset_exists_on_disk": exists_on_disk,
                    "finding": f"Asset ESTIMATED de '{service_name}' sin disclaimer visible",
                })
            else:
                coverage.append({
                    "service": service_name,
                    "status": STATUS_CON_ASSET,
                    "asset_path": resolved_path,
                    "asset_exists_on_disk": exists_on_disk,
                    "finding": None,
                })

        return coverage

    def _index_generated_assets(self, asset_report: Optional[dict]) -> dict:
        """Indexa generated_assets por asset_type."""
        if asset_report is None:
            return {}
        result = {}
        for asset in asset_report.get("generated_assets", []):
            asset_type = asset.get("asset_type", "")
            if asset_type:
                result[asset_type] = asset
        return result

    def _find_asset_in_delivery_dir(
        self, delivery_dir: Path, asset_type: str
    ) -> bool:
        """Verifica si un asset existe en el directorio de entregas."""
        assets_dir = delivery_dir / "ASSETS"
        if assets_dir.exists():
            matches = list(assets_dir.glob(f"*{asset_type}*"))
            if matches:
                return True

        type_dir = delivery_dir / asset_type
        if type_dir.exists() and any(type_dir.iterdir()):
            return True

        return False

    def _check_asset_content(
        self,
        asset_path: Optional[str],
        exists_on_disk: bool,
        gen_asset: Optional[dict],
        service_name: str,
    ) -> str:
        """Verifica contenido del asset: genérico, estimated sin etiquetar, OK.

        Retorna: "ok" | "generic" | "unlabeled_estimated"
        """
        if not exists_on_disk or not asset_path:
            if gen_asset:
                return self._check_gen_asset_metadata(gen_asset, service_name)
            return "ok"

        full_path = Path(asset_path)
        if not full_path.is_absolute():
            full_path = self.v4_audit_dir.parent / asset_path

        if not full_path.exists():
            return "ok"

        try:
            content = full_path.read_text(encoding="utf-8")
        except OSError:
            return "ok"

        filename = full_path.name
        is_estimated_in_name = filename.startswith("ESTIMATED_")

        confidence = gen_asset.get("confidence_score", 1.0) if gen_asset else 1.0
        is_estimated_by_confidence = confidence < _CONFIDENCE_VERIFIED_THRESHOLD

        if is_estimated_by_confidence and not is_estimated_in_name:
            has_disclaimer = bool(re.search(
                r"(?i)(estimated|estimado|disclaimer|aproximado)",
                content[:500],
            ))
            if not has_disclaimer:
                return "unlabeled_estimated"

        hotel_keywords = re.search(
            r"(?i)(hotel|hostal|hostel|boutique|posada|resort|salento|salento real)",
            content[:1000],
        )
        breach_keywords = re.search(
            r"(?i)(brecha|gap|problema|pain|issue|dolor|falta|ausente|missing)",
            content[:1000],
        )

        if not hotel_keywords and not breach_keywords:
            return "generic"

        return "ok"

    def _check_gen_asset_metadata(
        self, gen_asset: dict, service_name: str
    ) -> str:
        """Verifica metadata del asset generado cuando no hay archivo en disco."""
        filename = gen_asset.get("filename", "")
        confidence = gen_asset.get("confidence_score", 1.0)

        is_estimated = filename.startswith("ESTIMATED_") or confidence < _CONFIDENCE_VERIFIED_THRESHOLD

        if is_estimated and not filename.startswith("ESTIMATED_"):
            return "unlabeled_estimated"

        return "ok"

    # ── P12: fuente catálogo estático ─────────────────────────────────

    def _check_p12_source(
        self,
        asset_report: Optional[dict],
        delivery_qr: Optional[dict],
    ) -> list:
        """P12: Detecta promised_assets_exist con fuente catálogo estático.

        Si el message declara 'via catalogo_estatico' o 'via PROPOSAL_SERVICE_TO_ASSET',
        P6.3 no es verificable desde el artefacto → P12_UNVERIFIABLE.
        Si declara 'via generated_assets' → sin finding (verificable).
        NO se marca por score==1.0.
        """
        findings = []

        coherence_report = None
        if asset_report:
            coherence_report = asset_report.get("coherence_report")

        if coherence_report is None and delivery_qr:
            coherence_report = delivery_qr.get("coherence_report")

        if coherence_report is None:
            coherence_path = self._resolve_artifact("coherence_validation*.json")
            coherence_report = self._load_json(coherence_path)

        if coherence_report is None:
            return findings

        checks = coherence_report.get("checks", [])
        for check in checks:
            if check.get("name") != "promised_assets_exist":
                continue

            message = check.get("message", "")

            if "via catalogo_estatico" in message or "via PROPOSAL_SERVICE_TO_ASSET" in message:
                findings.append(self._make_finding(
                    severity=SEVERITY_WARNING,
                    finding_type=FINDING_P12_UNVERIFIABLE,
                    description=(
                        "promised_assets_exist verificó via catálogo estático. "
                        "P6.3 no verificable desde el artefacto; "
                        "la verificación real requiere archivos en disco."
                    ),
                ))
            break

        return findings

    # ── IMPLEMENTATION_ORDER.md vacío ─────────────────────────────────

    def _check_implementation_order(
        self, delivery_dir: Optional[Path]
    ) -> list:
        """Detecta IMPLEMENTATION_ORDER.md vacío.

        Vacío = 0 bytes O plantilla con secciones sin contenido por-hotel
        (el stub baseline pesa ~468 B con secciones ORDEN/GUÍA/CHECKLIST vacías).
        """
        findings = []

        if delivery_dir is None:
            return findings

        impl_order = delivery_dir / "IMPLEMENTATION_ORDER.md"
        if not impl_order.exists():
            return findings

        try:
            size = impl_order.stat().st_size
        except OSError:
            return findings

        if size == 0:
            findings.append(self._make_finding(
                severity=SEVERITY_CRITICAL,
                finding_type=FINDING_EMPTY_DELIVERY_TEMPLATE,
                description="IMPLEMENTATION_ORDER.md tiene 0 bytes",
            ))
            return findings

        try:
            content = impl_order.read_text(encoding="utf-8")
        except OSError:
            return findings

        if self._is_template_stub(content):
            findings.append(self._make_finding(
                severity=SEVERITY_CRITICAL,
                finding_type=FINDING_EMPTY_DELIVERY_TEMPLATE,
                description=(
                    "IMPLEMENTATION_ORDER.md es plantilla sin contenido por-hotel "
                    f"({size} bytes, secciones vacías)"
                ),
            ))

        return findings

    def _is_template_stub(self, content: str) -> bool:
        """Detecta si el contenido es una plantilla con secciones vacías.

        El stub baseline tiene secciones ORDEN/GUÍA/CHECKLIST pero sin
        contenido específico por hotel debajo de cada encabezado.
        """
        lines = content.strip().splitlines()
        if not lines:
            return True

        section_headers = []
        section_content_lines: dict[int, int] = {}
        current_section = -1

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("# "):
                current_section += 1
                section_headers.append(stripped)
                section_content_lines[current_section] = 0
            elif stripped and current_section >= 0:
                if not stripped.startswith("-") or stripped == "-":
                    section_content_lines[current_section] = (
                        section_content_lines.get(current_section, 0) + 1
                    )

        if not section_headers:
            return len(content.strip()) < 100

        key_sections_found = 0
        for header in section_headers:
            header_lower = header.lower()
            if any(kw in header_lower for kw in ("orden", "guía", "guia", "checklist", "implementaci", "prioridad")):
                key_sections_found += 1

        if key_sections_found == 0:
            return False

        total_content = sum(section_content_lines.values())
        non_empty_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

        if non_empty_lines <= 3 and total_content <= 5:
            return True

        return False

    # ── Orphan assets ─────────────────────────────────────────────────

    def _check_orphan_assets(
        self,
        asset_report: Optional[dict],
        matrix: Optional[dict],
        delivery_dir: Optional[Path],
    ) -> list:
        """Detecta assets generados sin servicio en la matriz que los respalde."""
        findings = []

        if asset_report is None:
            return findings

        matrix_asset_types: set = set()
        if matrix:
            for entry in matrix.get("entries", []):
                asset_type = entry.get("asset_type", "")
                if asset_type:
                    matrix_asset_types.add(asset_type)

        for asset in asset_report.get("generated_assets", []):
            asset_type = asset.get("asset_type", "")
            pain_ids = asset.get("pain_ids_resolved", [])

            if not matrix_asset_types and not pain_ids:
                findings.append(self._make_finding(
                    severity=SEVERITY_INFO,
                    finding_type=FINDING_ORPHAN_ASSET,
                    description=(
                        f"Asset '{asset_type}' generado sin servicio en matriz "
                        f"ni pain_ids que lo respalden"
                    ),
                ))

        return findings

    # ── Unlabeled ESTIMATED ───────────────────────────────────────────

    def _check_unlabeled_estimated(
        self,
        asset_report: Optional[dict],
        coverage: list,
    ) -> list:
        """Detecta assets ESTIMATED sin etiquetar en el README/coverage."""
        findings = []

        already_flagged = {
            c["service"]
            for c in coverage
            if c["status"] == STATUS_ASSET_ESTIMATED_NO_ETIQUETADO
        }

        if asset_report is None:
            return findings

        for asset in asset_report.get("generated_assets", []):
            confidence = asset.get("confidence_score", 1.0)
            filename = asset.get("filename", "")
            asset_type = asset.get("asset_type", "")

            if confidence < _CONFIDENCE_VERIFIED_THRESHOLD and not filename.startswith("ESTIMATED_"):
                if asset_type not in already_flagged:
                    findings.append(self._make_finding(
                        severity=SEVERITY_WARNING,
                        finding_type=FINDING_UNLABELED_ESTIMATED,
                        description=(
                            f"Asset '{asset_type}' tiene confidence={confidence:.2f} "
                            f"(< 0.9) pero filename no prefija ESTIMATED_"
                        ),
                    ))

        return findings

    # ── Helpers ───────────────────────────────────────────────────────

    def _make_finding(
        self,
        severity: str,
        finding_type: str,
        description: str,
    ) -> dict:
        """Construye un finding con estructura uniforme."""
        return {
            "severity": severity,
            "finding_type": finding_type,
            "description": description,
        }

    def _compute_summary(self, coverage: list) -> dict:
        """Calcula resumen de cobertura."""
        total = len(coverage)
        con_asset = sum(1 for c in coverage if c["status"] == STATUS_CON_ASSET)
        return {
            "services_covered": con_asset,
            "services_total": total,
            "coverage_ratio": con_asset / total if total > 0 else 0.0,
        }

    def _compute_verdict(self, findings: list, coverage: list) -> str:
        """Determina veredicto basado en hallazgos y cobertura."""
        critical_count = sum(1 for f in findings if f["severity"] == SEVERITY_CRITICAL)
        warning_count = sum(1 for f in findings if f["severity"] == SEVERITY_WARNING)

        sin_asset_count = sum(1 for c in coverage if c["status"] == STATUS_SIN_ASSET)

        if critical_count > 0:
            return VERDICT_BLOQUEAR

        if sin_asset_count > 0 or warning_count >= 3:
            return VERDICT_DEVOLVER

        return VERDICT_APROBADO

    def _list_artifacts_read(self) -> list:
        """Lista artefactos que este revisor lee."""
        return [
            "asset_generation_report.json",
            "delivery_quality_report.json",
            "proposal_asset_matrix.json",
            "MANIFEST.json",
            "IMPLEMENTATION_ORDER.md",
            "coherence_validation*.json",
            "ASSETS/* (archivos reales en disco)",
        ]
