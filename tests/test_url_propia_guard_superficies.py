"""FASE-B (VALIDADOR-URL-PROPIA) — Contratos de las superficies secundarias.

TDD: los contratos de cada superficie se escribieron rojos ANTES del fix
(lección SR-H2 "TDD también para extensiones"). Este archivo cubre:

  D-VUP-B1  El bypass --force del choke point (ensure_url) debe sobrevivir a la
            defensa en capa de datos. Sin esto, `v4complete --url <ota> --force`
            (sonda P9 del plan) quedaría abortado por WebScraper/auditor, que
            llaman al guard sin conocer la decisión del operador.
  AC7       hook-pdf rechaza la url del reporte cuando es de plataforma.
  T2        WebScraper.extract_hotel_data y V4ComprehensiveAuditor.audit fallan
            ANTES de cualquier petición HTTP/API.

El registro de bypass es por proceso y SOLO lo consulta el origen
"capa_datos": los orígenes --url y estado_persistente conservan exactamente la
semántica congelada en FASE-A (incluido TestCicloForceReinyeccion).
"""

import json
from pathlib import Path

import pytest

from modules.data_validation import own_site_guard
from modules.data_validation.own_site_guard import (
    FORCE_EVENTS_PATH,
    ORIGEN_CAPA_DATOS,
    ORIGEN_CLI,
    ORIGEN_ESTADO_PERSISTENTE,
    UrlNoPropiaError,
    assert_own_site,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

URL_BOOKING = "https://www.booking.com/hotel/co/finca-don-julio.es.html"
URL_BOOKING_OTRA_PAGINA = "https://www.booking.com/hotel/co/otra.hotel.html"
URL_INSTAGRAM = "https://www.instagram.com/fincahoteldonjulio"
URL_PROPIA = "https://www.hotelsalentoreal.com/"


@pytest.fixture(autouse=True)
def registro_forzadas_aislado():
    """El registro de netlocs forzados es global al proceso: los tests lo
    limpian y restauran para que el orden de recolección no cambie resultados."""
    previo = set(own_site_guard.FORZADAS_PROCESO)
    own_site_guard.FORZADAS_PROCESO.clear()
    yield
    own_site_guard.FORZADAS_PROCESO.clear()
    own_site_guard.FORZADAS_PROCESO.update(previo)


@pytest.fixture
def eventos_force():
    """Snapshot/restore del archivo append-only de eventos --force (mismo
    contrato que el fixture de FASE-A). Se vacía antes del test: los eventos
    reales de producción (ej. sondas --force) no deben contaminar conteos."""
    path = Path(FORCE_EVENTS_PATH)
    previo = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text("", encoding="utf-8")
    yield path
    if previo is None:
        if path.exists():
            path.unlink()
    else:
        path.write_text(previo, encoding="utf-8")


def _lineas_eventos(path: Path):
    if not path.exists():
        return []
    return [
        json.loads(linea)
        for linea in path.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


# ---------------------------------------------------------------------------
# D-VUP-B1 — capa de datos sin bypass previo / con bypass --force
# ---------------------------------------------------------------------------

class TestD_VUP_B1BypassForceEnCapaDatos:

    def test_capa_datos_sin_force_en_proceso_rechaza(self):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_BOOKING, origen=ORIGEN_CAPA_DATOS)
        assert excinfo.value.categoria == "ota"
        assert "persistente" not in str(excinfo.value)

    def test_force_en_choke_point_autoriza_el_mismo_netloc(self, eventos_force):
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        clasif = assert_own_site(URL_BOOKING_OTRA_PAGINA, origen=ORIGEN_CAPA_DATOS)
        assert clasif.bloqueada is True
        assert clasif.categoria == "ota"

    def test_bypass_no_duplica_el_evento_force(self, eventos_force):
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        assert_own_site(URL_BOOKING_OTRA_PAGINA, origen=ORIGEN_CAPA_DATOS)
        eventos = [e for e in _lineas_eventos(eventos_force) if "booking" in e["url"]]
        assert len(eventos) == 1

    def test_bypass_no_se_filtra_a_otros_origenes(self, eventos_force):
        """--force autoriza la capa de datos, no reabre el choke point: una
        reinyección posterior desde estado persistente sigue rechazándose."""
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        for origen in (ORIGEN_CLI, ORIGEN_ESTADO_PERSISTENTE):
            with pytest.raises(UrlNoPropiaError):
                assert_own_site(URL_BOOKING, origen=origen)

    def test_bypass_es_por_netloc_no_un_cheque_en_blanco(self, eventos_force):
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_INSTAGRAM, origen=ORIGEN_CAPA_DATOS)
        assert excinfo.value.categoria == "red_social"

    def test_sitio_propio_no_necesita_bypass(self, eventos_force):
        assert assert_own_site(URL_PROPIA, origen=ORIGEN_CAPA_DATOS).bloqueada is False


