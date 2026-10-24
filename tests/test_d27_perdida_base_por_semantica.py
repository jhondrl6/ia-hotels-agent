"""`D27` — las tres constantes homónimas de pérdida mensual, re-medidas tras FASE-D (FASE-F).

El contexto de deudas publicó tres constantes con el mismo nombre genérico (arriba, reconstruido
por piezas siguiendo `L23`: el guard no puede escribir contiguo el token que audita), con dos
valores y tres semánticas: 2.1M en `DynamicImpactCalculator` (la única consumida), 2.8M en
`GBPAuditor` (calibración regional del Caribe, sin consumidor) y 2.1M en
`GBPRevenueLeakDetector` (copia retirada, sin consumidor). FASE-D marcó el detector como
retirado pero lo conservó como oráculo del relevo, así que las tres constantes
**sobrevivieron**: esta fase las re-mide y las rebautiza por semántica.
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
POBLACION = ("modules", "tests", "scripts")
NOMBRE_GENERICO = "PERDIDA_MENSUAL" + "_BASE"

# (nombre semántico, módulo, valor, palabra que documenta su semántica, usos fuera de la definición)
CONSTANTES = (
    ("PERDIDA_BASE_SIN_PERFIL", "modules/utils/dynamic_impact.py", 2_100_000, "PERFIL_NO_RECLAMADO", 1),
    ("PERDIDA_BASE_CARIBE_CALIBRADA", "modules/scrapers/gbp_auditor.py", 2_800_000, "Caribe", 0),
    ("PERDIDA_BASE_CALIBRACION_15_20_HAB", "modules/scrapers/gbp_leak_detector.py", 2_100_000, "15-20", 0),
)


def _archivos_poblacion():
    archivos = []
    for carpeta in POBLACION:
        directorio = RAIZ / carpeta
        assert directorio.is_dir(), f"la población declarada no existe: {directorio}"
        archivos.extend(
            ruta
            for ruta in directorio.rglob("*.py")
            if "__pycache__" not in ruta.parts
        )
    assert archivos, f"población vacía en {POBLACION}: el guard no mediría nada"
    yield from archivos


def _asignaciones_de(nombre: str, texto_fuente: str):
    """Asignaciones (de clase o de módulo) que definen `nombre`."""
    definidas = []
    for nodo in ast.walk(ast.parse(texto_fuente)):
        if isinstance(nodo, (ast.Assign, ast.AnnAssign)):
            objetivos = nodo.targets if isinstance(nodo, ast.Assign) else [nodo.target]
            if any(isinstance(o, ast.Name) and o.id == nombre for o in objetivos):
                definidas.append(nodo)
    return definidas


def test_el_nombre_generico_no_usa_nadie_en_la_poblacion():
    """Grep por símbolo del nombre genérico: 0 usos en código y tests."""
    usos = [
        f"{ruta.relative_to(RAIZ)}:{linea}"
        for ruta in _archivos_poblacion()
        for linea, texto in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1)
        if NOMBRE_GENERICO in texto
    ]
    assert usos == [], f"sobreviven usos de {NOMBRE_GENERICO}: {usos}"


def test_main_no_referencia_el_nombre_generico():
    """La CLI tampoco: la población incluye el punto de entrada."""
    ruta = RAIZ / "main.py"
    assert NOMBRE_GENERICO not in ruta.read_text(encoding="utf-8")


def test_cada_constante_sobreviviente_tiene_nombre_valor_y_semantica_propios():
    """Un nombre por semántica, con su valor y su palabra de calibración en el propio módulo."""
    for nombre, rel_ruta, valor, semantica, _usos in CONSTANTES:
        ruta = RAIZ / rel_ruta
        texto = ruta.read_text(encoding="utf-8")
        definiciones = _asignaciones_de(nombre, texto)
        assert len(definiciones) == 1, f"{nombre} definido {len(definiciones)} veces en {rel_ruta}"
        valor_asignado = definiciones[0].value
        assert isinstance(valor_asignado, ast.Constant) and valor_asignado.value == valor, (
            f"{nombre} en {rel_ruta} no vale {valor}: {ast.unparse(valor_asignado)}"
        )
        assert semantica in texto, f"{nombre} perdió la palabra que documenta su semántica ({semantica})"


def test_los_valores_declaran_dos_calibraciones_distintas_bajo_un_mismo_nombre_generico():
    """2.8M (Caribe) y 2.1M (sin-perfil / 15-20 hab) eran la misma etiqueta para cosas distintas."""
    valores = {nombre: valor for nombre, _r, valor, _s, _u in CONSTANTES}
    assert valores["PERDIDA_BASE_CARIBE_CALIBRADA"] != valores["PERDIDA_BASE_SIN_PERFIL"], (
        "las dos bases divergían por calibración regional; unificarlas sin decisión volvería "
        "a esconder D27"
    )


def test_solo_la_constante_que_se_consume_tiene_usos():
    """Conteos de uso (fuera de la definición) pinchados: 1 en dynamic_impact, 0 en las huérfanas."""
    for nombre, rel_ruta, _valor, _semantica, usos_esperados in CONSTANTES:
        ruta = RAIZ / rel_ruta
        texto = ruta.read_text(encoding="utf-8")
        ocurrencias = texto.count(nombre)
        usos = ocurrencias - len(_asignaciones_de(nombre, texto))
        assert usos == usos_esperados, (
            f"{nombre} en {rel_ruta}: {usos} usos fuera de la definición, la población declara "
            f"{usos_esperados}. Si cambiaste el consumidor, re-declara la huérfana."
        )


def test_la_huerfana_del_oraculo_sigue_siendo_huerfana():
    """`gbp_leak_detector` está retirado del servicio: sus impactos usan `cop_mes`, no la base."""
    texto = (RAIZ / "modules/scrapers/gbp_leak_detector.py").read_text(encoding="utf-8")
    assert "cop_mes" in texto, "la copia retirada ya no calibra por cop_mes: re-mide D27"
