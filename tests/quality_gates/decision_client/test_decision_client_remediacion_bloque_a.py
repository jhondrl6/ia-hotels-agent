"""Regresiones del bloque A de ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.

Los cinco contraejemplos que la orden documenta como observaciones en memoria se versionan aqui.
Cada prueba esta escrita para que el verde llegue por el fix y no por la tolerancia: antes de la
remediacion caen todas, cada una por la causa que su propio docstring declara (el registro PRE esta
en `evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/contraejemplos-antes-despues.txt`).

Que se preserva y por que:
  * Ningun `except` convierte un fallo en favorable. Aqui se afirma `RespuestaIlegible` **en lugar
    de** `TypeError`: el contrato se rompe, y se rompe nombrando el campo roto.
  * Un lector que no pudo operar no se traduce a ausencia: `NO-CONFIGURADO` afirma que se busco y no
    se encontro, y eso no lo puede afirmar quien no logro leer donde estaba (L-PF6, R2.9).
  * La unicidad de IDs es un contrato del **lote** de preguntas, no de cada pregunta aislada: se
    falla antes de despachar, y no se empareja una respuesta por posicion.
"""

import json
from pathlib import Path

import pytest

ENV_PROVIDER = "IAH_DECISION_PROVIDER"
ENV_DIR = "IAH_DECISION_PROVIDERS_DIR"

# Una pregunta de cada primitiva, con sus literales escritos aqui y no heredados del fixture de la
# seleccion: las pruebas de payload inyectado comparan contra estas opciones, y si las dos listas de
# opciones se desalinean un payload impecable deja de serlo (misma razon que en el archivo de
# mutacion por guard).
_OPCIONES = ("a", "b", "c")
_LEYENDA = ("bajo", "medio", "alto")


def _tres(dc):
    return [dc.Pregunta("c1", "choice", "?", opciones=_OPCIONES),
            dc.Pregunta("s1", "score", "?", leyenda=_LEYENDA),
            dc.Pregunta("n1", "noul", "?")]


def _noul(pid="n1", **extra):
    r = {"pregunta_id": pid, "tipo": "noul", "probabilidad_si": 0.5}
    r.update(extra)
    return r


def _choice(pid="c1", eleccion="a", confidence=0.9):
    return {"pregunta_id": pid, "tipo": "choice", "eleccion": eleccion,
            "probabilidades": {o: (0.6 if o == eleccion else 0.2) for o in _OPCIONES},
            "confidence": confidence}


def _score(pid="s1", nivel=1, confidence=0.9):
    return {"pregunta_id": pid, "tipo": "score", "nivel": nivel,
            "leyenda": _LEYENDA[nivel], "confidence": confidence}


def _payload(*respuestas, modelo="falso-forma-0.1"):
    return {"modelo": modelo, "respuestas": list(respuestas), "usage": None,
            "request_id": None}


@pytest.fixture
def modulos_rotos(tmp_path):
    """Un directorio de proveedores cuyo unico modulo revienta al cargar."""
    d = tmp_path / "proveedores-rotos"
    d.mkdir()
    (d / "roto.py").write_text("raise RuntimeError('el modulo del proveedor no carga')\n",
                               encoding="utf-8")
    return d


# -----------------------------------------------------------------------------------------
# CX1 - un fallo de carga del modulo no es un proveedor no configurado
# -----------------------------------------------------------------------------------------

def test_un_proveedor_que_no_cargo_no_se_resuelve_como_no_configurado(dc, modulos_rotos):
    """Antes: `ProveedorNoConfigurado` con `nombre-no-esta-en-el-directorio`; se afirmaba que el
    nombre no estaba despues de no haber podido leer el archivo donde podia estar."""
    with pytest.raises(dc.LectorFallido) as exc:
        dc.resolver_proveedor({ENV_PROVIDER: "roto", ENV_DIR: str(modulos_rotos)})
    assert "no cargo" in str(exc.value), exc.value


