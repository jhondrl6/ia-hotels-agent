# GAP: Feature Flags OFF vs ON — Motor Financiero v4.10

**Fecha:** 2026-05-04
**Contexto:** FINANCIAL-ENGINE plan v1.0.0 — 8 fases completadas, pero motor nuevo en OFF

---

## Resumen Ejecutivo

Se ejecutaron 8 fases del plan FINANCIAL-ENGINE, validando infraestructura, tests y documentación. Sin embargo, los tres feature flags que activan el motor nuevo estaban en **OFF/SHADOW**, por lo que el motor legacy de $300,000 continuó siendo usado en producción.

---

## Estado Actual (FLAGS OFF — default production)

| Flag | Valor | Efecto |
|------|-------|--------|
| `financial_v410_enabled` | `False` | Motor nuevo completamente desactivado |
| `regional_adr_mode` | `SHADOW` | Calcula ADR regional pero no lo usa |
| `pricing_hybrid_mode` | `SHADOW` | Calcula pricing híbrido pero no lo usa |

**Consecuencia práctica:**
- `regional_adr_2026.json` existe y tiene datos para `eje_cafetero`
- BUT: `financial_v410_enabled=False` → `is_v410_active() = False`
- El ADR sale de `legacy_hardcode`: **$300,000 COP** (no de `$420,000`)
- Todos los escenarios se calculan sobre $300,000

---

## Estado Esperado (FLAGS ON — motor nuevo activo)

| Flag | Valor | Efecto |
|------|-------|--------|
| `financial_v410_enabled` | `True` | Motor nuevo activado |
| `regional_adr_mode` | `ACTIVE` | Usa ADR del JSON regional |
| `pricing_hybrid_mode` | `ACTIVE` | Usa pricing híbrido |

**Consecuencia práctica:**
- ADR para `eje_cafetero` → `boutique_10_25`: **$420,000 COP** (del JSON)
- `source` en output: `"regional_v410"` en vez de `"legacy_hardcode"`
- Escenarios cambian proporcionalmente

---

## Datos Regionales en `regional_adr_2026.json`

```json
{
  "eje_cafetero": {
    "boutique_10_25": { "adr_cop": 420000, "occupancy_rate": 0.512 },
    "standard_26_60": { "adr_cop": 350000, "occupancy_rate": 0.512 }
  },
  "antioquia": {
    "boutique_10_25": { "adr_cop": 620000, "occupancy_rate": 0.642 },
    "standard_26_60": { "adr_cop": 480000, "occupancy_rate": 0.642 }
  },
  "caribe": {
    "boutique_10_25": { "adr_cop": 950000, "occupancy_rate": 0.685 },
    "standard_26_60": { "adr_cop": 750000, "occupancy_rate": 0.685 }
  }
}
```

---

## Variables de Entorno para Activar

```bash
export FINANCIAL_V410_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=active
export FINANCIAL_PRICING_HYBRID_MODE=active
```

---

## Causa Raíz

El plan de fases validó:
- ✅ Infraestructura (ADRResolutionWrapper, regional_adr_resolver, etc.)
- ✅ Tests (coverage de la nueva lógica)
- ✅ Documentación (CHANGELOG, GUIA_TECNICA, REGISTRY)

PERO nadie activó los switches que hacen que el motor nuevo se use en producción. Los flags por defecto son **SAFE** (todos OFF) para no romper producción.

---

## Acción Tomada

Se ejecuta v4complete para **Hotel Castilla Real** (sitio web) con flags ACTIVOS para evidenciar:
1. El ADR cambia de $300,000 → $420,000 (eje_cafetero, boutique)
2. El `source` cambia de `legacy_hardcode` → `regional_v410`
3. Los escenarios financieros se recalculan con el ADR correcto

---

## Verificación Post-Ejecución

Después de ejecutar con flags ON, verificar en el diagnóstico:
- `adr_source`: debe ser `regional_v410` (no `legacy_hardcode`)
- `adr_value`: debe ser `420000` (no `300000`)
- `regional_adr_match`: `eje_cafetero:boutique_10_25`
