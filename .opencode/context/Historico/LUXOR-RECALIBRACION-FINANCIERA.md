# CONTEXTO HOTEL LUXOR — Recalibración Financiera + Plan FASE A Benchmarking

**Fecha:** 2026-07-16
**Sesión:** Validación contra código en vivo + decisión de benchmarking
**Estado:** Diagnóstico + Propuesta requieren recalibración antes de entrega.
Hotel Luxor NO verá el documento actual. Se inicia FASE A de benchmarking
con N=5 hoteles para validar patrón "transit vs destino" antes de tocar
el motor.
**Versión motor:** iah-cli v4.61.0 (HOOK-PDF post-implementation)
**Skill cargado:** `iah-cli-execution-conventions` (v1.0.0)

---

## 0. ACTUALIZACIONES POSTERIORES (mismo día, sesión extendida)

Esta sección se actualizó después del documento original. Lo cambió:

  - **Pregunta 6.1 RESUELTA** (2026-07-16, mismo día): el hotel Luxor NO ha
    visto el documento `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260710_101420.md`,
    y por ahora NO se lo voy a presentar. Recalibración puede hacerse
    offline antes de cualquier contacto.

  - **Decisión de benchmarking (2026-07-16)**: en lugar de presentar el
    documento recalibrado al Luxor o modificar `scenario_calculator.py`
    directamente, se inicia FASE A con **N=5 hoteles** para validar
    cualitativamente si el patrón "hotel de paso sub-25 habitaciones"
    es un caso aislado del Luxor o un patrón generalizable.

  - **Creado `data/hotel_observations/`** (mismo día): nuevo directorio
    con esquema JSON Schema, observación del Luxor cargada, formulario
    estandarizado para capturar los 5 datos canónicos. Documento en
    `data/hotel_observations/README.md` + formulario en
    `data/hotel_observations/forms/contact_form_ES.md`.

  - **El plan de "sesión nueva para correr `onboard` + `v4complete`"**
    descrito en este documento (sección 7) queda **DIFERIDO** hasta
    que FASE A confirme el patrón. Sin evidencia empírica, modificar
    el motor o reescribir la propuesta comercial sería prematuro.

  - **Razón principal del cambio de estrategia**: contactar al Luxor para
    presentarle una propuesta recalibrada AHORA tiene dos riesgos:
    (a) el Luxor es caso aislado y la recalibración resulta incorrecta,
    (b) el mercado colombiano de hoteles boutique sub-25 es heterogéneo
    y no admite una regla única. Mejor validar el patrón primero con
    5 hoteles antes de comprometerse con una narrativa.

---

## 1. RESUMEN EJECUTIVO

El Hotel Luxor hizo **contacto directo** y entregó datos reales operacionales.
Estos datos **invalidad la cifra de fuga financiera** publicada en el documento
`output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260710_101420.md` (línea 100:
~$2.993.356 - $4.490.035 COP/mes).

**Conclusión:** la cifra del documento es TIER B (benchmark regional aplicado
al perfil del hotel), no TIER A (datos reales del hotel). Al cruzar con datos
reales, la cifra colapsa 5-15× y el escenario se invierte: de "pérdida" a
"ganancia neta pequeña" (~-$213K COP/mes, valor negativo = ganancia).

**Implicación estratégica:** la propuesta comercial al Luxor debe REESCRIBIR
la narrativa. En lugar de vender "estás perdiendo $3M/mes en comisiones de
OTAs", debe vender **"estás dejando de capturar demanda porque tu hotel
prácticamente no aparece en el mercado digital"**. Son dos argumentos
distintos con magnitudes muy distintas.

---

## 2. DATOS REALES DEL HOTEL LUXOR (entregados por contacto directo)

| Campo | Valor | Unidad |
|-------|-------|--------|
| Número de habitaciones | 21 | hab |
| Reservas mensuales promedio | 15 | reservas/mes |
| Valor promedio por reserva | $200.000 | COP/reserva |
| Porcentaje canal directo | 60 | % |
| Porcentaje OTAs (implícito) | 40 | % |

