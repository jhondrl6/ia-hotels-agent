"""R2.8 sobre los guards de FASE-B - verde con el guard activo, rojo con el guard apagado.

Un verde a la primera no prueba que el guard exista (L-T4A.5, L-VUP-5). Cada mutante apaga **un
symbolo real** de `scripts/decision_client.py` y afirma dos cosas:

  1. que la detencion que se pretendia probar **deja de ocurrir**, y
  2. que lo que se pierde es **esa** detencion y no otra (L-V2.1: el primer mutation check de
     FASE-A apagaba el guard de A1 y nombraba a A4, porque anclar en un id posicional no observa la
     rama que uno cree estar mirando).

Por eso cada payload roto de este archivo esta elegido para que **un solo** guard lo rechace: si un
payload lo detectaran dos guards, apagar uno no prodria verde y la prueba no diria nada.
"""

import importlib.util
import re
from pathlib import Path

import pytest

FALSOS = Path(__file__).resolve().parent / "falsos_proveedores"
def _preguntas(dc):
    return [dc.Pregunta("c1", "choice", "¿Cual?", opciones=("a", "b", "c")),
            dc.Pregunta("s1", "score", "¿Nivel?", leyenda=("bajo", "medio", "alto")),
            dc.Pregunta("n1", "noul", "¿Aplica?")]


TRES = ("c1", "s1", "n1")
# Las opciones de `_preguntas` y los payloads de `_buena` tienen que cuadrar: si se desalinean, un
# payload «impecable» deja de serlo y el mutante aísla dos guards en vez de uno.


def _buena(ids=TRES):
    """Payload impecable: lo que queda despues de quitar SOLO la pieza que se quiere probar."""
    respuestas = []
    for i in ids:
        if i == "c1":
            respuestas.append({"pregunta_id": "c1", "tipo": "choice", "eleccion": "a",
                               "probabilidades": {"a": 0.6, "b": 0.2, "c": 0.2},
                               "confidence": 0.9})
        elif i == "s1":
            respuestas.append({"pregunta_id": "s1", "tipo": "score", "nivel": 1,
                               "leyenda": "medio", "confidence": 0.9})
        else:
            respuestas.append({"pregunta_id": "n1", "tipo": "noul", "probabilidad_si": 0.4})
    return {"modelo": "mutante-0.1", "respuestas": respuestas, "usage": None, "request_id": None}


def _payload_que_solo_ve(guard):
    """Un payload que **ningun otro** guard de la lista toca: asi el mutante aísla un guard."""
    if guard == "cobertura-de-preguntas":
        return _buena(ids=("c1", "s1"))                       # falta n1, lo demas impecable
    p = _buena()
    if guard == "forma-choice":
        p["respuestas"][0]["probabilidades"] = {"a": 0.4, "b": 0.1, "c": 0.1}
    elif guard == "forma-score":
        p["respuestas"][1].update({"nivel": 2, "leyenda": "bajo"})
    elif guard == "forma-noul":
        p["respuestas"][2]["probabilidad_si"] = 4.0
    elif guard == "metadata-modelo-usage":
        p["modelo"] = "   "
    elif guard == "campos-conocidos":
        p["respuestas"][0]["confianza_extra"] = 0.5
    else:
        raise AssertionError(guard)
    return p


GUARDS_DE_FORMA = ("campos-conocidos", "cobertura-de-preguntas", "forma-choice", "forma-score",
                   "forma-noul", "metadata-modelo-usage")


@pytest.mark.parametrize("guard", GUARDS_DE_FORMA)
def test_cada_guard_de_forma_carga_solo_con_lo_suyo(dc, monkeypatch, guard):
    """Verde con el guard activo, rojo con el apagado, **aislando** el guard en cada vuelta."""
    preguntas = _preguntas(dc)
    entorno = {"IAH_DECISION_PROVIDER": "falso-forma",
               "IAH_DECISION_PROVIDERS_DIR": str(FALSOS)}
    payload = _payload_que_solo_ve(guard)

    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno, _payload=payload)
    disparados = {dc._nombre_de_la_verificacion(m) for m in exc.value.motivos}
    assert disparados == {guard}, (
        f"este payload tenia que ser asunto exclusivo de {guard} y lo vieron {disparados}: el "
        "mutante no aislaria nada y el rojo no nombraria al guard mutado (L-V2.1)")

    monkeypatch.setattr(dc, "VERIFICACIONES_DE_FORMA",
                        tuple(v for v in dc.VERIFICACIONES_DE_FORMA if v[0] != guard))
    r = dc.evaluar("estado", preguntas, entorno, _payload=payload)
    assert r.provider_status == "RESUELTO", (
        f"apagado {guard} sigue fallando: hay un segundo guard sin nombrar en esta prueba")
    if guard == "cobertura-de-preguntas":
        assert [a.pregunta_id for a in r.respuestas] == ["c1", "s1"], (
            "el drop silencioso de n1 es justo lo que este guard impide")


