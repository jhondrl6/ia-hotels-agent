"""FASE-H1 (`D16`) — AC8: la rúbrica GBP se publica sobre su propio denominador.

Cinco dientes sobre el artefacto real del producto:
- el techo de la rúbrica es `SCORE_GBP_MAXIMO` (90), no 100;
- el reporte del propio módulo imprime ese denominador y ningún `/100` en su línea de score;
- `check_google_profile` delega en el productor único (la rúbrica duplicada del `_calculate_gbp_score`
  muerto queda unificada, no borrada);
- la rama API inexistente (`_places_api_lookup`) está retirada y `get_competitor_score` no la intenta;
- la estimación de competidor viaja con su escala y se declara no comparable con la rúbrica.

Citas por símbolo (R2.2): ningún test afirma `archivo:línea`.
"""

import ast
import inspect
from pathlib import Path

import pytest

from modules.common.rubrica_gbp import ESTIMACION_GBP_MAXIMO, SCORE_GBP_MAXIMO
from modules.scrapers.gbp_auditor import GBPAuditor

RAIZ_REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def auditor():
    """Instancia sin `__init__`: el auditor no abre navegador para calcular el score."""
    aud = GBPAuditor.__new__(GBPAuditor)
    aud.cache = {}
    return aud


def perfil_perfecto():
    return {
        'existe': True,
        'reviews': 250,
        'rating': 4.8,
        'fotos': 60,
        'horarios': True,
        'website': True,
        'telefono': True,
    }


def reporte_profile(auditor, score):
    profile = dict(perfil_perfecto())
    profile.update({
        'score': score,
        'perdida_total_mes_COP': 1000000,
        'perdida_anual_COP': 12000000,
        'prioridad_accion': 'ALTA',
        'fugas_detectadas': [],
        'whatsapp_visible': True,
    })
    return auditor.generar_reporte_ejecutivo(profile, 'Hotel Prueba')


def linea_del_score(reporte):
    for linea in reporte.splitlines():
        if 'Score actual GBP' in linea:
            return linea
    raise AssertionError('El reporte no publica la línea "Score actual GBP"')


def _segmento_fuente(nombre_de_funcion, fuente=None, sin_docstring=False):
    """Devuelve el fuente de una función del módulo `gbp_auditor` (o del indicado)."""
    texto = fuente if fuente is not None else inspect.getsource(GBPAuditor)
    arbol = ast.parse(texto)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre_de_funcion:
            segmento = ast.get_source_segment(texto, nodo)
            if sin_docstring and nodo.body and isinstance(nodo.body[0], ast.Expr):
                doc = nodo.body[0].value
                if isinstance(doc, ast.Constant) and isinstance(doc.value, str):
                    segmento = segmento.replace(ast.get_source_segment(texto, doc), '')
            return segmento
    raise AssertionError(f'{nombre_de_funcion} no está definida en la fuente revisada')


def _literales_de_codigo(fuente):
    """Constantes de string que el código evalúa, sin los docstrings (la prosa no es literal vivo)."""
    arbol = ast.parse(fuente)
    docstrings = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            cuerpo = getattr(nodo, 'body', None)
            if cuerpo and isinstance(cuerpo[0], ast.Expr) and isinstance(cuerpo[0].value, ast.Constant):
                if isinstance(cuerpo[0].value.value, str):
                    docstrings.add(id(cuerpo[0].value))
    return {
        nodo.value
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) and id(nodo) not in docstrings
    }


