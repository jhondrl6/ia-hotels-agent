"""HonestyReviewer — Bot 4 del tribunal de certificación.

Revisor híbrido que detecta sobre-presentación de datos ESTIMATED como verificados,
verifica que los 3 escenarios (70/20/10) están presentes, y lee los CG-* repartidos
en DOS archivos comerciales (canónico + diagnóstico).

Flujo:
1. LLM extrae promesas verbales de la propuesta con la API checked (cuatro estados);
   el estado del insumo se publica en el report clave ``extraccion``
2. La sobre-presentacion se mide sobre el TEXTO COMPLETO de la propuesta (no depende
   de las citas que el LLM eligio) y el resto se verifica contra tier labels y CG-*
3. Clasifica: OVER_PRESENTATION / TIER_MISMATCH / CG_WARNING_UNDISCLOSED / MISSING_SCENARIO
4. Produce revision_honestidad.json

CRÍTICO 1: El reporte comercial está PARTIDO en dos archivos. Leer solo el canónico
produce falso "todo pasó". El único gate que falló en la corrida real (CG-WHATSAPP-LEAD)
está en el archivo de diagnóstico.

CRÍTICO 2: La propuesta no vive en v4_audit_dir sino en v4_complete/, así que su
resolución se hace con el resolutor compartido del paquete (``artifact_paths``).

CRÍTICO 3: Los dos archivos comparten gate_ids, por lo que el conteo se reporta como
entradas Y como gate_ids distintos; los hallazgos se emiten una vez por gate_id.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from modules.quality_gates.tribunal.artifact_paths import (
    CG_CANONICAL_PATTERN,
    CG_DIAGNOSTIC_PATTERN,
    FINANCIAL_SCENARIOS_PATTERN,
    PROPOSAL_PATTERN,
    load_json,
    pick_most_recent,
    read_text,
    resolve_latest,
)
from modules.quality_gates.tribunal.llm_extractor import (
    PromiseExtractor,
    VerbalPromise,
)
from modules.quality_gates.tribunal.outcome import bloque_extraccion


FINDING_OVER_PRESENTATION = "OVER_PRESENTATION"
FINDING_TIER_MISMATCH = "TIER_MISMATCH"
FINDING_CG_WARNING_UNDISCLOSED = "CG_WARNING_UNDISCLOSED"
FINDING_MISSING_SCENARIO = "MISSING_SCENARIO"

FINDING_MISSING_ARTIFACT = "MISSING_ARTIFACT"

# Artefacto que declara el hallazgo (contrato de claves del acta, AC18).
ARTIFACTO_PROPUESTA = "02_PROPUESTA_COMERCIAL.md"

# Patrones de lenguaje de verificacion (AC10, cura N7). Viven a nivel de modulo porque
# la medicion de la superficie de falso positivo tiene que importar el patron del
# codigo; un regex equivalente re-escrito a mano mide otra cosa.
#
# Frontera curada: la alternante `100%` llevaba `\b` detras del signo, y `\b` despues
# de un no-palabra exige una palabra al lado, así que NINGUN `100%` del corpus matcheaba.
# Ahora `100[ \t]*%` matchea tambien en prosa de garantia.
VERIFICATION_GROUP_LENGUAJE = r"\b(verificad[oa]s?|confirmad[oa]s?|dato real|cifra exacta|validad[oa]s?)\b"
VERIFICATION_GROUP_CUANTIFICADOR = r"(?<!\d)100[ \t]*%|\b(?:total|absoluto|definitiv[ao]s?)\b"
VERIFICATION_PATTERNS = (VERIFICATION_GROUP_LENGUAJE, VERIFICATION_GROUP_CUANTIFICADOR)

# Criterio de la cura (medido sobre las 6 propuestas reales del repo, ver
# evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-B/medicion-falso-positivo.md): el grupo
# de cuantificadores solo se juzga fuera de fila de tabla y fuera de una linea que
# declara un monto. Sobre la propuesta del run de referencia (2026-10-07) sus 5
# coincidencias eran 3 totales financieros o de tabla y 2 absolutos de prosa; el grupo
# de lenguaje de verificacion conserva la tabla sin filtro: una celda que dice
# «Verificado» con tier B es justo lo que este bot existe para señalar.
VERIFICATION_SCAN_GROUPS = (
    ("LENGUAJE_VERIFICACION", VERIFICATION_GROUP_LENGUAJE, False),
    ("CUANTIFICADOR_ABSOLUTO", VERIFICATION_GROUP_CUANTIFICADOR, True),
)

LINEA_DE_TABLA = re.compile(r"^\s*\|.*\|?\s*$")
MONTO_DECLARADO = re.compile(r"\$\s?\d|(?<![\d.,])\d[\d.]{4,}\s?(?:COP|USD)\b")

VERDICT_APROBADO = "APROBADO"
VERDICT_DEVOLVER = "DEVOLVER-PRUEBAS"
VERDICT_BLOQUEAR = "BLOQUEAR"

SCENARIO_KEYS = ["conservative", "realistic", "optimistic"]
SCENARIO_LABELS = {
    "conservative": "conservador (70%)",
    "realistic": "realista (20%)",
    "optimistic": "optimista (10%)",
}

# Frases que nombran el PROBLEMA que cada WARNING detectó. Un gate_id sin entrada aquí
# no se juzga: adivinar divulgación con tokens sueltos produce falsos positivos (una
# propuesta que solo lista el número de contacto "divulgaría" CG-WHATSAPP-LEAD).
DISCLOSURE_PHRASES_BY_GATE = {
    "CG-WHATSAPP-LEAD": [
        "no aparece en la sección inicial",
        "sección inicial del diagnóstico",
        "número equivocado",
        "whatsapp web vs gbp",
        "abrir el diagnóstico",
        "gancho emocional",
    ],
    "CG-OTA-NARRATIVE": [
        "sin narrativa ota",
        "narrativa ota",
        "dependencia de ota",
        "mención a booking",
    ],
    "CG-TECH-JARGON": [
        "jerga técnica",
        "lenguaje técnico",
        "términos técnicos",
    ],
    "CG-TIER-CONSISTENCY": [
        "tier inconsistente",
        "inconsistencia de tier",
        "tier declarado",
    ],
}


from modules.quality_gates.tribunal.review_inputs import KIND_PROPUESTA, ReviewInputs


def _linea_conteniendo(texto: str, posicion: int) -> str:
    """La linea completa donde cae una coincidencia: el contexto que decide el filtro."""
    inicio = texto.rfind("\n", 0, posicion) + 1
    fin = texto.find("\n", posicion)
    return texto[inicio:] if fin == -1 else texto[inicio:fin]


def _es_contexto_financiero(linea: str) -> bool:
    """True si la linea es una fila de tabla o declara un monto (exclusion AC10)."""
    return bool(LINEA_DE_TABLA.match(linea)) or bool(MONTO_DECLARADO.search(linea))


def coincidencias_lenguaje_de_verificacion(texto: str) -> list[dict]:
    """Coincidencias de los dos grupos, con el criterio de la AC10 ya aplicado.

    Devuelve por cada una: grupo, literal y linea. Deduplica por (grupo, literal,
    linea) porque las plantillas repiten secciones en la misma propuesta.
    """
    halladas: list[dict] = []
    vistas: set = set()
    for grupo, patron, excluye_financiero in VERIFICATION_SCAN_GROUPS:
        for coincidencia in re.finditer(patron, texto or "", re.IGNORECASE):
            linea = _linea_conteniendo(texto, coincidencia.start()).strip()
            if excluye_financiero and _es_contexto_financiero(linea):
                continue
            firma = (grupo, coincidencia.group(0).lower(), linea)
            if firma in vistas:
                continue
            vistas.add(firma)
            halladas.append({
                "grupo": grupo,
                "literal": coincidencia.group(0),
                "linea": linea,
            })
    return halladas


class HonestyReviewer:
    """Revisor híbrido de honestidad comercial (Bot 4).

    Constructor: ``HonestyReviewer(v4_audit_dir, deliveries_dir=None)``.
    Lee propuesta + escenarios + CG-* (AMBOS archivos) + MANIFEST, extrae claims
    de sobre-presentación (LLM), verifica contra tier labels y CG-*.
    """

    def __init__(
        self,
        v4_audit_dir: str | Path,
        deliveries_dir: Optional[str | Path] = None,
        review_inputs=None,
    ):
        """Inicializa el revisor.

        Args:
            v4_audit_dir: Directorio v4_audit con artefactos del pipeline.
            deliveries_dir: Directorio deliveries con MANIFEST.json (si es None,
                           busca en v4_audit_dir/../deliveries).
            review_inputs: resolvedor unico de insumos (FASE-E / AC11). Si es None,
                           se construye desde ``v4_audit_dir`` y carga el manifiesto
                           del run cuando existe.
        """
        self.v4_audit_dir = Path(v4_audit_dir)
        self.deliveries_dir = Path(deliveries_dir) if deliveries_dir else self._resolve_deliveries_dir()
        self._inputs = review_inputs if review_inputs is not None else ReviewInputs.for_run(
            self.v4_audit_dir, deliveries_dir=self.deliveries_dir
        )
        self._proposal_read = None
        self._manifest_read = None

    def _resolve_deliveries_dir(self) -> Path:
        """Resuelve deliveries_dir como v4_audit_dir/../deliveries."""
        return self.v4_audit_dir.parent.parent / "deliveries"

    def review(self, extractor: PromiseExtractor) -> dict:
        """Retorna revision_honestidad.json con findings y commercial_gates_read.

        Args:
            extractor: Extractor de claims, obligatorio. El tribunal corre en modo
                offline y quien invoque desde el pipeline debe decidir qué extractor
                usa; no existe un default que instancie el LLM real.
        """
        paths = self._resolve_artifact_paths()
        proposal_text = self._load_proposal_input()
        financial_scenarios = load_json(paths["scenarios"])
        manifest_read = self._inputs.read_manifest_json()
        self._manifest_read = manifest_read
        manifest = manifest_read.content if manifest_read.ok else None

        if proposal_text is None:
            read = self._proposal_read
            return self._error_report(
                "No se pudo leer 02_PROPUESTA_COMERCIAL*.md "
                f"(read_status={getattr(read, 'read_status', 'sin intento')}, "
                f"source={getattr(read, 'source', None) or 'ninguna'}): "
                f"{getattr(read, 'cause', None) or 'sin causa declarada'}"
            )
        if financial_scenarios is None:
            return self._error_report("No se encontró financial_scenarios_*.json")

        cg_canonical = load_json(paths["cg_canonical"])
        cg_diagnostic = load_json(paths["cg_diagnostic"])
        commercial_gates_read = self._merge_commercial_gates(
            cg_canonical, cg_diagnostic, paths["cg_canonical"], paths["cg_diagnostic"]
        )

        findings = []

        evidence_tier = self._extract_evidence_tier(manifest, financial_scenarios)
        precision_tier = self._extract_precision_tier(manifest, financial_scenarios)

        outcome = extractor.extract_checked(proposal_text)
        claims = list(outcome.promises) if outcome.is_ok else []

        # N5/AC9: la sobre-presentacion se mide sobre el texto completo y no depende
        # de la extraccion, así que un no-OK del LLM ya no silencia este hallazgo.
        findings.extend(self._scan_sobre_presentacion(proposal_text, evidence_tier))

        for claim in claims:
            tier_mismatch = self._check_tier_mismatch(claim, evidence_tier, precision_tier)
            if tier_mismatch:
                findings.append(tier_mismatch)

        missing_scenario = self._check_missing_scenarios(financial_scenarios, evidence_tier)
        if missing_scenario:
            findings.extend(missing_scenario)

        cg_warnings = self._extract_cg_warnings(cg_canonical, cg_diagnostic)
        for warning in cg_warnings:
            undisclosed = self._check_cg_warning_undisclosed(warning, proposal_text, evidence_tier)
            if undisclosed:
                findings.append(undisclosed)

        summary = self._compute_summary(findings)
        verdict = self._compute_verdict(findings)
        if not outcome.is_ok and verdict == VERDICT_APROBADO:
            # El revisor no aprueba un insumo que no pudo leer (R2.9, tri-estado).
            verdict = VERDICT_DEVOLVER

        return {
            "reviewer": "honesty_reviewer",
            "clause": "P6.5",
            "findings": findings,
            "commercial_gates_read": commercial_gates_read,
            "summary": summary,
            "verdict_recommendation": verdict,
            "extraccion": bloque_extraccion(outcome),
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
            "review_inputs": self._inputs.reads_report(),
        }

    def write_report(self, extractor: PromiseExtractor, output_path: Optional[Path] = None) -> Path:
        """Escribe revision_honestidad.json y retorna la ruta."""
        report = self.review(extractor)
        if output_path is None:
            output_path = self.v4_audit_dir / "revision_honestidad.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_path

    def _resolve_artifact_paths(self) -> dict:
        """Resuelve cada artefacto una sola vez: el nombre reportado es el archivo leído."""
        return {
            "proposal": resolve_latest(PROPOSAL_PATTERN, self.v4_audit_dir, self.deliveries_dir),
            "scenarios": resolve_latest(FINANCIAL_SCENARIOS_PATTERN, self.v4_audit_dir),
            "manifest": self._resolve_manifest_path(),
            "cg_canonical": resolve_latest(CG_CANONICAL_PATTERN, self.v4_audit_dir),
            "cg_diagnostic": resolve_latest(CG_DIAGNOSTIC_PATTERN, self.v4_audit_dir),
        }

    def _resolve_manifest_path(self) -> Optional[Path]:
        """Resuelve MANIFEST.json en deliveries_dir (más reciente)."""
        if not self.deliveries_dir.exists():
            return None
        return pick_most_recent(self.deliveries_dir.glob("*/MANIFEST.json"))

    def _load_proposal_input(self) -> Optional[str]:
        """Propuesta del run por el resolvedor unico (AC11), con su estado de lectura."""
        read = self._inputs.read_document(KIND_PROPUESTA)
        self._proposal_read = read
        return read.content if read.ok else None

    def _load_proposal(self) -> Optional[str]:
        """Carga 02_PROPUESTA_COMERCIAL*.md (más reciente)."""
        return read_text(resolve_latest(PROPOSAL_PATTERN, self.v4_audit_dir, self.deliveries_dir))

    def _load_financial_scenarios(self) -> Optional[dict]:
        """Carga financial_scenarios_*.json (más reciente)."""
        return load_json(resolve_latest(FINANCIAL_SCENARIOS_PATTERN, self.v4_audit_dir))

    def _load_manifest(self) -> Optional[dict]:
        """Carga MANIFEST.json desde deliveries_dir (más reciente)."""
        return load_json(self._resolve_manifest_path())

    def _load_commercial_gates_canonical(self) -> Optional[dict]:
        """Carga commercial_gates_report.json (archivo canónico con 3 gates)."""
        return load_json(resolve_latest(CG_CANONICAL_PATTERN, self.v4_audit_dir))

    def _load_commercial_gates_diagnostic(self) -> Optional[dict]:
        """Carga commercial_gates_report_diagnostic_*.json (9 gates adicionales)."""
        return load_json(resolve_latest(CG_DIAGNOSTIC_PATTERN, self.v4_audit_dir))

    def _merge_commercial_gates(self, canonical: Optional[dict], diagnostic: Optional[dict],
                                canonical_path: Optional[Path] = None,
                                diagnostic_path: Optional[Path] = None) -> dict:
        """Une los CG-* de AMBOS archivos y reporta metadata de lectura.

        CRÍTICO: Leer solo el canónico produce falso "todo pasó". El único gate
        que falló en la corrida real (CG-WHATSAPP-LEAD) está en el diagnóstico.

        Los dos archivos comparten gate_ids, así que `total_cg_count` cuenta entradas
        y `distinct_cg_count` cuenta gate_ids únicos; `duplicate_gate_ids` explicita la
        diferencia en vez de dejarla ambigua.
        """
        all_gates = []
        warnings_found = []
        seen_gate_ids = set()
        duplicate_gate_ids = []

        for gate in self._iter_source_gates(canonical, diagnostic):
            gate_id = gate.get("gate_id")
            all_gates.append({
                "gate_id": gate_id,
                "severity": gate.get("severity"),
                "passed": gate.get("passed"),
            })
            if gate_id in seen_gate_ids and gate_id not in duplicate_gate_ids:
                duplicate_gate_ids.append(gate_id)
            seen_gate_ids.add(gate_id)
            if gate.get("severity") == "WARNING" and not gate.get("passed", True):
                if gate_id not in warnings_found:
                    warnings_found.append(gate_id)

        return {
            "canonical_file": canonical_path.name if canonical else None,
            "diagnostic_file": diagnostic_path.name if diagnostic else None,
            "total_cg_count": len(all_gates),
            "distinct_cg_count": len(seen_gate_ids),
            "duplicate_gate_ids": duplicate_gate_ids,
            "warnings_found": warnings_found,
            "all_gates": all_gates,
        }

    @staticmethod
    def _iter_source_gates(canonical: Optional[dict], diagnostic: Optional[dict]) -> list[dict]:
        """Gates crudos de ambos archivos, en orden canónico → diagnóstico."""
        return list((canonical or {}).get("results", [])) + list((diagnostic or {}).get("results", []))

    def _extract_evidence_tier(self, manifest: Optional[dict], financial_scenarios: Optional[dict]) -> str:
        """Extrae evidence_tier del MANIFEST o financial_scenarios."""
        if manifest and "quality_metadata" in manifest:
            tier = manifest["quality_metadata"].get("evidence_tier")
            if tier:
                return tier
        if financial_scenarios and "breakdown" in financial_scenarios:
            tier = financial_scenarios["breakdown"].get("evidence_tier")
            if tier:
                return tier
        return "UNKNOWN"

    def _extract_precision_tier(self, manifest: Optional[dict], financial_scenarios: Optional[dict]) -> str:
        """Extrae precision_tier del MANIFEST o financial_scenarios."""
        if manifest and "quality_metadata" in manifest:
            tier = manifest["quality_metadata"].get("precision_tier")
            if tier:
                return tier
        if financial_scenarios:
            tier = financial_scenarios.get("precision_tier")
            if tier:
                return tier
        return "UNKNOWN"

    def _scan_sobre_presentacion(self, proposal_text: str, evidence_tier: str) -> list[dict]:
        """OVER_PRESENTATION por lenguaje de verificacion en el TEXTO COMPLETO (AC9/N5).

        Antes el regex corria solo sobre las citas que el LLM eligio: una promesa
        sobre-presentada que el extractor omitia quedaba sin revisar, y con una
        extraccion no-OK la lista vacia silenciaba el check entero. El texto completo
        no depende del LLM, así que el hallazgo sigue emitiéndose aunque la extraccion
        falle. Con tier A o UNKNOWN no se emite (la precedencia del tier es AC11).
        """
        if evidence_tier in ["A", "UNKNOWN"]:
            return []

        findings = []
        for coincidencia in coincidencias_lenguaje_de_verificacion(proposal_text):
            findings.append({
                "finding_type": FINDING_OVER_PRESENTATION,
                "clause": "P6.5",
                "severity": "CRITICAL",
                "verification_group": coincidencia["grupo"],
                "claim_text": coincidencia["literal"],
                "matched_line": coincidencia["linea"][:240],
                "evidence_tier_declared": evidence_tier,
                "cg_reference": None,
                "source_artifact": ARTIFACTO_PROPUESTA,
                "description": (
                    f"La propuesta usa «{coincidencia['literal']}» ({coincidencia['grupo']}) "
                    f"con evidence_tier={evidence_tier} (no A) en: {coincidencia['linea'][:120]}"
                ),
            })
        return findings

    def _check_tier_mismatch(self, claim: VerbalPromise, evidence_tier: str, precision_tier: str) -> Optional[dict]:
        """Detecta TIER_MISMATCH: claim con tier declarado ≠ tier real.

        Si el claim menciona un tier específico (ej: "tier A") pero el tier real
        es B o C, es un mismatch.
        """
        claim_text = claim.text.lower()

        tier_mentions = {
            "tier a": "A",
            "evidence a": "A",
            "tier b": "B",
            "evidence b": "B",
            "tier c": "C",
            "evidence c": "C",
        }

        for mention, mentioned_tier in tier_mentions.items():
            if mention in claim_text and mentioned_tier != evidence_tier:
                return {
                    "finding_type": FINDING_TIER_MISMATCH,
                    "clause": "P6.5",
                    "severity": "WARNING",
                    "claim_text": claim.text,
                    "evidence_tier_declared": evidence_tier,
                    "cg_reference": None,
                    "source_artifact": ARTIFACTO_PROPUESTA,
                    "description": f"Claim menciona tier {mentioned_tier} pero evidence_tier real es {evidence_tier}",
                }

        return None

    def _check_missing_scenarios(self, financial_scenarios: dict, evidence_tier: str) -> list[dict]:
        """Detecta MISSING_SCENARIO: falta alguno de los 3 escenarios (70/20/10)."""
        findings = []
        scenarios = financial_scenarios.get("scenarios", {})

        for key in SCENARIO_KEYS:
            if key not in scenarios or scenarios[key] is None:
                findings.append({
                    "finding_type": FINDING_MISSING_SCENARIO,
                    "clause": "P6.5",
                    "severity": "CRITICAL",
                    "claim_text": None,
                    "evidence_tier_declared": evidence_tier,
                    "cg_reference": None,
                    "source_artifact": "financial_scenarios_*.json",
                    "description": f"Falta escenario {SCENARIO_LABELS.get(key, key)}",
                })

        return findings

    def _extract_cg_warnings(self, canonical: Optional[dict], diagnostic: Optional[dict]) -> list[dict]:
        """Extrae CG-* WARNING que no pasaron, una entrada por gate_id.

        Sin deduplicar, un gate presente en ambos archivos produciría dos findings
        idénticos.
        """
        warnings = []
        seen_gate_ids = set()
        for gate in self._iter_source_gates(canonical, diagnostic):
            gate_id = gate.get("gate_id")
            if gate.get("severity") != "WARNING" or gate.get("passed", True):
                continue
            if gate_id in seen_gate_ids:
                continue
            seen_gate_ids.add(gate_id)
            warnings.append({
                "gate_id": gate_id,
                "name": gate.get("name"),
                "message": gate.get("message"),
                "suggestion": gate.get("suggestion"),
            })
        return warnings

    def _check_cg_warning_undisclosed(self, warning: dict, proposal_text: str,
                                       evidence_tier: str) -> Optional[dict]:
        """Detecta CG_WARNING_UNDISCLOSED: la propuesta no divulga el problema.

        Se busca una frase que nombre el problema que el WARNING detectó
        (``DISCLOSURE_PHRASES_BY_GATE``), no palabras sueltas: una propuesta que solo
        lista el número de contacto menciona "WhatsApp" sin divulgar nada. Un gate_id
        sin entrada en la tabla no se juzga, para no afirmar divulgación sin criterio.
        """
        gate_id = warning.get("gate_id", "")
        phrases = DISCLOSURE_PHRASES_BY_GATE.get(gate_id)
        if not phrases:
            return None

        proposal_lower = proposal_text.lower()
        disclosed = any(phrase in proposal_lower for phrase in phrases)
        if disclosed:
            return None

        return {
            "finding_type": FINDING_CG_WARNING_UNDISCLOSED,
            "clause": "P6.5",
            "severity": "WARNING",
            "claim_text": None,
            "evidence_tier_declared": evidence_tier,
            "cg_reference": gate_id,
            "source_artifact": ARTIFACTO_PROPUESTA,
            "description": f"CG-* WARNING {gate_id} no divulgado en propuesta: {warning.get('message', '')[:100]}",
        }

    def _compute_summary(self, findings: list) -> dict:
        """Calcula resumen de hallazgos."""
        over_presentations = sum(1 for f in findings if f.get("finding_type") == FINDING_OVER_PRESENTATION)
        tier_mismatches = sum(1 for f in findings if f.get("finding_type") == FINDING_TIER_MISMATCH)
        undisclosed_warnings = sum(1 for f in findings if f.get("finding_type") == FINDING_CG_WARNING_UNDISCLOSED)
        missing_scenarios = sum(1 for f in findings if f.get("finding_type") == FINDING_MISSING_SCENARIO)
        return {
            "over_presentations": over_presentations,
            "tier_mismatches": tier_mismatches,
            "undisclosed_warnings": undisclosed_warnings,
            "missing_scenarios": missing_scenarios,
            "total_findings": len(findings),
        }

    def _compute_verdict(self, findings: list) -> str:
        """Veredicto recomendado: BLOQUEAR por CRITICAL, DEVOLVER-PRUEBAS por
        WARNING sustantivo, APROBADO en otro caso.
        """
        if any(f.get("severity") == "CRITICAL" for f in findings):
            return VERDICT_BLOQUEAR
        if any(f.get("severity") == "WARNING" for f in findings):
            return VERDICT_DEVOLVER
        return VERDICT_APROBADO

    def _error_report(self, message: str) -> dict:
        """Retorna reporte de error cuando falta un artefacto imprescindible.

        ``MISSING_ARTIFACT`` es la extensión de schema documentada: el error necesita
        expresarse como hallazgo y ese tipo no estaba en el enumerado del plan.
        """
        return {
            "reviewer": "honesty_reviewer",
            "clause": "P6.5",
            "findings": [{
                "finding_type": FINDING_MISSING_ARTIFACT,
                "clause": "P6.5",
                "severity": "CRITICAL",
                "claim_text": None,
                "evidence_tier_declared": "UNKNOWN",
                "cg_reference": None,
                "source_artifact": "N/A",
                "description": message,
            }],
            "commercial_gates_read": {
                "canonical_file": None,
                "diagnostic_file": None,
                "total_cg_count": 0,
                "distinct_cg_count": 0,
                "duplicate_gate_ids": [],
                "warnings_found": [],
                "all_gates": [],
            },
            "summary": {
                "over_presentations": 0,
                "tier_mismatches": 0,
                "undisclosed_warnings": 0,
                "missing_scenarios": 0,
                "total_findings": 1,
            },
            "verdict_recommendation": VERDICT_BLOQUEAR,
            "timestamp": datetime.now().isoformat(),
            "artifacts_read": self._list_artifacts_read(),
            "review_inputs": self._inputs.reads_report(),
        }

    def _list_artifacts_read(self) -> list:
        """Lista artefactos que este revisor lee."""
        return [
            "02_PROPUESTA_COMERCIAL*.md",
            "financial_scenarios_*.json",
            "commercial_gates_report.json",
            "commercial_gates_report_diagnostic_*.json",
            "MANIFEST.json (deliveries_dir)",
        ]
