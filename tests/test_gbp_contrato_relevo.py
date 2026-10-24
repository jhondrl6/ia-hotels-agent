"""Relevo de `gbp_leak_detector` + etiquetas de actividad (FASE-D, N2/N3).

POR QUÉ EXISTE (N3, DA-PLAN-9)
`modules/scrapers/gbp_leak_detector.py` es una copia muerta sin importador de
producción que conserva el vocabulario español CORRECTO del productor. La fase
porta su lógica de lectura como implementación del contrato
(`modules.utils.dynamic_impact.get_detected_issues`) y este test es el RELEVO:
demuestra, perfil a perfil, que la lógica portada produce el mismo resultado
que la copia muerta. La copia queda retirada del servicio (banner del módulo)
pero viva como oráculo: se importa con stubs porque sus imports de
`webdriver_manager` no existen en el entorno de tests.

DIVERGENCIAS DECLARADAS (no son fallas del relevo; se fijan como expectativa
para que cualquier cambio futuro se note):
  · la copia declara brecha por CONTEO de reseñas (`reviews < 10`,
    `RESEÑAS_INSUFICIENTES`) y el contrato no la tiene (la de rating sí);
  · la copia declara `SIN_TELEFONO_VISIBLE` y `IMPACT_TYPES` no la contempla;
  · `CERO_ACTIVIDAD_RECIENTE` es etiqueta PROPIA nueva (N2): la copia no la
    dispara nunca (su `ultima_actividad_dias` jamás se poblaba);
  · los valores numéricos de umbrales son de FASE-F (esta fase no los mueve).

MUTATION CHECK (R2.8): el mutante M3 restaura el colapso de `tipo_map`
(`CERO_ACTIVIDAD_RECIENTE` → `PERFIL_ABANDONADO`); los tests de N2 caen en
ROJO (dedupe aguas abajo undercounta). Par en `evidence/…/FASE-D/`.
"""

import sys
import types

import pytest


def _stub_faltantes():
    """Solo stubea lo que falta en el entorno (nunca pisa un módulo real)."""
    try:
        import webdriver_manager.chrome  # noqa: F401
        return
    except ImportError:
        pass
    pkg = types.ModuleType('webdriver_manager')
    sub = types.ModuleType('webdriver_manager.chrome')

    class ChromeDriverManager:  # noqa: D401 - stub de import, no se usa
        @staticmethod
        def install():
            raise RuntimeError('stub: el oráculo del relevo no lanza Selenium')

    sub.ChromeDriverManager = ChromeDriverManager
    pkg.chrome = sub
    sys.modules.setdefault('webdriver_manager', pkg)
    sys.modules.setdefault('webdriver_manager.chrome', sub)


_stub_faltantes()

from modules.scrapers.gbp_leak_detector import GBPRevenueLeakDetector  # noqa: E402
from modules.scrapers.gbp_auditor import GBPAuditor  # noqa: E402
from modules.utils.benchmarks import BenchmarkLoader  # noqa: E402
from modules.utils.dynamic_impact import get_detected_issues  # noqa: E402

SCHEMA_VALIDO = {'tiene_hotel_schema': True, 'has_faq': True}

# Canonificación declarada de etiquetas (copia muerta → dimensión común).
CANONICOS_COPIA = {
    'PERFIL_NO_RECLAMADO': 'PERFIL_NO_RECLAMADO',
    'FOTOS_INSUFICIENTES': 'FOTOS_INSUFICIENTES',
    'RESEÑAS_INSUFICIENTES': None,       # divergencia declarada
    'RATING_DESCALIFICANTE': 'RATING',
    'SIN_WHATSAPP_VISIBLE': 'SIN_WHATSAPP',
    'PERFIL_ABANDONADO': 'PERFIL_ABANDONADO',
    'SIN_FAQ_CONVERSACIONAL': 'SIN_FAQ',
    'SIN_HORARIOS': 'SIN_HORARIOS',
    'SIN_WEBSITE_DIRECTO': 'SIN_WEBSITE',
    'SIN_TELEFONO_VISIBLE': None,        # divergencia declarada
}
CANONICOS_CONTRATO = {
    'PERFIL_NO_RECLAMADO': 'PERFIL_NO_RECLAMADO',
    'FOTOS_INSUFICIENTES': 'FOTOS_INSUFICIENTES',
    'RESENAS_CRITICAS': 'RATING',
    'RATING_BAJO': 'RATING',
    'SIN_WHATSAPP': 'SIN_WHATSAPP',
    'PERFIL_ABANDONADO': 'PERFIL_ABANDONADO',
    'SIN_FAQ': 'SIN_FAQ',
    'SIN_HORARIOS': 'SIN_HORARIOS',
    'SIN_WEBSITE': 'SIN_WEBSITE',
    'CERO_ACTIVIDAD_RECIENTE': None,     # etiqueta propia nueva (N2)
}