class TestDenominadorDeRubrica:
    def test_techo_de_la_rubrica_es_score_gbp_maximo(self, auditor):
        score = auditor._calculate_gbp_score(perfil_perfecto())
        assert score == SCORE_GBP_MAXIMO
        assert score != 100, 'La rúbrica no llega a 100: publicarla así es el sesgo de D16'

    def test_reporte_publica_el_denominador_de_la_rubrica(self, auditor):
        linea = linea_del_score(reporte_profile(auditor, SCORE_GBP_MAXIMO))
        assert linea.rstrip().endswith(f'{SCORE_GBP_MAXIMO}/{SCORE_GBP_MAXIMO}')
        assert '/100' not in linea

    def test_un_score_intermedio_no_se_renorma_a_cien(self, auditor):
        linea = linea_del_score(reporte_profile(auditor, 45))
        assert '45/90' in linea

    def test_rubrica_define_un_solo_productor_en_el_modulo(self):
        """El bloque duplicado de la rúbrica queda unificado: `score += 20` aparece una vez."""
        fuente = (RAIZ_REPO / 'modules' / 'scrapers' / 'gbp_auditor.py').read_text(encoding='utf-8')
        assert fuente.count('score += 20') == 1, (
            'Dos rubricas vivas con el mismo techo es el defecto que D16 describe'
        )

    def test_scrape_maps_profile_delega_en_el_productor_unico(self):
        """Productor medido: la rúbrica vive en `_scrape_maps_profile`, no en `check_google_profile`."""
        fuente_modulo = (RAIZ_REPO / 'modules' / 'scrapers' / 'gbp_auditor.py').read_text(encoding='utf-8')
        cuerpo = _segmento_fuente('_scrape_maps_profile', fuente_modulo)
        assert 'self._calculate_gbp_score(' in cuerpo
        assert '+= 20' not in cuerpo, (
            '_scrape_maps_profile volvió a calcular la rúbrica por su cuenta'
        )


class TestRamaApiMuertaRetirada:
    def test_places_api_lookup_no_existe(self, auditor):
        assert not hasattr(GBPAuditor, '_places_api_lookup'), (
            'La rama API nunca implementada volvió al contrato público del auditor'
        )

    def test_get_competitor_score_no_recibe_use_api(self):
        parametros = inspect.signature(GBPAuditor.get_competitor_score).parameters
        assert 'use_api' not in parametros

    def test_ninguna_varilla_intenta_la_api_inexistente(self):
        cuerpo = _segmento_fuente('get_competitor_score', sin_docstring=True)
        assert '_places_api_lookup' not in cuerpo
        assert 'place_id' not in cuerpo

    def test_score_source_api_es_inalcanzable_en_el_modulo(self):
        fuente_modulo = (RAIZ_REPO / 'modules' / 'scrapers' / 'gbp_auditor.py').read_text(encoding='utf-8')
        assert 'api' not in _literales_de_codigo(fuente_modulo), (
            'El literal score_source="api" no tiene productor desde D16'
        )


class TestEstimacionNoComparableConRubrica:
    def test_estimacion_viaja_con_su_escala_y_su_fuente(self, auditor):
        resultado = auditor.get_competitor_score({'reviews': 500, 'rating': 5.0})
        assert resultado['score'] == ESTIMACION_GBP_MAXIMO
        assert resultado['score_maximo'] == ESTIMACION_GBP_MAXIMO
        assert resultado['score_source'] == 'estimation'
        assert resultado['comparable_con_rubrica_gbp'] is False

    def test_la_estimacion_supera_el_techo_de_la_rubrica(self, auditor):
        """Prueba de no-comparabilidad: un valor de estimación puede exceder el techo de la rúbrica."""
        resultado = auditor.get_competitor_score({'reviews': 500, 'rating': 5.0})
        assert resultado['score'] > SCORE_GBP_MAXIMO
        assert str(SCORE_GBP_MAXIMO) in resultado['metodologia']

    def test_perfiles_extremos_de_estimacion_no_renorman_la_rubrica(self, auditor):
        sin_resenas = auditor.get_competitor_score({'reviews': 0, 'rating': 0.0})
        assert sin_resenas['score'] == 0
        assert sin_resenas['score_maximo'] == ESTIMACION_GBP_MAXIMO


class TestDenominadorViajaAlConsumidor:
    def test_audit_competitor_profile_publica_geo_score_maximo(self):
        """El `geo_score` del audit es la rúbrica (/90): su denominador viaja con el valor."""
        cuerpo = _segmento_fuente('audit_competitor_profile')
        assert cuerpo.count("'geo_score_maximo': SCORE_GBP_MAXIMO") == 2, (
            'Las dos ramas (cache y live_audit) tienen que declarar el denominador'
        )

    def test_el_log_del_analizador_no_fija_cien(self):
        fuente = (RAIZ_REPO / 'modules' / 'analyzers' / 'competitor_analyzer.py').read_text(encoding='utf-8')
        assert 'geo_score_maximo' in fuente, (
            'El consumidor volvió a imprimir el GEO auditado sobre un /100 heredado'
        )
        assert "GEO {audit_result['geo_score']}/100" not in fuente
