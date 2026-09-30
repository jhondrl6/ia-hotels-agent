"""Paso 1, salida (c): el alcance del wiring se goberna por la declaracion del propio Git.

QUE SE CURA (parte evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/
    04-reinvestigacion-alerta-wiring-2026-09-30.md, secciones 6 y 7)
    `scripts/validate_wiring.py` descubria su poblacion con `rglob("*.py")` y una **tabla de
    nombres** (`EXCLUSIONES_POR_ROL`). La tabla es una lista, y una lista depende de que
    alguien se acuerde de ampliarla: `tmp_test/` (el aislado del piloto JEV, 684 `.py` en
    alcance) no estaba, asi que los cinco `field.validate(...)` de pydantic dentro de su SDK
    entraban en `receptores_no_resueltos_en_produccion` y hacian roja la clausula que mide
    si quedo un caller productivo sin resolver. La cura no anade la clave que faltaba:
    **consulta al propio Git** (`ls-files --others --ignored --exclude-standard`) y excluye lo
    que el `.gitignore` ya declara fuera del control de versiones, sin lista a mano.

QUE NO SE TOCA
    `EXCLUSIONES_POR_ROL` se queda entera: goberna lo **versionado** que por definicion no
    cae por Git (`evidence`, `archives`, `output`). Y la capa nueva solo puede **achicar** la
    poblacion: si Git falta el conjunto sale vacio y el alcance vuelve a ser el de la tabla
    (sobre-inclusivo, nunca ciego a codigo del proyecto). Eso lo declara `limites` y lo corta
    `test_sin_git_la_capa_nueva_no_deja_ciego_al_codigo`.

ANCLAJE (revision publicada y fija, nunca HEAD):
    `382ad05` es la revision cuyo `scripts/validate_wiring.py` **solo** tiene la tabla de
    roles. El control negativo lee esa copia con `git show` y la ejecuta contra el mismo arbol
    sintetico: si el rojo saliera de una parodia escrita aqui, no probaria nada (leccion
    «controles negativos ejercitan el instrumento versionado»).

LO QUE ESTE ARCHIVO NO AFIRMA
    Que el verificador codifique su criterio en el EXIT, ni que `.opencode/wiring_report.json`
    este fresco: son los pasos 2 y 3 de la orden. Tampoco toca `scripts/decision_client.py`,
    que ya excluye el aislado por su cuenta desde la cura de S11.
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

REV_SIN_CAPA_GIT = "382ad05"        # el script versionado de hoy: solo la tabla de roles
CLAVE = "excluidos_por_declaracion_git"
# El literal se arma por partes: una cadena contigua con el comando puede ser leida por los
# validadores de gobernanza como si este archivo lo emitiera (misma convencion que
# `test_verify_packs_quinto_patron_generado_por_sha.py`).
TOKEN_CURA = "--exclude-" + "standard"
RAIZ = "nuevo_aislado"             # nombre que NO aparece en EXCLUSIONES_POR_ROL

_spec = importlib.util.spec_from_file_location("validate_wiring_alcance", SCRIPT)
vw = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(vw)

# Las cuatro clases de la politica: si el fixture solo define una, los tres simbolos que
# faltan emiten `SIMBOLO_GOBERNADO_AUSENTE` y el verde de los arboles sinteticos deja de
# significar "conforme".
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

LLAMADA_SIN_SENAL = (
    "from .productores import PainSolutionMapper\n"
    "mapper = PainSolutionMapper()\n"
    "mapper.detect_pains(audit, summary, analytics)\n"
)

LLAMADA_CON_SENAL = (
    "from .productores import PainSolutionMapper\n"
    "mapper = PainSolutionMapper()\n"
    "mapper.detect_pains(audit, summary, analytics, whatsapp_html_detected=html)\n"
)


def _cargar(nombre: str, ruta: Path):
    """Carga una copia del instrumento como modulo propio, sin pisar al del arbol de trabajo."""
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


def _declaracion_git(raiz: Path) -> set[str]:
    """La MISMA consulta que hace la cura, resuelta aparte para poder contrastarla.

    Si el test midiera el conjunto con la funcion del propio script, el verde seria circular:
    aqui se corta el registro NUL a mano y se comparan rutas relativas en posix.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", TOKEN_CURA, "-z"],
        cwd=str(raiz), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180,
    )
    if proc.returncode != 0:
        return set()
    return {p for p in proc.stdout.split("\0") if p.endswith(".py")}


