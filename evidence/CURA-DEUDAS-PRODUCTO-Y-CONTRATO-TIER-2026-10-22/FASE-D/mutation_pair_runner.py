"""Mutation pair runner — FASE-D (R2.8, L-T4A.5).

Aplica cada mutante SOBRE EL SÍMBOL REAL del guard, corre la selección de
tests, guarda el crudo rojo y revierte verificando byte a byte. Tres mutantes:

  M1 — contrato viejo restaurado en `get_detected_issues` (claves inglesas
       `claimed`/`photos`/`has_whatsapp`/`has_hours` + semántica de schema
       vieja) y default `schema_data={}` del llamador: reproduce el reproductor
       medido de D28 (6 brechas, 39.600.000 COP/mes sobre perfil completo).
  M2 — `_map_brecha_to_issue_type` restaurado (`no_hotel_schema` y
       `low_citability` → `PERFIL_ABANDONADO`; `no_og_tags` → `FOTOS_INSUFICIENTES`).
  M3 — colapso de `tipo_map` restaurado (`CERO_ACTIVIDAD_RECIENTE` →
       `PERFIL_ABANDONADO`), el defecto N2.

El runner no muta la población que audita (L23): los literales del contrato
viejo viven AQUÍ, no en los tests del diente.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
EV = pathlib.Path(__file__).resolve().parent

VIEJO_CUERPO = """    issues = []

    if not gbp_data.get('claimed', False):
        issues.append('PERFIL_NO_RECLAMADO')

    photos = gbp_data.get('photos', 0)
    if photos < 5:
        issues.append('FOTOS_INSUFICIENTES')

    rating = gbp_data.get('rating', 5)
    if rating < 3.5:
        issues.append('RESENAS_CRITICAS')
    elif rating < 4.0:
        issues.append('RATING_BAJO')

    if not gbp_data.get('has_whatsapp', False):
        issues.append('SIN_WHATSAPP')

    if not gbp_data.get('has_hours', False):
        issues.append('SIN_HORARIOS')

    if not gbp_data.get('website', False):
        issues.append('SIN_WEBSITE')

    if not gbp_data.get('posts', 0) > 0:
        issues.append('CERO_ACTIVIDAD_RECIENTE')

    if not schema_data.get('tiene_hotel_schema', False):
        issues.append('PERFIL_ABANDONADO')

    if not schema_data.get('has_faq', False):
        issues.append('SIN_FAQ')

    return issues"""

NUEVO_CUERPO = """    issues: List[str] = []

    if not gbp_data.get('existe', False):
        issues.append('PERFIL_NO_RECLAMADO')

    if gbp_data.get('fotos', 0) < 5:
        issues.append('FOTOS_INSUFICIENTES')

    rating = gbp_data.get('rating', 5)
    if rating < 3.5:
        issues.append('RESENAS_CRITICAS')
    elif rating < 4.0:
        issues.append('RATING_BAJO')

    if not gbp_data.get('whatsapp_visible', False):
        issues.append('SIN_WHATSAPP')

    if not gbp_data.get('horarios', False):
        issues.append('SIN_HORARIOS')

    if not gbp_data.get('website', False):
        issues.append('SIN_WEBSITE')

    # Actividad del perfil: ÚNICA fuente de PERFIL_ABANDONADO (N2).
    if gbp_data.get('posts', 0) == 0:
        issues.append('PERFIL_ABANDONADO')

    # Etiqueta propia (N2): disparo distinto al de posts. `None` = no medido
    # → sin brecha (DA-C3).
    dias = gbp_data.get('ultima_actividad_dias')
    if dias is not None and dias > ACTIVIDAD_RECIENTE_DIAS:
        issues.append('CERO_ACTIVIDAD_RECIENTE')

    # FAQ/Q&A conversacional: cada fuente medida habla por sí sola (DA-C3).
    # `tiene_qa` es el Q&A de GBP (siempre medido por el scraper); `has_faq` es
    # el FAQ schema de la web (solo cuando se midió).
    faq_ausente = not gbp_data.get('tiene_qa', False)
    if schema_data is not None and not schema_data.get('has_faq', False):
        faq_ausente = True
    if faq_ausente:
        issues.append('SIN_FAQ')

    return issues"""

MUTANTES = [
    {
        'nombre': 'm1-claves-inglesas',
        'seleccion': ['tests/test_gbp_contrato_frontera.py'],
        'swaps': [
            ('modules/utils/dynamic_impact.py', NUEVO_CUERPO, VIEJO_CUERPO),
            (
                'modules/scrapers/gbp_auditor.py',
                "detected_issues = get_detected_issues(profile_data, profile_data.get('schema_data'))",
                "detected_issues = get_detected_issues(profile_data, profile_data.get('schema_data', {}))",
            ),
        ],
    },
    {
        'nombre': 'm2-mapa-schema-a-abandono',
        'seleccion': ['tests/test_gbp_contrato_frontera.py::TestPainSolutionMapperCaminoV4Complete'],
        'swaps': [
            (
                'modules/commercial_documents/v4_diagnostic_generator.py',
                "            'no_hotel_schema': '',\n            'no_whatsapp_visible': 'SIN_WHATSAPP',\n            'poor_performance': 'SIN_WEBSITE',\n            'whatsapp_conflict': 'SIN_WHATSAPP',\n            'metadata_defaults': 'CERO_ACTIVIDAD_RECIENTE',\n            'missing_reviews': 'RESENAS_CRITICAS',\n            'no_faq_schema': 'SIN_FAQ',\n            'no_og_tags': '',\n            'low_citability': '',",
                "            'no_hotel_schema': 'PERFIL_ABANDONADO',\n            'no_whatsapp_visible': 'SIN_WHATSAPP',\n            'poor_performance': 'SIN_WEBSITE',\n            'whatsapp_conflict': 'SIN_WHATSAPP',\n            'metadata_defaults': 'CERO_ACTIVIDAD_RECIENTE',\n            'missing_reviews': 'RESENAS_CRITICAS',\n            'no_faq_schema': 'SIN_FAQ',\n            'no_og_tags': 'FOTOS_INSUFICIENTES',\n            'low_citability': 'PERFIL_ABANDONADO',",
            ),
        ],
    },
    {
        'nombre': 'm3-tipo-map-colapsado',
        'seleccion': ['tests/test_gbp_contrato_relevo.py::TestN2EtiquetasPropias'],
        'swaps': [
            (
                'modules/scrapers/gbp_auditor.py',
                "                'CERO_ACTIVIDAD_RECIENTE': 'CERO_ACTIVIDAD_RECIENTE',",
                "                'CERO_ACTIVIDAD_RECIENTE': 'PERFIL_ABANDONADO',",
            ),
        ],
    },
]


def correr(seleccion, destino):
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest'] + seleccion + ['-q'],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    destino.write_text(
        f"CMD: pytest {' '.join(seleccion)} -q\nEXIT={proc.returncode}\n\n"
        + proc.stdout + proc.stderr,
        encoding='utf-8',
    )
    return proc.returncode


def main():
    resultados = []
    for i, mut in enumerate(MUTANTES, start=1):
        originales = {}
        for rel, viejo, nuevo in mut['swaps']:
            ruta = ROOT / rel
            texto = ruta.read_text(encoding='utf-8')
            assert texto.count(viejo) == 1, f"{rel}: ancla no única para {mut['nombre']}"
            originales[rel] = texto
            ruta.write_text(texto.replace(viejo, nuevo), encoding='utf-8')

        exit_rojo = correr(mut['seleccion'], EV / f"{2 * i:02d}-rojo-mutante-{mut['nombre']}.txt")

        for rel, texto in originales.items():
            (ROOT / rel).write_text(texto, encoding='utf-8')
            assert (ROOT / rel).read_text(encoding='utf-8') == texto, f"{rel}: reversión falló"

        exit_verde = correr(mut['seleccion'], EV / f"{2 * i + 1:02d}-verde-tras-restaurar-{mut['nombre'][:2]}.txt")
        resultados.append((mut['nombre'], exit_rojo, exit_verde))

    print("RESUMEN PAR ROJO/VERDE (rojo esperado != 0, verde esperado == 0):")
    for nombre, rojo, verde in resultados:
        estado = 'OK' if (rojo != 0 and verde == 0) else 'REVISAR'
        print(f"  [{estado}] {nombre}: rojo EXIT={rojo} | verde EXIT={verde}")


if __name__ == '__main__':
    main()