# ---------------------------------------------------------------------------
# Helpers de las superficies AC7 / T2
# ---------------------------------------------------------------------------

TEMPLATE_REAL = REPO_ROOT / "templates" / "hook_template.md"
STYLE_REAL = REPO_ROOT / "templates" / "hook_styles.css"


def _escribir_fuentes_hook_pdf(base: Path, url: str) -> None:
    """Crea los 3 archivos fuente que exige HookPDFGenerator.extract_data().

    Mismo patron que tests/commercial_documents/test_hook_pdf_generator.py:42-136
    (fixtures de Luxorhotel) con la url del reporte parametrizable: AC7 se
    congela sobre el campo "url" de v4_complete_report.json, no sobre el nombre.
    """
    diag = base / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260707_121029.md"
    diag.write_text(
        """\
---
financial_evidence_tier: B
financial_value_range:
  - 2619187
  - 374170
gbp_resenas: "277"
gbp_rating: "4.1"
financial_ota_commission_real: "$7.741.440 COP"
---

## Luxorhotel - Cl. 24 #8-35, Pereira, Risaralda, Colombia

277 reviews, 4.1/5 rating en Google Business Profile.

## Score de Visibilidad Digital

| Pilar | Hotel | Regional |
|-------|-------|----------|
| SEO | 25/100 | 45/100 |
| GEO | 30/100 | 50/100 |
| AEO | 20/100 | 40/100 |
| IAO | 15/100 | 35/100 |
""",
        encoding="utf-8",
    )

    prop = base / "02_PROPUESTA_COMERCIAL_20260707_121029.md"
    prop.write_text(
        """\
---
precio_mensual: "400.000"
setup_fee: "2.500.000"
---

ROICR: 3.5x

Plan mensual: $400.000 COP/mes
Setup: $2.500.000 COP
""",
        encoding="utf-8",
    )

    report = base / "v4_complete_report.json"
    report.write_text(
        json.dumps(
            {
                "hotel_name": "Luxorhotel",
                "url": url,
                "region": "Pereira, Risaralda, Colombia",
                "financial_data": {"expected_monthly": 3741696},
                "opportunity_scores": [
                    {
                        "rank": 1,
                        "brecha_name": "SEO Local",
                        "estimated_monthly_cop": 1500000,
                        "justification": "Falta Google Business Profile optimizado",
                    },
                    {
                        "rank": 2,
                        "brecha_name": "Contenido Web",
                        "estimated_monthly_cop": 1200000,
                        "justification": "Sitio web sin estructura semantica",
                    },
                    {
                        "rank": 3,
                        "brecha_name": "Presencia en Maps",
                        "estimated_monthly_cop": 800000,
                        "justification": "Ficha de Google incompleta",
                    },
                ],
                "phases": {
                    "phase_4_publication_gates": {
                        "gate_results": [
                            {
                                "gate_name": "tier_c_onboarding_required",
                                "details": {"tier": "B"},
                            }
                        ]
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _gen_hook_pdf(base: Path):
    """HookPDFGenerator apuntando a los templates reales del repo."""
    from modules.commercial_documents.hook_pdf_generator import HookPDFGenerator

    return HookPDFGenerator(
        output_dir=base,
        template_path=TEMPLATE_REAL,
        style_path=STYLE_REAL if STYLE_REAL.exists() else None,
    )


class _CentinelaError(Exception):
    """Señal de "el flujo avanzo mas alla del guard" sin tocar la red."""


def _revienta(*args, **kwargs):
    raise _CentinelaError("el flujo avanzo del guard")


class _Espia:
    """Espia callable: registra cada llamada y devuelve None.

    Sustituye metodos del auditor (o la clase HttpClient del modulo) para
    probar que el guard corta ANTES de cualquier red/API.
    """

    def __init__(self):
        self.llamadas = []

    def __call__(self, *args, **kwargs):
        self.llamadas.append((args, kwargs))
        return None


class _CentinelaHttp:
    """Cliente HTTP espia: registra cada get() y nunca hace red real.

    Responde (None, {...}) porque WebScraper.extract_hotel_data ya tolera un
    fallo de red y lo devuelve como dict de fallback.
    """

    def __init__(self, respuesta=None):
        self.llamadas = []
        self._respuesta = respuesta if respuesta is not None else (None, {"error": "sin red"})

    def get(self, *args, **kwargs):
        self.llamadas.append((args, kwargs))
        return self._respuesta


# ---------------------------------------------------------------------------
# AC7 — hook-pdf: la url del reporte Tambien pasa el guard
# ---------------------------------------------------------------------------

class TestAC7HookPdfRechazaUrlNoPropia:

    def test_extract_data_rechaza_url_ota_del_reporte(self, tmp_path):
        """El url del reporte NO es confianza heredada: si es una OTA, AC7."""
        _escribir_fuentes_hook_pdf(tmp_path, URL_BOOKING)
        gen = _gen_hook_pdf(tmp_path)

        with pytest.raises(UrlNoPropiaError) as excinfo:
            gen.extract_data()

        mensaje = str(excinfo.value)
        assert "booking" in mensaje.lower()
        assert "sitio web propio" in mensaje
        assert excinfo.value.categoria == "ota"
        # Y no se escribio ningun PDF ni directorio de entrega.
        assert not list(tmp_path.rglob("*.pdf"))

    def test_extract_data_no_toca_el_disco_al_rechazar(self, tmp_path):
        """Rechazo antes de cualquier parse/render: solo los 3 archivos fuente."""
        _escribir_fuentes_hook_pdf(tmp_path, URL_BOOKING)
        gen = _gen_hook_pdf(tmp_path)

        con_ese_nombre = sorted(p.name for p in tmp_path.iterdir())
        with pytest.raises(UrlNoPropiaError):
            gen.extract_data()

        assert sorted(p.name for p in tmp_path.iterdir()) == con_ese_nombre

    def test_extract_data_con_force_no_lanza_y_registra_evento(self, tmp_path, eventos_force):
        """--force del operador significa tambien "no bloquear este reporte"."""
        from modules.commercial_documents.data_structures import HookPDFData

        _escribir_fuentes_hook_pdf(tmp_path, URL_BOOKING)
        gen = _gen_hook_pdf(tmp_path)

        data = gen.extract_data(force=True)

        assert isinstance(data, HookPDFData)
        assert data.hotel_url == URL_BOOKING
        eventos = [
            e for e in _lineas_eventos(eventos_force)
            if e["url"] == URL_BOOKING and e["comando"] == "hook-pdf"
        ]
        assert len(eventos) == 1

    def test_extract_data_url_propia_no_regride(self, tmp_path):
        """Sitio propio: extract_data() retorna HookPDFData con la url intacta."""
        from modules.commercial_documents.data_structures import HookPDFData

        _escribir_fuentes_hook_pdf(tmp_path, URL_PROPIA)
        gen = _gen_hook_pdf(tmp_path)

        data = gen.extract_data()

        assert isinstance(data, HookPDFData)
        assert data.hotel_url == URL_PROPIA
        assert data.hotel_nombre == "Luxorhotel"


# ---------------------------------------------------------------------------
# T2 — capa de datos: WebScraper / V4ComprehensiveAuditor antes de la red
# ---------------------------------------------------------------------------

class TestT2WebScraperCapaDatos:

    def test_extract_hotel_data_rechaza_antes_de_cualquier_http(self):
        """El guard va ANTES del try: el except propio no puede tragarselo."""
        from modules.scrapers.web_scraper import WebScraper

        scraper = WebScraper()
        centinela = _CentinelaHttp()
        scraper.http_client = centinela

        with pytest.raises(UrlNoPropiaError) as excinfo:
            scraper.extract_hotel_data(URL_BOOKING)

        assert excinfo.value.categoria == "ota"
        assert centinela.llamadas == []

    def test_extract_hotel_data_url_propia_si_usa_http(self):
        from modules.scrapers.web_scraper import WebScraper

        scraper = WebScraper()
        centinela = _CentinelaHttp()
        scraper.http_client = centinela

        data = scraper.extract_hotel_data(URL_PROPIA)

        assert len(centinela.llamadas) == 1
        assert isinstance(data, dict)
        assert data["url"] == URL_PROPIA

    def test_bypass_del_choke_point_sobrevive_en_el_scraper(self, eventos_force):
        """D-VUP-B1 end-to-end: `v4complete --url <ota> --force` no puede morir
        en la capa de datos, que no recibe args.force."""
        from modules.scrapers.web_scraper import WebScraper

        assert_own_site(URL_BOOKING, force=True, comando="v4complete")

        scraper = WebScraper()
        centinela = _CentinelaHttp()
        scraper.http_client = centinela

        data = scraper.extract_hotel_data(URL_BOOKING)

        assert isinstance(data, dict)
        assert len(centinela.llamadas) == 1


class TestT2AuditorCapaDatos:

    def _auditor_con_espias(self, monkeypatch):
        from modules.auditors import v4_comprehensive as v4c

        auditor = v4c.V4ComprehensiveAuditor()
        espias = {
            "schemas": _Espia(),
            "gbp": _Espia(),
            "http": _Espia(),
        }
        monkeypatch.setattr(auditor, "_audit_schemas", espias["schemas"])
        monkeypatch.setattr(auditor, "_audit_gbp", espias["gbp"])
        monkeypatch.setattr(v4c, "HttpClient", espias["http"])
        return auditor, espias

    def test_audit_rechaza_antes_de_red_y_places(self, monkeypatch):
        auditor, espias = self._auditor_con_espias(monkeypatch)

        with pytest.raises(UrlNoPropiaError) as excinfo:
            auditor.audit(URL_BOOKING)

        assert excinfo.value.categoria == "ota"
        assert espias["schemas"].llamadas == []
        assert espias["gbp"].llamadas == []
        assert espias["http"].llamadas == []

    def test_audit_url_propia_si_avanza_del_guard(self, monkeypatch):
        """Url propia: el guard es inocuo y el flujo continua (se comprueba con
        un centinela que interrumpe justo en el primer paso de red)."""
        from modules.auditors import v4_comprehensive as v4c

        auditor = v4c.V4ComprehensiveAuditor()
        http = _Espia()
        monkeypatch.setattr(auditor, "_audit_schemas", _revienta)
        monkeypatch.setattr(v4c, "HttpClient", http)

        with pytest.raises(_CentinelaError):
            auditor.audit(URL_PROPIA)

    def test_bypass_del_choke_point_sobrevive_en_el_auditor(self, monkeypatch, eventos_force):
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        auditor, espias = self._auditor_con_espias(monkeypatch)
        monkeypatch.setattr(auditor, "_audit_schemas", _revienta)

        with pytest.raises(_CentinelaError):
            auditor.audit(URL_BOOKING)

        assert espias["http"].llamadas == []


# ---------------------------------------------------------------------------
# T3 (parent) — el exit code de hook-pdf es el mismo del choke point (FASE-A)
# ---------------------------------------------------------------------------

def _args_hook_pdf(output_dir, force=False):
    import argparse
    return argparse.Namespace(
        command="hook-pdf",
        output_dir=str(output_dir),
        template=None,
        style=None,
        dry_run=True,
        force=force,
        debug=False,
    )


class TestAC7CliSaleConCodigo2:
    """run_hook_pdf_mode captura UrlNoPropiaError ANTES del except Exception
    genérico: sin esto el rechazo saldría con exit 1 y divergiría de ensure_url."""

    def test_reporte_con_url_ota_sale_con_codigo_2(self, tmp_path, capsys):
        from main import run_hook_pdf_mode
        from modules.data_validation.own_site_guard import EXIT_CODE_URL_NO_PROPIA

        _escribir_fuentes_hook_pdf(tmp_path, URL_BOOKING)
        with pytest.raises(SystemExit) as excinfo:
            run_hook_pdf_mode(_args_hook_pdf(tmp_path))

        assert excinfo.value.code == EXIT_CODE_URL_NO_PROPIA == 2
        stderr = capsys.readouterr().err
        assert "booking" in stderr.lower()
        assert "sitio web propio" in stderr
        assert not list(tmp_path.rglob("*.pdf"))

    def test_rechazo_no_cae_en_el_error_generico(self, tmp_path, capsys):
        """El mensaje del guard llega crudo (sin prefijo [ERROR] duplicado de
        otros handlers) y con la guía específica de hook-pdf."""
        from main import run_hook_pdf_mode

        _escribir_fuentes_hook_pdf(tmp_path, URL_INSTAGRAM)
        with pytest.raises(SystemExit) as excinfo:
            run_hook_pdf_mode(_args_hook_pdf(tmp_path))

        assert excinfo.value.code == 2
        stderr = capsys.readouterr().err
        assert "v4_complete_report.json" in stderr
        assert "--force" in stderr

    def test_force_llega_al_flujo_normal(self, tmp_path, capsys, eventos_force):
        from main import run_hook_pdf_mode

        _escribir_fuentes_hook_pdf(tmp_path, URL_BOOKING)
        with pytest.raises(SystemExit) as excinfo:
            run_hook_pdf_mode(_args_hook_pdf(tmp_path, force=True))

        assert excinfo.value.code == 0
        assert any("booking" in e["url"] for e in _lineas_eventos(eventos_force))
