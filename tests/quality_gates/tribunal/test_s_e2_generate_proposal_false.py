"""FASE-T2-C (S-E2): presencia canónica sin NameError.

Verifica que los bloques presence_lookup en v4_proposal_generator.py
consumen correctamente el dict canónico de normalize_site_presence
(el antiguo hasattr(…, 'results') era siempre False contra un dict).

AC15: generate_proposal=False no lanza NameError — la asignación de
site_presence_report está hoisted fuera del bloque condicional.

FASE-P3-B amplía el mismo contrato al segundo hoist del flujo (AC-F5): las banderas
reales de analítica que consume el bloque FASE-K también deben asignarse fuera del
guard `if generate_proposal:` — ver TestAnalyticsFlagsReachableWithoutProposal.

Remediación D-T2C-A1 (auditoría 2026-09-11): TestPresenceLookupLiveConsumers
ejecuta los tres métodos reales de v4_proposal_generator.py que construyen
presence_lookup (_generate_dynamic_services_table, _generate_technical_assets_table,
_generate_asset_quality_table) con el dict canónico, con None y con variantes
de estado — fija el delta post-T2-C contra código de producción, no contra una
re-implementación de la lógica.
"""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.asset_generation.site_presence_adapter import normalize_site_presence
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


CANONICAL_SNAPSHOT = normalize_site_presence(None)
assert isinstance(CANONICAL_SNAPSHOT, dict)


class TestPresenceLookupCanonicalDict:
    """presence_lookup debe funcionar con el dict canónico."""

    def test_none_normalize_produces_empty_results(self):
        snapshot = normalize_site_presence(None)
        assert snapshot == {"results": {}}

    def test_canonical_dict_has_results_key(self):
        snapshot = normalize_site_presence({
            "results": {
                "whatsapp_button": {"status": "exists", "confidence": 1.0},
                "hotel_schema": {"status": "not_exists", "confidence": 0.9},
            }
        })
        assert "results" in snapshot
        assert "whatsapp_button" in snapshot["results"]
        assert snapshot["whatsapp_button"]["status"] == "exists"

    def test_presence_lookup_extracts_status_from_canonical(self):
        """Simula la lógica del presence_lookup corregido."""
        from modules.asset_generation.site_presence_checker import is_present_in_production

        site_presence_report = normalize_site_presence({
            "results": {
                "whatsapp_button": {"status": "exists", "confidence": 1.0},
                "faq_page": {"status": "exists_with_issues", "confidence": 0.8},
                "hotel_schema": {"status": "not_exists", "confidence": 0.9},
            }
        })

        presence_lookup = {}
        if site_presence_report:
            _results = site_presence_report.get("results", {}) if isinstance(site_presence_report, dict) else {}
            for asset_type, result in _results.items():
                status = result.get("status", "") if isinstance(result, dict) else getattr(result, "status", "")
                presence_lookup[asset_type] = {
                    "present_in_production": is_present_in_production(status),
                    "presence_verified": True,
                }

        assert presence_lookup["whatsapp_button"]["present_in_production"] is True
        assert presence_lookup["faq_page"]["present_in_production"] is True
        assert presence_lookup["hotel_schema"]["present_in_production"] is False

    def test_presence_lookup_empty_when_none_report(self):
        """site_presence_report=None → presence_lookup vacío (sin error)."""
        site_presence_report = None

        presence_lookup = {}
        if site_presence_report:
            pass  # pragma: no cover

        assert presence_lookup == {}

    def test_presence_lookup_empty_when_empty_results(self):
        """site_presence_report con results vacíos → presence_lookup vacío."""
        site_presence_report = normalize_site_presence(None)

        presence_lookup = {}
        if site_presence_report:
            _results = site_presence_report.get("results", {}) if isinstance(site_presence_report, dict) else {}
            for asset_type, result in _results.items():
                status = result.get("status", "") if isinstance(result, dict) else getattr(result, "status", "")
                from modules.asset_generation.site_presence_checker import is_present_in_production
                presence_lookup[asset_type] = {
                    "present_in_production": is_present_in_production(status),
                    "presence_verified": True,
                }

        assert presence_lookup == {}


