# FASE-2: Cascade Fix — Proposal Generator (H1) + Falsa Confianza ValidationSummary (H3)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)
> **⚠️ FASE DE MAYOR COMPLEJIDAD TÉCNICA**

## Contexto previo

FASE-1 completada: el payload del harness ahora incluye `user_provided_adr` y `occupancy_source`. El handler respeta ambos. `adr_source` en main.py ya lee de `result_data["adr_resolution"]["source"]`.

Resultado de FASE-1:
- `main.py` financial_task payload incluye `user_provided_adr` y `occupancy_source`
- `harness_handlers.py` no sobrescribe occupancy cuando `occupancy_source == "onboarding"`
- `main.py:1861` ya no usa placeholder "handler"

PERO quedan 2 problemas cascada:

1. **H1**: `v4_proposal_generator.py:760` llama `self._get_adr_from_benchmarks(region)` que instancia su propio `RegionalADRResolver` con `user_provided_adr=None` (L1859-1873). La propuesta SIEMPRE muestra $420K.

2. **H3**: `main.py:2162-2163` deriva `confidence=VERIFIED` y `sources=["Onboarding"]` de `adr_from_onboarding_verified` (flag de existencia), pero `value=adr_cop` (L2166) puede ser regional si el harness lo ignoró. Aunque FASE-1 fixea el harness, la lógica de ValidationSummary sigue siendo incorrecta: acopla `confidence`/`sources` a un flag de existencia, no a la fuente real del valor.

## Objetivo de esta fase

1. Hacer que el proposal generator use el ADR del onboarding (no su propio resolver paralelo)
2. Hacer que ValidationSummary derive `confidence` y `sources` de la fuente REAL del valor (`adr_source`), no de un flag de existencia

### Tareas

- [ ] 2.1 Fix H1: Proposal generator ADR from onboarding
  - En `v4_proposal_generator.py:760`: cambiar `_adr_value = self._get_adr_from_benchmarks(region)` para recibir `adr_from_onboarding` del orquestador
  - Opción: agregar parámetro `user_provided_adr` al método que llama L760, o pasar el ADR vía el data dict que recibe el generador
  - En `_get_adr_from_benchmarks` (L1859-1873): aceptar `user_provided_adr` opcional. Si viene y es > 0, usarlo en lugar del resolver regional.
  - Verificar que el caller en main.py pasa `adr_from_onboarding` al proposal generator

- [ ] 2.2 Fix H3: ValidationSummary confidence/sources from real source
  - En `main.py:~2160-2170` (bloque adr_cop ValidatedField):
    - ANTES: `confidence = VERIFIED if adr_from_onboarding_verified else ESTIMATED`
    - DESPUÉS: derivar de `adr_source` real: si `adr_source == "user_provided"`, VERIFIED + ["Onboarding"]; si `adr_source == "regional_v410"`, ESTIMATED + ["Benchmark"]; else ESTIMATED + ["Default"]
  - Aplicar el mismo patrón a occupancy_rate (L~2174) y direct_channel_percentage (L~2186): derivar confidence de la fuente real, no del flag de existencia

- [ ] 2.3 Verificación de invariantes
  - Grep: `grep "adr_from_onboarding_verified" main.py` — el flag puede seguir existiendo pero ya no debe ser la única fuente de `confidence`
  - Grep: `grep "user_provided_adr=None" v4_proposal_generator.py` — no debe aparecer
  - Test: ejecutar `pytest tests/commercial_documents/ -v --timeout=60 -x` (no regresión)

### Restricciones

- NO unificar taxonomía de fuentes (H2 — eso es FASE-3)
- NO fixear CTAs de onboarding (BUG-2 — eso es FASE-3)
- NO agregar tests e2e (H4 — eso es FASE-4)
- Máximo 4 tareas, 0 comandos largos
- El proposal generator es un archivo grande: leer las secciones relevantes antes de patchear
- Si el método que llama `_get_adr_from_benchmarks` tiene una firma compleja, preferir inyectar el ADR vía el data dict existente en lugar de cambiar la firma

### Criterios de completitud

