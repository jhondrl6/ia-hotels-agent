"""Test propio de `scripts/validate_wiring.py` (FASE-G, AC7 + AC16).

Por que este archivo existe y no basta el verde del check en el quick
    L-V2.1: un test que solo mira **que check** disparo puede quedar verde por una rama
    distinta de la que queria observar. Por eso cada rojo de aqui aserta sobre el
    **mensaje y el tipo de la violacion**, no sobre un codigo compartido. Y L-T4A.5: un
    test verde puede no alcanzar la rama que dice certificar, asi que el verificador se
    prueba con **callers nuevos en archivos nuevos** (fixtures bajo `tmp_path`), no con
    el caller que FASE-B ya corregira, y ademas contra el repo real para probar que la
    cobertura llega a la divergencia vigente.

Los fixtures declaran las clases con el nombre exacto del productor (`PainSolutionMapper`,
    `CoherenceValidator`, `AssessmentBuilder`) porque eso es lo que el AST resuelve: el
    verificador no ejecuta import, deduce tipos de la fuente.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_wiring.py"

_spec = importlib.util.spec_from_file_location("validate_wiring", SCRIPT)
vw = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(vw)


# ------------------------------------------------------------------------------ fixtures
PRODUCTORES = '''
class PainSolutionMapper:
    def detect_pains(self, audit_result, validation_summary, analytics_data=None,
                     whatsapp_html_detected=False):
        return []


class CoherenceValidator:
    def validate(self, diagnostic, proposal, assets, validation_summary,
                 whatsapp_html_detected=False, generated_assets=None,
                 site_presence_report=None):
        return None


class AssessmentBuilder:
    def with_validation(self, validation_summary):
        return self


class V4ProposalGenerator:
    """Productor de PROMESAS: gobernar solo los pains dejaria la propuesta sin guard."""

    def _generate_dynamic_services_table(self, detected_pain_ids=None, score_aeo=None,
                                         assets_generated=None, site_presence_report=None,
                                         whatsapp_conflict=False,
                                         opportunity_scores=None,
                                         committed_services=None):
        return ""


class PrecisionValidator:
    """Homonimo: se llama `validate` y NO esta gobernado (AC1 exige excluirlo)."""

    def validate(self, data, sources=None):
        return None
'''


def _arbol(tmp_path: Path, modulos: dict[str, str]) -> Path:
    (tmp_path / "modules").mkdir(parents=True, exist_ok=True)
    for nombre, codigo in modulos.items():
        (tmp_path / "modules" / nombre).write_text(codigo, encoding="utf-8")
    return tmp_path


@pytest.fixture(scope="module")
def reporte_repo():
    """Medicion del arbol vivo, una sola vez por modulo (cada pasada cuesta ~25 s)."""
    return vw.construir_reporte(ROOT)


@pytest.fixture(scope="module")
def reporte_repo_sin_excepciones():
    """La misma medicion sin el registro de excepciones: lo que estas tapan."""
    return vw.construir_reporte(ROOT, ignore_known=True)

# --------------------------------------------------------------- AC7: la poblacion se descubre
def test_caller_nuevo_en_archivo_nuevo_que_omite_la_senal_rompe(tmp_path):
    """El caso rojo central de AC7: nadie registro este archivo y aun asi cae gobernado.

    Es la diferencia entre un verificador y una lista de pruebas: si gobernar dependiera
    de acordarse de escribir un test por caller, este archivo no existiria y el defecto
    quedaria verde.
    """
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "nada_que_ver.py": (
            "from .productores import PainSolutionMapper\n"
            "mapper = PainSolutionMapper()\n"
            "pains = mapper.detect_pains(audit, summary, analytics,\n"
            "                             whatsapp_html_detected=html)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    assert reporte["violaciones"] == [], [v["detalle"] for v in reporte["violaciones"]]

    _arbol(tmp_path, {
        "caller_olvidadizo.py": (
            "from .productores import PainSolutionMapper\n"
            "mapper = PainSolutionMapper()\n"
            "pains = mapper.detect_pains(audit, summary, analytics)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    assert len(reporte["violaciones"]) == 1, reporte["violaciones"]
    violacion = reporte["violaciones"][0]
    # Se aserta sobre el MENSAJE y el simbolo, no solo sobre el check (L-V2.1).
    assert violacion["tipo"] == "SENAL_OMITIDA"
    assert "whatsapp_html_detected" in violacion["detalle"]
    assert violacion["simbolo"] == "PainSolutionMapper.detect_pains"
    assert violacion["archivo"] == "modules/caller_olvidadizo.py"


def test_ocultar_la_senal_tras_kwargs_opacos_rompe(tmp_path):
    """AC7: `**kwargs` no puede leerse como cumplido; ausente + opaco = violacion."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "envoltorio.py": (
            "from .productores import PainSolutionMapper\n"
            "def envolver(audit, summary, **kwargs):\n"
            "    return PainSolutionMapper().detect_pains(audit, summary, **kwargs)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    tipos = {v["tipo"] for v in reporte["violaciones"]}
    assert "KWARGS_OPACOS" in tipos, reporte["violaciones"]
    detalle = next(v for v in reporte["violaciones"] if v["tipo"] == "KWARGS_OPACOS")
    assert "whatsapp_html_detected" in detalle["detalle"]


