"""Sonda post-fix AC-F5 — techo de tier: que pone el cableado y que pone el dato.

El plan decide Q5=(a) porque el Tier A era inalcanzable **por construccion**: FASE-K
fijaba `ga4_enabled=False` y `gsc_enabled=False` descartando la disponibilidad real.
Tras el hoist, la pregunta que queda para FASE-P4 (AC-O0) es distinta y hay que
separarla en dos duenos:

  1. **Cableado** — ¿la corrida propaga las banderas?  Se mide aqui con los clientes
     reales en este entorno (sin credenciales, ambas deben salir False; con
     credenciales, True).
  2. **Dato del hotel** — ¿las fuentes del breakdown son verificadas?  La regla FASE-1
     exige `has_verified_data` **ademas** de la conectividad, asi que un hotel sin
     onboarding verificado sigue sin Tier A con las banderas en True.

La sonda reconstruye `HotelFinancialData` con las fuentes del artefacto real de
FASE-I y reporta el tier bajo las cuatro combinaciones. No escribe nada: lo que se
lee por consola va a `probe-post-fix.txt`.

Ejecuta:  python evidence/FASE-P3-B/verify_probe_ac_f5_techo_tier.py
"""

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.analytics.google_analytics_client import GoogleAnalyticsClient  # noqa: E402
from modules.analytics.google_search_console_client import (  # noqa: E402
    GoogleSearchConsoleClient,
)
from modules.financial_engine.scenario_calculator import (  # noqa: E402
    HotelFinancialData,
    ScenarioCalculator,
)

BASELINE = (
    ROOT / "output" / "FASE-I_salentoreal_post_estabilizacion"
    / "v4_complete" / "hotelsalentoreal" / "v4_audit"
)


def _latest(pattern):
    hits = sorted(glob.glob(str(BASELINE / pattern)))
    return Path(hits[-1]) if hits else None


def _tier_para(sources, ga4, gsc):
    data = HotelFinancialData(
        rooms=24,
        adr_cop=280000.0,
        occupancy_rate=0.55,
        direct_channel_percentage=0.10,
        ota_commission_rate=0.20,
        adr_source=sources.get("adr", "unknown"),
        occupancy_source=sources.get("occupancy", "unknown"),
        channel_source=sources.get("direct_channel", "unknown"),
        ga4_enabled=ga4,
        gsc_enabled=gsc,
    )
    return ScenarioCalculator().calculate_breakdown(data).evidence_tier


def main():
    ga4_available = GoogleAnalyticsClient(property_id=None).is_available()
    gsc_available = GoogleSearchConsoleClient().is_configured()

    print("== Capa 1: cableado (lo que FASE-K propaga desde AC-F5) ==")
    print(f"  ga4_available (is_available)     = {ga4_available}")
    print(f"  gsc_available (is_configured)    = {gsc_available}")
    print("  -> en este entorno sin credenciales ambas son False: el hoist no inventa")
    print("     conectividad, solo deja de negar la que exista.\n")

    scenarios_path = _latest("financial_scenarios*.json")
    if scenarios_path is None:
        print(f"  [skip] baseline real no disponible en {BASELINE}")
        return 0

    breakdown = json.loads(scenarios_path.read_text(encoding="utf-8")).get("breakdown", {})
    sources = breakdown.get("data_sources", {})
    print("== Capa 2: el dato (regla FASE-1, intacta) ==")
    print(f"  artefacto real: {scenarios_path.name}")
    print(f"  tier publicado por la corrida : {breakdown.get('evidence_tier')}")
    print(f"  fuentes: adr={sources.get('adr')!r} "
          f"occupancy={sources.get('occupancy')!r} "
          f"direct_channel={sources.get('direct_channel')!r}")
    for ga4, gsc in [(False, False), (True, False), (False, True), (True, True)]:
        print(f"  tier con ga4={ga4!s:<5} gsc={gsc!s:<5} -> {_tier_para(sources, ga4, gsc)}")
    print("\n  Lectura: con las fuentes de esta corrida el techo NO lo pone el cableado")
    print("  sino la ausencia de dato verificado (adr=regional_v410, canal=default).")
    print("  Por eso AC-O0 exige declarar el dueno del techo, no solo su letra.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