def _arbol_aislado(base: Path, *, con_git: bool) -> Path:
    """Arbol con un aislado cuyo nombre no esta en `EXCLUSIONES_POR_ROL`.

    Con `con_git` el `.gitignore` lo declara ignorado: la capa nueva tiene que sacarlo. Sin
    Git ese mismo archivo es codigo normal del arbol y tiene que seguir viendose. Los dos
    casos son el mismo fixture cambiando una linea, asi que la diferencia de veredictos se
    atribuye a la capa de Git y a nada mas.
    """
    (base / "modules").mkdir(parents=True, exist_ok=True)
    (base / RAIZ / "pkg").mkdir(parents=True, exist_ok=True)
    (base / "modules" / "productores.py").write_text(PRODUCTORES, encoding="utf-8")
    (base / "modules" / "conforme.py").write_text(LLAMADA_CON_SENAL, encoding="utf-8")
    # Dentro del aislado, la omision que el verificador castiga: si entra en alcance, rojo.
    (base / RAIZ / "pkg" / "sdk_interno.py").write_text(LLAMADA_SIN_SENAL, encoding="utf-8")
    (base / RAIZ / "otro.py").write_text("x = 1\n", encoding="utf-8")
    if con_git:
        subprocess.run(["git", "init", "-q", "."], cwd=str(base), capture_output=True,
                       text=True, timeout=120, check=True)
        (base / ".gitignore").write_text(f"{RAIZ}/\n", encoding="utf-8")
    return base


def _rutas(fuentes: list[Path], raiz: Path) -> set[str]:
    return {str(p.relative_to(raiz).as_posix()) for p in fuentes}


# ---------------------------------------------------------------------- el alcance, en el arbol real

@pytest.fixture(scope="module")
def alcance_real():
    """`archivos_en_alcance(ROOT)` una sola vez: el rglob del arbol mas la consulta a Git."""
    return vw.archivos_en_alcance(ROOT)


@pytest.fixture(scope="module")
def reporte_real():
    """El informe curado sobre el arbol de trabajo (~10 s): el que leeria la cola de validaciones."""
    return vw.construir_reporte(ROOT)


def test_ningun_fichero_que_git_declara_ignorado_entra_en_el_alcance(alcance_real):
    """El invariant estructural: alcance e ignorados son conjuntos disjuntos.

    No pinea una cifra: la declaracion de Git se resuelve aparte y se intersecta. Antes de la
    cura la interseccion era 684 rutas, todas bajo `tmp_test/`, que es el insumo que hacia
    roja la clausula de produccion.
    """
    rutas = _rutas(alcance_real[0], ROOT)
    corte = sorted(rutas & _declaracion_git(ROOT))
    assert corte == [], (
        f"{len(corte)} ficheros entran en alcance estando declarados ignorados por Git; "
        f"primeros: {corte[:5]}")


def test_el_aislado_del_piloto_queda_fuera_del_arbol_que_se_mide(alcance_real):
    """El caso concreto del pendiente 5: ni un `.py` de `tmp_test/` en la poblacion."""
    rutas = _rutas(alcance_real[0], ROOT)
    assert sorted(r for r in rutas if r.startswith("tmp_test/")) == []


