# 05-prompt-inicio-sesion-fase-COPY-A

**Fase**: COPY-A — Template Restructuring + Generator Fixes
**Plan**: COPYWRITING-REFACTOR (Copywriting.jsonl → Refactorización Comercial)
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: Ninguna (primera fase)
**Bloquea a**: COPY-B

## Objetivo

Reestructurar los templates V6 de diagnóstico y propuesta para hablar en lenguaje de dueño/gerente hotelero (no auditor técnico), y corregir bugs de lógica financiera que sabotean la conversión comercial.

## Contexto de Fases Anteriores

N/A — esta es la primera fase. El contexto completo está en:
- `.opencode/context/Copywriting.jsonl` — 12 hallazgos validados, 12 reglas de copywriting, mapa de traducción técnica→dueño, estructura recomendada de documentos
- `.opencode/plans/COPYWRITING-REFACTOR/README.md` — plan maestro con decisiones arquitectónicas

## Tareas

### T1: Restructurar `diagnostico_v6_template.md` — Vista Gerencia primero

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

Reordenar el template para que las primeras 6 secciones sean legibles por un dueño de hotel sin jerga técnica. La sección 7 en adelante será el anexo técnico.

Nueva estructura (secciones 1-6):
1. 🚨 Titular de impacto: "Hoy hay reservas escapándose por WhatsApp, Google Maps e IA"
2. 📱 Evidencia inmediata: conflicto WhatsApp web vs GBP + métricas GBP (reseñas, rating)
3. 💰 Fuga financiera: comisión OTA base + rango de oportunidad (no cifra exacta si Tier < A)
4. 🔍 Las 3 fugas principales en lenguaje dueño: contacto, vitrina Google/Maps, recomendación IA
5. ⚡ Quick wins del dueño esta semana (acciones verificables, no tareas técnicas)
6. 🤖 Qué hace IA Hoteles Agent (1 párrafo simple)

Sección 7+: Anexo Técnico (movido aquí):
- Scores (SEO, GEO, AEO, IAO) con desgloses
- Métricas de acceso IA
- Metodología
- Schema/AEO/IAO/Open Graph
- Escenarios de recuperación detallados

**Reglas de copywriting a aplicar** (del Copywriting.jsonl):
- R01: No usar Schema, AEO, IAO, Open Graph, NAP, Rich Snippets en secciones 1-6 (solo entre paréntesis o en anexo)
- R03: Cada brecha técnica debe renderizarse como "qué ve el huésped / qué pierde el hotel / qué corregimos"
- R04: WhatsApp como prueba de realidad — abrir con conflicto si `whatsapp_status == conflict`
- R08: "IA Bloqueada" solo si `blocked_crawlers` tiene elementos; si no, "IA sin guía"
- R12: Contexto regional reducido a 1 bloque de negocio conectado con "el turista que ya está cerca y decide en el celular"

**Placeholders a mover explícitamente al anexo técnico (sección 7+)**:
- `${ia_metrics_table}` — contiene "Perplexity", "Crawlers", "Bloqueos" que son jerga técnica
- `${seo_score_breakdown}`, `${geo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}` — desgloses técnicos
- `${ia_metrics_table}` actualmente en línea 76 — DEBE moverse a sección 7+

**Placeholders a mantener en secciones 1-6 (vista dueño)**:
- `${whatsapp_conflict_business_note}` — gancho emocional #1
- `${regional_context}` — contexto de negocio
- `${monthly_loss_display}` — impacto financiero
- `${brechas_section}` — las 3 fugas principales
- `${quick_wins}` — acciones del dueño