**Nota:** NO se entregó ADR como ADR; se entregó valor promedio por reserva
que en este caso es equivalente (single-rate, no segmento mixto).

**Métricas derivadas:**

```
Revenue bruto/mes                  = 15 × $200.000          = $3.000.000 COP
Revenue canal directo (60%)        = 0.60 × $3M             = $1.800.000 COP
Revenue OTAs (40%)                 = 0.40 × $3M             = $1.200.000 COP
Noches OTA/mes                     = 15 × 0.40              = 6 noches
Occupancy real                     = 15 / (21 × 30)         = 2.38 %
```

---

## 3. VALIDACIÓN CONTRA CÓDIGO EN VIVO (doctrina "validate against live code")

### 3.1 Benchmark regional aplicable

Archivo: `data/benchmarks/regional_adr_2026.json` (versión 1.0.0, actualizado 2026-05-04)

```json
"eje_cafetero": {
  "boutique_10_25": {
    "adr_cop": 420000,
    "occupancy_rate": 0.512,
    "rooms_range": [10, 25]
  }
}
```

**Match:** Luxor tiene 21 habitaciones → entra en `boutique_10_25`.
**Región inferida:** Eje Cafetero (no explícita del usuario, inferida por el
benchmark aplicado en el documento).

### 3.2 Comparación Luxor real vs Benchmark regional

| Métrica | Luxor Real | Benchmark Eje Cafetero boutique_10_25 | Gap |
|---------|-----------|---------------------------------------|-----|
| ADR | $200.000 | $420.000 | **-52%** (Luxor cobra 52% menos) |
| Occupancy | 2.38% | 51.2% | **-95%** (Luxor opera a 1/22 del benchmark) |
| Revenue/hab/mes | $142.857 | $644.800 | **-78%** |

**Lectura crítica:** El Luxor NO opera en el segmento "hotel boutique
competitivo del Eje Cafetero". Opera en un régimen muy distinto — probablemente
hotel de paso, hostal, o establecimiento de baja rotación donde el ADR es bajo
y la ocupación es muy baja. El benchmark regional aplicado al perfil de la
categoría es **conceptualmente incorrecto** para este hotel.

### 3.3 Fórmula del motor financiero (scenario_calculator.py L215-292)

**Escenario Conservador:**
```python
conservative_occupancy = hotel_data.occupancy_rate * 0.90
max_ota_commission = 0.18
minimal_improvement = 0.05  # shift OTA→direct

noches_OTA = rooms × 30 × occupancy_rate × (1 - direct_channel_pct)
current_ota_commission_loss = noches_OTA × adr_cop × ota_commission_rate
potential_shift = noches_OTA × minimal_improvement
savings = potential_shift × adr_cop × max_ota_commission
monthly_loss = current_ota_commission_loss - savings
```

**Escenario Realista:**
```python
occupied_nights = rooms × 30 × occupancy_rate
ota_bookings = occupied_nights × (1 - direct_channel_pct)
current_ota_commission_loss = ota_bookings × adr_cop × ota_commission_rate
moderate_shift = 0.10
savings = ota_bookings × moderate_shift × adr_cop × ota_commission_rate
ia_visibility_boost = occupied_nights × 0.05 × adr_cop
monthly_loss = current_ota_commission_loss - savings - ia_visibility_boost
```

**Escenario Optimista:**
```python
optimistic_occupancy = min(occupancy_rate × 1.05, 1.0)
optimistic_shift = 0.20
ia_visibility_boost = 0.10
# Similar structure with optimistic params
```

### 3.4 Cálculo con datos REALES del Luxor

