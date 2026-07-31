# FASE-3: Unificación de Taxonomía de Fuentes (H2) + Fix CTA Onboarding Redundante (BUG-2)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)

## Contexto previo

FASE-1 completada: harness recibe y respeta ADR + occupancy del onboarding. adr_source lee de adr_resolution.source.

FASE-2 completada: proposal generator usa ADR del onboarding. ValidationSummary deriva confidence de la fuente real (adr_source), no de flag de existencia.

Quedan 2 problemas:

1. **H2**: 3 vocabularios incompatibles para "fuente del ADR":
   - Vocabulario A: `ADRSource` enum (`"user_provided"`, `"regional_v410"`, ...) en `adr_resolution_wrapper.py:23`
   - Vocabulario B: `ValidationSummary.sources` (`["Onboarding"]`, `["Benchmark"]`, ...) en `main.py:2151-2187`
   - Vocabulario C: JSON `input_data.adr_source` (`"handler"`, `"onboarding"`, `"regional"`) en `main.py:1861`
   - El discriminador `v4_diagnostic_generator.py:~1244` compara `adr_source in ("user_provided", "web_scraping")` pero recibe `["Onboarding"]` (PascalCase) → nunca matchea → `adr_source_label` siempre es "estimado"

2. **BUG-2**: 7 CTAs de "Complete el onboarding" en 3 superficies, siempre visibles incluso cuando onboarding ya fue cargado:
   - Diagnóstico L1259-1267: CTA hardcodeado
   - Diagnóstico L2493-2496: nota assets baja confianza
   - Diagnóstico L1084-1088: banner Tier C
   - Propuesta template L102, L104, L126: condicionales Tier C
   - Log final main.py:3281

## Objetivo de esta fase

1. Unificar la taxonomía de fuentes para que el discriminador del diagnóstico matchee correctamente
2. Centralizar los 7 CTAs de onboarding en una función `_build_onboarding_cta(has_onboarding, precision_tier)` que decida el mensaje correcto según contexto real (Opción C del contexto)

## Decisión: Opción C para BUG-2

El plan original usaba Opción B (inferir has_onboarding y condicionar cada CTA individualmente). Se eleva a Opción C: centralizar los CTAs en una función única. Justificación:

- El bug original fue que NUNCA se checkeó has_onboarding en NINGÚN sitio. Con Opción B, un futuro desarrollador debe recordar agregar el check en cada nuevo CTA. Con Opción C, la función centralizada fuerza la disciplina por construcción.
- 7 bloques condicionales con la misma lógica es duplicación (DRY).
- Una función `_build_onboarding_cta` es trivialmente testable (2-3 casos). Con Opción B, verificar los 7 sitios requiere 7 tests separados.

### Tareas

- [ ] 3.1 Fix H2: Unificar discriminador del diagnóstico
  - En `v4_diagnostic_generator.py:~1244`: el discriminador recibe `sources` (Vocabulario B, PascalCase) pero compara con Vocabulario A (snake_case)
  - Fix: cambiar el discriminador para comparar contra Vocabulario B:
    ```python
    if "Onboarding" in sources or "user_provided" in sources:
        adr_source_label = "datos del hotel"
    ```
  - Verificar que `adr_source_label` ya no sea siempre "estimado"

- [ ] 3.2 Fix BUG-2 (Opción C): Crear función centralizada `_build_onboarding_cta`
  - Inferir `has_onboarding` de `validation_summary.fields[i].sources` — si algún campo tiene `sources=["Onboarding"]`, onboarding está cargado
  - Crear función `_build_onboarding_cta(has_onboarding: bool, can_show_exact: bool, surface: str) -> str` en `v4_diagnostic_generator.py`
  - La función recibe `surface` para distinguir el contexto del CTA: `"diagnostic_cta"`, `"diagnostic_banner"`, `"diagnostic_assets_note"`, `"proposal_template"`, `"log_final"`
  - Lógica central:
    ```python
    def _build_onboarding_cta(has_onboarding: bool, can_show_exact: bool, surface: str = "diagnostic_cta") -> str:
        if can_show_exact:
            return ""
        if not has_onboarding:
            # CTA original: pedir onboarding
            return _ONBOARDING_CTA_MESSAGES[surface]["no_onboarding"]
        else:
            # Onboarding ya cargado, falta GA4
            return _ONBOARDING_CTA_MESSAGES[surface]["has_onboarding"]
    ```
  - Definir `_ONBOARDING_CTA_MESSAGES` como dict de mensajes por surface y estado

