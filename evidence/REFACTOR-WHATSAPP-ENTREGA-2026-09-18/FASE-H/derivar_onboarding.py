"""FASE-H -- derivacion trazable del onboarding de Hotel Don Alfonso (AC14).

Lee la fuente inmutable, la selecciona por `hotel_name`, la transforma con el writer real
del repo (`main._observation_to_onboarding_format`) y cambia **una sola** clave: `hotel.url`.
No estima, no rellena y no fecha a hoy: los campos que el transformador no propaga quedan
declarados `no_disponible` en la procedencia.

Salidas (con `--raiz` se reubican, para que los tests no toquen el arbol de la corrida):
  <raiz>/output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/hotel_don_alfonso_onboarding.yaml
  <raiz>/evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/onboarding_provenance.json

Uso:
  ./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import yaml  # noqa: E402  (el loader real del repo tambien lo usa)

from main import (  # noqa: E402
    _load_latest_onboarding_data,
    _normalize_url,
    _observation_to_onboarding_format,
)

PLAN = "REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
SELECTOR_NOMBRE = "Hotel Don Alfonso"
URL_SOLICITADA = "https://www.donalfonsohotel.com/"
RESPALDO_A = f"evidence/{PLAN}/FASE-A/fuente-publica-precios-2026-09-19.md"

# SS5 del maestro: lo que el derivado debe conservar tal como se capturo.
CAMPOS_CONSERVAR = {
    "fecha_captura": "2026-07-22",
    "habitaciones": 11,
    "reservas_mes": 140,
    "valor_reserva_cop": 330000,
    "canal_directo_pct": 30.0,
}
# `adr_cop` y `occupancy_rate` existen en la observacion pero `_FIELD_MAP` del transformador
# no los propaga. Se declaran no disponibles; nunca se estiman ni se rellenan (DA-P1.9).
CAMPOS_NO_TRANSPORTADOS = ("adr_cop", "occupancy_rate")


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def seleccionar_unicamente(texto_fuente: str) -> tuple[dict, int]:
    """Un solo registro o se detiene: cero y multiples no son un preflight aprobable."""
    observaciones = json.loads(texto_fuente).get("observations", [])
    coincidencias = [o for o in observaciones if o.get("hotel_name") == SELECTOR_NOMBRE]
    if len(coincidencias) != 1:
        raise ValueError(
            f"selector {SELECTOR_NOMBRE!r} devolvio {len(coincidencias)} coincidencias; "
            "cero o multiples detienen el preflight"
        )
    return coincidencias[0], len(observaciones)


def ramas_del_loader(lectura: dict | None, yaml_esperado: dict) -> str:
    """La rama se decide por contenido, no por la clave `fuente`.

    El propio transformador escribe `observations_tier_a` dentro del YAML, asi que esa clave no
    distingue la rama YAML del fallback dentro de la funcion. Lo que si distingue es que el
    loader devuelva exactamente lo que se escribio en `clientes/`.
    """
    if lectura is None:
        return "NINGUNA (defaults en run_v4_complete_mode)"
    return "YAML_DE_DIR_CLIENTES" if lectura == yaml_esperado else "OBSERVATIONS_DENTRO_DE_LA_FUNCION"


def derivar(*, hoy: str, raiz: Path | None = None) -> dict:
    raiz = Path(raiz) if raiz else RAIZ
    fuente = raiz / "data" / "hotel_observations" / "observations.json"
    dir_clientes = raiz / "output" / PLAN / "clientes"
    yaml_derivado = dir_clientes / "hotel_don_alfonso_onboarding.yaml"
    destino = raiz / "evidence" / PLAN / "FASE-H" / "onboarding_provenance.json"

    antes = sha256_de(fuente)
    observacion, total = seleccionar_unicamente(fuente.read_text(encoding="utf-8"))

    derivado = _observation_to_onboarding_format(observacion)
    url_original = derivado["hotel"]["url"]
    derivado["hotel"]["url"] = URL_SOLICITADA  # unica edicion del contenido

    metadatos = derivado.setdefault("metadatos", {})
    if not metadatos.get("fecha_captura"):
        raise ValueError(
            "el transformador no propago fecha_captura: sin fecha el bloque de frescura del "
            "loader se salta (`if fecha_str:`) y H rechaza en vez de seguir"
        )

    confirmados = set(metadatos.get("campos_confirmados", []))
    faltantes = sorted(set(CAMPOS_CONSERVAR) - {"fecha_captura"} - confirmados)
    if faltantes:
        raise ValueError(f"campos que SS5 exige conservar no llegaron al derivado: {faltantes}")

    dir_clientes.mkdir(parents=True, exist_ok=True)
    yaml_derivado.write_text(
        yaml.safe_dump(derivado, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )

    despues = sha256_de(fuente)
    if antes != despues:
        raise ValueError("la fuente inmutable cambio durante la derivacion")

    lectura = _load_latest_onboarding_data(
        hotel_url=URL_SOLICITADA,
        hotel_name=SELECTOR_NOMBRE,
        output_dir=dir_clientes,
    )
    releido = yaml.safe_load(yaml_derivado.read_text(encoding="utf-8"))
    rama = ramas_del_loader(lectura, releido)

    produccion = {"hotel.url": "unica edicion explicita de esta fase (URL indicada por el operador)"}
    for campo in metadatos.get("campos_confirmados", []):
        produccion[f"datos_operativos.{campo}"] = (
            f"_observation_to_onboarding_format._FIELD_MAP desde observations.json[{SELECTOR_NOMBRE}]"
        )
    for campo_no in CAMPOS_NO_TRANSPORTADOS:
        produccion[campo_no] = (
            "no_disponible: _FIELD_MAP del transformador no lo propaga; no se estima ni se rellena"
        )

    documento = {
        "schema": "iah-onboarding-provenance/1.0",
        "plan": PLAN,
        "fase": "FASE-H",
        "generado_el": hoy,
        "fuente_inmutable": {
            "ruta": "data/hotel_observations/observations.json",
            "sha256_antes": antes,
            "sha256_despues": despues,
            "sin_cambio": True,
            "observaciones_en_la_fuente": total,
        },
        "selector": {
            "expresion": f'hotel_name == "{SELECTOR_NOMBRE}"',
            "coincidencias": 1,
            "cero_o_multiples_detienen": True,
        },
        "transformador": {
            "simbolo": "main._observation_to_onboarding_format",
            "campos_que_propaga": ["canal_directo_pct", "habitaciones", "reservas_mes", "valor_reserva_cop"],
            "campos_no_transportados": list(CAMPOS_NO_TRANSPORTADOS),
        },
        "derivado": {
            "ruta": yaml_derivado.relative_to(raiz).as_posix(),
            "sha256": sha256_de(yaml_derivado),
            "bytes": yaml_derivado.stat().st_size,
        },
        "url": {
            "original_en_la_fuente": url_original,
            "solicitada_por_el_operador": URL_SOLICITADA,
            "normalizada_solicitada": _normalize_url(URL_SOLICITADA),
            "normalizada_original": _normalize_url(url_original),
            "casan": _normalize_url(URL_SOLICITADA) == _normalize_url(url_original),
            "matching_del_loader": "por _normalize_url(hotel.url); el nombre no participa (Args de su docstring)",
            "declaracion": (
                "correccion de identidad trazable con atribucion al operador. No se afirma "
                "equivalencia universal de dominios ni redireccion comprobada en esta fase."
            ),
        },
        "valores_declarados_por_el_operador": {
            "fecha_captura": CAMPOS_CONSERVAR["fecha_captura"],
            "habitaciones": CAMPOS_CONSERVAR["habitaciones"],
            "reservas_mes": CAMPOS_CONSERVAR["reservas_mes"],
            "valor_reserva_cop": CAMPOS_CONSERVAR["valor_reserva_cop"],
            "canal_directo_pct": CAMPOS_CONSERVAR["canal_directo_pct"],
            "epistemic_status_de_la_fuente": observacion.get("epistemic_status"),
            "confidence_de_la_fuente": observacion.get("confidence"),
            "limite": (
                "dato capturado el 2026-07-22; NO se presenta como verificado hoy. Su edad la "
                "calcula el control de frescura de H, que es fail-closed, no este archivo."
            ),
        },
        "productor_por_campo": produccion,
        "respaldo_externo": {
            "ruta": RESPALDO_A,
            "corrobora": ["rooms: 11 productos de alojamiento, cero divergencia"],
            "no_corrobora": ["monthly_reservations", "direct_channel_percentage"],
            "declaracion": (
                "registro de FASE-A con fecha y metodo; no genero ningun valor nuevo y no es "
                "consentimiento ni autorizacion de entrega."
            ),
        },
        "ramas_posibles_del_loader": [
            "YAML_DE_DIR_CLIENTES",
            "OBSERVATIONS_DENTRO_DE_LA_FUNCION",
            "NINGUNA (defaults en run_v4_complete_mode)",
        ],
        "rama_efectiva": rama,
        "rama_aceptable_para_certificar_ac14": "YAML_DE_DIR_CLIENTES",
        "fixture_descartado_como_modelo": {
            "ruta": "tests/fixtures/donalfonsohotel_onboarding.yaml",
            "motivo": (
                "carece de metadatos.fecha_captura y de campos_confirmados, y su "
                "canal_directo_pct 20.0 es el default del pipeline cristalizado"
            ),
        },
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(documento, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return documento


def main(argv: list[str]) -> int:
    raiz = RAIZ
    hoy = "2026-10-06"
    if "--raiz" in argv:
        raiz = Path(argv[argv.index("--raiz") + 1]).resolve()
    if "--fecha" in argv:
        hoy = argv[argv.index("--fecha") + 1]
    doc = derivar(hoy=hoy, raiz=raiz)
    print(json.dumps({"rama_efectiva": doc["rama_efectiva"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