### T2: Restructurar `propuesta_v6_template.md` — Finanzas honestas + OTA narrative

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md`

Reestructurar para:
1. Eliminar absolutos no soportados: cambiar "No aparece / Aparece último / No hay botón WhatsApp" por claims trazables condicionales
2. Insertar narrativa OTA: "menos dependencia de Booking/Expedia, más reserva directa por WhatsApp/Google"
3. Quick wins del dueño primero (acciones verificables), luego delegación técnica
4. La sección de proyección financiera debe mostrar plan de onboarding cuando ROI < 1.0X (no tabla de pérdidas como argumento de cierre)

**Reglas R06, R07, R09** del Copywriting.jsonl.

### T3: Fix `_build_scenario_table_rows()` — Clamp de escenarios

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Línea**: ~888-901

Problema actual:
```python
central = getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max
```
Esto pasa valores negativos sin validar. El output muestra "Optimista | $-270.950 COP/mes | 10%".

Fix:
1. Validar orden escenarios: conservador ≤ realista ≤ optimista (en recuperación, optimista debe ser el MAYOR)
2. Si optimista < realista: clamp a realista con label "(= realista)"
3. Si optimista < 0: mostrar "$0 COP/mes (Equilibrio — sin pérdida neta)"
4. Agregar label "(estimado)" cuando evidence_tier < A

```python
def _build_scenario_table_rows(self, scenarios: FinancialScenarios) -> str:
    rows = []
    # Obtener valores — NOTA: NO usar 'or' porque 0 es un valor válido
    # (monthly_loss_central puede ser 0 → "sin pérdida")
    # Python evalúa '0 or X' como X → usar 'is not None' explícito
    cons = (
        scenarios.conservative.monthly_loss_central
        if getattr(scenarios.conservative, 'monthly_loss_central', None) is not None
        else scenarios.conservative.monthly_loss_max
    )
    real = (
        scenarios.realistic.monthly_loss_central
        if getattr(scenarios.realistic, 'monthly_loss_central', None) is not None
        else scenarios.realistic.monthly_loss_max
    )
    opt = (
        scenarios.optimistic.monthly_loss_central
        if getattr(scenarios.optimistic, 'monthly_loss_central', None) is not None
        else scenarios.optimistic.monthly_loss_max
    )
    
    # Clamp: optimista no puede ser menor que realista ni negativo como recuperación
    if opt < 0:
        opt = 0
    if opt < real:
        opt = real
    
    for name, value, prob in [
        ("Conservador", cons, scenarios.conservative.probability),
        ("Realista", real, scenarios.realistic.probability),
        ("Optimista", opt, scenarios.optimistic.probability),
    ]:
        prob_pct = int(prob * 100)
        if value == 0:
            label = "$0 COP/mes (Equilibrio — sin pérdida neta)"
        else:
            label = f"{format_cop(value)}/mes"
        rows.append(f"| {name} | {label} | {prob_pct}% |")
    return "\n".join(rows)
```

### T4: Fix `_build_financial_placeholders()` — Consistencia de tier

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Línea**: ~921-967

Problema: El tier de evidencia puede divergir entre:
- Frontmatter (`financial_evidence_tier`)
- Texto del documento (`evidence_tier` en la sección financiera)
- `financial_json.evidence_tier`

Fix: Unificar usando `financial_breakdown.evidence_tier` como fuente única. Si no hay breakdown, usar el tier del `PrecisionValidator` (FIN-3).

## Criterios de Completitud

- [ ] Template diagnóstico: secciones 1-6 en lenguaje dueño, sección 7+ anexo técnico
- [ ] Template propuesta: sin absolutos no soportados, OTA narrative presente
- [ ] `_build_scenario_table_rows`: clamp aplicado, optimista nunca negativo
- [ ] `_build_financial_placeholders`: tier unificado de una sola fuente
- [ ] Todos los placeholders `${...}` existentes conservados (no eliminar ninguno)
- [ ] `log_phase_completion.py` ejecutado al finalizar

## Restricciones

- **NO ejecutar v4complete** en esta fase
- **NO modificar** service_catalog.py, pain_solution_mapper.py, coherence_validator.py
- **NO modificar** lógica de pricing (los valores mensuales se mantienen)
- **NO eliminar** placeholders del template — solo reubicar
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-A --desc "Template restructuring: owner-first view, scenario clamp, tier consistency" --check-manual-docs
```

Luego actualizar `09-documentacion-post-proyecto.md` marcando FASE-COPY-A como [x].