def test_la_sonda_de_estado_distingue_lector_roto_de_ausencia(dc, modulos_rotos):
    est = dc.estado_proveedor({ENV_PROVIDER: "roto", ENV_DIR: str(modulos_rotos)})
    assert est["provider_status"] != "NO-CONFIGURADO", est
    assert est["estado_lector"] == "LECTOR-FALLIDO", est


def test_el_codigo_de_salida_del_diagnostico_es_distinto_para_lector_roto(dc, modulos_rotos,
                                                                          monkeypatch):
    """El docstring de la puerta publica 2 = AUSENTE y 3 = LECTOR-FALLIDO; el diagnostico tiene que
    devolver el suyo, si no un instrumento de evidencia leeria un lector caido como ausencia."""
    monkeypatch.setenv(ENV_PROVIDER, "roto")
    monkeypatch.setenv(ENV_DIR, str(modulos_rotos))
    assert dc.main(["--provider-status"]) == 3


def test_un_directorio_con_un_modulo_legible_y_otro_roto_tampoco_certifica_ausencia(dc, tmp_path):
    """Que un modulo cargue y conteste no autoriza a afirmar que el otro nombre no esta: el archivo
    ilegible pudo declararlo. El estado sigue siendo del lector, no de ausencia."""
    d = tmp_path / "mezcla"
    d.mkdir()
    (d / "roto.py").write_text("raise RuntimeError('no carga')\n", encoding="utf-8")
    (d / "bueno.py").write_text(
        "PROVEEDOR = {'nombre': 'bueno'}\n\n"
        "def evaluar(state, preguntas):\n"
        "    return {'modelo': 'm', 'respuestas': [], 'usage': None, 'request_id': None}\n",
        encoding="utf-8")
    with pytest.raises(dc.LectorFallido):
        dc.resolver_proveedor({ENV_PROVIDER: "otro", ENV_DIR: str(d)})


def test_un_nombre_ausente_en_un_directorio_legible_sigue_siendo_no_configurado(dc,
                                                                                proveedores_falsos):
    """El fix no puede mover el estado contrario: aqui si se leyo todo el directorio y el nombre no
    estaba, y eso SI es `NO-CONFIGURADO`."""
    est = dc.estado_proveedor({ENV_PROVIDER: "jev-sdk", ENV_DIR: str(proveedores_falsos)})
    assert est["provider_status"] == "NO-CONFIGURADO"
    assert est["motivo_clase"] == "nombre-no-esta-en-el-directorio"


# -----------------------------------------------------------------------------------------
# CX2 - la primitiva noul tampoco admite campos fuera de contrato
# -----------------------------------------------------------------------------------------

def test_noul_con_un_campo_desconocido_esta_fuera_de_contrato(dc):
    """Antes: `noul` era el unico tipo al que se le perdonaban los campos extra, y un campo extra ES
    la redefincion de la primitiva que este contrato existe para detectar."""
    motivos = dc.check_campos_conocidos(_payload(_noul(probabilidad_no=0.5)),
                                        [dc.Pregunta("n1", "noul", "?")])
    assert any("fuera de contrato" in m and "probabilidad_no" in m for m in motivos), motivos


def test_noul_sin_campos_extra_sigue_pasando(dc):
    """El fix no puede estrechar la forma correcta: la respuesta de la primitiva sigue siendo legal."""
    assert dc.check_campos_conocidos(_payload(_noul()),
                                     [dc.Pregunta("n1", "noul", "?")]) == []


def test_noul_con_confidence_inventada_sigue_nombrando_solo_su_confidence(dc, preguntas,
                                                                          entorno_falso):
    """`confidence` tiene su propio motivo y no se reporta dos veces: es el caso que distingue este
    guard del generico, y el que el mutante de `campos-conocidos` necesita aislado."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload(_noul(confidence=0.5)))
    assert any("noul no debe reportar confidence" in m for m in exc.value.motivos), exc.value.motivos


# -----------------------------------------------------------------------------------------
# CX3 - un tipo o un id mal formados son ILEGIBLE, no TypeError
# -----------------------------------------------------------------------------------------

def test_tipo_que_no_es_texto_es_ilegible_y_no_revienta(dc, entorno_falso):
    """`[] in CAMPOS_POR_TIPO` lanza TypeError antes de que el guard pueda nombrar el fallo: el
    instrumento se cae en lugar de publicar que la forma no pasa."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload({"pregunta_id": "n1", "tipo": [], "probabilidad_si": 0.5}))
    assert any("tipo" in m for m in exc.value.motivos), exc.value.motivos