```
Datos de entrada: rooms=21, adr=$200.000, occupancy=0.0238, direct=0.60,
ota_commission=0.15

CONSERVADOR:
  occupancy_real × 0.90 = 0.02142
  noches_OTA = 21 × 30 × 0.0238 × 0.40 = 6.0
  ota_commission_loss = 6 × $200.000 × 0.15 = $180.000
  savings = 6 × 0.05 × $200.000 × 0.18 = $10.800
  PÉRDIDA CONSERVADOR = $180.000 - $10.800 = $169.200 COP/mes

REALISTA:
  noches_OTA = 6 (mismo, sin factor 0.90)
  ota_commission_loss = 6 × $200.000 × 0.15 = $180.000
  savings = 6 × 0.10 × $200.000 × 0.15 = $18.000
  ia_boost = (21 × 30 × 0.0238) × 0.05 × $200.000 = 15 × 0.05 × $200.000 = $150.000
  PÉRDIDA REALISTA = $180.000 - $18.000 - $150.000 = $12.000 COP/mes
  (prácticamente neutral — esto es lo que el documento NO dice)

OPTIMISTA:
  optimistic_occupancy = min(0.0238 × 1.05, 1.0) = 0.02499
  noches_OTA = 21 × 30 × 0.02499 × 0.40 = 6.3
  ota_commission_loss = 6.3 × $200.000 × 0.15 = $189.000
  savings = 6.3 × 0.20 × $200.000 × 0.15 = $37.800
  ia_revenue = (21 × 30 × 0.02499) × 0.10 × $200.000 = 15.7 × 0.10 × $200.000 = $314.790
  PÉRDIDA OPTIMISTA = $189.000 - $37.800 - $314.790 = -$163.590 COP/mes
  → NET GAIN (ganancia neta, no pérdida)
```

**Resumen de escenarios con datos reales Luxor:**

| Escenario | Probabilidad | Pérdida/Ganancia mensual | Base |
|-----------|--------------|--------------------------|------|
| Conservador | 70% | **+$169.200 COP** (pérdida) | 90% occ, 18% comisión, 5% shift |
| Realista | 20% | **+$12.000 COP** (pérdida neutra) | 100% occ, 10% shift, 5% IA boost |
| Optimista | 10% | **-$163.590 COP** (ganancia neta) | 105% occ, 20% shift, 10% IA boost |

**Esperanza matemática ponderada:**
E[fuga] = 0.70 × $169.200 + 0.20 × $12.000 + 0.10 × (-$163.590)
       = $118.440 + $2.400 - $16.359
       = **$104.481 COP/mes de pérdida esperada**

NO $3.000.000 COP/mes como dice el documento.

---

## 4. DE DÓNDE SALE LA CIFRA DE LA LÍNEA 100 (INVESTIGACIÓN)

El documento dice (línea 113): "La cifra de revenue perdido está calculada
con benchmarks reales de la región."

**Verificación con código (calculator_v2.py + scenario_calculator.py):**

Si se aplica el benchmark regional (ADR=$420K, occ=51.2%) con el perfil
del Luxor (21 hab, 60% directo):

```
CONSERVADOR:
  occupancy = 0.512 × 0.90 = 0.4608
  noches_OTA = 21 × 30 × 0.512 × 0.40 = 129.02
  ota_commission_loss = 129.02 × $420.000 × 0.15 = $8.127.000
  savings = 129.02 × 0.05 × $420.000 × 0.18 = $487.620
  PÉRDIDA = $8.127.000 - $487.620 = $7.639.380 COP/mes
```

Tampoco cuadra con la línea 100 ($2.99M-$4.49M).

**Hipótesis:** la cifra del documento fue producida por una versión anterior
del motor, con parámetros diferentes (probablemente `ota_commission_rate=0.20`
o similar), o fue calculada manualmente con una metodología distinta a la del
código actual. **En cualquier caso, NO se reproduce con calculator_v2.py ni
con scenario_calculator.py actuales.**

Esto NO es necesariamente un bug del motor — es que el documento se generó
bajo condiciones que el código actual no reproduce.

---

## 5. ANÁLISIS ESTRATÉGICO: POR QUÉ EL ARGUMENTO COMERCIAL CAMBIA