- [ ] `grep "_get_adr_from_benchmarks" v4_proposal_generator.py` muestra que el método acepta `user_provided_adr` o recibe el ADR del caller
- [ ] `grep "user_provided_adr=None" v4_proposal_generator.py` no aparece (o aparece solo en fallback final)
- [ ] `grep "adr_from_onboarding_verified" main.py` muestra que el flag ya no es la única fuente de confidence
- [ ] 700 tests preexistentes siguen pasando
- [ ] Commit: `fix(H1+H3): proposal ADR from onboarding + validation summary real source`

### Próxima sesión

FASE-3: Unificación de taxonomía de fuentes (H2) + fix CTA onboarding redundante (BUG-2).

---

## Prompt para delegate_task (auto-contenido)

```
Eres un subagente que trabaja en el proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.

OBJETIVO: Corregir H1 (consumidor paralelo divergente en proposal generator) y H3 (falsa confianza en ValidationSummary).

CONTEXTO TÉCNICO:

H1 — Proposal generator ADR paralelo:
- v4_proposal_generator.py:760 llama _adr_value = self._get_adr_from_benchmarks(region or 'eje_cafetero')
- v4_proposal_generator.py:1859 define _get_adr_from_benchmarks(self, region) que instancia RegionalADRResolver con user_provided_adr=None
- Resultado: la propuesta SIEMPRE muestra ADR regional ($420K) incluso si el onboarding tiene $330K

H3 — Falsa confianza en ValidationSummary:
- main.py:2107: adr_from_onboarding_verified = adr_from_onboarding is not None and adr_from_onboarding > 0
- main.py:2162: confidence = ConfidenceLevel.VERIFIED if adr_from_onboarding_verified else ConfidenceLevel.ESTIMATED
- main.py:2163: sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]
- main.py:2166: value=adr_cop (que puede ser regional si el harness lo ignoró)
- El flag dice "verified" pero el valor puede no venir del onboarding
- Mismo patrón en occupancy_rate (~L2174) y direct_channel_percentage (~L2186)

FASE-1 YA COMPLETADA:
- main.py financial_task payload ahora incluye user_provided_adr y occupancy_source
- harness_handlers.py respeta occupancy cuando occupancy_source == "onboarding"
- main.py ya lee adr_source de result_data["adr_resolution"]["source"]
- adr_source puede ser: "user_provided", "regional_v410", "legacy_hardcode", "web_scraping" (del enum ADRSource)

CAMBIOS REQUERIDOS:

A) Fix H1 — Proposal generator:
   1. Leer v4_proposal_generator.py alrededor de L760 y L1859-1873
   2. Modificar _get_adr_from_benchmarks para aceptar user_provided_adr opcional:
      def _get_adr_from_benchmarks(self, region, user_provided_adr=None):
          if user_provided_adr and user_provided_adr > 0:
              return user_provided_adr
          # ... existing resolver logic
   3. En L760, pasar el ADR del onboarding al método. Buscar cómo el generador recibe datos del orquestador (probablemente via un data dict o parámetro). Si el ADR no está disponible en ese scope, buscar cómo pasarlo desde main.py.

B) Fix H3 — ValidationSummary:
   1. En main.py:~2160-2170, cambiar la lógica de confidence/sources:
      - Si adr_source == "user_provided": confidence=VERIFIED, sources=["Onboarding"]
      - Si adr_source == "regional_v410": confidence=ESTIMATED, sources=["Benchmark"]
      - Else: confidence=ESTIMATED, sources=["Default"]
   2. Aplicar el mismo patrón a occupancy_rate y direct_channel_percentage (buscar "VERIFIED if" cerca de L2174 y L2186)

VERIFICACIÓN:
- grep "user_provided_adr=None" v4_proposal_generator.py — no debe aparecer (o solo como fallback final)
- grep "adr_from_onboarding_verified" main.py — el flag ya no debe ser la única fuente de confidence
- python3 -m pytest tests/commercial_documents/ -v --timeout=60 -x
- python3 -m pytest tests/financial_engine/ -v --timeout=60 -x

IMPORTANTE: Los line numbers son referencia y pueden haber driftado. Usa grep para encontrar las ubicaciones reales. Lee cada archivo antes de modificarlo. El proposal generator es un archivo grande (~1900+ líneas), leer solo las secciones relevantes.
```