- [ ] 3.3 Fix BUG-2: Refactorizar los 7 CTAs para usar `_build_onboarding_cta`
  - Diagnóstico L1259-1267 (show_onboarding_cta): reemplazar bloque if/else con llamada a `_build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_cta")`
  - Diagnóstico L1084-1088 (banner Tier C): reemplazar con `_build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_banner")`
  - Diagnóstico L2493-2496 (nota assets): reemplazar con `_build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_assets_note")`
  - Propuesta template L102, L104, L126: los condicionales Tier C deben usar `has_onboarding` (vía variable en el data dict del generador)
  - Log final main.py:3281: condicionar a `not has_onboarding` (este CTA vive en main.py, no en el generador — llamar a la función o inlinear la lógica)

- [ ] 3.4 Verificación de centralización
  - Grep: `grep "_build_onboarding_cta" v4_diagnostic_generator.py` — debe mostrar la definición + todas las llamadas
  - Grep: `grep "Complete el onboarding" v4_diagnostic_generator.py` — debe aparecer solo dentro de `_ONBOARDING_CTA_MESSAGES`, no en lógica dispersa
  - Test: verificar que para `has_onboarding=True, can_show_exact=False` ningún CTA pide "Complete el onboarding"
  - Test: verificar que para `has_onboarding=False, can_show_exact=False` el CTA original sí aparece

### Restricciones

- NO agregar tests e2e (H4 — eso es FASE-4)
- NO ejecutar v4complete (FASE-4)
- Máximo 4 tareas, 0 comandos largos
- Para `propuesta_v6_template.md`: los condicionales son Jinja2/Mustache — verificar sintaxis antes de patchear
- `has_onboarding` se infiere de validation_summary, NO requiere cambio de firma del generador
- La función `_build_onboarding_cta` debe ser pura (sin side effects, sin I/O) para testabilidad
- Los 7 mensajes actuales no son idénticos ("Complete el onboarding", "ejecute onboarding con datos reales", "completar el proceso de onboarding (15 minutos)") — el dict `_ONBOARDING_CTA_MESSAGES` debe preservar las variaciones por surface

### Criterios de completitud

- [ ] `grep "adr_source_label" v4_diagnostic_generator.py` muestra que el discriminador matchea correctamente
- [ ] `grep "_build_onboarding_cta" v4_diagnostic_generator.py` muestra la definición + 3+ llamadas
- [ ] `grep "_ONBOARDING_CTA_MESSAGES" v4_diagnostic_generator.py` muestra el dict de mensajes
- [ ] `grep "Complete el onboarding" v4_diagnostic_generator.py` aparece solo dentro de `_ONBOARDING_CTA_MESSAGES`
- [ ] No hay bloques `if not can_show_exact:` sueltos fuera de `_build_onboarding_cta`
- [ ] 700 tests preexistentes siguen pasando
- [ ] Commit: `fix(H2+BUG-2): unify source taxonomy + centralized onboarding CTA function`

### Próxima sesión

FASE-4: Tests e2e (H4) + ejecución v4complete para Hotel Don Alfonso + análisis post-implementación.

---

## Prompt para delegate_task (auto-contenido)