def test_pregunta_id_que_no_es_texto_es_ilegible_y_no_revienta(dc, entorno_falso):
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload({"pregunta_id": [], "tipo": "noul", "probabilidad_si": 0.5}))
    assert any("pregunta_id" in m for m in exc.value.motivos), exc.value.motivos


def test_dos_ids_invalidos_iguales_no_esconden_el_duplicado_bajo_el_typeerror(dc, entorno_falso):
    """El calculo de duplicados mete los ids en un set: dos listas iguales eran el caso en que el
    TypeError tapaba al duplicado que si estaba ahi."""
    malo = {"pregunta_id": [], "tipo": "noul", "probabilidad_si": 0.5}
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso, _payload=_payload(malo, malo))
    assert any("pregunta_id" in m for m in exc.value.motivos), exc.value.motivos


def test_dos_respuestas_para_la_misma_pregunta_siguen_siendo_duplicado(dc, entorno_falso):
    """Regresion del guard que ya existia: que lo nuevo no lo borre."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload(_choice(), _choice(eleccion="b"), _score(), _noul()))
    assert any("duplicadas" in m for m in exc.value.motivos), exc.value.motivos


# -----------------------------------------------------------------------------------------
# CX4 - un lote de preguntas con IDs repetidos no es un lote evaluable
# -----------------------------------------------------------------------------------------

def test_dos_preguntas_del_mismo_id_se_fallan_antes_de_despachar(dc, entorno_falso):
    """Antes: dos preguntas compartiendo id y una sola respuesta cerraban en `RESUELTO`, y
    `por_pregunta` devolvia la unica respuesta para las dos sin poder decir cual se contesto."""
    lote = [dc.Pregunta("mismo", "noul", "? A"), dc.Pregunta("mismo", "noul", "? B")]
    with pytest.raises(ValueError) as exc:
        dc.evaluar("estado", lote, entorno_falso)
    assert "mismo" in str(exc.value), exc.value


def test_los_ids_repetidos_no_dependen_de_lo_que_conteste_el_proveedor(dc, entorno_falso):
    """El rechazo es del lote: ni un payload inyectado con dos respuestas impecables lo evita. Si no,
    la unicidad quedaria del lado de quien contesta y no del que pregunta."""
    lote = [dc.Pregunta("mismo", "noul", "? A"), dc.Pregunta("mismo", "noul", "? B")]
    with pytest.raises(ValueError):
        dc.evaluar("estado", lote, entorno_falso,
                   _payload=_payload(_noul(pid="mismo", probabilidad_si=0.4),
                                     _noul(pid="mismo", probabilidad_si=0.7)))


def test_un_lote_con_ids_distintos_sigue_resolviendose(dc, preguntas, entorno_falso):
    r = dc.evaluar("estado", preguntas, entorno_falso)
    assert r.provider_status == "RESUELTO"
    assert len(r.respuestas) == len(preguntas)


# -----------------------------------------------------------------------------------------
# El par de CX4: una respuesta por pregunta, emparejada por identidad y no por posicion
# -----------------------------------------------------------------------------------------

def test_respuestas_en_otro_orden_no_inventan_una_primitiva_equivocada(dc, entorno_falso):
    """El emparejamiento posicional del guard de cobertura comparaba `tipo` contra la pregunta que
    estaba en la misma posicion, no contra la que su id nombra: con el orden invertido declaraba que
    el proveedor contesto `noul` a una `choice` que no era suya."""
    r = dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload(_noul(), _score(), _choice()))
    assert r.provider_status == "RESUELTO"
    assert [a.pregunta_id for a in r.respuestas] == ["n1", "s1", "c1"]


def test_la_primitiva_que_no_corresponde_al_id_sigue_siendo_ilegible(dc, entorno_falso):
    """Y el guard sigue viendo el tipo equivocado cuando el id si lo nombra."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", _tres(dc), entorno_falso,
                   _payload=_payload({"pregunta_id": "n1", "tipo": "score", "nivel": 1,
                                      "leyenda": "medio", "confidence": 0.9},
                                     _score(), _choice()))
    assert any("n1" in m and "score" in m and "noul" in m for m in exc.value.motivos), exc.value.motivos