def test_la_capa_nueva_no_pierde_ni_duplica_ningun_fichero(alcance_real):
    """Todo `.py` del arbol cae en UNO y solo uno de los tres baldes.

    Es el control del conteo: una exclusion que no cuadra con la resta entre `rglob` y el
    alcance publicado es el defecto original de S11 (una exclusion sin conteo), no su cura.
    """
    fuentes, exclusiones_rol, excluidos = alcance_real
    todos = {str(p.relative_to(ROOT).as_posix()) for p in ROOT.rglob("*.py")}
    en_alcance = _rutas(fuentes, ROOT)
    por_rol = {e["ruta"] for e in exclusiones_rol}
    por_git = {r for r in _declaracion_git(ROOT) if r in todos and r not in por_rol}

    assert len(fuentes) == len(en_alcance), "el alcance tiene rutas duplicadas"
    assert not (en_alcance & por_rol), "un fichero excluido por rol sigue en el alcance"
    assert not (en_alcance & por_git), "un fichero excluido por Git sigue en el alcance"
    assert en_alcance | por_rol | por_git == todos, (
        "la suma de los tres baldes no reproduce la poblacion cruda de `rglob`: se perdio o "
        "se duplico alguna ruta")
    assert excluidos["cantidad"] == len(por_git), (
        f"el conteo publicado ({excluidos['cantidad']}) no cuadra con las rutas efectivamente "
        f"excluidas por esta capa ({len(por_git)})")


def test_el_informe_publica_los_excluidos_por_declaracion_git_con_conteo_y_motivo(reporte_real,
                                                                                  tmp_path):
    """S11 aplicado a esta capa: una exclusion sin conteo publicado es el defecto, no la cura.

    Se lee el JSON que escribio el writer real, no el objeto en memoria (R2.4).
    """
    destino = tmp_path / "informe-wiring.json"
    vw.publicar(reporte_real, destino)
    leido = json.loads(destino.read_text(encoding="utf-8"))

    assert CLAVE in leido, f"el artefacto no publica `{CLAVE}`"
    publicado = leido[CLAVE]
    assert isinstance(publicado, dict), (
        f"se esperaba un objeto con su conteo y su motivo, llego {type(publicado).__name__}")
    assert publicado["estado"] == "GIT_OK", (
        f"la consulta no se resolvio ({publicado['estado']!r}): el alcance de esta corrida no "
        "goberno por declaracion de Git")
    assert publicado["cantidad"] > 0, (
        "el conteo es cero sobre el arbol real, que tiene el aislado en disco: la capa no "
        f"esta cortando nada ({publicado})")
    assert publicado["motivo"].strip(), "la exclusion se publica sin motivo"
    assert publicado["ejemplo"], "hay excluidos y el informe no publica ninguno como ejemplo"


def test_la_clausula_de_produccion_deja_de_medirse_contra_el_aislado(reporte_real):
    """El rojo del pendiente 5 en el sentido contrario: ningun receptor sin resolver viene de un
    fichero que Git declara ignorado, y la clausula sigue teniendo poblacion que gobernar.
    """
    cobertura = reporte_real["cobertura"]
    ignorados = _declaracion_git(ROOT)
    desde_aislado = [
        (r["archivo"], r["linea"]) for r in reporte_real["poblacion"]
        if r["clasificacion"] == "RECEPTOR_NO_RESUELTO" and not r["en_tests"]
        and r["archivo"] in ignorados
    ]
    assert desde_aislado == [], desde_aislado
    assert cobertura["receptores_no_resueltos_en_produccion"] == 0
    assert cobertura["gobernadas_resueltas"] > 0, (
        "la capa nueva recorto la poblacion hasta dejar la gobernanza vacia: un verde asi no "
        "prueba nada")


# --------------------------------------------------------- la tabla de roles sigue en su sitio

