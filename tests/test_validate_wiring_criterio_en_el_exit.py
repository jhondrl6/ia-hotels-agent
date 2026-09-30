"""Paso 2: el verificador de cableado codifica su clausula de produccion en el EXIT.

QUE SE CURA (parte evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/
    04-reinvestigacion-alerta-wiring-2026-09-30.md, seccion 4)
    Con la clausula de produccion rota, `python scripts/validate_wiring.py --quiet` sale **EXIT 0**:
    `RECEPTOR_NO_RESUELTO` «se cuenta y publica» pero nunca se mira al decidir el codigo. Medido con
    los 5 receptores del aislado todavia en poblacion: verificador 0, `run_all_validations.py --quick`
    [11/13] en verde, y la suite roja. O sea la cola puede dar 13/13 mientras la clausula que se
    supone que protege esta rota, y el unico diente vivia en
    `tests/test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`.
    La cura no es un diente nuevo: es que el **mismo** diente se codifique en el exit code.

EL CRITERIO, DEFINIDO AQUI ANTES QUE EN EL CODIGO
    Rojo:  un `RECEPTOR_NO_RESUELTO` **fuera** de `tests/` (alla es donde una senal se puede
           esconder), y una poblacion gobernada **vacia** (`gobernadas_resueltas == 0`), que es el
           verde vacio de la misma clausula: sin un solo caller resuelto, «cero huecos» no afirma
           nada.
    Registro, no rojo: `TEST_EXENTO_DE_SENAL` y `RECEPTOR_NO_RESUELTO` **bajo** `tests/`. Un test
           que ejerce el default lo hace a proposito, y un hueco bajo `tests/` solo puede esconder
           un test, no un caller real. Los dos siguen publicados en `cobertura` y en `poblacion`.
    El contrato de codigos del CLI no se mueve: 0 conforme, 1 hallazgos, 2 error de uso o lector
           fallido. Lo que cambia es **que** entra en «hallazgos».

ANCLAJE (revision publicada y fija, nunca HEAD)
    `abd181c` es la revision que YA tiene la cura de alcance (paso 1, salida (c)) y TODAVIA NO tiene
    este criterio. El control negativo lee esa copia con `git show` y la **ejecuta** contra el mismo
    arbol sintetico que al curado lo hace rojo: si el verde falso lo inventara una parodia escrita
    aqui, no probaria nada.

LO QUE ESTE ARCHIVO NO AFIRMA
    Que `.opencode/wiring_report.json` este fresco ni tenga `--check`: eso es el paso 3 de la orden.
    Tampoco toca `scripts/decision_client.py` (prohibido en esta tanda).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_wiring.py"

REV_SIN_CRITERIO = "abd181c"          # tiene la cura de alcance, no tiene este criterio
TOKEN_ALCANCE = "--exclude-" + "standard"
TIPO_HUECO = "HUECO_DE_COBERTURA_EN_PRODUCCION"
TIPO_VACIO = "VERDE_VACIO_SIN_GOBERNADOS_RESUELTOS"

_spec = importlib.util.spec_from_file_location("validate_wiring_criterio", SCRIPT)
vw = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(vw)

# Las cuatro clases de la politica, enteras: si el fixture define solo una, los tres simbolos que
# faltan emiten `SIMBOLO_GOBERNADO_AUSENTE` y el exit 1 llegaria por un motivo distinto del que se
# quiere medir (misma razon que en `test_validate_wiring_alcance_por_declaracion_git.py`).
PRODUCTORES = '''
class PainSolutionMapper:
    def detect_pains(self, audit_result, validation_summary, analytics_data=None,
                     whatsapp_html_detected=False):
        return []


class CoherenceValidator:
    def validate(self, diagnostic, proposal, assets, validation_summary,
                 whatsapp_html_detected=False):
        return None


class AssessmentBuilder:
    def with_validation(self, validation_summary):
        return self


class V4ProposalGenerator:
    def _generate_dynamic_services_table(self, site_presence_report=None,
                                         whatsapp_conflict=False):
        return ""
'''

CONFORME = (
    "from .productores import PainSolutionMapper\n"
    "mapper = PainSolutionMapper()\n"
    "mapper.detect_pains(audit, summary, analytics, whatsapp_html_detected=html)\n"
)

# Receptor cuyo tipo el AST no deduce (parametro sin anotacion, sin binding en el ambito): eso es
# exactamente lo que publica `RECEPTOR_NO_RESUELTO`.
SIN_RESOLVER = (
    "def correr(cosa):\n"
    "    return cosa.detect_pains(a, s, x)\n"
)

OMISION_BAJO_TESTS = (
    "from ..modules.productores import PainSolutionMapper\n"
    "PainSolutionMapper().detect_pains(a, s, x)\n"
)

# --------------------------------------------------------------------------- fixtures de arbol


def _arbol(base: Path, archivos: dict[str, str]) -> Path:
    """Escribe rutas relativas arbitrarias: hace falta un `tests/` sintetico ademas de `modules/`."""
    for rel, codigo in archivos.items():
        destino = base / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(codigo, encoding="utf-8", newline="\n")
    return base


def _con_productores(**extra: str) -> dict[str, str]:
    """Todo arbol lleva los cuatro productores y un caller gobernado conforme.

    Sin `modules/conforme.py` la mitad de los casos caeria en `gobernadas_resueltas == 0` y el rojo
    llegaria por la clausula del verde vacio, no por la que se esta afirmando.
    """
    base = {"modules/productores.py": PRODUCTORES, "modules/conforme.py": CONFORME}
    base.update(extra)
    return base


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def _correr_silencioso(instrumento: Path, raiz: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(instrumento), "--root", str(raiz), "--quiet"],
                          capture_output=True, text=True)


def _correr_instrumento(instrumento: Path, *args: str) -> subprocess.CompletedProcess:
    """Ejecuta una copia del instrumento leida del historial, no una re-implementacion."""
    return subprocess.run([sys.executable, str(instrumento), *args],
                          capture_output=True, text=True)


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT), capture_output=True,
    ).returncode == 0


def _fuente_versionada(destino: Path, rev: str, rel: str) -> Path:
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, f"no se pudo leer {rel} en {rev}: {proc.stderr[:200]}"
    ruta = destino / Path(rel).name
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(proc.stdout, encoding="utf-8", newline="\n")
    return ruta


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    anterior = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = anterior
    return mod


# ---------------------------------------------------------------------- el EXIT, que es la cura


def test_la_clausula_de_produccion_rota_ya_no_sale_con_exit_cero(tmp_path):
    """El defecto de la seccion 4, en el sentido contrario: clausula rota => EXIT 1 y rojo impreso.

    El arbol sintetico tiene un `RECEPTOR_NO_RESUELTO` fuera de `tests/` y **cero** violaciones de
    cableado, asi que lo unico que puede levantar el exit 1 es la clausula de produccion.
    """
    base = _arbol(tmp_path / "roto", _con_productores(**{"modules/ajeno.py": SIN_RESOLVER}))
    reporte = vw.construir_reporte(base, ignore_known=True)
    assert reporte["cobertura"]["receptores_no_resueltos_en_produccion"] == 1, (
        "premissa del caso: el fixture dejo de producir un hueco de cobertura en produccion")
    assert [v["tipo"] for v in reporte["violaciones"] if v["tipo"] != TIPO_HUECO] == [], (
        "el fixture also tiene una violacion de cableado: el exit 1 no seria atribuible al criterio")

    corrido = _correr("--root", str(base))
    assert corrido.returncode == 1, corrido.stdout + corrido.stderr
    assert TIPO_HUECO in corrido.stdout, corrido.stdout
    assert "modules/ajeno.py" in corrido.stdout, corrido.stdout


def test_el_hallazgo_del_criterio_es_legible_en_el_artefacto_publicado(tmp_path):
    """R2.4: una clausula que no se lee en el artefacto es advertencia, no guard.

    Se lee el JSON que escribio el writer real (`publicar`), no el objeto en memoria, y el hallazgo
    tiene que nombrar archivo, linea y receptor: un rojo sin coordenadas no es reparable.
    """
    base = _arbol(tmp_path / "artefacto", _con_productores(**{"modules/ajeno.py": SIN_RESOLVER}))
    destino = tmp_path / "wiring_report.json"
    vw.publicar(vw.construir_reporte(base, ignore_known=True), destino)

    leido = json.loads(destino.read_text(encoding="utf-8"))
    huecos = [v for v in leido["violaciones"] if v["tipo"] == TIPO_HUECO]
    assert len(huecos) == 1, leido["violaciones"]
    hallazgo = huecos[0]
    assert hallazgo["archivo"] == "modules/ajeno.py"
    assert hallazgo["linea"] >= 1
    assert hallazgo["receptor"] == "cosa", hallazgo
    assert hallazgo["fuente_politica"], "el hallazgo no dice que clausula lo produj"
    assert leido["cobertura"]["receptores_no_resueltos_en_produccion"] == len(huecos), (
        "el conteo publicado y el numero de hallazgos del criterio son dos cifras distintas")


def test_un_receptor_no_resuelto_bajo_tests_es_registro_y_no_rojo(tmp_path):
    """La mitad negativa del criterio: el hueco bajo `tests/` se publica, no castiga.

    Sin esta prueba bastaria con hacer rojo `receptores_no_resueltos > 0` (sin cortar por `en_tests`)
    para dar verde en los dos casos de arriba, y el quick se llenaria de rojos de suite ajenos al
    contrato.
    """
    base = _arbol(tmp_path / "registro", _con_productores(**{"tests/test_ajeno.py": SIN_RESOLVER}))
    reporte = vw.construir_reporte(base, ignore_known=True)
    assert reporte["cobertura"]["receptores_no_resueltos"] == 1, reporte["cobertura"]
    assert reporte["cobertura"]["receptores_no_resueltos_en_produccion"] == 0

    corrido = _correr("--root", str(base))
    assert corrido.returncode == 0, corrido.stdout + corrido.stderr
    assert any("RECEPTOR_NO_RESUELTO" in l for l in reporte["limites"]), (
        "el hueco bajo tests/ dejo de declararse como limite del instrumento")


def test_un_test_exento_de_senal_es_registro_y_no_rojo(tmp_path):
    """`TEST_EXENTO_DE_SENAL` no es hallazgo: un test que ejercita el default lo hace a proposito.

    El mismo caller, sin la senal, es rojo en `modules/` y registro en `tests/`. Las dos mitades
    estan en el mismo arbol para que la diferencia se atribuya a `en_tests` y a nada mas.
    """
    base = _arbol(tmp_path / "exento", _con_productores(**{"tests/test_default.py": OMISION_BAJO_TESTS}))
    reporte = vw.construir_reporte(base, ignore_known=True)
    tipos = {r["clasificacion"] for r in reporte["poblacion"]}
    assert "TEST_EXENTO_DE_SENAL" in tipos, sorted(tipos)
    assert reporte["cobertura"]["por_clasificacion"]["TEST_EXENTO_DE_SENAL"] == 1
    assert reporte["violaciones"] == [], reporte["violaciones"]

    corrido = _correr("--root", str(base))
    assert corrido.returncode == 0, corrido.stdout + corrido.stderr

    # Y su espejo: la misma omision fuera de tests/ si es roja por cableado.
    base2 = _arbol(tmp_path / "no_exento",
                   _con_productores(**{"modules/default.py": OMISION_BAJO_TESTS}))
    assert _correr("--root", str(base2)).returncode == 1


def test_la_poblacion_gobernada_vacia_tambien_es_rojo(tmp_path):
    """La segunda mitad del diente (`gobernadas_resueltas > 0`): sin caller resuelto, cero huecos no afirma nada.

    El arbol define los cuatro productores y no llama a ninguno: no hay hueco de cobertura y no hay
    violacion de cableado, asi que el exit 1 solo puede venir del verde vacio.
    """
    base = _arbol(tmp_path / "vacio", {"modules/productores.py": PRODUCTORES})
    reporte = vw.construir_reporte(base, ignore_known=True)
    assert reporte["cobertura"]["gobernadas_resueltas"] == 0
    assert reporte["cobertura"]["receptores_no_resueltos_en_produccion"] == 0
    assert reporte["violaciones"] == [] or all(
        v["tipo"] == TIPO_VACIO for v in reporte["violaciones"]), reporte["violaciones"]

    corrido = _correr("--root", str(base))
    assert corrido.returncode == 1, corrido.stdout + corrido.stderr
    assert TIPO_VACIO in corrido.stdout, corrido.stdout


def test_el_contrato_de_codigos_del_cli_sigue_intacto(tmp_path):
    """0 conforme, 1 hallazgos, 2 error de uso o lector fallido: el criterio no anade codigos.

    Se afirma aqui porque la clausula se codifica **dentro** del exit 1 existente; si alguien la
    moviera a un 3 propio, `run_all_validations.py` la leeria como LECTOR-FALLIDO o como verde.
    """
    conforme = _arbol(tmp_path / "ok", _con_productores())
    assert _correr("--root", str(conforme)).returncode == 0

    culpable = _arbol(tmp_path / "omision", _con_productores(**{
        "modules/olvidadizo.py": (
            "from .productores import PainSolutionMapper\n"
            "PainSolutionMapper().detect_pains(a, s, x)\n"
        )}))
    rojo = _correr("--root", str(culpable))
    assert rojo.returncode == 1
    assert "SENAL_OMITIDA" in rojo.stdout

    assert _correr("--root", str(tmp_path / "no-existe")).returncode == 2


# ------------------------------------------------------------- control negativo y dientes


def test_control_negativo_el_script_versionado_de_abd181c_daba_verde_con_esto_roto(tmp_path):
    """El mismo arbol, medido con el instrumento de `abd181c`: EXIT 0 con la clausula rota.

    `abd181c` es la cura del paso 1, asi que **si** trae la capa de alcance y **no** trae este
    criterio; la premissa se comprueba en la fuente leida con `git show` antes de ejecutarla, porque
    un control que ya no es anterior a la cura no prueba nada.
    """
    assert _rev_existe(REV_SIN_CRITERIO), f"la revision {REV_SIN_CRITERIO} no esta en el repo"
    viejo = _fuente_versionada(tmp_path / "instrumento-viejo", REV_SIN_CRITERIO,
                               "scripts/validate_wiring.py")
    fuente = viejo.read_text(encoding="utf-8")

    assert TOKEN_ALCANCE in fuente, (
        f"{REV_SIN_CRITERIO} ya no consulta la declaracion de Git: la revision anclada dejo de ser "
        "la del paso 1 y el control ya no prueba la secuencia")
    assert TIPO_HUECO not in fuente and TIPO_VACIO not in fuente, (
        f"{REV_SIN_CRITERIO} ya codifica el criterio en el EXIT: el control dejo de ser anterior "
        "a esta cura")

    base = _arbol(tmp_path / "arbol-control", _con_productores(**{"modules/ajeno.py": SIN_RESOLVER}))
    curado = _correr("--root", str(base))
    viejo_corrido = _correr_instrumento(viejo, "--root", str(base))

    assert curado.returncode == 1, curado.stdout
    assert viejo_corrido.returncode == 0, (
        "el instrumento versionado ya no da verde con la clausula rota: o el fixture perdio su "
        "hueco, o la revision anclada ya tenia la cura. En ambos casos esta prueba esta vacia")
    assert "receptores no resueltos 1" in viejo_corrido.stdout, viejo_corrido.stdout
    assert TIPO_HUECO not in viejo_corrido.stdout, viejo_corrido.stdout


def test_dientes_si_se_apaga_el_criterio_vuelve_el_verde_falso(tmp_path):
    """Mutante: se desactiva SOLO la llamada al criterio y la clausula vuelve a estar muda.

    Prueba que el exit 1 de arriba lo produce el criterio y no una coincidencia de la poblacion: el
    ancla tiene que ser unica, y el mutante se verifica **ejecutandolo**, no leyendo su fuente.
    """
    fuente = SCRIPT.read_text(encoding="utf-8")
    ancla = 'abiertas.extend(_hallazgos_del_criterio(cobertura, datos["poblacion"]))'
    assert fuente.count(ancla) == 1, (
        f"el ancla del mutante aparece {fuente.count(ancla)} veces: el criterio se escribio con "
        "otra forma y el mutante no apaga lo que se cree que apaga")
    mutado = fuente.replace(ancla, "abiertas.extend([])  # MUTADO-SIN-CRITERIO", 1)
    assert mutado != fuente and "MUTADO-SIN-CRITERIO" in mutado
    assert "_hallazgos_del_criterio" in mutado, (
        "el mutante borro la definicion, no la llamada: apaga tambien la clausula del verde vacio "
        "por un camino que no es el que se quiere probar")
    ast.parse(mutado)  # un mutante con SyntaxError da rojos que no miden nada

    copia = tmp_path / "validate_wiring_mutado.py"
    copia.write_text(mutado, encoding="utf-8", newline="\n")
    mod = _cargar("validate_wiring_mutado", copia)

    base = _arbol(tmp_path / "arbol-mutante", _con_productores(**{"modules/ajeno.py": SIN_RESOLVER}))
    reporte = mod.construir_reporte(base, ignore_known=True)
    assert reporte["cobertura"]["receptores_no_resueltos_en_produccion"] == 1, (
        "premissa: el arbol del mutante tiene el hueco y el mutante no lo esta viendo por otro lado")
    assert reporte["violaciones"] == [], (
        "el mutante apago el criterio pero sigue saliendo un hallazgo: el rojo no venia del criterio")
    assert _correr_silencioso(copia, base).returncode == 0, (
        "con el criterio apagado el CLI sigue rojo: el exit 1 no lo produce el criterio")

    vacio = _arbol(tmp_path / "arbol-vacio-mutado", {"modules/productores.py": PRODUCTORES})
    assert mod.construir_reporte(vacio, ignore_known=True)["violaciones"] == []
