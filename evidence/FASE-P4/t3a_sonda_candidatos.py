# -*- coding: utf-8 -*-
"""FASE-P4 / Tarea 1 — sonda de candidatos T3a.

Responde con medición, no con lectura de docs: cual de los hoteles de
`data/hotel_observations/observations.json` (o de `output/clientes/`) satisface
T3a y que techo de tier tendria la corrida bajo los predicados reales de
analitica (AC-F5).

Usa el camino real del pipeline:
  - `main._load_latest_onboarding_data` (YAML por URL normalizada + fallback a observations.json)
  - `ScenarioCalculator._determine_evidence_tier` con `HotelFinancialData` construido
    como el bloque FASE-K de `main.py`

Salida: stdout con codificacion ASCII-safe + `t3a-sonda-candidatos.md` junto a este archivo.
No escribe ni modifica datos de hoteles; es solo lectura.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent / "t3a-sonda-candidatos.md"

import main  # noqa: E402  (carga .env: es lo que permite medir disponibilidad real)

from modules.financial_engine import ScenarioCalculator, HotelFinancialData  # noqa: E402
from modules.analytics.google_analytics_client import GoogleAnalyticsClient  # noqa: E402
from modules.analytics.google_search_console_client import GoogleSearchConsoleClient  # noqa: E402
from modules.utils.financial_factors import FinancialFactors  # noqa: E402

OBS = ROOT / "data" / "hotel_observations" / "observations.json"


def ascii_safe(text: str) -> str:
    return (
        str(text)
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )


def p(text: str = "") -> None:
    print(ascii_safe(text))


def availability() -> dict:
    """Mismo calculo del hoist AC-F5 en main.py (lineas del bloque previo a FASE-K)."""
    return {
        "ga4_available": GoogleAnalyticsClient(property_id=None).is_available(),
        "gsc_available": GoogleSearchConsoleClient().is_configured(),
    }


def loader_resolution(url: str, name: str) -> dict:
    data = main._load_latest_onboarding_data(url, name)
    if not data:
        return {"resuelve": False}
    meta = data.get("metadatos", {})
    return {
        "resuelve": True,
        "fuente": meta.get("fuente", "?"),
        "fecha_captura": meta.get("fecha_captura", ""),
        "campos": len(meta.get("campos_confirmados", []) or []),
        "from_observations_fallback": meta.get("fuente") == "observations_tier_a",
    }


def tier_for(obs: dict, flags: dict, adr_source: str) -> dict:
    """Recorre exactamente la construccion de HotelFinancialData del bloque FASE-K."""
    rooms = obs["rooms"]
    reservations = obs["monthly_reservations"]
    data = main._load_latest_onboarding_data(obs["website"], obs["hotel_name"])
    if data:
        dos = data.get("datos_operativos", {})
        rooms = dos.get("habitaciones", rooms)
        reservations = dos.get("reservas_mes", reservations)
    occupancy = reservations / (rooms * 30)
    fin = HotelFinancialData(
        rooms=rooms,
        adr_cop=obs["adr_cop"],
        occupancy_rate=occupancy,
        direct_channel_percentage=obs["direct_channel_percentage"],
        ota_commission_rate=FinancialFactors().get_comision_ota()["base"],
        adr_source=adr_source,
        occupancy_source="onboarding" if data else "regional",
        channel_source="onboarding" if data else "default",
        ga4_enabled=flags["ga4_available"],
        gsc_enabled=flags["gsc_available"],
    )
    sc = ScenarioCalculator()
    sources = sc._trace_data_sources(fin)
    return {
        "tier": str(sc._determine_evidence_tier(fin).value),
        "carga": bool(data),
        "sources": {k: sources.get(k, "") for k in ("adr", "occupancy", "direct_channel")},
        "verified": any(
            s in ("onboarding", "verified", "industry_standard_15pct", "user_provided")
            for s in (sources.get("adr", ""), sources.get("direct_channel", ""))
        ),
    }


def main_probe() -> int:
    obs_all = json.loads(OBS.read_text(encoding="utf-8")).get("observations", [])
    flags = availability()
    today = datetime.now(timezone.utc).date()

    yaml_urls = {}
    for f in sorted((ROOT / "output" / "clientes").glob("*_onboarding.yaml")):
        try:
            import yaml as _yaml
            d = _yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            yaml_urls[d.get("hotel", {}).get("url", "")] = f.name
        except Exception as exc:  # noqa: BLE001
            p(f"  ! no se pudo leer {f.name}: {exc}")

    lines: list[str] = []
    p("== FASE-P4 Tarea 1: sonda T3a ==")
    p(f"fecha medición: {today}")
    p(f"disponibilidad analítica real (predicados AC-F5): {flags}")
    p(f"YAMLs en output/clientes/: {yaml_urls or '(ninguno)'}")
    p("")
    header = (
        f"{'hotel':<24}{'url':<34}{'carga':<7}{'dias':<6}"
        f"{'tier(onb)':<11}{'transito':<10}{'consent'}"
    )
    p(header)
    p("-" * len(header))

    for obs in obs_all:
        url = obs["website"]
        name = obs["hotel_name"]
        res = loader_resolution(url, name)
        collected = obs.get("collected_at", "")
        try:
            age = (today - datetime.fromisoformat(collected).date()).days
        except Exception:  # noqa: BLE001
            age = -1
        with_onb = tier_for(obs, flags, "user_provided")
        notes = obs.get("notes", "") or ""
        consent = "registro_no_encontrado"
        if "confidencialidad" in notes:
            consent = "confidencialidad"
        row = (
            f"{name[:23]:<24}{url[:33]:<34}{str(res['resuelve']):<7}{age:<6}"
            f"{with_onb['tier']:<11}{str(obs.get('is_transit_hotel')):<10}{consent}"
        )
        p(row)
        lines.append(
            {
                "hotel": name,
                "url": url,
                "loader_resuelve": res["resuelve"],
                "loader_detalle": res,
                "dias_desde_captura": age,
                "tier_con_onboarding": with_onb,
                "yaml_en_clientes": yaml_urls.get(url),
                "source": obs.get("source"),
                "confidence": obs.get("confidence"),
                "epistemic_status": obs.get("epistemic_status"),
                "is_transit_hotel": obs.get("is_transit_hotel"),
                "notes": notes,
            }
        )

    baseline = json.loads(
        (ROOT / "evidence/FASE-E2E/financial_scenarios_20260911_175958.json").read_text(encoding="utf-8")
    )
    p("")
    p(f"baseline delta (evidence/FASE-E2E): url={baseline.get('url')} "
      f"tier={baseline.get('breakdown', {}).get('evidence_tier')}")

    OUT.with_suffix(".json").write_text(
        json.dumps(
            {"medido_el": str(today), "flags": flags, "candidatos": lines,
             "baseline": {"url": baseline.get("url"),
                          "tier": baseline.get("breakdown", {}).get("evidence_tier")}},
            ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    p(f"json: {OUT.with_suffix('.json').name}")
    return 0


if __name__ == "__main__":
    sys.exit(main_probe())