def test_alias_de_import_y_self_quedan_cubiertos(tmp_path):
    """AC7 nombra explicitamente aliases e instancias `self.*`: los dos tienen que romper."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "por_alias.py": (
            "from .productores import PainSolutionMapper as PSM\n"
            "mapper = PSM()\n"
            "mapper.detect_pains(audit, summary, analytics)\n"
        ),
        "por_self.py": (
            "from .productores import PainSolutionMapper\n"
            "class Orquestador:\n"
            "    def __init__(self):\n"
            "        self.pain_mapper = PainSolutionMapper()\n"
            "    def generar(self):\n"
            "        return self.pain_mapper.detect_pains(audit, summary, analytics)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    archivos = {v["archivo"] for v in reporte["violaciones"]}
    assert archivos == {"modules/por_alias.py", "modules/por_self.py"}, reporte["violaciones"]
    # Y no quedaron en el hueco de cobertura: el AST resolvio los dos al productor real.
    # Lo que se prueba es la CLASE resuelta (alias `PSM` -> `PainSolutionMapper`;
    # `self.pain_mapper` -> idem), no en que estrategia la encontro cada archivo.
    por_archivo = {r["archivo"]: r for r in reporte["poblacion"] if r["gobernado"]}
    assert por_archivo["modules/por_alias.py"]["clase_resuelta"] == "PainSolutionMapper"
    assert por_archivo["modules/por_self.py"]["clase_resuelta"] == "PainSolutionMapper"
    assert por_archivo["modules/por_self.py"]["resolucion"] == "self_binding_en_la_clase"


def test_clases_validate_no_relacionadas_quedan_excluidas(tmp_path):
    """AC7: excluir la clase homonima, no el nombre de metodo. Sin esto todo `validate` seria sospechoso."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "ajeno.py": (
            "from .productores import PrecisionValidator\n"
            "pv = PrecisionValidator()\n"
            "pv.validate(data, sources)\n"
            "from .productores import CoherenceValidator\n"
            "CoherenceValidator().validate(d, p, a, s, whatsapp_html_detected=h)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    assert reporte["violaciones"] == [], reporte["violaciones"]
    # Dos llamadas en el MISMO archivo: hay que indexar por (archivo, linea), no por
    # archivo, o el segundo registro taparia al primero.
    por_linea = {(r["archivo"], r["linea"]): r for r in reporte["poblacion"]}
    del_ajeno = por_linea[("modules/ajeno.py", 3)]
    assert del_ajeno["clasificacion"] == "EXCLUIDA_POR_CLASE"
    assert "no es un productor gobernado" in del_ajeno["motivo"] or \
        "no promesa WhatsApp" in del_ajeno["motivo"]
    del_gobernado = por_linea[("modules/ajeno.py", 5)]
    assert del_gobernado["clasificacion"] == "GOBERNADA_CONFORME"
    assert del_gobernado["clase_resuelta"] == "CoherenceValidator"


