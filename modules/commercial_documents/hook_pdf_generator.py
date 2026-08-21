"""
HookPDFGenerator — Genera el PDF de 2 páginas "¿Cuánto pierde su hotel?"

Extrae datos de los 3 archivos fuente de v4_complete:
- 01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md (frontmatter YAML + scores + GBP)
- 02_PROPUESTA_COMERCIAL_{timestamp}.md (frontmatter YAML + fuga + proyección + ROI + pricing)
- v4_complete_report.json (opportunity_scores, gates, pricing)

Usa el template templates/hook_template.md (HTML con placeholders {{CAMPO}})
y los estilos CSS templates/hook_styles.css.

Genera el PDF con weasyprint.
"""

import json
import re
import unicodedata
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import yaml
from weasyprint import HTML

from modules.commercial_documents.data_structures import HookPDFData
from modules.financial_engine.pricing_calculator import _load_pricing_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_yaml_frontmatter(text: str) -> dict:
    """Extrae el bloque YAML frontmatter (entre '---' al inicio del archivo)."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)[1:]
    if len(parts) >= 1:
        try:
            return yaml.safe_load(parts[0]) or {}
        except yaml.YAMLError:
            return {}
    return {}


def _format_cop(value: float | int | str) -> str:
    """Formato COP: separador de miles (.) sin decimales. Ej: 3741696 → '3.741.696'"""
    if isinstance(value, str):
        value = value.replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            value = float(value)
        except ValueError:
            return value  # devolver tal cual si no es numérico
    if value is None:
        return ""
    return f"{value:,.0f}".replace(",", ".")


def _slugify(text: str) -> str:
    """Convierte nombre de hotel a slug: sin acentos, minúsculas, sin especiales."""
    text = text.lower().strip()
    # Normalizar y quitar acentos
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Solo letras, números, espacios y guiones bajos
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip("_")


def _parse_score_cell(value: str) -> str:
    """Extrae el valor numérico de una celda como '25/100' → '25'."""
    value = value.strip()
    # Si ya es solo número, devolverlo
    if re.match(r"^\d+$", value):
        return value
    # Intentar extraer "25/100"
    m = re.match(r"(\d+)\s*/\s*\d+", value)
    if m:
        return m.group(1)
    return value


def _parse_cop_number(value: str) -> float | None:
    """Parsea un string COP formateado ('3.741.696') a float. None si no es numérico."""
    if not value or not isinstance(value, str):
        return None
    clean = value.replace("$", "").replace(".", "").replace(",", "").strip()
    try:
        return float(clean)
    except ValueError:
        return None


def _extract_row_cells(text: str, section_label: str, row_label: str) -> list[str]:
    """
    Encuentra una tabla en el markdown y extrae celdas de una fila específica.
    Busca sección por H2/H3, luego fila por texto en la primera columna.
    Retorna lista de celdas de esa fila.
    """
    # Buscar la sección
    section_pattern = rf"(?:^|\n)#{{2,3}}\s+[^\n]*{re.escape(section_label)}[^\n]*\n(.*?)(?:\n#{{2,3}}\s|\n\n##|\Z)"
    section_match = re.search(section_pattern, text, re.DOTALL | re.IGNORECASE)
    if not section_match:
        section_match = re.search(rf"(?:^|\n)#{{2,3}}\s+[^\n]*score[^\n]*\n(.*?)(?:\n#{{2,3}}\s|\n\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return []

    section = section_match.group(1) if section_match.lastindex and section_match.lastindex >= 1 else ""

    # Buscar la fila que contiene row_label
    lines = section.split("\n")
    for line in lines:
        if re.search(re.escape(row_label), line, re.IGNORECASE):
            # Parsear celdas de tabla markdown: | celda | celda | ...
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c]  # quitar vacíos de bordes
            return cells

    return []


# ---------------------------------------------------------------------------
# HookPDFGenerator
# ---------------------------------------------------------------------------

class HookPDFGenerator:
    """Genera el PDF de gancho comercial de 2 páginas para v4_complete.

    Pricing cargado dinámicamente desde config/pricing.yaml (D6: fuente única).
    """

    def __init__(
        self,
        output_dir: Path,
        template_path: Optional[Path] = None,
        style_path: Optional[Path] = None,
    ):
        """
        Args:
            output_dir: Directorio donde están los 3 archivos fuente (output/v4_complete/).
            template_path: Ruta al template HTML. Default: PROJECT_ROOT/templates/hook_template.md
            style_path: Ruta al CSS. Default: PROJECT_ROOT/templates/hook_styles.css
        """
        self.output_dir = Path(output_dir)
        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.template_path = template_path or self.project_root / "templates" / "hook_template.md"
        self.style_path = style_path or self.project_root / "templates" / "hook_styles.css"
        self._pricing_packages = None

    def _get_pricing_packages(self) -> dict:
        """Carga pricing.yaml con caché de instancia. Fuente única D6."""
        if self._pricing_packages is None:
            try:
                self._pricing_packages = _load_pricing_config()["packages"]
            except Exception:
                self._pricing_packages = {
                    "monthly_default": 1_200_000,
                    "setup_fee_default": 2_500_000,
                    "express_price": 120_000,
                }
        return self._pricing_packages

    # ------------------------------------------------------------------
    # extract_data
    # ------------------------------------------------------------------

    def extract_data(self) -> HookPDFData:
        """
        Extrae todos los datos desde los 3 archivos fuente de v4_complete.

        Returns:
            HookPDFData con los 34 campos poblados.

        Raises:
            FileNotFoundError: Si falta alguno de los 3 archivos fuente.
        """
        # --- 1. Localizar archivos fuente con glob ---
        diag_files = sorted(self.output_dir.glob("01_DIAGNOSTICO_*.md"))
        prop_files = sorted(self.output_dir.glob("02_PROPUESTA_*.md"))
        report_files = sorted(self.output_dir.glob("v4_complete_report.json"))

        if not diag_files:
            raise FileNotFoundError(
                f"No se encontró 01_DIAGNOSTICO_*.md en {self.output_dir}"
            )
        if not prop_files:
            raise FileNotFoundError(
                f"No se encontró 02_PROPUESTA_*.md en {self.output_dir}"
            )
        if not report_files:
            raise FileNotFoundError(
                f"No se encontró v4_complete_report.json en {self.output_dir}"
            )

        diag_path = diag_files[-1]  # más reciente
        prop_path = prop_files[-1]
        report_path = report_files[-1]

        # --- 2. Leer archivos ---
        diag_text = diag_path.read_text(encoding="utf-8")
        prop_text = prop_path.read_text(encoding="utf-8")
        report_json = json.loads(report_path.read_text(encoding="utf-8"))

        # --- 3. Parsear frontmatter YAML ---
        diag_fm = _parse_yaml_frontmatter(diag_text)
        prop_fm = _parse_yaml_frontmatter(prop_text)

        # --- 4. Datos del hotel ---
        hotel_nombre = report_json.get("hotel_name", "")
        hotel_url = report_json.get("url", "")
        hotel_region = report_json.get("region", "")

        # Dirección: buscar en el cuerpo del diagnóstico (línea con "##" que contiene hotel + dirección)
        direccion = ""
        for line in diag_text.split("\n"):
            if line.startswith("## ") and hotel_nombre.lower() in line.lower():
                # "## Luxorhotel - Cl. 24 #8-35, Pereira, Risaralda, Colombia"
                parts = line.split("## ", 1)[-1].split(" - ", 1)
                if len(parts) >= 2:
                    direccion = parts[1].strip()
                break

        # GBP: buscar en el cuerpo del diagnóstico
        gbp_resenas = ""
        gbp_rating = ""
        gbp_match = re.search(
            r"(\d+)\s*reviews?.*?(\d+\.?\d*)\s*/\s*\d+\s*rating",
            diag_text, re.IGNORECASE
        )
        if not gbp_match:
            # Formato alternativo: "277 reviews, 4.1/5 rating"
            gbp_match = re.search(
                r"(\d+)\s*reviews?.*?(\d+\.?\d*)/\d+\s*rating",
                diag_text, re.IGNORECASE
            )
        if gbp_match:
            gbp_resenas = gbp_match.group(1)
            gbp_rating = gbp_match.group(2)

        if not gbp_resenas:
            # Buscar en el frontmatter
            gbp_resenas = str(diag_fm.get("gbp_resenas", ""))
            gbp_rating = str(diag_fm.get("gbp_rating", ""))

        # --- 5. Scores de visibilidad digital ---
        seo_score = ""
        seo_regional = ""
        geo_score = ""
        geo_regional = ""
        aeo_score = ""
        aeo_regional = ""
        iao_score = ""
        iao_regional = ""

        # Buscar tabla de scores en diagnóstico
        seo_cells = _extract_row_cells(diag_text, "Score de Visibilidad", "SEO")
        if seo_cells and len(seo_cells) >= 3:
            seo_score = _parse_score_cell(seo_cells[1])
            seo_regional = _parse_score_cell(seo_cells[2])

        geo_cells = _extract_row_cells(diag_text, "Score de Visibilidad", "GEO")
        if geo_cells and len(geo_cells) >= 3:
            geo_score = _parse_score_cell(geo_cells[1])
            geo_regional = _parse_score_cell(geo_cells[2])

        aeo_cells = _extract_row_cells(diag_text, "Score de Visibilidad", "AEO")
        if aeo_cells and len(aeo_cells) >= 3:
            aeo_score = _parse_score_cell(aeo_cells[1])
            aeo_regional = _parse_score_cell(aeo_cells[2])

        iao_cells = _extract_row_cells(diag_text, "Score de Visibilidad", "IAO")
        if iao_cells and len(iao_cells) >= 3:
            iao_score = _parse_score_cell(iao_cells[1])
            iao_regional = _parse_score_cell(iao_cells[2])

        # Fallback: usar scores del JSON
        if not seo_score:
            seo_score = str(report_json.get("seo_score", ""))
        if not geo_score:
            geo_score = str(diag_fm.get("geo_score", report_json.get("geo_score", "")))
        if not aeo_score:
            aeo_score = str(diag_fm.get("aeo_score", ""))
        if not iao_score:
            iao_score = str(diag_fm.get("iao_score", ""))

        # --- 6. Datos financieros ---
        financial = report_json.get("financial_data", {})
        expected_monthly = financial.get("expected_monthly", 0)

        fuga_mensual = _format_cop(expected_monthly)

        # Fuga mínima y máxima del frontmatter del diagnóstico
        fuga_minima = ""
        fuga_maxima = ""
        fm_range = diag_fm.get("financial_value_range", [])
        if isinstance(fm_range, list) and len(fm_range) >= 2:
            fuga_minima = _format_cop(fm_range[0])
            fuga_maxima = _format_cop(fm_range[1])

        # Comisión OTA del frontmatter
        ota_value = diag_fm.get("financial_ota_commission_real", "")
        if isinstance(ota_value, str):
            # Limpiar: "$7.741.440 COP" → 7741440
            ota_value = ota_value.replace("$", "").replace(".", "").replace("COP", "").strip()
            try:
                ota_value = float(ota_value)
            except ValueError:
                ota_value = 0.0
        comision_ota_real = _format_cop(ota_value) if ota_value else ""

        # Recuperación 6m y fuga 6m — del cuerpo del diagnóstico
        # Buscar la tabla "Lo que está en juego" o la fila "Monto"
        # Formato: || **Monto** | $22.450.176 COP | $1.571.508 COP ||
        recuperacion_6m = ""
        fuga_6m = ""

        monto_match = re.search(
            r"\*\*Monto\*\*\s*\|\s*\$?\s*([\d.,]+)\s*COP\s*\|\s*\$?\s*([\d.,]+)\s*COP",
            diag_text, re.IGNORECASE
        )
        if monto_match:
            fuga_6m = _format_cop(monto_match.group(1).replace(".", "").replace(",", ""))
            recuperacion_6m = _format_cop(monto_match.group(2).replace(".", "").replace(",", ""))

        # Fallback: Proyección 6 meses
        if not fuga_6m:
            proj_match = re.search(
                r"Proyección 6 meses.*?\$\s*([\d.,]+)\s*COP",
                diag_text, re.IGNORECASE
            )
            if proj_match:
                fuga_6m = _format_cop(proj_match.group(1).replace(".", "").replace(",", ""))

        # ROI desde la propuesta
        roi = ""
        roi_match = re.search(
            r"ROIC?R?:\s*([\d.]+)x?",
            prop_text, re.IGNORECASE
        )
        if roi_match:
            roi = f"{roi_match.group(1)}x"

        # --- 7. Top 3 brechas desde opportunity_scores ---
        opportunity_scores = report_json.get("opportunity_scores", [])

        brecha_1_nombre = ""
        brecha_1_cop = ""
        brecha_1_justificacion = ""
        brecha_2_nombre = ""
        brecha_2_cop = ""
        brecha_2_justificacion = ""
        brecha_3_nombre = ""
        brecha_3_cop = ""
        brecha_3_justificacion = ""

        # Ordenar por rank (ya deberían estar ordenados, pero aseguramos)
        sorted_opps = sorted(opportunity_scores, key=lambda x: x.get("rank", 999))

        for i, opp in enumerate(sorted_opps[:3]):
            nombre = opp.get("brecha_name", "")
            cop = _format_cop(opp.get("estimated_monthly_cop", 0))
            justificacion = opp.get("justification", "")

            # Truncar justificación larga
            if len(justificacion) > 200:
                justificacion = justificacion[:197] + "..."

            if i == 0:
                brecha_1_nombre = nombre
                brecha_1_cop = cop
                brecha_1_justificacion = justificacion
            elif i == 1:
                brecha_2_nombre = nombre
                brecha_2_cop = cop
                brecha_2_justificacion = justificacion
            elif i == 2:
                brecha_3_nombre = nombre
                brecha_3_cop = cop
                brecha_3_justificacion = justificacion

        # --- 8. Pricing desde pricing.yaml (D6: fuente única) ---
        pricing = self._get_pricing_packages()
        precio_express = _format_cop(pricing.get("express_price", 120_000))
        precio_mensual = _format_cop(pricing.get("monthly_default", 1_200_000))
        setup_fee = _format_cop(pricing.get("setup_fee_default", 2_500_000))

        # --- 9. Evidence tier ---
        evidence_tier = ""
        # Del frontmatter del diagnóstico
        tier = diag_fm.get("financial_evidence_tier", "")
        if tier:
            evidence_tier = str(tier).strip('"').upper()
        if not evidence_tier:
            # Del JSON gates
            gates = report_json.get("phases", {}).get("phase_4_publication_gates", {}).get("gate_results", [])
            for gate in gates:
                if gate.get("gate_name") == "tier_c_onboarding_required":
                    details = gate.get("details", {})
                    tier = details.get("tier", "")
                    if tier:
                        evidence_tier = str(tier).strip('"').upper()
                    break

        if not evidence_tier:
            evidence_tier = "B"  # default

        # --- 10. Construir el dataclass ---
        return HookPDFData(
            hotel_nombre=hotel_nombre,
            hotel_url=hotel_url,
            hotel_region=hotel_region,
            hotel_direccion=direccion,
            gbp_resenas=gbp_resenas,
            gbp_rating=gbp_rating,
            fuga_mensual=fuga_mensual,
            fuga_minima=fuga_minima,
            fuga_maxima=fuga_maxima,
            comision_ota_real=comision_ota_real,
            recuperacion_6m=recuperacion_6m,
            roi=roi,
            fuga_6m=fuga_6m,
            seo_score=seo_score,
            seo_regional=seo_regional,
            geo_score=geo_score,
            geo_regional=geo_regional,
            aeo_score=aeo_score,
            aeo_regional=aeo_regional,
            iao_score=iao_score,
            iao_regional=iao_regional,
            brecha_1_nombre=brecha_1_nombre,
            brecha_1_cop=brecha_1_cop,
            brecha_1_justificacion=brecha_1_justificacion,
            brecha_2_nombre=brecha_2_nombre,
            brecha_2_cop=brecha_2_cop,
            brecha_2_justificacion=brecha_2_justificacion,
            brecha_3_nombre=brecha_3_nombre,
            brecha_3_cop=brecha_3_cop,
            brecha_3_justificacion=brecha_3_justificacion,
            precio_express=precio_express,
            precio_mensual=precio_mensual,
            setup_fee=setup_fee,
            evidence_tier=evidence_tier,
        )

    # ------------------------------------------------------------------
    # validate_data
    # ------------------------------------------------------------------

    def validate_data(self, data: HookPDFData) -> list[str]:
        """
        Ejecuta las 8 validaciones sobre los datos extraídos.

        Args:
            data: Dataclass con los datos extraídos.

        Returns:
            Lista de strings con warnings/errores. Lista vacía = todo ok.
        """
        warnings: list[str] = []

        # 1. Placeholders sin llenar: verificar que ningún campo obligatorio está vacío
        # (excepto los opcionales: fuga_minima, fuga_maxima, comision_ota_real, recuperacion_6m, roi, fuga_6m)
        optional_fields = {
            "fuga_minima", "fuga_maxima", "comision_ota_real",
            "recuperacion_6m", "roi", "fuga_6m",
        }
        data_dict = asdict(data)
        for field_name, value in data_dict.items():
            if field_name in optional_fields:
                continue
            if not value or (isinstance(value, str) and not value.strip()):
                warnings.append(f"[WARN] Campo obligatorio vacio: {field_name}")

        # 2. Campos obligatorios críticos
        critical_fields = {
            "hotel_nombre": data.hotel_nombre,
            "fuga_mensual": data.fuga_mensual,
            "brecha_1_nombre": data.brecha_1_nombre,
            "seo_score": data.seo_score,
            "precio_mensual": data.precio_mensual,
        }
        for name, value in critical_fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                warnings.append(f"[ERROR] CAMPO OBLIGATORIO FALTANTE: {name}")

        # 3. Timestamps: verificar que los archivos fuente existen (ya se validó en extract)
        diag_files = list(self.output_dir.glob("01_DIAGNOSTICO_*.md"))
        prop_files = list(self.output_dir.glob("02_PROPUESTA_*.md"))
        report_files = list(self.output_dir.glob("v4_complete_report.json"))

        if not diag_files:
            warnings.append("[ERROR] Archivo fuente faltante: 01_DIAGNOSTICO_*.md")
        if not prop_files:
            warnings.append("[ERROR] Archivo fuente faltante: 02_PROPUESTA_*.md")
        if not report_files:
            warnings.append("[ERROR] Archivo fuente faltante: v4_complete_report.json")

        # 4. Formato COP: verificar que los campos financieros usen separador de miles (.)
        cop_fields = {
            "fuga_mensual": data.fuga_mensual,
            "fuga_minima": data.fuga_minima,
            "fuga_maxima": data.fuga_maxima,
            "comision_ota_real": data.comision_ota_real,
            "recuperacion_6m": data.recuperacion_6m,
            "fuga_6m": data.fuga_6m,
            "brecha_1_cop": data.brecha_1_cop,
            "brecha_2_cop": data.brecha_2_cop,
            "brecha_3_cop": data.brecha_3_cop,
        }
        for name, value in cop_fields.items():
            if value and isinstance(value, str) and value.strip():
                # Debe tener formato con puntos como separador de miles
                # Solo verificar si es numérico
                clean = value.replace(".", "").strip()
                if clean.isdigit() and "." not in value and len(clean) > 3:
                    warnings.append(f"[WARN] Formato COP sospechoso en {name}: '{value}' -- falta separador de miles?")

        # 5. Slug: verificar que el nombre no tenga acentos ni especiales
        slug = _slugify(data.hotel_nombre)
        # Verificar que no hay acentos en el original
        normalized = unicodedata.normalize("NFKD", data.hotel_nombre)
        if normalized != data.hotel_nombre:
            warnings.append(
                f"[WARN] El nombre del hotel '{data.hotel_nombre}' contiene acentos. "
                f"Slug generado: '{slug}'"
            )

        # 6. No-sobrescritura: se maneja en generate(), no aquí
        # 7. Dry-run: se maneja en generate(), no aquí

        # 8. Tier detection: evidence_tier debe ser "A", "B", o "C"
        valid_tiers = {"A", "B+", "B", "C"}
        if data.evidence_tier not in valid_tiers:
            warnings.append(
                f"[WARN] Evidence tier invalido: '{data.evidence_tier}'. "
                f"Debe ser A, B o C. Usando 'B' como fallback."
            )

        # 9. F11 (FASE-P1-C): corredor Hook → Express — si el rango del hook está
        # disponible, verificar que la fuga real calculada caiga dentro del
        # corredor prometido (advisory, tolerancia 10%).
        if data.fuga_minima and data.fuga_maxima and data.fuga_mensual:
            vmin = _parse_cop_number(data.fuga_minima)
            vmax = _parse_cop_number(data.fuga_maxima)
            vreal = _parse_cop_number(data.fuga_mensual)
            if vmin is not None and vmax is not None and vreal is not None and vmin > 0:
                tolerance = 0.10
                if vreal < vmin * (1 - tolerance) or vreal > vmax * (1 + tolerance):
                    warnings.append(
                        f"[WARN] F11: fuga_mensual {data.fuga_mensual} fuera del "
                        f"corredor del hook [{data.fuga_minima} - {data.fuga_maxima}] "
                        f"(tolerancia 10%). Documentar la delta benchmark → dato real."
                    )

        return warnings

    # ------------------------------------------------------------------
    # render_html
    # ------------------------------------------------------------------

    def render_html(self, data: HookPDFData) -> str:
        """
        Renderiza el HTML reemplazando placeholders {{CAMPO}} en el template.

        Args:
            data: Dataclass con los datos completos.

        Returns:
            String HTML con todos los placeholders reemplazados.
        """
        template_html = self.template_path.read_text(encoding="utf-8")

        # Leer el CSS e inyectarlo inline (weasyprint lo necesita para PDF)
        try:
            css_content = self.style_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            css_content = ""

        # Mapa de placeholders: {{CAMPO}} → valor
        data_dict = asdict(data)

        placeholder_map = {}
        for field_name, value in data_dict.items():
            placeholder = "{{" + field_name.upper() + "}}"
            placeholder_map[placeholder] = str(value) if value is not None else ""

        html = template_html
        for placeholder, value in placeholder_map.items():
            html = html.replace(placeholder, value)

        # Inyectar CSS inline en <style> si no hay link externo funcional
        if css_content and '<link rel="stylesheet"' in html:
            # Reemplazar el link por un <style> inline
            html = re.sub(
                r'<link[^>]*href="hook_styles\.css"[^>]*>',
                f"<style>\n{css_content}\n</style>",
                html,
            )
        elif css_content:
            # Insertar antes de </head>
            html = html.replace(
                "</head>",
                f"<style>\n{css_content}\n</style>\n</head>",
            )

        return html

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    def generate(self, force: bool = False, dry_run: bool = False) -> Path:
        """
        Orquesta la generación completa del PDF.

        Args:
            force: Si True, sobrescribe PDF existente.
            dry_run: Si True, imprime los datos y retorna sin generar PDF.

        Returns:
            Path al archivo PDF generado.

        Raises:
            FileNotFoundError: Si faltan archivos fuente.
            RuntimeError: Si hay errores fatales de validación.
        """
        # 1. Extraer datos
        data = self.extract_data()

        # 2. Validar
        warnings = self.validate_data(data)

        # Separar errores fatales de warnings
        fatal_errors = [w for w in warnings if w.startswith("[ERROR]")]
        soft_warnings = [w for w in warnings if not w.startswith("[ERROR]")]

        if soft_warnings:
            print("[WARN] Warnings de validacion:")
            for w in soft_warnings:
                print(f"  {w}")

        if fatal_errors:
            print("[ERROR] Errores fatales de validacion:")
            for e in fatal_errors:
                print(f"  {e}")
            raise RuntimeError(
                f"Se encontraron {len(fatal_errors)} errores fatales. "
                "Corrija los datos fuente antes de generar el PDF."
            )

        # 3. Renderizar HTML
        html = self.render_html(data)

        # 4. Dry run
        if dry_run:
            print("\n[DRY RUN] Datos extraidos:")
            for field_name, value in asdict(data).items():
                print(f"  {field_name}: {value}")
            print(f"\n[DRY RUN] HTML generado ({len(html)} caracteres)")
            # Retornar un path dummy
            return self.output_dir / "deliveries" / f"{_slugify(data.hotel_nombre)}_gancho.pdf"

        # 5. Crear output
        slug = _slugify(data.hotel_nombre)
        deliveries_dir = self.output_dir / "deliveries"
        deliveries_dir.mkdir(parents=True, exist_ok=True)
        output_path = deliveries_dir / f"{slug}_gancho.pdf"

        # 6. Verificar no-sobrescritura
        if output_path.exists() and not force:
            raise FileExistsError(
                f"El archivo '{output_path}' ya existe. "
                "Use force=True para sobrescribir."
            )

        # 7. Generar PDF con weasyprint
        HTML(string=html).write_pdf(output_path)

        print(f"[OK] PDF generado: {output_path}")
        return output_path