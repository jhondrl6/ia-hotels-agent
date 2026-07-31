# FASE-7: ADR audit status — cosmetic fix (adr_status: unknown → estimated)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (investigación + fix simple, sin comando largo)

## Contexto previo

- **FASE-0 a FASE-6** ✅ TODAS completadas
- v4complete Hotel Castilla Real: coherence 0.85, 11/11 gates, Tier B
- 6/7 fixes verificados OK

## Problema identificado

En el audit_report de Hotel Castilla Real:
```
"adr_status": "unknown"
```

Pero en la propuesta comercial:
```
| ADR regional promedio | $420,000 COP |
```

**Causa raíz:** `_run_cross_validation()` (v4_comprehensive.py L1445) solo recibe `adr_web` (del scraper) y nunca recibe `benchmark_region`. Cuando `validate_adr()` no tiene scraped_price ni user_input, devuelve `None` → `ConfidenceLevel.UNKNOWN`.

El ADR $420,000 viene de otro pipeline (financial_evidence → GEO-BRIDGE benchmarks → pricing_calculator) — pipelines separados.

**Impacto:** Cosmetic. Los gates pasan, la propuesta es correcta. Solo el campo `adr_status` en el JSON del audit muestra "unknown" en vez de "estimated".

## Objetivo de esta fase

Bridge del benchmark ADR al pipeline de cross-validation del auditor, para que `adr_status` refleje `estimated` cuando se usa ADR regional.

---

### Tareas

- [ ] **T1: Investigar cómo obtener benchmark ADR disponible**

  Investigar en `v4_comprehensive.py` y `v4audit` command flow:
  - ¿Hay alguna forma de obtener el `benchmark_cop` o `adr_cop` desde `audit_context` o `args`?
  - ¿El auditor recibe `region` o `hotel_type` como input?
  - ¿existe algún resolver de ADR regional ya en el auditor?

  Comandos de investigación:
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  grep -n "def run\|def execute\|audit_context\|benchmark\|adr_cop" \
      modules/auditors/v4_comprehensive.py | head -30

  grep -n "benchmark\|region\|adr" \
      modules/auditors/v4_comprehensive.py | grep -i "def\|class" | head -15
  ```

- [ ] **T2: Determinar estrategia de fix**

  Opciones identificadas (T1 determina cuál aplica):

  **Opción A (más simple):** Si `_run_cross_validation` recibe `region` o puede inferirla:
  - Agregar `benchmark_region` a `validate_adr()` cuando no hay scraped_price
  - Inyectar el benchmark regional directamente

  **Opción B (más acoplado):** Si hay un `AuditContext` con `hotel_context`:
  - Leer `benchmark_adr` del contexto del auditor
  - Pasar `benchmark_region=float` a `validate_adr()`

  **Opción C (no fix):** Si no hay forma limpia de obtener el benchmark en el auditor:
  - Marcar como `WONTFIX` — el ADR de la propuesta es correcto, el `unknown` en audit es cosmetic
  - Documentar en notas técnicas

- [ ] **T3: Implementar fix (si A o B viable)**

  Si opción A o B:
  ```bash
  # Patch mínimo en _run_cross_validation
  # 1. Agregar benchmark_region a validate_adr() call
  adr_dp = self.cross_validator.validate_adr(
      scraped_price=str(adr_web) if adr_web else None,
      benchmark_region=benchmark_adr_float,  # NUEVO
  )
  ```

  Si opción C:
  - Agregar nota en el audit report explicando por qué `adr_status: unknown` es esperado
  - No modificar código del generador

- [ ] **T4: Tests de regresión**

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe -m pytest tests/auditors/test_v4_comprehensive.py -v -x 2>&1 | head -40
  ```

- [ ] **T5: Actualizar checklist + log_phase**

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-7 \
      --desc "ADR audit status cosmetic fix" \
      --archivos-mod "modules/auditors/v4_comprehensive.py" \
      --tests "N" --check-manual-docs
  ```

### Restricciones

- NO modificar el pipeline de financial_evidence (propuesta) — está funcionando correctamente
- NO ejecutar v4complete en esta fase
- Máximo 60 iteraciones

### Criterios de completitud

- [x] ADR audit status documentado (fix o wontfix) — **FIX IMPLEMENTADO**
- [x] Si fix: tests pasan — **134 passed**
- [x] Checklist actualizado
- [x] Estado en REGISTRY

### Resolución

**Causa raíz:** `_run_cross_validation()` (v4_comprehensive.py L1451) solo recibía `adr_web` del schema `priceRange`, sin acceso al benchmark regional.

**Fix implementado (Opción A):**
1. Import `RegionalADRResolver` en `v4_comprehensive.py`
2. `_resolve_regional_adr(gbp_address)` — infiere región de la dirección GBP y resuelve ADR benchmark via `RegionalADRResolver`
3. Bridge al `validate_adr()` call con `benchmark_region=`
4. Cache por sesión de auditor para evitar resoluciones redundantes

**Resultado:** `adr_status: unknown` → `adr_status: estimated` cuando no hay scraped_price pero sí benchmark regional disponible.

**Verificación:**
- Pereira → 420,000 COP ✅
- Medellín → 420,000 COP ✅
- None address → 420,000 COP (default fallback) ✅

### Archivos involucrados

| Archivo | Acción |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | ✅ FIJO — import + _resolve_regional_adr() + validate_adr() bridge |
| `evidence/FASE-PENDIENTE-V4COMPLETE/v4_audit/audit_report_20260529_133633.json` | Lectura (evidencia baseline) |

### Próxima sesión

```
Carga y ejecuta .opencode/plans/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-RELEASE.md
```
