# FASE-E2E-ZIONE: Corrida ÚNICA v4complete — Zi One Luxury + Verificación de Fixes + Lecciones

> 🎯 **FASE DE CIERRE FUNCIONAL DEL PLAN** — Única ejecución de `v4complete` autorizada en todo el plan.

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-E2E-ZIONE
**Objetivo**: Ejecutar UNA corrida real de `v4complete` para Zi One Luxury (https://zione.co/) con
datos de onboarding Tier A, verificar que los 13 criterios (V1-V13) de los fixes F1-F14 fueron
superados, contrastar contra el sitio vivo, y registrar lecciones aprendidas + análisis post-implementación.
**Dependencias**: FASE-P0-A/B/C, FASE-P1-A/B/C/D, FASE-P2-A/B — **TODAS ✅** (gate de entrada duro)
**Duración estimada**: 1 sesión (≤60 iteraciones) — incluye comando de larga duración (5-10 min)
**Skill**: `phased_project_executor.md` — **v4complete vía `delegate_task` (OBLIGATORIO)**

## Modo de Ejecución — delegate_task para v4complete

`v4complete` tarda 5-10 minutos (scraping + APIs + generación). Según la regla del executor,
**NUNCA ejecutar v4complete directamente sin notify_on_complete o sin subagente** — si el agente
parent se agota antes de terminar, el output se genera pero la verificación/docs no se ejecutan.

```
Protocolo (phased_project_executor §Protocolo-Subagente-v4complete):

1. delegate_task(
     goal="Ejecutar v4complete para Zi One Luxury y generar diagnóstico, propuesta y assets",
     context="""
       URL: https://zione.co/
       Comando exacto:
         cd C:/Users/Jhond/Github/iah-cli
         ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
       El onboarding Tier A se carga AUTOMATICAMENTE desde
       output/clientes/zi-one-luxury_onboarding.yaml (34 hab, 800 reservas/mes,
       ADR 290000, occupancy calculada 0.7843 -> source 'onboarding').
       Expected output: 01_DIAGNOSTICO, 02_PROPUESTA, assets, coherence >= 0.80,
       gate_report.json, financial_scenarios.json, pain_ledger.json.
       Output dir por defecto: output/v4_complete/ (o el que elija el flujo).
     """,
     timeout=900,             # 15 minutos — v4complete necesita 5-10 min
     notify_on_complete=True,
     toolsets=["terminal"]
   )

2. MIENTRAS el subagente corre (o al completar): el agente principal NO hace nada que
   consuma muchas iteraciones. Reserva presupuesto para evidencia + verificación + lecciones.

3. Cuando el subagente completa → ejecutar INMEDIATAMENTE el Protocolo de Evidencia Proactiva.
```

## Protocolo de Evidencia Proactiva (OBLIGATORIO — antes de cualquier verificación)

> ⚠️ Inmediatamente después de que `v4complete` genera output, ANTES de verificar o investigar.
> El shell del proyecto es **pwsh** — NO usar sintaxis bash (`mkdir -p`, `cp ... 2>/dev/null`, ni
> llaves `{hotel_id}`: no funcionan en PowerShell):

```powershell
New-Item -ItemType Directory -Force evidence/E2E-ZIONE | Out-Null
# Inspeccionar la estructura real generada (las rutas pueden variar):
Get-ChildItem output/v4_complete -Recurse -File | Select-Object -ExpandProperty FullName
# Copiar artefactos clave (los ausentes no abortan):
Copy-Item output/v4_complete/01_DIAGNOSTICO_*.md evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
Copy-Item output/v4_complete/02_PROPUESTA_*.md evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
Copy-Item output/v4_complete/financial_scenarios_*.json evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
Copy-Item output/v4_complete/gate_report_*.json evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
Copy-Item output/v4_complete/pain_ledger.json evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
Copy-Item output/v4_complete/coherence_validation.json evidence/E2E-ZIONE/ -ErrorAction SilentlyContinue
# JSONs de auditoría (están en subdirectorio del hotel — recorrer y filtrar):
Get-ChildItem output/v4_complete -Recurse -Filter *.json |
  Where-Object { $_.FullName -match 'audit' } |
  Copy-Item -Destination evidence/E2E-ZIONE/
```
Esto es OBLIGATORIO sin importar el presupuesto restante. Si el agente se agota después,
la evidencia ya está a salvo para la siguiente sesión.

## Contexto

Corrida de validación E2E del plan CREDIBILIDAD-NUMERICA-2026-08-20. Zi One Luxury es el mejor
datapoint de la base (CONTEXT §6.5): ocupación 78.43%, 800 reservas/mes, ADR $290K, 2 sedes
(Pereira + Cartagena), motor de reservas operativo. Es el hotel que motivó los fallos F12/F13/F14
(verificados contra el sitio vivo en CONTEXT §7). Los datos de onboarding ya están en
`output/clientes/zi-one-luxury_onboarding.yaml` y en `data/hotel_observations/observations.json`.

**Lección metodológica a aplicar (CONTEXT §7.4)**: nunca declarar brecha HIGH sin verificación
contra sitio vivo. Los criterios V8/V9/V10 deben contrastarse con https://zione.co/ (botón de
WhatsApp presente en barra sticky Elementor, footer y enlaces wa.me; números por sede).