class TestSitePresenceReportAlwaysDefined:
    """AC15: site_presence_report always defined regardless of generate_proposal."""

    def test_site_presence_snapshot_initialized_before_proposal_gate(self):
        """Verifica que site_presence_snapshot se inicializa en main.py
        antes del if generate_proposal (hoist S-E2).

        Lee el fuente de main.py y verifica que la asignación
        'site_presence_report = site_presence_snapshot' aparece antes
        del bloque 'if generate_proposal'.
        """
        from pathlib import Path

        main_py = Path(__file__).parents[3] / "main.py"
        source = main_py.read_text(encoding="utf-8")

        hoist_pos = source.find("site_presence_report = site_presence_snapshot")
        assert hoist_pos != -1, "Hoist assignment not found in main.py"

        if_proposal_pos = source.find("if generate_proposal:")
        assert if_proposal_pos != -1, "if generate_proposal: not found in main.py"

        assert hoist_pos < if_proposal_pos, (
            "site_presence_report = site_presence_snapshot debe estar "
            "ANTES del if generate_proposal: (S-E2 hoist)"
        )

    def test_no_duplicate_assignment_inside_proposal_block(self):
        """La asignación dentro del if generate_proposal: fue retirada."""
        from pathlib import Path

        main_py = Path(__file__).parents[3] / "main.py"
        lines = main_py.read_text(encoding="utf-8").splitlines()

        in_proposal_block = False
        inside_assignments = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "if generate_proposal:":
                in_proposal_block = True
            if in_proposal_block and "site_presence_report = site_presence_snapshot" in line:
                inside_assignments.append(i + 1)
            if in_proposal_block and stripped and not stripped.startswith("#") and not line.startswith("        ") and not line.startswith("\t"):
                in_proposal_block = False

        assert not inside_assignments, (
            f"Asignación duplicada encontrada dentro del bloque if generate_proposal "
            f"en línea(s) {inside_assignments} — debe estar hoisted fuera del bloque"
        )


class TestAnalyticsFlagsReachableWithoutProposal:
    """AC-F5 (FASE-P3-B): las banderas de analitica heredan el contrato de AC15.

    Ampliacion del patron S-E2 sobre el segundo hoist del mismo flujo. El consumidor
    (bloque FASE-K) vive ANTES del guard `if generate_proposal:`, asi que si el hoist
    de `ga4_available`/`gsc_available` cayera dentro de ese guard, el regimen
    generate_proposal=False producira un NameError que el `except Exception` de FASE-K
    traga imprimiendo un warning: el tier de las corridas reales bajaria en silencio y
    nada lo diria (L-T2C.2). Por eso se comprueba por AST, no por busqueda de texto.
    """

    MAIN_SOURCE = (Path(__file__).parents[3] / "main.py").read_text(encoding="utf-8")

    @classmethod
    def _tree(cls):
        return ast.parse(cls.MAIN_SOURCE)

    @classmethod
    def _func(cls):
        for node in ast.walk(cls._tree()):
            if isinstance(node, ast.FunctionDef) and node.name == "run_v4_complete_mode":
                return node
        raise AssertionError("main.py ya no define run_v4_complete_mode()")

    @classmethod
    def _parents(cls):
        parents = {}
        for node in ast.walk(cls._tree()):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        return parents

    @staticmethod
    def _assignments(func, target):
        return [
            node
            for node in ast.walk(func)
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == target for t in node.targets)
        ]

    @staticmethod
    def _proposal_guards(func):
        """Nodos `if` cuya condicion es exactamente el nombre generate_proposal."""
        return [
            node
            for node in ast.walk(func)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "generate_proposal"
        ]

    @classmethod
    def _under_guard(cls, node, parents, guards):
        cur = node
        parent = parents.get(cur)
        while parent is not None:
            if parent in guards and any(cur is b for b in parent.body):
                return True
            cur = parent
            parent = parents.get(cur)
        return False

    @pytest.mark.parametrize("target", ["ga4_available", "gsc_available"])
    def test_banderas_calculadas_antes_de_decidir_generate_proposal(self, target):
        func = self._func()
        assigns = self._assignments(func, target)
        assert len(assigns) == 1, f"{target} debe asignarse una sola vez, hay {len(assigns)}"

        gate = self._assignments(func, "generate_proposal")
        assert gate, "main.py ya no asigna generate_proposal"
        assert assigns[0].lineno < min(a.lineno for a in gate), (
            f"{target} se calcula despues de decidir generate_proposal: con el flag "
            f"falso el bloque FASE-K lo consumiria sin asignar"
        )

    @pytest.mark.parametrize("target", ["ga4_available", "gsc_available"])
    def test_banderas_no_bajo_el_guard_de_propuesta(self, target):
        func = self._func()
        parents = self._parents()
        guards = self._proposal_guards(func)
        assert guards, "no existe el bloque if generate_proposal:"
        assign = self._assignments(func, target)[0]
        assert not self._under_guard(assign, parents, guards), (
            f"{target} quedo dentro de `if generate_proposal:` — regimen False produce "
            f"NameError y el except ancho de FASE-K lo enmascara"
        )

    def test_bloque_fase_k_tampoco_bajo_el_guard(self):
        """Si ambos cayeran dentro del guard el pair anterior pasaria y el tier desapareceria."""
        func = self._func()
        parents = self._parents()
        guards = self._proposal_guards(func)
        call = next(
            n for n in ast.walk(func)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "HotelFinancialData"
        )
        assert not self._under_guard(call, parents, guards), (
            "el bloque FASE-K se volvio condicional a la propuesta: sin propuesta no "
            "hay evidence_tier y el acta cae al default"
        )