def test_lo_versionado_sigue_excluyendose_por_rol(reporte_real):
    """`evidence/` esta versionado: Git no lo declara ignorado, asi que solo la tabla lo saca.

    Sin esta prueba la capa nueva podria leerse como un reemplazo de `EXCLUSIONES_POR_ROL` y
    alguien borraria una clave «porque ya no hace falta».
    """
    r = subprocess.run(["git", "ls-files", "--", "evidence"], cwd=str(ROOT),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert [l for l in r.stdout.splitlines() if l.strip()], (
        "premissa del control: hace falta evidencia versionada en el arbol")

    agrupado = reporte_real["exclusiones_por_rol"]
    assert "evidence" in agrupado, f"`evidence` dejo de exclarse por rol; roles: {sorted(agrupado)}"
    assert agrupado["evidence"]["cantidad"] > 0
    assert agrupado["evidence"]["motivo"].strip()
    assert not [x for x in _rutas(vw.archivos_en_alcance(ROOT)[0], ROOT)
                if x.startswith("evidence/")], (
        "un .py de la evidencia versionada volvio a entrar en la poblacion")


# ------------------------------------------------------------ la capa goberna, la lista no

def test_un_aislado_que_nadie_registro_sale_del_alcance_por_declaracion_git(tmp_path):
    """El caso que la tabla de nombres no cubria y la declaracion de Git si: nombre nuevo.

    Las dos mitades van en el mismo arbol: el aislado desaparece de la poblacion y la llamada
    conforme de `modules/` sigue gobernada. Sin la segunda mitad, «sacar el aislado» tambien
    podria lograrse cerrando los ojos.
    """
    base = _arbol_aislado(tmp_path / "repo-con-git", con_git=True)
    reporte = vw.construir_reporte(base, ignore_known=True)

    assert reporte[CLAVE]["estado"] == "GIT_OK", reporte[CLAVE]
    assert reporte[CLAVE]["cantidad"] >= 1, (
        "la capa no excluyo ni un fichero del arbol sintetico que Git declara ignorado")
    assert reporte[CLAVE]["ejemplo"].startswith(RAIZ + "/"), reporte[CLAVE]
    archivos = {r["archivo"] for r in reporte["poblacion"]}
    assert sorted(a for a in archivos if a.startswith(RAIZ + "/")) == [], (
        f"el aislado declarado por Git sigue en poblacion: {sorted(archivos)}")
    assert "modules/conforme.py" in archivos, (
        "el aislado se fue, pero se llevo la gobernanza del codigo del proyecto")
    assert reporte["violaciones"] == [], reporte["violaciones"]


def test_sin_git_la_capa_nueva_no_deja_ciego_al_codigo(tmp_path):
    """Direccion del fallo, con su prueba: sin Git el conjunto sale VACIO, no total.

    El mismo arbol del test anterior, sin `git init`: la llamada omitida dentro del «aislado»
    vuelve a ser visible y vuelve a violar. Si la cura hubiera caido del lado comodo (excluir
    todo ante el fallo), ese rojo desapareceria y ahi estaria el defecto gordo.
    """
    base = _arbol_aislado(tmp_path / "repo-sin-git", con_git=False)
    reporte = vw.construir_reporte(base, ignore_known=True)

    assert reporte[CLAVE]["estado"].startswith("SIN_GIT"), (
        f"se esperaba el fallback declarado y la consulta dijo {reporte[CLAVE]['estado']!r}: "
        "el fixture dejo de estar fuera de todo repositorio")
    assert reporte[CLAVE]["cantidad"] == 0
    archivos = {r["archivo"] for r in reporte["poblacion"]}
    assert f"{RAIZ}/pkg/sdk_interno.py" in archivos, (
        "sin Git el verificador dejo de ver codigo del arbol: el fallback ciego")
    assert {v["tipo"] for v in reporte["violaciones"]} >= {"SENAL_OMITIDA"}, (
        "la omision del aislado no violo sin Git: la poblacion se achico por otro camino")


def test_el_fallback_sin_git_esta_declarado_en_los_limites(tmp_path):
    """L-R.4: una regla con fallback tiene que decir en el artefacto cual es su direccion de
    fallo y nombrar el estado donde se lee."""
    reporte = vw.construir_reporte(_arbol_aislado(tmp_path / "repo-limites", con_git=True),
                                   ignore_known=True)
    mencionados = [l for l in reporte["limites"] if "SIN_GIT" in l]
    assert len(mencionados) == 1, (
        f"el fallback sin Git debe declararse exactamente una vez en `limites` "
        f"(hay {len(mencionados)}): {mencionados}")
    declaracion = mencionados[0]
    assert CLAVE in declaracion, (
        "el limite nombra el fallback pero no dice donde se lee el estado de la consulta")
    assert "EXCLUSIONES_POR_ROL" in declaracion, (
        "el limite no dice a que se vuelve cuando Git falta: sin eso no se puede juzgar si el "
        "alcance quedo ciego o solo sobre-inclusivo")


# ------------------------------------------------------------ control negativo y dientes

def test_control_negativo_el_script_versionado_de_hoy_si_incluye_el_aislado(tmp_path):
    """El mismo arbol sintetico, medido con el instrumento de `382ad05`: el aislado entra.

    El rojo sale del script versionado, no de una parodia escrita aqui (por eso se lee con
    `git show` y se ejecuta). Y se verifica la premissa: esa revision todavia no tiene la cura,
    porque un control que no es anterior a la cura no prueba nada.
    """
    assert _rev_existe(REV_SIN_CAPA_GIT), f"la revision {REV_SIN_CAPA_GIT} no esta en el repo"
    viejo = _fuente_versionada(tmp_path / "instrumento-viejo", REV_SIN_CAPA_GIT,
                               "scripts/validate_wiring.py")
    fuente = viejo.read_text(encoding="utf-8")
    assert TOKEN_CURA not in fuente, (
        f"{REV_SIN_CAPA_GIT} ya consulta la declaracion de Git: el control dejo de ser "
        "anterior a la cura")
    assert "def archivos_en_alcance" in fuente

    mod_viejo = _cargar("validate_wiring_viejo", viejo)
    base = _arbol_aislado(tmp_path / "arbol-control", con_git=True)

    vieja = mod_viejo.archivos_en_alcance(base)
    assert len(vieja) == 2, (
        "el script versionado ya devuelve tres baldes: la firma de la cura esta en la revision "
        "que se creia sin cura")
    rutas_viejas = _rutas(vieja[0], base)
    assert f"{RAIZ}/pkg/sdk_interno.py" in rutas_viejas, (
        "el instrumento versionado NO incluye el aislado: el defecto que se queria curar ya no "
        "existe en la revision anclada y la cura no tiene nada que probar")

    curadas, _roles, excluidos = vw.archivos_en_alcance(base)
    rutas_nuevas = _rutas(curadas, base)
    assert rutas_nuevas == rutas_viejas - {f"{RAIZ}/pkg/sdk_interno.py", f"{RAIZ}/otro.py"}, (
        "la cura no es exactamente «sacar lo que Git declara»: sobran o faltan rutas")
    assert excluidos["cantidad"] == 2, excluidos


def test_dientes_si_se_borra_un_rol_de_la_tabla_lo_versionado_vuelve_a_entrar(tmp_path):
    """Y los dientes de la otra capa: `EXCLUSIONES_POR_ROL` no es decoracion de la cura.

    El mutante quita SOLO la clave `evidence` de la tabla. Git no declara ignorado a ese
    directorio (esta versionado), asi que sin la clave su codigo entra en alcance y la omision
    que contiene pasa a violar. Prueba que «gobernar por declaracion de Git» no reemplaza a la
    tabla de roles: las dos capas cortan poblaciones distintas.
    """
    fuente = SCRIPT.read_text(encoding="utf-8")
    ancla = '    "evidence": "scripts de medicion historicos; el contrato del plan'
    assert fuente.count(ancla) == 1, (
        "el ancla del mutante no es unica: la clave `evidence` de la tabla cambio de forma y el "
        "mutante no esta borrando lo que se cree que borra")
    crudo = next(l for l in fuente.splitlines() if l.startswith(ancla))
    mutado = fuente.replace(crudo + "\n", "", 1)
    assert mutado != fuente and ancla not in mutado
    ast.parse(mutado)

    copia = tmp_path / "validate_wiring_sin_rol.py"
    copia.write_text(mutado, encoding="utf-8", newline="\n")
    mod = _cargar("validate_wiring_sin_rol", copia)

    base = _arbol_aislado(tmp_path / "arbol-roles", con_git=True)
    (base / "evidence").mkdir()
    (base / "evidence" / "medicion.py").write_text(LLAMADA_SIN_SENAL, encoding="utf-8")

    curadas, excluidas_rol, _excluidas_git = vw.archivos_en_alcance(base)
    assert sorted(r for r in _rutas(curadas, base) if r.startswith("evidence/")) == [], (
        "premissa: el script curado ya dejaba entrar a `evidence/`, el mutante no tiene de "
        "donde salir")
    assert [e["ruta"] for e in excluidas_rol if e["rol"] == "evidence"] == ["evidence/medicion.py"]

    mutantes, excluidas_rol_mut, _git_mut = mod.archivos_en_alcance(base)
    assert "evidence/medicion.py" in _rutas(mutantes, base), (
        "sin la clave `evidence` el versionado sigue fuera del alcance: quien lo saca es otra "
        "capa y esta prueba no afirma lo que dice")
    assert not any(e["rol"] == "evidence" for e in excluidas_rol_mut)
    reporte = mod.construir_reporte(base, ignore_known=True)
    assert "evidence/medicion.py" in {v["archivo"] for v in reporte["violaciones"]}, (
        "el mutante metio la ruta en el alcance pero no en la poblacion gobernada")


def test_dientes_si_se_apaga_la_consulta_a_git_vuelve_el_aislado(tmp_path):
    """Mutante: se desactiva SOLO la consulta a Git y la tabla de roles queda intacta.

    Prueba que los dientes son de la capa nueva y no de `EXCLUSIONES_POR_ROL`: si el rojo
    viniera de la tabla, apagar la consulta no cambiaria nada.
    """
    fuente = SCRIPT.read_text(encoding="utf-8")
    ancla = "ignorados, estado = _declaracion_de_ignorados(root)"
    assert fuente.count(ancla) == 1, (
        "el ancla del mutante no es unica (o la cura se re-escribio con otra forma): el mutante "
        "no toca lo que se cree que toca")
    mutado = fuente.replace(ancla, 'ignorados, estado = set(), "MUTADO-SIN-CONSULTA"', 1)
    assert mutado != fuente
    ast.parse(mutado)  # un mutante con SyntaxError da rojos que no miden nada

    copia = tmp_path / "validate_wiring_mutado.py"
    copia.write_text(mutado, encoding="utf-8", newline="\n")
    mod = _cargar("validate_wiring_mutado", copia)

    base = _arbol_aislado(tmp_path / "arbol-mutante", con_git=True)
    fuentes, _roles, excluidos = mod.archivos_en_alcance(base)
    assert excluidos["estado"] == "MUTADO-SIN-CONSULTA", excluidos
    assert excluidos["cantidad"] == 0, excluidos
    assert f"{RAIZ}/pkg/sdk_interno.py" in _rutas(fuentes, base), (
        "sin la consulta a Git el aislado sigue fuera: quien lo saca es otra capa y esta prueba "
        "no esta afirmando lo que dice")

    reporte = mod.construir_reporte(base, ignore_known=True)
    assert reporte[CLAVE]["cantidad"] == 0, reporte[CLAVE]
    assert "SENAL_OMITIDA" in {v["tipo"] for v in reporte["violaciones"]}, (
        "el mutante reincorporo la ruta al alcance pero no a la poblacion: el verde del arbol "
        "curado no vendria de la gobernanza")