### 5.1 Lo que dice el documento actual (argumento "comisión OTA")

> "Cada mes, viajeros reservan en su zona a través de Booking, Expedia y otros
> intermediarios. Cada reserva cobra una comisión promedio del 15-25%.
> Mientras más reservas pasan por intermediarios, menos quedan en la caja del
> hotel. La cifra arriba es nuestra mejor estimación de cuánto dinero se
> escapa cada mes por fugas en su visibilidad digital."

**Cifra:** ~$2.99M-$4.49M COP/mes
**Mecánica:** comisión sobre intermediarios existentes
**Validación:** NO se sostiene con datos reales del Luxor
**Tamaño real con datos Luxor:** ~$169K-$180K COP/mes (escenario conservador)

### 5.2 Lo que el argumento DEBERÍA ser (argumento "demanda no activada")

El Luxor opera a 2.4% de ocupación vs benchmark regional de 51.2%.
Eso significa que **hay ~49 puntos porcentuales de demanda potencial no
capturada**.

```
Demanda potencial al nivel benchmark:
  noches_potenciales = 21 × 30 × 0.512 = 322.6 noches/mes
  noches_reales = 15
  noches_no_capturadas = 322.6 - 15 = 307.6 noches/mes
  revenue_potencial = 307.6 × $200.000 = $61.523.000 COP/mes

Si capturáramos el 10% de esa demanda no activada:
  noches_recuperadas = 30.76
  revenue_recuperado = 30.76 × $200.000 = $6.152.300 COP/mes
```

**Cifra:** hasta $6M COP/mes en revenue incremental (no todo recuperable,
pero el upside ES de ese orden)
**Mecánica:** demanda del mercado que no llega al Luxor por falta de
visibilidad digital
**Validación:** coherente con el gap observado vs benchmark regional
**Riesgo:** depende de que el mercado EXISTA y esté siendo capturado por
competidores (esto requiere el audit con Places API + scraping, que es
lo que hace v4audit).

### 5.3 Cuál es el mejor argumento para el Luxor

| Argumento | Cifra | Verificable | Persuasivo | Honesto |
|-----------|-------|-------------|------------|---------|
| Comisión OTA | $169K-$180K | ✅ Sí, con datos reales | ⚠️ Bajo (poco dinero) | ✅ Sí |
| Demanda no activada (10% del gap) | ~$6.15M | ⚠️ Requiere audit | ✅ Muy alto | ⚠️ Especulativo (hay que verificar mercado) |
| Demanda no activada (3% del gap, conservador) | ~$1.85M | ⚠️ Requiere audit | ✅ Alto | ✅ Si se demuestra mercado |

**Recomendación:** vender el argumento "demanda no activada" PERO anclado a
evidencia del audit (Places API + scraping de competidores en la zona).
Sin esa evidencia, la cifra es especulativa.

---

## 6. DECISIÓN PENDIENTE CRÍTICA

### 6.1 ¿El hotel Luxor YA VIO el documento actual?

Esto cambia TODO el plan:

