"""FASE-E (AC4, `D25-ter`/`N4`): `BenchmarkLoader` lee el JSON publicado y el contrato de maestros esta declarado.

Los valores esperados no se copian de `DEFAULT_DATA`: se recalculan del artefacto
publicado (`data/benchmarks/plan_maestro_data.json`) y de su maestro
(`data/benchmarks/regional_adr_2026.json`). Eso es lo que hace que un fossil devuelto
por un getter sea rojo y no un verde gemelo del fallback.

Decision escrita: `10-analisis` §Decisiones, DA-PLAN-8a.
"""

import json
from pathlib import Path

import pytest

from modules.utils.benchmarks import (
    BLOQUES_LEIDOS_DEL_JSON,
    BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO,
    BLOQUES_MAESTRO_DECLARADO,
    CLAVES_REGION_MAESTRO_DECLARADO,
    CLAVES_REGION_PUBLICADAS,
    DEFAULT_DATA,
    BenchmarkLoader,
    assert_coherencia_maestros,
    auditoria_maestros,
)
from modules.utils.financial_factors import FinancialFactors

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTO = ROOT / "data" / "benchmarks" / "plan_maestro_data.json"
MAESTRO = ROOT / "data" / "benchmarks" / "regional_adr_2026.json"

# Los cinco bloques que nombro el plan: ningun nodo del JSON los contiene.
CINCO_DEL_PLAN = frozenset({
    "actividad_gbp_pesos", "kpis_objetivo_v23", "terminologia_cliente",
    "disclaimers_cliente", "certificados",
})
# Medición de la fase: tres bloques SI tienen nodo publicado bajo v25_config, con otro
# vocabulario y valores divergentes. El contrato del producto es el de DEFAULT_DATA.
FORQUES_PUBLICADOS = frozenset({"paquetes_servicios_v23", "umbrales_decision", "addons_v242"})

# Divergencia medida del horque de umbrales (la unica con claves comunes): se pincha
# aqui porque FASE-F es la duena de los umbrales y nadie debe re-valorar el horque
# sin re-declarar que el producto lee otra cifra.
DIVERGENCIA_UMBRALES = {"impacto_catastrofico": (8_000_000, 6_000_000),
                        "brecha_conversion_critica": (3_000_000, 2_500_000),
                        "revpar_premium": (250_000, 180_000)}