def _perfil_base() -> dict:
    """Perfil completo en el vocabulario REAL del productor (ambos detectores
    leen estas mismas claves)."""
    return {
        'existe': True,
        'score': 0,
        'issues': [],
        'reviews': 120,
        'rating': 4.6,
        'fotos': 40,
        'horarios': True,
        'descripcion': True,
        'website': True,
        'telefono': True,
        'whatsapp_visible': True,
        'posts': 5,
        'tiene_qa': True,
        'ultima_actividad_dias': None,
        'fugas_detectadas': [],
        'perdida_total_mes_COP': 0,
        'perdida_anual_COP': 0,
        'prioridad_accion': None,
        'meta': {},
    }


def _copia_detecta(perfil: dict) -> set:
    detector = GBPRevenueLeakDetector(headless=True)
    fugas, _ = detector._detectar_fugas(dict(perfil))
    return {f['tipo'] for f in fugas}


def _contrato_detecta(perfil: dict) -> set:
    return set(get_detected_issues(dict(perfil), SCHEMA_VALIDO))


def _canon(tipos: set, tabla: dict) -> set:
    return {tabla[t] for t in tipos if tabla.get(t) is not None}


# Cada caso rompe UNA dimensión con valor dentro de la zona de acuerdo de los
# dos detectores (los umbrales son de FASE-F y esta fase no los mueve).
MATRIZ = {
    'perfil_completo': {},
    'sin_perfil': {'existe': False},
    'fotos_pocas': {'fotos': 2},
    'rating_bajo': {'rating': 3.2},
    'sin_whatsapp': {'whatsapp_visible': False},
    'sin_horarios': {'horarios': False},
    'sin_website': {'website': False},
    'sin_posts': {'posts': 0},
    'sin_qa': {'tiene_qa': False},
}


class TestRelevo:
    """La lógica portada produce el mismo resultado que la copia muerta."""

    @pytest.mark.parametrize('caso', sorted(MATRIZ))
    def test_mismo_resultado_por_perfil(self, caso):
        perfil = _perfil_base()
        perfil.update(MATRIZ[caso])
        copia = _canon(_copia_detecta(perfil), CANONICOS_COPIA)
        contrato = _canon(_contrato_detecta(perfil), CANONICOS_CONTRATO)
        assert copia == contrato, (
            f"{caso}: copia muerta {sorted(copia)} vs contrato {sorted(contrato)}"
        )

    def test_perfil_completo_cero_en_ambos_y_cero_perdida(self):
        perfil = _perfil_base()
        detector = GBPRevenueLeakDetector(headless=True)
        fugas, perdida = detector._detectar_fugas(dict(perfil))
        assert fugas == [] and perdida == 0
        assert _contrato_detecta(perfil) == set()

    def test_divergencias_declaradas_fijadas(self):
        """Las no-equivalencias declaradas quedan fijadas: si alguien las mueve,
        este test se cae y obliga a re-declarar."""
        sin_telefono = _perfil_base()
        sin_telefono['telefono'] = False
        assert _copia_detecta(sin_telefono) == {'SIN_TELEFONO_VISIBLE'}
        assert _contrato_detecta(sin_telefono) == set()

        pocas_resenas = _perfil_base()
        pocas_resenas['reviews'] = 5
        assert _copia_detecta(pocas_resenas) == {'RESEÑAS_INSUFICIENTES'}
        assert _contrato_detecta(pocas_resenas) == set()

        actividad_antigua = _perfil_base()
        actividad_antigua['ultima_actividad_dias'] = 90
        assert _copia_detecta(actividad_antigua) == set()
        assert _contrato_detecta(actividad_antigua) == {'CERO_ACTIVIDAD_RECIENTE'}


class TestN2EtiquetasPropias:
    """`tipo_map` no colapsa las dos brechas de actividad (N2)."""

    def _fugas_actividad(self) -> list:
        perfil = _perfil_base()
        perfil['posts'] = 0
        perfil['ultima_actividad_dias'] = 90
        auditor = GBPAuditor.__new__(GBPAuditor)
        auditor.benchmark_loader = BenchmarkLoader()
        fugas, _ = auditor._detectar_fugas(perfil)
        return fugas

    def test_dos_tipos_distintos_no_colapsados(self):
        tipos = [f['tipo'] for f in self._fugas_actividad()]
        assert 'PERFIL_ABANDONADO' in tipos
        assert 'CERO_ACTIVIDAD_RECIENTE' in tipos

    def test_dedupe_aguas_abajo_no_undercounta(self):
        fugas = self._fugas_actividad()
        dedup = {f['tipo']: f for f in fugas}  # dedupe por `tipo` aguas abajo
        assert len(dedup) == 2, (
            f"dedupe por tipo undercounta: {sorted(dedup)} sobre {len(fugas)} fugas"
        )

    def test_los_textos_no_repite_la_misma_queja(self):
        fugas = self._fugas_actividad()
        motivos = [f['motivo'] for f in fugas]
        assert len(set(motivos)) == len(motivos), motivos