- **Si NO lo ha visto** → corregir antes de entregar (flujo limpio).
- **Si YA lo vio y avanzó con esa cifra** → honestidad exige REABRIR la
  conversación, no enviar un "corregido silenciosamente" (memory: "Post 019
  incident — pasado afirmativo requiere evidencia respaldable").

**Esta respuesta del usuario bloquea cualquier plan de reescritura.**

### 6.2 Tres opciones de reescritura (para cuando se levante el bloqueo 6.1)

**OPCIÓN 1 — Reescribir sección 3 con cifras reales (recomendada)**
- Línea 100 → "Fuga conservadora: $150K-$400K COP/mes por comisión OTAs.
  Si sumamos demanda no activada (ocupación actual 2.4% vs benchmark
  regional 51.2%), el potencial recuperable estimado es de hasta $X COP/mes
  en revenue incremental — no todo es comisión, la mayor parte es demanda
  no capturada."
- Pros: honesto, defendible, eleva la propuesta.
- Contras: implica re-entrega del documento.

**OPCIÓN 2 — Vender "demanda no activada" como argumento principal**
- Pros: más persuasivo para hotel que claramente necesita visibilidad.
- Contras: requiere audit de Places API + scraping previo para tener
  evidencia de que el mercado existe en la zona.

**OPCIÓN 3 — Onboarding + recalcular con Tier A**
- Ejecutar `python main.py onboard` con los 4 datos reales → calculator_v2
  genera Tier A (confidence ≥0.9). Resultado será ~$180K/mes en comisión
  OTA, NO $3M/mes.
- Pros: datos limpios, confianza VERIFIED, coherencia alta.
- Contras: la propuesta pierde potencia persuasiva si solo se ancla a
  comisión OTA.

### 6.3 Recomendación combinada

OPCIÓN 1 + OPCIÓN 2 combinadas:
1. **En esta sesión (cuando se levante el bloqueo 6.1):** decidir qué decir
   y reescribir sección 3 con la cifra real + el argumento de demanda no
   activada (anclado a evidencia cuando se obtenga).
2. **En sesión nueva (FASE 2):** correr `onboard` con los 4 datos para tener
   memoria persistente, regenerar propuesta con Tier A, y entregar al hotel
   con el lenguaje correcto.

**Restricción operacional (USER PROFILE memory):** "una fase = una sesión".
La ejecución va en sesión nueva; esta sesión solo planifica.

---

## 7. IMPLEMENTACIÓN: PASOS EN SESIÓN NUEVA (FASE 2)

### 7.1 Pre-condiciones

- [ ] Bloqueo 6.1 resuelto (¿hotel vio o no el documento?)
- [ ] Confirmar región del Luxor (asumido Eje Cafetero por inferencia)
- [ ] Verificar que el documento vigente es el del 2026-07-10 (vigencia OK:
      6 días < umbral 20 días según AGENTS.md §Criterios-de-Exito)

### 7.2 Comandos a ejecutar (en sesión nueva)

```bash
# 1. Onboarding con datos reales (Tier A)
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py onboard --rooms 21 \
  --monthly-reservations 15 \
  --avg-reservation-cop 200000 \
  --direct-channel-pct 60

# 2. Regenerar análisis completo con datos Tier A
python main.py v4complete --url <URL_HOTEL_LUXOR> --recalculate

# 3. Validar coherence score (debe ser ≥0.8)
python scripts/run_all_validations.py --quick

# 4. Verificar gates de publicación (FASE 4.5)
cat output/v4_complete/*/gate_report.json

# 5. Si coherence OK, regenerar documentos comerciales
python main.py execute --url <URL_HOTEL_LUXOR> --package starter_geo
```

### 7.3 Validaciones post-ejecución

- [ ] Tier A confirmado (no Tier B/C) en financial_evidence_tier
- [ ] Coherence score ≥0.8
- [ ] Hard contradictions = 0
- [ ] Evidence coverage ≥95%
- [ ] Critical recall ≥90%
- [ ] Sección 3 del documento reescrita con cifra real + argumento demanda no activada
- [ ] Línea 113 eliminada o reescrita (ya no aplica el "complete el onboarding")

### 7.4 Documentación a actualizar (post-implementación)

- [ ] CHANGELOG.md con entrada sobre recalibración Luxor
- [ ] REGISTRY.md via `log_phase_completion.py`
- [ ] Plan README.md si aplica
- [ ] 06-checklist-implementacion.md si aplica
- [ ] Sincronizar versiones (`python scripts/sync_versions.py`)

---

## 8. LECCIONES OPERATIVAS (para futuros hoteles pequeños)

### 8.1 Pitfall identificado: benchmark ≠ realidad operativa

**Cuándo aplica:** hoteles con `rooms < 25` que operan con `occupancy < 10%`
(perfil "sub-benchmark extremo").

**Síntoma:** la cifra de fuga calculada con benchmark regional es 5-15×
mayor que la calculada con datos reales del hotel.

**Causa raíz:** el motor usa `data/benchmarks/regional_adr_2026.json` que
representa el segmento competitivo, no el segmento operativo real del hotel.

**Mitigación futura:** agregar check pre-cálculo que detecte:
- Si `occupancy_real < 0.10` Y `rooms < 25` → activar modo "demanda no
  activada" en lugar de modo "comisión OTA".
- El modo "demanda no activada" usa el gap vs benchmark como variable
  principal, no la comisión sobre noches reales.

### 8.2 Pitfall identificado: el documento "convence" con cifras infladas

**Cuándo aplica:** cualquier hotel que recibe un diagnóstico v4 antes de
haber hecho onboarding.

**Síntoma:** cifras de fuga financiera que parecen "demasiado buenas para
ser verdad" para el perfil operativo real del hotel.

**Causa raíz:** el hook (FASE 1) usa benchmarks para generar rango
estimado. Sin onboarding, no hay datos del hotel que contradigan el
benchmark. El hotel firma una expectativa inflada.

**Mitigación futura:** incluir en el hook una nota explícita del orden de
magnitud esperado para el perfil del hotel, basada en heurística:

```
Si rooms < 25 y occupancy < 10% → nota: "el upside principal NO es
comisión de OTAs, es demanda no activada. Verificar con audit antes
de comprometerse con cifras."
```

### 8.3 Doctrina confirmada: "validate against live code"

El skill `iah-cli-execution-conventions` (v1.0.0) confirma:

> "When the user says 'valida que [archivo] se haya cumplido a cabalidad'
> or 'verifica la implementación', the meaning is:
> - Cross-check the claim against the LIVE codebase, params, and tests
> - Do NOT accept the document (plan, checklist, fase prompt) as truth
> - If code and document disagree, code wins; the document is updated
>   to match"

**Aplicado en este caso:** el documento decía $2.99M-$4.49M, el código
dice ~$169K (conservador) o ~$12K (realista) o -$163K (optimista, neto).
**El código gana.** El documento se actualizará para reflejar la realidad
cuando se levante el bloqueo 6.1.

---

## 9. REFERENCIAS CRUZADAS

### 9.1 Archivos del proyecto consultados

- `AGENTS.md` (v4.61.0, líneas 1-294) — contexto global, flujo v4
- `modules/financial_engine/calculator_v2.py` (499 líneas) — fachada del motor
- `modules/financial_engine/scenario_calculator.py` (534 líneas, leídas 1-500) — fórmula real
- `data/benchmarks/regional_adr_2026.json` (55 líneas, v1.0.0) — benchmark regional
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260710_101420.md` (339 líneas,
  consultadas 95-154) — documento a recalibrar

### 9.2 Skills cargados

- `iah-cli-execution-conventions` (v1.0.0) — convenciones curator iah-cli

### 9.3 Memory entries relevantes (del profile)

- WSL safety guard pitfall (sandbox bloquea destructivos)
- iah-cli financial_engine benchmark limitation (entrada consolidada 2026-07-16)
- Prompt engineering audit (5 checks)
- Post 019 incident (pasado afirmativo requiere evidencia)
- User references `.agents/workflows/*.md` → load skill FIRST
- Push strategy (merge --no-ff)

### 9.4 Pitfalls del skill cargados

- "Validate against live code" (HARD) — código gana sobre documento
- "Phase tracking" — REGISTRY + checklist + plan README en sync
- "TIER 1 vs TIER 2 documentation" — log_phase solo para fases A-D, no TIER 2
- "v4_complete output structure" — Tier pipeline (B/C pre-Express, A post-Express)
- "WSL venv strategy" — usar `./venv/Scripts/python.exe` para project scripts

---

## 10. ESTADO DE LA SESIÓN Y PRÓXIMOS PASOS

**Estado:** Sesión de planificación cerrada (no se ejecutaron comandos del
flujo v4). Solo se inspeccionó código en vivo y se calcularon escenarios
manualmente.

**Decisiones tomadas:**
1. Memoria consolidada — PENDIENTE por el usuario (bloqueo técnico por
   capacidad del store, ver §10.1 abajo)
2. Carpeta `data/hotel_observations/` creada con esquema + observación
   Luxor + formulario estandarizado
3. FASE A de benchmarking planificada con N=5 hoteles
4. Ejecución del flujo v4 queda DIFERIDA hasta cierre de FASE A

### 10.1 Bloqueo de memoria — RESUELTO (decisión del usuario 2026-07-16)

El intento de consolidar la entrada #2 de memory (iah-cli dinámico,
225 chars) con la lección Luxor (~700 chars) y remover 2 entradas menos
críticas (sync_versions pitfall, Instagram note) **excedió la capacidad**
del store de memoria (2,200 chars total). La herramienta rehusó aplicar
los cambios tras 4 intentos.

**Decisión del usuario (2026-07-16): "Olvidar memoria y confiar solo en el
archivo de contexto. El archivo es la fuente durable; memoria es cache de
hechos muy recurrentes."**

Implicaciones:
  - **NO se reintentará la consolidación de memoria.** El archivo
    `.opencode/context/LUXOR-RECALIBRACION-FINANCIERA.md` y el directorio
    `data/hotel_observations/README.md` son las fuentes durables de la
    lección Luxor.
  - **Memoria queda en su estado actual (7 entradas, 2,184/2,200 chars).**
    Las 7 entradas existentes representan hechos recurrentes (WSL guard,
    prompt engineering audit, Post 019 incident, `.agents/workflows` load
    pattern, etc.) — esos SÍ justifican estar en memoria.
  - **Lección Luxor NO estará en memory.** En sesiones futuras donde el
    usuario NO cargue este contexto, el agente no recordará el caso Luxor.
    Aceptable porque el contexto está en `.opencode/context/` (cargable
    por convención del repo) y en `data/hotel_observations/` (parte del
    dataset del proyecto).
  - **Doctrina confirmada**: para hechos muy recurrentes → memory. Para
    análisis de un caso específico → context files.

### 10.2 Bloqueo activo al cierre de sesión

- Pregunta 6.1 RESUELTA: hotel Luxor NO ha visto el documento y NO se
  lo presentaré por ahora (decisión 2026-07-16).
- FASE A de benchmarking NO iniciada: pendiente de que el usuario
  recopile los 5 datos de los 5 hoteles (criterio de parada definido).

**Próximos pasos cuando se complete FASE A (N=5 hoteles):**

  1. Análisis cuantitativo del patrón paso vs destino (sesión nueva).
  2. Si patrón CONFIRMADO → FASE B (N=15-20, calibración).
  3. Si patrón NO confirmado → replantear hipótesis antes de tocar motor.
  4. Solo después de FASE B → modificar `scenario_calculator.py` (con plan,
     no directo) y/o recalibrar `data/benchmarks/regional_adr_2026.json`.

**Próximos pasos inmediatos (esta semana, por el usuario):**

  1. Identificar 5 hoteles contactables vía dueño/gerente.
  2. Estratificar: 2 de paso pequeños + 2 destino pequeños + 1 destino
     mediano (recomendación de `forms/contact_form_ES.md`).
  3. Preparar las llamadas usando el formulario estandarizado.
  4. Recopilar los 5 datos canónicos + clasificación paso/destino.
  5. Agregar cada observación a `data/hotel_observations/observations.json`
     siguiendo el README actualizado (procedimiento de 7 pasos).
  6. Validar cada nueva entrada con el script de jsonschema (incluido
     en el README).

---

**FIN DEL CONTEXTO**

Próxima acción del usuario: Responder pregunta 6.1 (¿hotel Luxor ya vio
el documento actual?). Esa respuesta desbloquea la planificación de la
recalibración.