# -----------------------------------------------------------------------------------------
# S12 - el informe del cliente tampoco tiene una ruta de evidencia como default de escritura
# -----------------------------------------------------------------------------------------
# Mismo defecto que `validate_governance_numbers.py`, misma cura: `--report` a secas escribia en
# `evidence/…/FASE-B/informe.json`, asi que volver a medir re-escribia el expediente de la fase
# cerrada. Se prueba la conducta del CLI con el coste de la medicion chunkeado, no la del escaneo
# completo (que ya cubre el archivo de aislamiento).

INFORME_FALSO = {"status": "SIN-HALLAZGOS", "provider_status": {},
                 "aislamiento_imports": {"conteos": {"coincidencias_de_import_fuera_de_la_puerta": 0},
                                         "coverage_basis": {"archivos_escaneados": 0}},
                 "costura": {"files_changed_to_add_provider": 1}}


@pytest.fixture
def informe_chunkeado(dc, monkeypatch):
    monkeypatch.setattr(dc, "construir_informe", lambda *a, **kw: dict(INFORME_FALSO))
    return INFORME_FALSO


def test_report_sin_destino_no_escribe_nada(dc, informe_chunkeado, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert dc.main(["--report"]) == 0
    assert list(tmp_path.rglob("*.json")) == [], (
        "el default del informe volvio a escribir un archivo: re-medir no puede gobernar el "
        "expediente de una fase cerrada (S12)")
    assert '"status"' in capsys.readouterr().out


def test_report_con_destino_nombrado_si_escribe_ahi(dc, informe_chunkeado, tmp_path):
    destino = tmp_path / "evidencia-remediacion" / "informe.json"
    assert dc.main(["--report", str(destino)]) == 0
    assert destino.is_file()
    assert '"status"' in destino.read_text(encoding="utf-8")


def test_la_ruta_de_evidencia_de_una_fase_cerrada_ya_no_vive_en_el_modulo(dc):
    """Estructura: si la ruta reaparece como constante del modulo, el default puede volver por
    descuido y esto se pone rojo sin esperar a que alguien la pise."""
    from pathlib import Path as _P
    texto = _P(dc.__file__).read_text(encoding="utf-8")
    sospechosas = [linea.strip() for linea in texto.splitlines()
                   if "evidence" in linea.lower() and not linea.strip().startswith("#")]
    assert sospechosas == [], f"el modulo vuelve a nombrar evidence/: {sospechosas}"


# -----------------------------------------------------------------------------------------
# El estado del informe refleja escaneo, sonda y costura (orden 2026-09-22 §4.A-c)
# -----------------------------------------------------------------------------------------
# `construir_informe` ya no hereda el status del escaneo a secas: las tres componentes cierran, y la
# sonda distingue sus negativos esperados (NO-CONFIGURADO e ILEGIBLE, que son el resultado sano de
# una sonda que opera) de un fallo al ejecutarla. Comportamiento, parcheando las tres fuentes.

SCAN_LIMPIO = {"status": "SIN-HALLAZGOS",
               "hallazgos": [], "hallazgos_carga_dinamica": [], "no_parseables": [],
               "coverage_basis": {"archivos_escaneados": 700, "archivos_py_en_el_arbol": 700}}

SONDA_SANA = {
    "RESUELTO": {"provider_status": "RESUELTO"},
    "NO-CONFIGURADO": {"provider_status": "NO-CONFIGURADO"},
    "ILEGIBLE": {"provider_status": "ILEGIBLE"},
}

# El `1` de archivos es necessario pero NO suficiente: el contract test de AC9
# (test_decision_client_segundo_proveedor_un_archivo) exige ademas doble RESUELTO, dos proveedores
# distintos y respuestas distintas. El veredicto del informe exige el mismo contrato (sesion 3).
COSTURA_OK = {"files_changed_to_add_provider": 1,
              "provider_status": ["RESUELTO", "RESUELTO"],
              "costura_funciona_con_ambos": ["falso-forma", "falso-segundo-medido"],
              "los_dos_despachan_respuestas_distintas": True}


def _informe_con(dc, monkeypatch, scan=SCAN_LIMPIO, sonda=SONDA_SANA, costura=COSTURA_OK):
    monkeypatch.setattr(dc, "escanear_aislamiento", lambda *a, **kw: dict(scan))
    monkeypatch.setattr(dc, "sonda_tres_estados",
                        lambda *a, **kw: {k: dict(v) for k, v in sonda.items()})
    monkeypatch.setattr(dc, "medir_costura", lambda *a, **kw: dict(costura))
    return dc.construir_informe(Path("."))


def test_el_informe_solo_cierra_favorable_con_las_tres_componentes_ok(dc, monkeypatch, tmp_path):
    informe = _informe_con(dc, monkeypatch)
    assert informe["status"] == "SIN-HALLAZGOS"
    assert informe["componentes"] == {"aislamiento_imports": "SIN-HALLAZGOS",
                                      "sonda_tres_estados": "OK", "costura": "OK"}


def test_los_negativos_esperados_de_la_sonda_sana_no_fallan_el_informe(dc, monkeypatch, tmp_path):
    """NO-CONFIGURADO e ILEGIBLE son lo que una sonda correcta produce al provocarlos: no son un
    fallo de la sonda y no degradan el informe."""
    informe = _informe_con(dc, monkeypatch, sonda=SONDA_SANA)
    assert informe["componentes"]["sonda_tres_estados"] == "OK"
    assert informe["status"] == "SIN-HALLAZGOS"


def test_una_sonda_caida_no_deja_el_informe_en_favorable(dc, monkeypatch, tmp_path):
    """La provocacion RESUELTO devuelve LECTOR-FALLIDO: la sonda fallo al ejecutarse. El informe lo
    publica en su componente en vez de cerrar SIN-HALLAZGOS heredando un escaneo limpio."""
    rota = {**SONDA_SANA, "RESUELTO": {"provider_status": "LECTOR-FALLIDO", "motivo": "x"}}
    informe = _informe_con(dc, monkeypatch, sonda=rota)
    assert informe["status"] != "SIN-HALLAZGOS"
    assert informe["componentes"]["sonda_tres_estados"] == "SONDA-FALLIDA"


def test_una_sonda_incompleta_tampoco_cierra_favorable(dc, monkeypatch, tmp_path):
    trunca = {k: v for k, v in SONDA_SANA.items() if k != "ILEGIBLE"}
    informe = _informe_con(dc, monkeypatch, sonda=trunca)
    assert informe["status"] != "SIN-HALLAZGOS"
    assert informe["componentes"]["sonda_tres_estados"] == "SONDA-INCOMPLETA"


def test_una_costura_rota_no_deja_el_informe_en_favorable(dc, monkeypatch, tmp_path):
    informe = _informe_con(dc, monkeypatch, costura={"files_changed_to_add_provider": 2})
    assert informe["status"] != "SIN-HALLAZGOS"
    assert informe["componentes"]["costura"] == "FALLIDA"


def test_poblacion_ausente_o_lectura_incompleta_no_cierran_el_informe_favorable(dc, monkeypatch,
                                                                                tmp_path):
    """Los dos estados nuevos del escaneo llegan al informe tal cual son: no favorables."""
    for estado in ("SIN-POBLACION", "LECTURA-INCOMPLETA"):
        informe = _informe_con(dc, monkeypatch, scan={**SCAN_LIMPIO, "status": estado})
        assert informe["status"] != "SIN-HALLAZGOS", estado
        assert informe["componentes"]["aislamiento_imports"] == estado


def test_report_sin_destino_imprime_json_parseable_por_stdout(dc, informe_chunkeado, capsys):
    """stdout lleva SOLO el JSON (el aviso de no-escritura va a stderr): un consumidor que parsea
    stdout no tiene que filtrar relatos."""
    assert dc.main(["--report"]) == 0
    capturado = capsys.readouterr()
    datos = json.loads(capturado.out)
    assert datos["status"] == "SIN-HALLAZGOS"
    assert "no se escribio" in capturado.err


# -----------------------------------------------------------------------------------------
# Sesion 3: el «1» de la costura no es un despacho, y un fallo no borra lo ya medido
# -----------------------------------------------------------------------------------------

def test_el_uno_de_la_costura_sin_despacho_real_no_es_favorable(dc, monkeypatch, tmp_path):
    """`files_changed==1` con un proveedor que no resuelve, el mismo proveedor repetido o las mismas
    respuestas contaria una frontera que no despacha: el veredicto exige el contrato de AC9."""
    variantes = {
        "no-resuelve": {**COSTURA_OK, "provider_status": ["ILEGIBLE", "RESUELTO"]},
        "repite-proveedor": {**COSTURA_OK,
                             "costura_funciona_con_ambos": ["falso-forma", "falso-forma"]},
        "mismas-respuestas": {**COSTURA_OK, "los_dos_despachan_respuestas_distintas": False},
    }
    for etiqueta, costura in variantes.items():
        informe = _informe_con(dc, monkeypatch, costura=costura)
        assert informe["componentes"]["costura"] == "FALLIDA", etiqueta
        assert informe["status"] != "SIN-HALLAZGOS", etiqueta


def test_el_cli_de_costura_tampoco_sale_0_con_uno_sin_despacho(dc, monkeypatch, capsys):
    """`--costura` publicaba 0 con solo contar el archivo; ahora sale 1 si el veredicto de la
    costura no cierra, y 2 con la ruta de proveedores ausente (la tabla del docstring)."""
    monkeypatch.setattr(dc, "medir_costura",
                        lambda *a, **kw: {**COSTURA_OK,
                                          "provider_status": ["RESUELTO", "NO-CONFIGURADO"]})
    assert dc.main(["--costura"]) == 1

    def ausencia(*a, **kw):
        raise dc.Ausente("directorio de proveedores falsos no existe: X")

    monkeypatch.setattr(dc, "medir_costura", ausencia)
    assert dc.main(["--costura"]) == 2
    assert "AUSENTE" in capsys.readouterr().out


def test_report_parcial_conserva_el_escaneo_cuando_la_costura_no_pudo_operar(dc, monkeypatch,
                                                                             tmp_path, capsys):
    """El hallazgo ya obtenido no puede desaparecer porque una componente posterior fallo: el
    informe sale parcial (status no favorable, exit 2 por la ruta ausente, causa publicada)."""
    scan_roto = {**SCAN_LIMPIO, "status": "HALLAZGOS",
                 "hallazgos": [{"archivo": "modules/fuga.py", "import": "typesafe"}],
                 "conteos": {"coincidencias_de_import_fuera_de_la_puerta": 1},
                 "coverage_basis": {"archivos_escaneados": 700}}
    monkeypatch.setattr(dc, "escanear_aislamiento", lambda *a, **kw: dict(scan_roto))
    monkeypatch.setattr(dc, "sonda_tres_estados",
                        lambda *a, **kw: {k: dict(v) for k, v in SONDA_SANA.items()})
    destino = tmp_path / "informe-parcial.json"
    missing = str(tmp_path / "no-existe-proveedores-falsos")
    code = dc.main(["--report", str(destino), "--falsos-directorio", missing])
    assert code == 2, code
    assert destino.is_file()
    datos = json.loads(destino.read_text(encoding="utf-8"))
    assert any("fuga.py" in h["archivo"] for h in datos["aislamiento_imports"]["hallazgos"]), (
        "el escaneo previo se perdio por el fallo de otra componente")
    assert datos["status"] != "SIN-HALLAZGOS"
    fallos = {f["componente"]: f for f in datos["fallos_de_componentes"]}
    assert fallos["costura"]["estado"] == "AUSENTE"
    assert "no existe" in fallos["costura"]["motivo"]