@pytest.fixture(scope="module")
def arte() -> dict:
    return json.loads(ARTIFACTO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def maestro() -> dict:
    return json.loads(MAESTRO.read_text(encoding="utf-8"))


@pytest.fixture()
def loader() -> BenchmarkLoader:
    return BenchmarkLoader()


def _claves_de_todos_los_nodos(nodo, acumulado=None) -> set:
    """Todas las claves del artefacto, a cualquier profundidad (la busqueda de la fase)."""
    acumulado = acumulado if acumulado is not None else set()
    if isinstance(nodo, dict):
        for clave, valor in nodo.items():
            acumulado.add(clave)
            _claves_de_todos_los_nodos(valor, acumulado)
    return acumulado


# ---------------------------------------------------------------------------
# Getters contra el artefacto publicado
# ---------------------------------------------------------------------------
def test_region_se_lee_del_publicado(loader, arte):
    """`regiones` es el bloque LEIDO del JSON: cada clave publicada llega tal cual."""
    publicadas = arte["v25_config"]["regiones"]
    assert publicadas, "el artefacto dejo de publicar v25_config.regiones"
    for region, valores in publicadas.items():
        perfil = loader.get_regional_data(region)
        for clave in CLAVES_REGION_PUBLICADAS:
            if clave in valores:
                assert perfil[clave] == valores[clave], f"{region}.{clave} no viene del JSON"


def test_caribe_no_es_default(loader):
    """Prueba por nombre del defecto: el argumento region tenia que dejar de ser decorativo."""
    caribe = loader.get_regional_data("caribe")
    default = loader.get_regional_data("default")
    antioquia = loader.get_regional_data("antioquia")
    assert caribe != default
    assert antioquia != default != caribe
    assert caribe["precio_promedio"] == 450000
    assert caribe["ocupacion"] == pytest.approx(0.685)
    assert antioquia["precio_promedio"] == 500000


def test_regiones_aceptan_la_forma_de_nivel_superior(loader, tmp_path):
    """`regiones` en el nivel superior tambien es fuente: el puente no solo sabe de `v25_config`."""
    datos = {"version": "v9", "regiones": {"litoral": {"precio_promedio": 120000, "ocupacion": 0.25}}}
    ruta = tmp_path / "maestro_legado.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    perfil = BenchmarkLoader(data_path=ruta).get_regional_data("litoral")
    assert perfil["precio_promedio"] == 120000
    assert perfil["revpar_cop"] == 30000
    assert perfil["revpar_derivado"] is True


def test_revpar_cop_se_deriva_del_valor_publicado(loader, arte):
    """`revpar_cop = precio_promedio x ocupacion`, calculado a mano desde el artefacto."""
    for region, valores in arte["v25_config"]["regiones"].items():
        perfil = loader.get_regional_data(region)
        esperado = int(round(valores["precio_promedio"] * valores["ocupacion"]))
        assert perfil["revpar_cop"] == esperado, region
        assert perfil["revpar_derivado"] is True, region


def test_revpar_derivado_casa_con_el_maestro(loader, maestro):
    """El valor derivado es el del maestro para las regiones que el maestro publica."""
    for region, datos in maestro["regions"].items():
        if region == "default":
            continue
        boutique = datos["boutique_10_25"]
        esperado = int(round(boutique["adr_cop"] * boutique["occupancy_rate"]))
        assert loader.get_regional_data(region)["revpar_cop"] == esperado, region


def test_default_esta_exento_y_su_divergencia_es_medida(loader, maestro, arte):
    """`default` no casa con el maestro y esa divergencia esta declarada (DA-PLAN-8c)."""
    master_default = maestro["regions"]["default"]["any"]
    publicado = arte["v25_config"]["regiones"]["default"]
    assert master_default["adr_cop"] - publicado["precio_promedio"] == 20000
    assert master_default["occupancy_rate"] == pytest.approx(0.50)
    assert publicado["ocupacion"] == pytest.approx(0.60)
    derivado = loader.get_regional_data("default")["revpar_cop"]
    assert derivado == int(round(publicado["precio_promedio"] * publicado["ocupacion"]))
    assert derivado != int(round(master_default["adr_cop"] * master_default["occupancy_rate"]))


def test_get_all_regions_devuelve_las_regiones_publicadas(loader, arte):
    assert loader.get_all_regions() == sorted(arte["v25_config"]["regiones"])
    assert loader.get_all_regions() == ["antioquia", "bogota", "caribe", "default", "eje_cafetero"]


def test_financial_factors_get_all_regions_deja_de_morir_y_delega(arte):
    """`_plan_data` no existia en `BenchmarkLoader`: el metodo lanzaba AttributeError."""
    factores = FinancialFactors()
    assert factores.get_all_regions() == sorted(arte["v25_config"]["regiones"])
    assert BenchmarkLoader().regiones().keys() >= set(factores.get_all_regions())


def test_los_consumidores_de_revpar_reciben_valor_por_region(arte):
    """`FinancialFactors` es el consumidor real del puente: antes daba el fossil global."""
    for region in ("caribe", "eje_cafetero", "antioquia", "bogota"):
        config = FinancialFactors().get_config(region)
        publicados = arte["v25_config"]["regiones"][region]
        assert config.revpar_cop == int(round(publicados["precio_promedio"] * publicados["ocupacion"]))
        assert config.factor_captura_aila == DEFAULT_DATA["regiones"]["default"]["factor_captura_aila"]


def test_plan_versions_si_leya_el_publicado_y_sigue_ahi(loader, arte):
    """`plan_versions` era la unica clave de nivel superior que se leia: conserva su lectura."""
    assert loader.get_plan_versions() == arte["plan_versions"]
    assert loader.get_decision_plan_meta() == arte["plan_versions"]["decision_core_v24"]
    assert loader.get_delivery_plan_meta() == arte["plan_versions"]["delivery_remote_v25"]


# ---------------------------------------------------------------------------
# Bloques sin dato publicado: DEFAULT_DATA es el maestro, y la premisa se comprueba
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("getter,bloque", [
    ("get_activity_weights", "actividad_gbp_pesos"),
    ("get_kpis", "kpis_objetivo_v23"),
    ("get_client_terminology", "terminologia_cliente"),
    ("get_client_disclaimers", "disclaimers_cliente"),
    ("get_certificates_config", "certificados"),
])
def test_bloque_sin_dato_publicado_devuelve_su_maestro_declado(loader, arte, getter, bloque):
    """Si alguien publica el bloque sin mover la declaracion, esta prueba cae por la premisa."""
    assert bloque not in _claves_de_todos_los_nodos(arte), (
        f"{bloque} tiene nodo publicado en el JSON: la particion de maestros vencio")
    assert bloque in CINCO_DEL_PLAN and bloque in BLOQUES_MAESTRO_DECLARADO
    assert getattr(loader, getter)() == DEFAULT_DATA[bloque]


@pytest.mark.parametrize("getter,bloque", [
    ("get_packages", "paquetes_servicios_v23"),
    ("get_thresholds", "umbrales_decision"),
    ("get_addons", "addons_v242"),
])
def test_bloque_con_forque_publicado_no_lo_lee(loader, arte, getter, bloque):
    """El JSON publica una copia con otro vocabulario: el getter lee el maestro declarado.

    Medido en la fase: `get_packages`/`get_thresholds`/`get_addons` leen el nivel
    superior, el horque vive bajo `v25_config` y los dos vocabularios no casan
    (`precio_cop` vs `inversion_mensual_cop`, claves en slug vs nombre visible).
    """
    assert bloque in FORQUES_PUBLICADOS and bloque in BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO
    assert bloque in arte["v25_config"]
    assert getattr(loader, getter)() == DEFAULT_DATA[bloque]
    assert loader.load().get(bloque) is None, "el horque se publico arriba: hay que re-decidir"


def test_la_divergencia_del_forque_de_umbrales_es_la_medida(arte):
    """Pineado porque FASE-F es la duena de los umbrales: moverlo sin re-declarar es rojo."""
    publicado = arte["v25_config"]["umbrales_decision"]
    for clave, (maestro_declado, horque) in DIVERGENCIA_UMBRALES.items():
        assert DEFAULT_DATA["umbrales_decision"][clave] == maestro_declado, clave
        assert publicado[clave] == horque, clave
    # las dos claves que el producto si usa para recomendar paquetes no existen en el horque
    for clave in ("gbp_score_bajo", "factor_gbp_punto"):
        assert clave not in publicado, clave


def test_el_forque_de_paquetes_no_comparte_claves_con_el_contrato(arte):
    """Cinco paquetes, dos vocabularios: cambiar de maestro sin adaptador romperia al consumidor."""
    publicado = arte["v25_config"]["paquetes_servicios_v23"]
    assert set(publicado) & set(DEFAULT_DATA["paquetes_servicios_v23"]) == set()
    assert set(publicado) == {"starter_geo", "pro_aeo", "pro_aeo_plus", "elite", "elite_plus"}


# ---------------------------------------------------------------------------
# Mutantes: un getter que lee de verdad cambia de respuesta con el artefacto
# ---------------------------------------------------------------------------
def test_mutante_de_valor_corrompido_vuelve_rojo_el_getter(artefacto_corrupto):
    """Corromper el ADR publicado en una copia cambia el getter: el dato viene del archivo."""
    real = BenchmarkLoader().get_regional_data("caribe")
    corrupto = BenchmarkLoader(data_path=artefacto_corrupto).get_regional_data("caribe")
    assert corrupto["precio_promedio"] == 1
    assert corrupto["revpar_cop"] == int(round(1 * 0.685))
    assert corrupto["revpar_cop"] != real["revpar_cop"]
    # las claves del maestro declarado siguen viniendo del modulo, no del archivo
    assert corrupto["factor_captura_aila"] == real["factor_captura_aila"]


def test_mutante_de_ocupacion_corrompida_cambia_el_derivado(artefacto_corrupto_ocupacion):
    real = BenchmarkLoader().get_regional_data("eje_cafetero")["revpar_cop"]
    corrupto = BenchmarkLoader(data_path=artefacto_corrupto_ocupacion).get_regional_data("eje_cafetero")
    assert corrupto["revpar_cop"] == int(round(280000 * 0.99))
    assert corrupto["revpar_cop"] != real


@pytest.fixture()
def artefacto_corrupto(tmp_path, arte) -> Path:
    datos = json.loads(json.dumps(arte))
    datos["v25_config"]["regiones"]["caribe"]["precio_promedio"] = 1
    ruta = tmp_path / "artefacto_adr_corrupto.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


@pytest.fixture()
def artefacto_corrupto_ocupacion(tmp_path, arte) -> Path:
    datos = json.loads(json.dumps(arte))
    datos["v25_config"]["regiones"]["eje_cafetero"]["ocupacion"] = 0.99
    ruta = tmp_path / "artefacto_ocupacion_corrupta.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------------------
# Assert del contrato de maestros (Tarea 1)
# ---------------------------------------------------------------------------
def test_la_poblacion_de_bloques_es_exacta():
    """Tres poblaciones cerradas: leido, maestro-declarado (los cinco), maestro-con-horque (los tres)."""
    assert CINCO_DEL_PLAN == BLOQUES_MAESTRO_DECLARADO
    assert FORQUES_PUBLICADOS == BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO
    assert BLOQUES_LEIDOS_DEL_JSON == frozenset({"regiones"})
    assert CINCO_DEL_PLAN & FORQUES_PUBLICADOS == set()
    assert_coherencia_maestros()
    assert auditoria_maestros()["bloques_sin_declarar"] == []
    assert auditoria_maestros()["forques_sin_nodo"] == []


def test_bloque_sexo_sin_declaracion_corta_el_assert(monkeypatch):
    """El sexto bloque sin declaracion es rojo: el vocabulario esta cerrado por assert."""
    monkeypatch.setitem(DEFAULT_DATA, "bloque_nuevo_sin_declarar", {"x": 1})
    with pytest.raises(AssertionError, match="bloque_nuevo_sin_declarar"):
        assert_coherencia_maestros()
    assert auditoria_maestros()["bloques_sin_declarar"] == ["bloque_nuevo_sin_declarar"]


def test_bloque_declurado_sin_horque_corta_el_assert():
    """Un horque declarado que deja de estar publicado vence la decision: corta."""
    sin_horque = {"version": "v1", "v25_config": {"regiones": {"default": {}}}}
    with pytest.raises(AssertionError, match="umbrales_decision"):
        assert_coherencia_maestros(sin_horque)


def test_bloque_del_maestro_declurado_que_alguien_publica_corta_el_assert():
    """Publicar uno de los cinco sin mover la poblacion tambien corta (por la otra via)."""
    publicado = {"version": "v1", "v25_config": {
        "regiones": {"default": {}}, "umbrales_decision": {}, "paquetes_servicios_v23": {},
        "addons_v242": {}, "kpis_objetivo_v23": {}}}
    with pytest.raises(AssertionError, match="kpis_objetivo_v23"):
        assert_coherencia_maestros(publicado)


def test_clave_de_region_sin_declaracion_corta_el_assert(monkeypatch):
    """Una clave regional nueva del maestro declarado sin vocabulario tambien corta."""
    monkeypatch.setitem(DEFAULT_DATA["regiones"]["default"], "factor_nuevo_sin_declarar", 0.5)
    with pytest.raises(AssertionError, match="factor_nuevo_sin_declarar"):
        assert_coherencia_maestros()


def test_el_vocabulario_declarado_cubre_las_claves_del_maestro():
    """`revpar_cop` sale del vocabulario como derivada, no como fossil del maestro."""
    claves = set(DEFAULT_DATA["regiones"]["default"])
    vocabulario = CLAVES_REGION_PUBLICADAS | CLAVES_REGION_MAESTRO_DECLARADO | {"revpar_cop"}
    assert claves <= vocabulario
    assert "revpar_cop" not in CLAVES_REGION_MAESTRO_DECLARADO
    assert "revpar_cop" not in CLAVES_REGION_PUBLICADAS


def test_una_region_sin_valores_publicados_no_inventa_un_derivado(tmp_path):
    """Sin precio u ocupacion el lector conserva el maestro declarado y lo marca (DA-C3)."""
    datos = {"version": "v9", "regiones": {"sin_dato": {"habitaciones_promedio": 9}}}
    ruta = tmp_path / "sin_publicacion.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    perfil = BenchmarkLoader(data_path=ruta).get_regional_data("sin_dato")
    assert perfil["revpar_derivado"] is False
    assert perfil["revpar_cop"] == DEFAULT_DATA["regiones"]["default"]["revpar_cop"]