def test_la_senal_viaja_tambien_como_posicional(tmp_path):
    """Un caller legitimo que pasa la senal por posicion no es un falso positivo."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "posicional.py": (
            "from .productores import PainSolutionMapper\n"
            "PainSolutionMapper().detect_pains(audit, summary, analytics, html)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    assert reporte["violaciones"] == [], reporte["violaciones"]
    assert reporte["poblacion"][0]["clasificacion"] == "GOBERNADA_CONFORME"


# --------------------------------------------------------------------- AC16: contrato muerto
def test_caller_con_la_firma_vieja_rompe_el_contrato(tmp_path):
    """AC16: inyectar un caller que vuelva a pedir `whatsapp_validation` hace rojo."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "constructor.py": (
            "from .productores import AssessmentBuilder\n"
            "AssessmentBuilder().with_validation(summary)\n"
        ),
    })
    assert vw.construir_reporte(tmp_path, ignore_known=True)["violaciones"] == []

    _arbol(tmp_path, {
        "constructor.py": (
            "from .productores import AssessmentBuilder\n"
            "AssessmentBuilder().with_validation(summary, whatsapp_validation)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    assert len(reporte["violaciones"]) == 1, reporte["violaciones"]
    violacion = reporte["violaciones"][0]
    assert violacion["tipo"] == "ARGUMENTO_PROHIBIDO"
    assert "whatsapp_validation" in violacion["detalle"]


def test_re_introducir_el_parametro_en_la_firma_rompe(tmp_path):
    """El contrato muerto puede reaparecer por la definicion, no solo por el caller."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "consumidor.py": (
            "from .productores import AssessmentBuilder\n"
            "AssessmentBuilder().with_validation(summary)\n"
        ),
    })
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES.replace(
            "    def with_validation(self, validation_summary):",
            "    def with_validation(self, validation_summary, whatsapp_validation):"),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    tipos = {v["tipo"] for v in reporte["violaciones"]}
    assert "CONTRATO_MUERTO_VIGENTE" in tipos, reporte["violaciones"]


def test_retiro_real_en_el_repo_deja_el_contrato_cerrado(reporte_repo):
    """AC16 sobre el arbol vivo: la firma ya no declara el parametro descartado."""
    firma = reporte_repo["politica"]["AssessmentBuilder.with_validation"]["firma_real"]
    assert "whatsapp_validation" not in firma["parametros"]
    assert firma["parametros_de_llamada"] == ["validation_summary"]
    assert not any(v["tipo"] == "SIMBOLO_GOBERNADO_AUSENTE"
                   for v in reporte_repo["violaciones"]), (
        "la politica declara un simbolo que ya no existe: caduco el verificador")


# ------------------------------------------------------------------ excepciones tipadas
def test_excepcion_que_ya_no_ampa_nada_es_en_si_una_violacion(tmp_path):
    """El registro de excepciones no puede degradarse a allowlist: si sobra, hace rojo.

    Sin esta prueba, la unica salida de un hallazgo incomodo seria anadir una excepcion y
    dejarla alli para siempre.
    """
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "correcto.py": (
            "from .productores import PainSolutionMapper\n"
            "PainSolutionMapper().detect_pains(a, s, x, whatsapp_html_detected=h)\n"
        ),
    })
    exc_huerfana = {
        "tipo": "HALLAZGO_CONOCIDO",
        "archivo": "modules/archivo_que_no_existe.py",
        "simbolo": "PainSolutionMapper.detect_pains",
        "senal": "whatsapp_html_detected",
        "motivo": "prueba", "dueno": "X", "ac": "AC7", "baja_cuando": "nunca",
    }
    emparejado = vw.aplicar_excepciones([], [exc_huerfana])
    assert len(emparejado["abiertas"]) == 1
    assert emparejado["abiertas"][0]["tipo"] == "EXCEPCION_VAGA"
    assert "allowlist" in emparejado["abiertas"][0]["detalle"]


def test_ignore_known_deja_ver_lo_que_tapan_las_excepciones(reporte_repo,                                                   reporte_repo_sin_excepciones):
    """El mecanismo anti-allowlist: cualquiera puede pedir el rojo completo del repo real."""
    con_exc = reporte_repo
    sin_exc = reporte_repo_sin_excepciones
    assert con_exc["violaciones"] == [], (
        "el quick va a rojo sobre el arbol vivo; los hallazgos conocidos deberian estar "
        "registrados con dueno, no sin registrar")
    assert len(sin_exc["violaciones"]) > len(con_exc["violaciones"])
    assert len(con_exc["excepciones_aplicadas"]) == len(sin_exc["violaciones"]) - \
        len(con_exc["violaciones"])


def test_una_politica_que_declara_un_simbolo_inexistente_hace_rojo(tmp_path):
    """Caducar la politica no puede degradarse a verde silencioso.

    Medido de verdad: este rojo aparecio solo, cuando FASE-G goberno un productor nuevo
    y los fixtures aun no lo definian. Un verificador que ignora lo que ya no encuentra
    se parece demasiado a un verificador que no encuentra nada.
    """
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES.replace(
            "class V4ProposalGenerator:", "class YaNoGobernado:"),
        "consumidor.py": (
            "from .productores import PainSolutionMapper\n"
            "PainSolutionMapper().detect_pains(a, s, x, whatsapp_html_detected=h)\n"
        ),
    })
    reporte = vw.construir_reporte(tmp_path, ignore_known=True)
    tipos = [v["tipo"] for v in reporte["violaciones"]]
    assert "SIMBOLO_GOBERNADO_AUSENTE" in tipos, reporte["violaciones"]
    ausente = next(v for v in reporte["violaciones"]
                   if v["tipo"] == "SIMBOLO_GOBERNADO_AUSENTE")
    assert ausente["simbolo"] == "V4ProposalGenerator._generate_dynamic_services_table"
    # Y sale por CLI con exit 1, no como advertencia.
    assert _correr("--root", str(tmp_path), "--ignore-known").returncode == 1


# ------------------------------------------------- AC7 sobre la divergencia real de hoy
def test_el_rojo_de_ac7_llega_a_la_divergencia_vigente_en_el_repo(        reporte_repo_sin_excepciones, reporte_repo):
    """El verificador debe poder nombrar la divergencia F-A' tal como esta hoy.

    Si en el codigo actual saliera verde, la cobertura del verificador estaria mal, no el
    producto. Medido: `V4AssetOrchestrator.generate_assets` omite la senal en TRES
    invocaciones (una a `detect_pains`, dos a `validate`), no en una como decia el plan.
    """
    reporte = reporte_repo_sin_excepciones
    hallazgos = [v for v in reporte["violaciones"] if v["tipo"] == "SENAL_OMITIDA"]
    del_orquestador = [h for h in hallazgos
                       if h["archivo"] == "modules/asset_generation/v4_asset_orchestrator.py"]
    assert len(del_orquestador) == 3, [h["linea"] for h in del_orquestador]
    simbolos = sorted(h["simbolo"] for h in del_orquestador)
    assert simbolos == ["CoherenceValidator.validate", "CoherenceValidator.validate",
                        "PainSolutionMapper.detect_pains"]
    for h in del_orquestador:
        assert "whatsapp_html_detected" in h["detalle"]
    # Y estan publicados con dueno y condicion de baja, no silenciados.
    amparadas = {a["linea_amparada"]: a for a in
                 reporte_repo["excepciones_aplicadas"]}
    for h in del_orquestador:
        assert h["linea"] in amparadas, f"halla {h['linea']} sin excepcion registrada"
        assert amparadas[h["linea"]]["dueno"] == "FASE-B"
        assert amparadas[h["linea"]]["ac"] == "AC1"


def test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion(reporte_repo):
    """El hueco declarado tiene que ser cero en produccion: alla es donde una senal se esconde.

    Un ✅ del check no prueba ausencia de callers invisibles (limite declarado). Lo que si
    puede probarse es que ningun caller **productivo** quedo sin resolver.
    """
    reporte = reporte_repo
    assert reporte["cobertura"]["receptores_no_resueltos_en_produccion"] == 0, [
        (r["archivo"], r["linea"], r["receptor"]) for r in reporte["poblacion"]
        if r["clasificacion"] == "RECEPTOR_NO_RESUELTO" and not r["en_tests"]]
    assert reporte["cobertura"]["gobernadas_resueltas"] > 0


# ---------------------------------------------------------------- serializacion (R2.4)
def test_el_reporte_escrito_por_el_writer_es_legible_y_lleva_la_cobertura(tmp_path,                                                                         reporte_repo):
    """R2.4: un AC que no es legible en el artefacto es ⚠️, no ✅.

    Se lee el JSON que escribio el writer real, no el objeto en memoria, y se exige que la
    cuenta de poblacion del archivo coincida con la del calculo fresco.
    """
    destino = tmp_path / "wiring_report.json"
    vw.publicar(reporte_repo, destino)

    leido = json.loads(destino.read_text(encoding="utf-8"))
    assert leido["schema_version"] == vw.SCHEMA_VERSION
    assert leido["git_sha"]
    for clave in ("politica", "cobertura", "poblacion", "violaciones",
                  "excepciones_aplicadas", "limites"):
        assert clave in leido, f"el artefacto no publica `{clave}`"
    assert leido["cobertura"]["llamadas_descubiertas"] == len(leido["poblacion"])
    assert len(leido["limites"]) >= 4, "el verificador no declara que es lo que no ve"
    assert all("senales_requeridas" in v for v in leido["politica"].values())


def test_los_tres_estados_del_lector_de_reporte(tmp_path, reporte_repo):
    """R2.9: ausente, ilegible y conforme son tres estados y no dos con un default."""
    destino = tmp_path / "informe.json"

    def leer(ruta: Path) -> str:
        if not ruta.exists():
            return "ABSENT"
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return "READ_ERROR"
        return "READ_OK" if datos.get("poblacion") is not None else "READ_ERROR"

    assert leer(destino) == "ABSENT"
    destino.write_text("{ no es json", encoding="utf-8")
    assert leer(destino) == "READ_ERROR"
    vw.publicar(reporte_repo, destino)
    assert leer(destino) == "READ_OK"


# ------------------------------------------------------------------------------- CLI (AC15)
def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def test_exit_codes_del_cli():
    """0 conforme, 1 violaciones, 2 arbol inexistente. Un 2 no puede leerse como verde."""
    ok = _correr("--root", str(ROOT))
    assert ok.returncode == 0, ok.stdout + ok.stderr

    rojo = _correr("--root", str(ROOT), "--ignore-known")
    assert rojo.returncode == 1
    assert "SENAL_OMITIDA" in rojo.stdout

    malo = _correr("--root", str(Path(__file__).parent / "no-existe-esta-ruta"))
    assert malo.returncode == 2
    assert "no existe el arbol" in malo.stdout


def test_el_rojo_nombra_archivo_y_senal_para_que_sea_reparable(tmp_path):
    """Un rojo que no dice donde ni porque no es un guard, es ruido."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "culpable.py": (
            "from .productores import CoherenceValidator\n"
            "CoherenceValidator().validate(d, p, a, s)\n"
        ),
    })
    salida = _correr("--root", str(tmp_path), "--ignore-known")
    assert salida.returncode == 1
    assert "modules/culpable.py" in salida.stdout
    assert "whatsapp_html_detected" in salida.stdout
    assert "AC7" in salida.stdout


def test_el_verificador_no_reescribe_nada(tmp_path):
    """Doctrina del repo: reporta, no auto-arregla. Un fix automatico pondria el kwarg y el verde sin entender el defecto."""
    _arbol(tmp_path, {
        "productores.py": PRODUCTORES,
        "culpable.py": (
            "from .productores import PainSolutionMapper\n"
            "PainSolutionMapper().detect_pains(a, s, x)\n"
        ),
    })
    antes = {p: p.read_text(encoding="utf-8") for p in tmp_path.rglob("*.py")}
    _correr("--root", str(tmp_path), "--ignore-known")
    despues = {p: p.read_text(encoding="utf-8") for p in tmp_path.rglob("*.py")}
    assert antes == despues