### Estado de Fases Anteriores (gate de entrada — verificar ANTES de lanzar v4complete)
| Fase | Estado requerido |
|------|------------------|
| FASE-P0-A/B/C | ✅ |
| FASE-P1-A/B/C/D | ✅ |
| FASE-P2-A/B | ✅ |

**Si alguna NO está ✅ → ABORTAR esta fase y reportar qué falta.** No ejecutar v4complete con fixes pendientes.

## Tareas

### T1: Ejecutar v4complete (vía subagente) + guardar evidencia
- Lanzar `delegate_task` según el protocolo de arriba.
- Al completar: ejecutar el Protocolo de Evidencia Proactiva.
- **Criterio**: todos los artefactos copiados a `evidence/E2E-ZIONE/`.

### T2: Verificar la matriz V1-V13 contra los artefactos generados
Recorrer cada criterio de `01-plan-maestro.md §4` contra los JSON/MD de `evidence/E2E-ZIONE/`:

| # | Fix | Verificación concreta |
|---|-----|------------------------|
| V1 | F1 | Precio en hook/propuesta == `pricing.monthly_price_cop` (un solo valor) |
| V2 | F1 | `pricing_compliance` presente y PASSED en gate_report (diseño floor-aware D1: para el ratio 0.0724 de Zione, a lo sumo WARNING) |
| V3 | F7 | `delivery_quality_report.json` y demás JSONs leen utf-8 sin UnicodeDecodeError |
| V4 | F2/F4 | Un solo ADR benchmark para eje_cafetero; Bogotá presente |
| V5 | F3 | Fallback no produce `caribe` para dirección país-genérico |
| V6 | F5 | `ota_commission_source` con rango + fuente |
| V7 | F6 | Rango del hook acotado (ratio max/min ≤ umbral de P1-C) |
| V8 | F12 | Sin BRECHA 1 falsa: GBP Pereira comparado con web Pereira (no Cartagena) |
| V9 | F13 | `no_whatsapp_visible` NO está DETECTED HIGH en pain_ledger (botón existe) |
| V10 | F14 | coherence y gate de acuerdo sobre `whatsapp_button` |
| V11 | F8 | `data_sources.occupancy == "onboarding"` |
| V12 | — | coherence ≥ 0.8, sin regresión de gates, READY_FOR_PUBLICATION ("sin regresión" = sin fallos NUEVOS vs línea base §6 del 01-plan-maestro) |
| V13 | C9 | Tiempo de corrida medido (inicio→fin del subagente), registrado como "tiempo con caches cálidos": `data/cache/places_cache.json` y `data/cache/scraped_sites.json` son caches GLOBALES que persisten aunque el output-dir sea nuevo (scraper_fallback.py L13-14) |

**Criterio**: matriz V1-V13 llenada en `10-analisis-post-implementacion.md` con Expected/Real/Status.

### T3: Contrastar V8/V9/V10 contra el sitio vivo + registrar lecciones
- Verificar (vía fetch/navegador si hay herramienta disponible, o contra la evidencia
  `temp/zione_*.png` del CONTEXT) que el botón de WhatsApp existe y los números por sede son correctos.
- Registrar en `10-analisis-post-implementacion.md`: Métricas de Ejecución (coherence, gates,
  tiempo con caches cálidos), Lecciones Aprendidas (mínimo 3), Seguimientos abiertos, y el
  veredicto de si los fixes F1-F14 fueron superados.

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado vía delegate_task y output completo generado
- [ ] Evidencia copiada a `evidence/E2E-ZIONE/` (Protocolo Proactivo)
- [ ] Matriz V1-V13 llenada con Expected/Real/Status
- [ ] V8/V9/V10 contrastados contra sitio vivo https://zione.co/
- [ ] Lecciones aprendidas (≥3) y Métricas registradas en 10-analisis
- [ ] Veredicto explícito: fixes superados / fixes con regresión

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-E2E-ZIONE ✅.
2. `README.md` del plan: actualizar tabla de progreso (habilita FASE-RELEASE).
3. `09-documentacion-post-proyecto.md`: Sección D — métricas E2E (coherence, tiempo con caches cálidos, gates).
4. `10-analisis-post-implementacion.md`: Matriz V1-V13 + Métricas + Lecciones + Seguimientos.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-E2E-ZIONE --desc "Corrida unica v4complete Zi One Luxury + verificacion V1-V13 + lecciones" --tests "0" --check-manual-docs
```
6. Evidencia preservada en `evidence/E2E-ZIONE/`.

## Restricciones

- Máximo 60 iteraciones (el comando v4complete cuenta como 1 tool call pero consume tiempo de pared).
- **UNA sola ejecución de v4complete en esta fase** — si falla, investigar la causa y reportar, NO re-ejecutar en loop (agotaría el presupuesto).
- NO ejecutar el ZIP/deploy; esta fase solo verifica el output de la corrida.
- NO modificar código fuente — esta fase es de VERIFICACIÓN. Si un fix regresa, registrarlo como fallo y dejarlo para seguimiento, NO parchear aquí.
- NO ejecutar FASE-RELEASE (es la siguiente sesión).