def test_apagar_toda_la_lista_no_hace_que_la_puerta_invente_campos(dc, monkeypatch):
    """Con los seis guards apagados la puerta **tampoco** rellena: sigue sin decision por defecto.

    Es el anti-default de L-PF6 llevado al limite: la conversion a tipos no pone un `0.0` donde no
    hay confidence, se declara inoperante. Por eso `M-AC7-forma` apaga guard a guard y no la lista
    entera: la lista entera ya no basta para fabricar una decision falsa.
    """
    preguntas = _preguntas(dc)
    monkeypatch.setattr(dc, "VERIFICACIONES_DE_FORMA", ())
    roto = _buena()
    del roto["respuestas"][0]["confidence"]
    with pytest.raises(dc.LectorFallido) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "falso-forma",
                                        "IAH_DECISION_PROVIDERS_DIR": str(FALSOS)}, _payload=roto)
    assert "no rellena campos" in str(exc.value)


def test_M_AC6_token_prohibido_deja_de_ver_el_import(dc, monkeypatch, tmp_path):
    raiz = tmp_path / "repo"
    (raiz / "modules").mkdir(parents=True)
    (raiz / "modules" / "fuga.py").write_text("import typesafe\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    assert dc.escanear_aislamiento(raiz, puerta=puerta)["status"] == "HALLAZGOS"

    monkeypatch.setattr(dc, "NOMBRES_PROHIBIDOS", ())
    monkeypatch.setattr(dc, "ALIAS_ADAPTER", ())
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "SIN-HALLAZGOS"
    assert scan["conteos"]["coincidencias_de_import_fuera_de_la_puerta"] == 0
    # El escaneo sigue informado (no revienta): eso es lo que hace peligroso a este mutante, porque
    # un guard vaciado produce un verde perfectamente silencioso.
    assert scan["coverage_basis"]["tokens_buscados"] == []


def test_M_AC6_carga_dinamica_deja_de_ver_el_contrabando(dc, monkeypatch, tmp_path):
    raiz = tmp_path / "repo2"
    provs = raiz / "decision_proveedores"
    provs.mkdir(parents=True)
    (provs / "tramposo.py").write_text(
        "import importlib\nimportlib.import_module('je' + 'v')\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    activo = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert activo["status"] == "HALLAZGOS"
    assert activo["conteos"]["cargas_no_resueltas_en_directorios_de_proveedor"] == 1

    monkeypatch.setattr(dc, "FUNCIONES_DE_CARGA", ())
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "SIN-HALLAZGOS", scan["hallazgos_carga_dinamica"]


def test_M_AC6_superficie_de_proveedores_deja_de_aplicar(dc, monkeypatch, tmp_path):
    """Sin la superficie, la carga no literal deja de ser hallazgo: ahi se pierde el contrabando."""
    raiz = tmp_path / "repo3"
    provs = raiz / "decision_proveedores"
    provs.mkdir(parents=True)
    (provs / "tramposo.py").write_text(
        "import importlib\nimportlib.import_module('je' + 'v')\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    monkeypatch.setattr(dc, "DIRECTORIO_PROVEEDORES_RE", re.compile(r"(?!)"))
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "SIN-HALLAZGOS"
    assert scan["conteos"]["cargas_dinamicas_no_resueltas"] == 1, (
        "la carga sigue contada: lo unico que se perdio es su consideracion como hallazgo")


def test_M_AC7_proveedor_por_defecto_inventa_una_decision(dc, monkeypatch, preguntas):
    """El mutante que la fase prohibe por nombre: un default en la resolucion fabrica la decision."""
    path = FALSOS / "falso_forma.py"
    spec = importlib.util.spec_from_file_location("mutante_default", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def con_default(entorno=None):
        return {"nombre": mod.PROVEEDOR["nombre"], "modulo": mod, "path": path,
                "credencial_env": None, "declara": mod.PROVEEDOR, "directorio": "(mutante)"}

    monkeypatch.setattr(dc, "resolver_proveedor", con_default)
    r = dc.evaluar("estado", _preguntas(dc), {})          # entorno vacio: ningun proveedor nombrado
    assert r.provider_status == "RESUELTO", (
        "el mutante no produjo decision: resolver_proveedor ya no era la unica puerta")
    assert r.proveedor == "falso-forma"


def test_cada_mutante_apunta_a_un_simbolo_distinto_y_vigente(dc):
    """Si dos mutantes apagaran el mismo symbolo, un rojo podria venir de la rama equivocada."""
    simbolos = {"M-AC6-token": ("NOMBRES_PROHIBIDOS", "ALIAS_ADAPTER"),
                "M-AC6-carga": ("FUNCIONES_DE_CARGA",),
                "M-AC6-superficie": ("DIRECTORIO_PROVEEDORES_RE",),
                "M-AC7-forma": ("VERIFICACIONES_DE_FORMA",),
                "M-AC7-default": ("resolver_proveedor",)}
    planos = [s for nombres in simbolos.values() for s in nombres]
    assert len(set(planos)) == len(planos), "dos mutantes comparten symbolo"
    for s in planos:
        assert hasattr(dc, s), f"{s} ya no existe en la puerta: el mutante quedo huerfano"
    assert len(dc.VERIFICACIONES_DE_FORMA) == len(GUARDS_DE_FORMA) == 6