class TestPresenceLookupLiveConsumers:
    """D-T2C-A1: los métodos reales que consumen presence_lookup, con el dict
    canónico (reactivados) y con None/alternativas (sin regresión ni crash)."""

    ASSET_PRESENT = "whatsapp_button"
    ASSET_TECHNICAL = "analytics_setup_guide"

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    @classmethod
    def _service_for(cls, asset_type: str) -> str:
        return next(
            name for name, at in PROPOSAL_SERVICE_TO_ASSET.items()
            if at == asset_type
        )

    @staticmethod
    def _snapshot(asset_type: str, status: str) -> dict:
        return normalize_site_presence({
            "results": {asset_type: {"status": status, "confidence": 1.0}}
        })

    @staticmethod
    def _row_for(table: str, service_name: str) -> str:
        return next(
            line for line in table.splitlines()
            if line.startswith("|") and service_name in line
        )

    # ---- _generate_dynamic_services_table --------------------------------

    def test_services_table_canonical_dict_shows_presente_en_sitio(self):
        table = self.gen._generate_dynamic_services_table(
            site_presence_report=self._snapshot(self.ASSET_PRESENT, "exists")
        )
        row = self._row_for(table, self._service_for(self.ASSET_PRESENT))
        assert "ℹ️ Presente en sitio" in row

    def test_services_table_exists_with_issues_counts_as_presente(self):
        """Criterio canónico FASE-SR-E (H7): exists_with_issues es presente."""
        table = self.gen._generate_dynamic_services_table(
            site_presence_report=self._snapshot(self.ASSET_PRESENT, "exists_with_issues")
        )
        row = self._row_for(table, self._service_for(self.ASSET_PRESENT))
        assert "ℹ️ Presente en sitio" in row

    def test_services_table_not_exists_does_not_claim_presente(self):
        table = self.gen._generate_dynamic_services_table(
            site_presence_report=self._snapshot(self.ASSET_PRESENT, "not_exists")
        )
        assert "Presente en sitio" not in table

    def test_services_table_none_report_preserves_legacy_behavior(self):
        """Con None no hay claim de presencia — el régimen pre-post idéntico."""
        table = self.gen._generate_dynamic_services_table(site_presence_report=None)
        assert "Presente en sitio" not in table

    def test_services_table_empty_results_no_claim_no_crash(self):
        table = self.gen._generate_dynamic_services_table(
            site_presence_report=normalize_site_presence(None)
        )
        assert "Presente en sitio" not in table

    # ---- _generate_technical_assets_table ---------------------------------

    def test_technical_assets_table_canonical_dict_shows_presente(self):
        table = self.gen._generate_technical_assets_table(
            site_presence_report=self._snapshot(self.ASSET_TECHNICAL, "exists")
        )
        assert "ℹ️ Presente en sitio" in table

    def test_technical_assets_table_none_shows_no_presente(self):
        table = self.gen._generate_technical_assets_table(site_presence_report=None)
        assert "Presente en sitio" not in table

    # ---- _generate_asset_quality_table -------------------------------------

    def test_quality_table_canonical_dict_shows_verificado(self):
        table = self.gen._generate_asset_quality_table(
            assets_generated=[],
            site_presence_report=self._snapshot(self.ASSET_PRESENT, "exists"),
        )
        row = self._row_for(table, self._service_for(self.ASSET_PRESENT))
        assert "✅ Día 1 (Verificado)" in row

    def test_quality_table_none_no_verificado(self):
        table = self.gen._generate_asset_quality_table(
            assets_generated=[], site_presence_report=None
        )
        assert "(Verificado)" not in table

    # ---- ramas de compatibilidad y robustez del guard -----------------------

    def test_services_table_dataclass_like_report_still_works(self):
        """Rama hasattr(report, 'results') — compat pre-dict preservada."""
        report = SimpleNamespace(
            results={self.ASSET_PRESENT: SimpleNamespace(status="exists")}
        )
        table = self.gen._generate_dynamic_services_table(site_presence_report=report)
        row = self._row_for(table, self._service_for(self.ASSET_PRESENT))
        assert "ℹ️ Presente en sitio" in row

    def test_services_table_object_without_results_is_tolerated(self):
        """Rama else: objeto truthy sin results → lookup vacío, sin crash."""
        table = self.gen._generate_dynamic_services_table(
            site_presence_report=object()
        )
        assert "Presente en sitio" not in table
