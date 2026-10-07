"""FASE-H (AC14): procedencia del onboarding derivado, rama efectiva del loader y frescura.

Se mide contra el loader y el transformador **reales** de `main.py`, nunca contra un mock de
exito. La fuente inmutable no se toca: las ramas de fallo corren sobre copias en `tmp_path`.
Nada de aqui lanza la CLI ni consume el intento productivo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
PLAN = "REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
DIR_FASE = RAIZ / "evidence" / PLAN / "FASE-H"
FUENTE = RAIZ / "data" / "hotel_observations" / "observations.json"
YAML_PRODUCTIVO = RAIZ / "output" / PLAN / "clientes" / "hotel_don_alfonso_onboarding.yaml"
CONTROL_PRODUCTIVO = RAIZ / "evidence" / PLAN / "FASE-E2E" / "run_control.json"

sys.path.insert(0, str(RAIZ))

from main import (  # noqa: E402
    _load_latest_onboarding_data,
    _normalize_url,
    _observation_to_onboarding_format,
)


def _cargar(nombre: str, ruta: Path):
    espec = importlib.util.spec_from_file_location(nombre, str(ruta))
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


derivar = _cargar("derivar_onboarding_h", DIR_FASE / "derivar_onboarding.py")
run_once = _cargar("run_once_h_ac14", DIR_FASE / "run_once.py")

URL_ORIGINAL = "https://hoteldonalfonso.com/"


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def registro(**cambios) -> dict:
    base = {
        "hotel_name": "Hotel Don Alfonso",
        "website": URL_ORIGINAL,
        "rooms": 11,
        "monthly_reservations": 140,
        "avg_reservation_cop": 330000,
        "direct_channel_percentage": 30.0,
        "occupancy_rate": 0.4242,
        "adr_cop": 330000,
        "region": "eje_cafetero",
        "confidence": 0.95,
        "epistemic_status": "verified",
        "collected_at": "2026-07-22",
    }
    base.update(cambios)
    return base


def arbol_fuente(destino: Path, observaciones: list[dict]) -> Path:
    """Monta la raiz minima que `derivar` necesita: fuente inmutable + carpeta de fase."""
    fuente = destino / "data" / "hotel_observations" / "observations.json"
    fuente.parent.mkdir(parents=True, exist_ok=True)
    datos = json.loads(FUENTE.read_text(encoding="utf-8"))
    datos["observations"] = observaciones
    fuente.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8", newline="\n")
    (destino / "evidence" / PLAN / "FASE-H").mkdir(parents=True, exist_ok=True)
    return fuente


# ---------------------------------------------------------------------------
# Selector unico, sobre la fuente real
# ---------------------------------------------------------------------------
def test_el_selector_case_una_sola_observacion_de_seis():
    observacion, total = derivar.seleccionar_unicamente(FUENTE.read_text(encoding="utf-8"))
    assert total >= 2, "la fuente tiene varias observaciones: el selector debe discriminar"
    assert observacion["hotel_name"] == "Hotel Don Alfonso"
    assert observacion["rooms"] == 11
    assert observacion["monthly_reservations"] == 140
    assert observacion["avg_reservation_cop"] == 330000
    assert observacion["direct_channel_percentage"] == 30.0
    assert observacion["collected_at"] == "2026-07-22"


def test_cero_coincidencias_detienen_el_preflight():
    texto = json.dumps({"observations": [registro(hotel_name="Hotel Otro")]}, ensure_ascii=False)
    with pytest.raises(ValueError, match="detienen el preflight"):
        derivar.seleccionar_unicamente(texto)


def test_multiples_coincidencias_detienen_el_preflight():
    texto = json.dumps({"observations": [registro(), registro()]}, ensure_ascii=False)
    with pytest.raises(ValueError, match="2 coincidencias"):
        derivar.seleccionar_unicamente(texto)


# ---------------------------------------------------------------------------
# El transformador real y lo que no propaga
# ---------------------------------------------------------------------------
def test_el_transformador_real_descarta_adr_y_occupancy_que_si_existen_en_la_fuente():
    observacion = registro()
    derivado = _observation_to_onboarding_format(observacion)
    assert set(derivado["datos_operativos"]) == {
        "habitaciones",
        "reservas_mes",
        "valor_reserva_cop",
        "canal_directo_pct",
    }
    assert "adr_cop" in observacion and "occupancy_rate" in observacion


def test_la_procedencia_declarar_no_disponible_los_campos_no_transportados(tmp_path):
    arbol_fuente(tmp_path, [registro()])
    documento = derivar.derivar(hoy="2026-10-06", raiz=tmp_path)
    assert documento["rama_efectiva"] == "YAML_DE_DIR_CLIENTES", (
        "el derivado de la copia tiene que tomar la rama YAML: si no, la prueba no llega al loader"
    )
    assert set(documento["transformador"]["campos_no_transportados"]) == {
        "adr_cop",
        "occupancy_rate",
    }
    for campo in ("adr_cop", "occupancy_rate"):
        assert documento["productor_por_campo"][campo].startswith("no_disponible")
    texto_yaml = (
        tmp_path / "output" / PLAN / "clientes" / "hotel_don_alfonso_onboarding.yaml"
    ).read_text(encoding="utf-8")
    assert "adr_cop" not in texto_yaml and "occupancy" not in texto_yaml, (
        "un campo declarado no_disponible no puede aparecer rellenado en el derivado"
    )


def test_la_fuente_inmutable_sale_igual_antes_y_despues_de_derivar(tmp_path):
    fuente = arbol_fuente(tmp_path, [registro()])
    antes = sha256(fuente)
    documento = derivar.derivar(hoy="2026-10-06", raiz=tmp_path)
    assert sha256(fuente) == antes
    assert documento["fuente_inmutable"]["sha256_antes"] == antes
    assert documento["fuente_inmutable"]["sin_cambio"] is True


def test_sin_fecha_de_captura_la_derivacion_rechaza_en_lugar_de_seguir(tmp_path):
    """Fail-closed propio de H: el bloque de frescura del loader se salta sin fecha (`if fecha_str:`)."""
    arbol_fuente(tmp_path, [registro(collected_at=None)])
    with pytest.raises(ValueError, match="fecha_captura"):
        derivar.derivar(hoy="2026-10-06", raiz=tmp_path)


# ---------------------------------------------------------------------------
# URL: la clave de matching es la URL normalizada; el nombre no participa
# ---------------------------------------------------------------------------
def test_la_url_original_no_normaliza_a_la_de_la_corrida():
    assert _normalize_url(URL_ORIGINAL) != _normalize_url(derivar.URL_SOLICITADA)


def test_con_la_url_historica_el_loader_cae_a_defaults_sin_reportarlo(tmp_path):
    """Contrafactual de AC14(ii): conservar la URL del warehouse es un fallback silencioso."""
    clientes = tmp_path / "clientes"
    clientes.mkdir()
    derivado = _observation_to_onboarding_format(registro())  # conserva hoteldonalfonso.com
    (clientes / "hotel_don_alfonso_onboarding.yaml").write_text(
        yaml.safe_dump(derivado, allow_unicode=True), encoding="utf-8", newline="\n"
    )
    lectura = _load_latest_onboarding_data(
        hotel_url=derivar.URL_SOLICITADA, hotel_name="Hotel Don Alfonso", output_dir=clientes
    )
    assert lectura is None
    assert (
        derivar.ramas_del_loader(lectura, derivado)
        == "NINGUNA (defaults en run_v4_complete_mode)"
    )


def test_el_nombre_del_hotel_no_participa_en_el_match_del_loader(tmp_path):
    clientes = tmp_path / "clientes"
    clientes.mkdir()
    derivado = _observation_to_onboarding_format(registro())
    derivado["hotel"]["url"] = derivar.URL_SOLICITADA
    derivado["hotel"]["nombre"] = "Nombre Que No Coincide Para Nada"
    (clientes / "cualquier_cosa_onboarding.yaml").write_text(
        yaml.safe_dump(derivado, allow_unicode=True), encoding="utf-8", newline="\n"
    )
    lectura = _load_latest_onboarding_data(
        hotel_url=derivar.URL_SOLICITADA, hotel_name="otro nombre", output_dir=clientes
    )
    assert lectura is not None, "el nombre es solo logging: el match es por URL normalizada"


# ---------------------------------------------------------------------------
# Rama efectiva sobre el derivado productivo (el de la corrida)
# ---------------------------------------------------------------------------
def test_el_derivado_productivo_toma_la_rama_yaml_y_su_hash_casa():
    if not (DIR_FASE / "onboarding_provenance.json").is_file() or not YAML_PRODUCTIVO.is_file():
        pytest.skip("falta la evidencia de H: AC14 queda sin certificar sobre el derivado productivo")
    documento = json.loads((DIR_FASE / "onboarding_provenance.json").read_text(encoding="utf-8"))
    assert documento["rama_efectiva"] == "YAML_DE_DIR_CLIENTES"
    assert sha256(YAML_PRODUCTIVO) == documento["derivado"]["sha256"]
    assert sha256(FUENTE) == documento["fuente_inmutable"]["sha256_despues"], (
        "la fuente inmutable sigue intacta despues de la derivacion"
    )
    lectura = _load_latest_onboarding_data(
        hotel_url=derivar.URL_SOLICITADA,
        hotel_name="Hotel Don Alfonso",
        output_dir=YAML_PRODUCTIVO.parent,
    )
    assert lectura is not None
    assert lectura["datos_operativos"]["canal_directo_pct"] == 30.0, (
        "el default cristalizado del fixture viejo (20.0) no puede aparecer en el derivado"
    )


def test_un_mock_externo_no_anula_al_loader_real(monkeypatch):
    """Parchar el warehouse no cambia el resultado: la rama YAML manda sobre el fallback."""
    if not YAML_PRODUCTIVO.is_file():
        pytest.skip("no esta el derivado productivo")
    import main

    monkeypatch.setattr(
        main, "_observation_to_onboarding_format", lambda obs: {"envenenado": True}
    )
    lectura = _load_latest_onboarding_data(
        hotel_url=derivar.URL_SOLICITADA,
        hotel_name="Hotel Don Alfonso",
        output_dir=YAML_PRODUCTIVO.parent,
    )
    assert lectura is not None and "envenenado" not in lectura


# ---------------------------------------------------------------------------
# Frescura: el control de H es fail-closed y no depende de la variable
# ---------------------------------------------------------------------------
def test_sin_la_variable_el_loader_acepta_un_dato_de_hace_meses(tmp_path, monkeypatch):
    """Medido: `ONBOARDING_FRESHNESS_HOURS` no esta definida, asi que el bloque no corre."""
    monkeypatch.delenv("ONBOARDING_FRESHNESS_HOURS", raising=False)
    clientes = tmp_path / "clientes"
    clientes.mkdir()
    derivado = _observation_to_onboarding_format(registro())
    derivado["hotel"]["url"] = derivar.URL_SOLICITADA
    (clientes / "x_onboarding.yaml").write_text(
        yaml.safe_dump(derivado, allow_unicode=True), encoding="utf-8", newline="\n"
    )
    assert _load_latest_onboarding_data(derivar.URL_SOLICITADA, "n", clientes) is not None
    evaluado = run_once.evaluar_consentimiento(
        tmp_path / "no-hay.md", fecha_captura="2026-07-22", edad_dias=76
    )
    assert evaluado["autoriza_entrega"] is False, (
        "el control de H no puede heredar el silencio del loader"
    )


def test_con_la_variable_activa_el_loader_si_rechaza_el_dato_viejo(tmp_path, monkeypatch):
    monkeypatch.setenv("ONBOARDING_FRESHNESS_HOURS", "24")
    clientes = tmp_path / "clientes"
    clientes.mkdir()
    derivado = _observation_to_onboarding_format(registro())
    derivado["hotel"]["url"] = derivar.URL_SOLICITADA
    (clientes / "x_onboarding.yaml").write_text(
        yaml.safe_dump(derivado, allow_unicode=True), encoding="utf-8", newline="\n"
    )
    assert _load_latest_onboarding_data(derivar.URL_SOLICITADA, "n", clientes) is None


def test_sin_fecha_el_control_de_frescura_rechaza_aunque_haya_bloque(tmp_path):
    ruta = tmp_path / "c.md"
    ruta.write_text(
        "iah-consentimiento: "
        + json.dumps(
            {
                "url_amparada": derivar.URL_SOLICITADA,
                "fecha_captura_aceptada": "2026-07-22",
                "limite_de_frescura_dias": 90,
                "autoriza": "entrega a cliente",
                "declarado_por": "operador",
                "fecha": "2026-10-06",
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="", edad_dias=None)
    assert evaluado["autoriza_entrega"] is False
    assert "rechaza" in evaluado["causa"]


# ---------------------------------------------------------------------------
# Consentimiento: solo el operador lo emite y solo sobre la URL viva
# ---------------------------------------------------------------------------
def _escribir_consentimiento(destino: Path, **cambios) -> Path:
    bloque = {
        "url_amparada": derivar.URL_SOLICITADA,
        "fecha_captura_aceptada": "2026-07-22",
        "limite_de_frescura_dias": 90,
        "autoriza": "entrega a cliente",
        "declarado_por": "operador",
        "fecha": "2026-10-06",
    }
    bloque.update(cambios)
    destino.write_text(
        "iah-consentimiento: " + json.dumps(bloque, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    return destino


def test_un_consentimiento_datado_sobre_la_url_viva_si_autoriza(tmp_path):
    ruta = _escribir_consentimiento(tmp_path / "c.md")
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="2026-07-22", edad_dias=76)
    assert evaluado["autoriza_entrega"] is True, evaluado.get("causa")


def test_el_consentimiento_de_fase_p4_no_ampara_la_url_viva(tmp_path):
    """El de P4 ampara otra URL y declara que no es entrega: no abre el spawn (L-ENT.6)."""
    ruta = RAIZ / "evidence" / "FASE-P4" / "consentimiento-donalfonso.md"
    if not ruta.is_file():
        pytest.skip("no esta el consentimiento de FASE-P4")
    evaluado = run_once.evaluar_consentimiento(
        ruta, fecha_captura="2026-07-22", edad_dias=76, url=derivar.URL_SOLICITADA
    )
    assert evaluado["autoriza_entrega"] is False
    assert evaluado["causa"]


def test_un_consentimiento_de_otra_url_no_autoriza(tmp_path):
    ruta = _escribir_consentimiento(tmp_path / "c.md", url_amparada=URL_ORIGINAL)
    evaluado = run_once.evaluar_consentimiento(
        ruta, fecha_captura="2026-07-22", edad_dias=76, url=derivar.URL_SOLICITADA
    )
    assert evaluado["autoriza_entrega"] is False
    assert URL_ORIGINAL in evaluado["causa"]


def test_un_consentimiento_sin_alcance_de_entrega_no_autoriza(tmp_path):
    ruta = _escribir_consentimiento(tmp_path / "c.md", autoriza="solo observacion")
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="2026-07-22", edad_dias=76)
    assert evaluado["autoriza_entrega"] is False


def test_un_consentimiento_anterior_a_la_captura_no_autoriza(tmp_path):
    ruta = _escribir_consentimiento(tmp_path / "c.md", fecha="2026-07-01")
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="2026-07-22", edad_dias=76)
    assert evaluado["autoriza_entrega"] is False


def test_un_limite_de_frescura_mas_alla_del_techo_de_H_no_autoriza(tmp_path):
    ruta = _escribir_consentimiento(tmp_path / "c.md", limite_de_frescura_dias=3650)
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="2026-07-22", edad_dias=76)
    assert evaluado["autoriza_entrega"] is False
    assert str(run_once.EDAD_MAXIMA_DIAS) in evaluado["causa"]


def test_un_bloque_incompleto_no_autoriza(tmp_path):
    ruta = tmp_path / "c.md"
    ruta.write_text(
        "iah-consentimiento: " + json.dumps({"url_amparada": derivar.URL_SOLICITADA}),
        encoding="utf-8",
        newline="\n",
    )
    evaluado = run_once.evaluar_consentimiento(ruta, fecha_captura="2026-07-22", edad_dias=76)
    assert evaluado["autoriza_entrega"] is False
    assert "faltan campos" in evaluado["causa"]


# ---------------------------------------------------------------------------
# Los dos relojes: el del dato y el de la memoria
# ---------------------------------------------------------------------------
def test_el_recorrido_offline_declarar_la_edad_del_dato_y_los_dos_relojes():
    ruta = DIR_FASE / "integracion_offline.json"
    if not ruta.is_file():
        pytest.skip("falta el recorrido offline de H")
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    assert documento["frescura"]["fecha_captura_presente"] is True
    assert documento["frescura"]["edad_dias"] > 20
    assert documento["frescura"]["variable_en_el_entorno"] is False
    memoria = documento["snapshot_memoria_previo"]
    assert memoria["analysis_reutilizable_para_el_canonical_url"]["encontrado"] is True
    assert memoria["sesiones_que_cleanup_old_sessions_20_dias_borraria"] >= 1


def test_el_espejo_de_cleanup_coincide_con_el_productor(tmp_path):
    """El inventario de H nombra exactamente las sesiones que `cleanup_old_sessions` borraria."""
    from agent_harness.memory import MemoryManager

    sesiones = tmp_path / ".agent" / "memory" / "sessions"
    sesiones.mkdir(parents=True)
    archivadas = tmp_path / ".agent" / "memory" / "archives" / "sessions"
    archivadas.mkdir(parents=True)
    viejo_vivo = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
    joven = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    (sesiones / f"{viejo_vivo}_aaa.json").write_text("{}", encoding="utf-8")
    (sesiones / f"{joven}_bbb.json").write_text("{}", encoding="utf-8")
    (sesiones / "sin_fecha.json").write_text("{}", encoding="utf-8")
    (archivadas / f"{viejo_vivo}_ccc.json").write_text("{}", encoding="utf-8")

    espejo = run_once.inventario_memoria(raiz=tmp_path)
    nombradas = {Path(r).name for r in espejo["borraria_cleanup_20_dias"]}
    assert nombradas == {f"{viejo_vivo}_aaa.json"}

    # El productor decide: se invoca sobre la copia y se compara lo que efectivamente borra.
    manager = MemoryManager(memory_path=tmp_path / ".agent" / "memory")
    antes = {p.name for p in sesiones.glob("*.json")}
    borrados = manager.cleanup_old_sessions(days=20)
    despues = {p.name for p in sesiones.glob("*.json")}
    assert borrados == len(antes - despues) == len(nombradas)
    assert (archivadas / f"{viejo_vivo}_ccc.json").exists(), (
        "el glob del productor no es recursivo: archives/sessions queda fuera, como en el espejo"
    )


# ---------------------------------------------------------------------------
# La rama del loader como predicado gobernable (L-VUP-13)
# ---------------------------------------------------------------------------
def test_las_ram_silenciosas_del_loader_no_son_favorables():
    favorable = {"loader": {"rama_efectiva": "YAML_DE_DIR_CLIENTES"}}
    propia = {"rama_efectiva": "YAML_DE_DIR_CLIENTES"}
    assert run_once.rama_favorable(favorable, propia) is True
    for silencia in (
        "NINGUNA (defaults en run_v4_complete_mode)",
        "OBSERVATIONS_DENTRO_DE_LA_FUNCION",
    ):
        assert run_once.rama_favorable({"loader": {"rama_efectiva": silencia}}, propia) is False
        assert run_once.rama_favorable(favorable, {"rama_efectiva": silencia}) is False
    assert (
        run_once.rama_favorable(
            {"loader": {"rama_efectiva": "YAML_DE_DIR_CLIENTES"}},
            {"rama_efectiva": "OBSERVATIONS_DENTRO_DE_LA_FUNCION"},
        )
        is False
    ), "las dos mediciones tienen que coincidir: una sola no certifica la rama"


def test_el_preflight_recalculado_no_inventa_el_consentimiento(tmp_path):
    """Se re-calcula el preflight en vivo: si el requisito se hardcodeara True, esto cae.

    Las dos ramas hacen falta: sin documento en el arbol el requisito es FALSO (H no puede
    autosatisfacerlo), y con el documento del operador sobre el arbol real es VERDADERO porque lo lee.
    """
    fase_tmp = tmp_path / DIR_FASE.relative_to(RAIZ)
    fase_tmp.mkdir(parents=True)
    fase_f_tmp = tmp_path / "evidence" / PLAN / "FASE-F"
    fase_f_tmp.mkdir(parents=True)
    for nombre in ("integracion_offline.json", "onboarding_provenance.json"):
        (fase_tmp / nombre).write_text(
            (DIR_FASE / nombre).read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
        )
    (fase_f_tmp / "credential_status.json").write_text(
        (RAIZ / "evidence" / PLAN / "FASE-F" / "credential_status.json").read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="\n",
    )

    documento = run_once.preflight(raiz=tmp_path)
    assert documento["intentos"] == 0
    requisito = documento["requisitos"]["consentimiento_datado_sobre_la_url_viva"]
    assert requisito["cumple"] is False, (
        "el consentimiento es acto del operador; H no puede autosatisfacerlo"
    )
    assert "iah-consentimiento" in requisito["causa"]
    assert documento["spawn_autorizado"] is False
    assert "consentimiento_datado_sobre_la_url_viva" in documento["requisitos_no_favorables"]

    real = run_once.preflight()
    assert real["requisitos"]["consentimiento_datado_sobre_la_url_viva"]["cumple"] is True, (
        "el documento del operador esta en el arbol: negarlo tambien seria inventar"
    )
    assert run_once.rama_favorable(
        json.loads((DIR_FASE / "integracion_offline.json").read_text(encoding="utf-8")),
        json.loads((DIR_FASE / "onboarding_provenance.json").read_text(encoding="utf-8")),
    ) is True


# ---------------------------------------------------------------------------
# El preflight productivo: attempts=0 y requisito de consentimiento en contra
# ---------------------------------------------------------------------------
def test_el_preflight_publicado_declara_el_consentimiento_pendiente_y_attempts_cero():
    """El preflight que publico `1c20695`: consentimiento pendiente y spawn bloqueado.

    El arbol de trabajo ya lleva el consentimiento del operador y su preflight es favorable, asi
    que el baseline historico se lee en la copia preservada (sha identico al blob de HEAD), no en
    el archivo mutable.
    """
    ruta = DIR_FASE / "preflight_2026-10-06_no_favorable.json"
    if not ruta.is_file():
        pytest.skip("no esta la copia preservada del preflight publicado")
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    assert documento["intentos"] == 0
    requisito = documento["requisitos"]["consentimiento_datado_sobre_la_url_viva"]
    assert requisito["cumple"] is False
    assert "iah-consentimiento" in requisito["causa"]
    assert documento["spawn_autorizado"] is False


def test_el_preflight_vigente_es_favorable_por_lectura_no_por_endulzamiento():
    """Lo que autoriza el spawn es el documento del operador, y la edad published casa con su aritmetica."""
    documento = json.loads((DIR_FASE / "preflight.json").read_text(encoding="utf-8"))
    assert documento["intentos"] == 0
    requisito = documento["requisitos"]["consentimiento_datado_sobre_la_url_viva"]
    assert requisito["cumple"] is True
    assert requisito["detalle"]["declarado_por"], "la autorizacion declara quien la emite"
    assert requisito["detalle"]["limite_dias"] == 90
    assert documento["spawn_autorizado"] is True
    assert documento["requisitos_no_favorables"] == []

    frescura = documento["requisitos"]["frescura_fail_closed"]
    fecha_captura = json.loads((DIR_FASE / "onboarding_provenance.json").read_text(encoding="utf-8"))[
        "valores_declarados_por_el_operador"
    ]["fecha_captura"]
    assert frescura["edad_dias"] == run_once.edad_contra_la_emision(
        fecha_captura, datetime.fromisoformat(documento["emitido_el"])
    ), "la edad publicada debe ser la aritmetica entre la captura y la emision, no la del artefacto"
    assert frescura["edad_fuente"] == "computada_contra_la_emision"


def test_nada_de_esta_fase_creara_el_control_productivo():
    assert not CONTROL_PRODUCTIVO.exists(), (
        "el intento unico es de E2E: si run_control.json existe, H lo consumo"
    )