```
Eres un subagente que trabaja en el proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.

OBJETIVO: Corregir H2 (3 vocabularios incompatibles para fuente del ADR) y BUG-2 (7 CTAs de onboarding siempre visibles) centralizando los CTAs en una función única.

CONTEXTO TÉCNICO:

H2 — Divergencia de taxonomía:
- adr_resolution_wrapper.py:23 define class ADRSource(Enum) con valores: user_provided, regional_v410, legacy_hardcode, web_scraping
- main.py:2163 construye sources = ["Onboarding"] o ["Benchmark"] (PascalCase)
- v4_diagnostic_generator.py:~1244 tiene un discriminador: if adr_source in ("user_provided", "web_scraping"): adr_source_label = "datos del hotel"
- Pero sources trae ["Onboarding"] (PascalCase) → nunca matchea → adr_source_label siempre es "estimado"

BUG-2 — 7 CTAs siempre visibles en 3 superficies:
- v4_diagnostic_generator.py:~1259-1267: show_onboarding_cta = "Complete el onboarding..." (cuando not can_show_exact)
- v4_diagnostic_generator.py:~1084-1088: banner Tier C "ejecute onboarding con datos reales"
- v4_diagnostic_generator.py:~2493-2496: nota assets "ejecute onboarding con datos reales"
- propuesta_v6_template.md: L102, L104, L126: condicionales Tier C
- main.py:3281: log "Para precisar las cifras, ejecute con datos operativos"

FASES ANTERIORES COMPLETADAS:
- FASE-1: harness recibe user_provided_adr y occupancy_source del payload
- FASE-2: proposal generator usa ADR del onboarding; ValidationSummary deriva confidence de adr_source real

CAMBIOS REQUERIDOS:

A) Fix H2 — Discriminador del diagnóstico:
   1. Leer v4_diagnostic_generator.py alrededor de L1244 (buscar "adr_source_label" o "user_provided" o "datos del hotel")
   2. El discriminador recibe sources (lista PascalCase como ["Onboarding"]) pero compara con snake_case
   3. Fix: cambiar la comparación para matchear Vocabulario B:
      if "Onboarding" in sources or "user_provided" in sources:
          adr_source_label = "datos del hotel"
   4. Verificar que adr_source_label ya no cae siempre a "estimado"

B) Fix BUG-2 (Opción C) — Crear función centralizada _build_onboarding_cta:
   1. Inferir has_onboarding de validation_summary: buscar si algún campo tiene sources=["Onboarding"]
   2. Crear función pura _build_onboarding_cta(has_onboarding: bool, can_show_exact: bool, surface: str) -> str
   3. Definir dict _ONBOARDING_CTA_MESSAGES con los 7 mensajes actuales indexados por surface y estado:
      surfaces: "diagnostic_cta", "diagnostic_banner", "diagnostic_assets_note", "proposal_template", "log_final"
      estados: "no_onboarding" (mensaje actual pidiendo onboarding), "has_onboarding" (mensaje nuevo: "✅ Datos operativos verificados. Para obtener la cifra exacta al peso, conecte Google Analytics 4...")
   4. Lógica:
      def _build_onboarding_cta(has_onboarding, can_show_exact, surface="diagnostic_cta"):
          if can_show_exact:
              return ""
          if not has_onboarding:
              return _ONBOARDING_CTA_MESSAGES[surface]["no_onboarding"]
          else:
              return _ONBOARDING_CTA_MESSAGES[surface]["has_onboarding"]
   5. Preservar las variaciones de mensaje actuales por surface (no son idénticos)

C) Refactorizar los 7 CTAs para usar _build_onboarding_cta:
   1. Diagnóstico L1259-1267: reemplazar bloque if/else con _build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_cta")
   2. Diagnóstico L1084-1088: _build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_banner")
   3. Diagnóstico L2493-2496: _build_onboarding_cta(has_onboarding, can_show_exact, "diagnostic_assets_note")
   4. Propuesta template L102, L104, L126: condicionar a has_onboarding via variable en data dict
   5. main.py:3281: condicionar log a not has_onboarding

VERIFICACIÓN:
- grep "adr_source_label" v4_diagnostic_generator.py — discriminador corregido
- grep "_build_onboarding_cta" v4_diagnostic_generator.py — definición + 3+ llamadas
- grep "_ONBOARDING_CTA_MESSAGES" v4_diagnostic_generator.py — dict de mensajes
- grep "Complete el onboarding" v4_diagnostic_generator.py — solo dentro de _ONBOARDING_CTA_MESSAGES
- python3 -m pytest tests/commercial_documents/ -v --timeout=60 -x
- python3 -m pytest tests/financial_engine/ -v --timeout=60 -x

IMPORTANTE: Los line numbers son referencia y pueden haber driftado. Usa grep para encontrar las ubicaciones reales. Lee cada archivo antes de modificarlo. La función _build_onboarding_cta debe ser pura (sin side effects) para testabilidad.
```
