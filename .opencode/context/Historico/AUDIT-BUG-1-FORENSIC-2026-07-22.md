# Auditoría Forense BUG-1 — ADR de Onboarding Ignorado

> **Fecha auditoría**: 2026-07-22
> **Documento auditado**: `/.opencode/context/Historico/BUGS-ONBOARDING-ADR-TEMPLATE-2026-07-22.md`
> **Alcance**: Validar cada claim de BUG-1 contra código vivo, trazar el flujo completo
> YAML → harness → resolver → escenarios → JSON → ValidationSummary → tests.
> Buscar consumidores paralelos, divergencias de claves, procedencia/confianza falsa
> y riesgos del fix de una línea. **Sin implementación.**

---

## 1. Veredicto Global

**BUG-1 es REAL, REPRODUCIBLE y MÁS GRAVE de lo que el documento reporta.**

El documento describe correctamente el síntoma y la cadena causal de 5 pasos,
pero omite **4 hallazgos sistémicos críticos** que el fix de "1 línea" no resuelve
y que perpetúan el mismo defecto en otros puntos del pipeline:

| # | Hallazgo sistémico | Severidad |
|---|--------------------|-----------|
| H1 | **Consumidor paralelo divergente en proposal generator** — `_get_adr_from_benchmarks()` (L1859-1873) usa su propio `RegionalADRResolver` con `user_provided_adr=None`. El ADR de la propuesta comercial SIEMPRE será regional ($420K), independiente del fix del harness. | ALTA |
| H2 | **Divergencia de claves de fuente (snake_case vs PascalCase vs mixto)** — 3 vocabularios incompatibles para el mismo concepto: `ADRSource.USER_PROVIDED.value="user_provided"` vs `sources=["Onboarding"]` vs `input_data.adr_source="handler"`. El discriminador `if adr_source in ("user_provided", "web_scraping")` (v4_diagnostic_generator.py:1244) **nunca coincide** con la PascalCase que emite main.py. | ALTA |
| H3 | **Falsa confianza + falsa procedencia en ValidationSummary** — Cuando `adr_from_onboarding=330000` existe pero el valor final es 420000, se etiqueta `confidence=VERIFIED` + `sources=["Onboarding"]` para `value=420000`. La divergencia entre `value` y la realidad de su fuente es estructural. | ALTA |
| H4 | **Sin tests end-to-end del path onboarding → harness → JSON** — Tests cubren `adr_resolution_wrapper` aislado (test_fallback_chain_honesto, test_adr_resolution_wrapper) pero NINGUNO asserta que el `payload` enviado al `harness.run_task(...)` incluya `user_provided_adr` cuando hay YAML. | MEDIA |

Adicionalmente, el claim del fix de **"1 línea"** es insuficiente: corregir solo
`main.py:1797-1806` deja intactos H1, H2, H3 (parcialmente) y no resuelve la
**divergencia de fuentes** que es la raíz del problema.

---

## 2. Traza Forense Paso a Paso

### 2.1 Carga del YAML de onboarding — CONFIRMADO

| Claim del doc | Verificación | Estado |
|---------------|--------------|--------|
| `main.py:1739 → _load_latest_onboarding_data(args.url, hotel_name)` | L1739 exacto | ✅ CONFIRMADO |
| `main.py:1746 → datos_operativos = onboarding_data.get('datos_operativos', {})` | L1746 exacto | ✅ CONFIRMADO |
| `main.py:1747 → rooms = datos_operativos.get('habitaciones', 10)` | L1747 exacto | ✅ CONFIRMADO |
| `main.py:1761 → canal_directo = datos_operativos.get('canal_directo_pct', 20.0)` | L1761 exacto | ✅ CONFIRMADO |
| `main.py:1765 → adr_from_onboarding = datos_operativos.get('valor_reserva_cop')` | L1765 exacto. **Nota**: el YAML tiene `valor_reserva_cop: 330000` Y `adr_cop: 330000` (L9 del YAML). El código **solo lee `valor_reserva_cop`**, ignora la clave `adr_cop` que semánticamente debería ser el campo canónico. | ✅ CONFIRMADO + nota |
| `_load_latest_onboarding_data` busca `output/clientes/{slug}_onboarding.yaml` con frescura <24h | L3338-3367: `output_dir = Path("output/clientes")`, `generate_slug(hotel_name)`, `timedelta(hours=24)` | ✅ CONFIRMADO |
| YAML tiene `valor_reserva_cop: 330000` y `adr_cop: 330000` (Pereira, eje_cafetero) | `donalfonsohotel_onboarding.yaml` L7 y L9 | ✅ CONFIRMADO |
| Log muestra "✅ Onboarding data loaded: 6 campos confirmados" | `ejecucion-con-datos-reales.log:159` | ✅ CONFIRMADO |

**Sub-observación — divergencia interna YAML**: El campo `valor_reserva_cop`
representa "valor promedio de reserva" (precio promedio por reserva), mientras
`adr_cop` es "Average Daily Rate" (precio promedio por noche). Para un hotel
con `reservas_mes=140` y `habitaciones=11`, `reservas_mes / (rooms*30) = 0.424`
noches/mes-habitación, lo que implica reservas de ~1 noche promedio. En ese
caso `valor_reserva_cop ≈ adr_cop`. **PERO si las reservas son multi-noche,
`valor_reserva_cop > adr_cop`**. El código usa `valor_reserva_cop` como ADR
en el harness, lo cual es **semánticamente incorrecto** en el caso general.
El campo canónico `adr_cop` del YAML es ignorado.

### 2.2 Construcción del payload del harness — CONFIRMADO

| Claim del doc | Verificación | Estado |
|---------------|--------------|--------|
| `main.py:1797-1806 → financial_task = AgentTask(payload={...})` sin `user_provided_adr` | L1797-1807. Payload exacto: `rooms, region, occupancy_rate, direct_channel_percentage, hotel_id, hotel_name`. **NO incluye `user_provided_adr`** | ✅ CONFIRMADO |
| `main.py:1810 → financial_result = harness.run_task(financial_task)` | L1810 exacto | ✅ CONFIRMADO |
| `main.py:1814 → adr_cop = result_data["adr_cop"]` | L1814 exacto | ✅ CONFIRMADO |
| `main.py:1861 → adr_source = result_data.get("adr_source", "handler")` | L1861 exacto. **Detalle crítico**: el handler **NO** retorna clave top-level `adr_source` (solo `adr_resolution.source`), por lo que `result_data.get("adr_source", "handler")` **siempre cae al fallback `"handler"`** — esto explica por qué `financial_scenarios.json:7` dice `"adr_source": "handler"`. El valor `"handler"` es un placeholder muerto que nunca se actualiza con la fuente real. | ✅ CONFIRMADO + hallazgo |

**Sub-observación — el valor `"handler"` es un leak de placeholder**.
El JSON público dice `"adr_source": "handler"` cuando el código real sabe
que la fuente es `"regional_v410"` (vía `adr_resolution.source`). Esto es
información incorrecta hacia abajo (coherence_validator, v4_audit, downstream).

### 2.3 Recepción en el handler — CONFIRMADO

| Claim del doc | Verificación | Estado |
|---------------|--------------|--------|
| `harness_handlers.py:49 → user_provided_adr = payload.get("user_provided_adr")` | L49 exacto | ✅ CONFIRMADO |
| `harness_handlers.py:65-71 → resolve_adr_with_shadow(user_provided_adr=None)` | L65-71 exacto. Llama a `resolve_adr_with_shadow(region, rooms, user_provided_adr, hotel_id, hotel_name)` | ✅ CONFIRMADO |
| Handler retorna `{"adr_resolution": {"source": ..., "confidence": ...}}` | L142-153: sí retorna `adr_resolution.source = adr_result.source` | ✅ CONFIRMADO |

### 2.4 Resolver wrapper — CONFIRMADO con nota

`adr_resolution_wrapper.py:resolve()` (L68-134) tiene 4 ramas:
- `FORCE_LEGACY` → `_legacy_resolution_with_scraping(user_provided_adr)` → usa `user_provided_adr` si está (L151-159)
- `ACTIVE` + use_regional → `_new_resolution_with_scraping` → `user_provided_adr siempre gana` (L170)
- `SHADOW`/`CANARY` → `_shadow_resolution_with_scraping` → `user_provided_adr siempre gana` (L216)

**Nota crítica**: Cuando `user_provided_adr` llega correctamente, el resolver
lo prioriza correctamente y emite `source="user_provided"` con
`epistemic_status="measured"` y `can_show_exact=True`. **El resolver funciona
bien cuando recibe el dato; el problema es upstream — el payload no lo
transporta.**

### 2.5 ValidationSummary — CONFIRMADO + hallazgo H3

| Claim del doc | Verificación | Estado |
|---------------|--------------|--------|
| `main.py:2107 → adr_from_onboarding_verified = (adr_from_onboarding is not None and > 0)` | L2107 exacto | ✅ CONFIRMADO |
| `main.py:2162 → confidence = VERIFIED if adr_from_onboarding_verified else ESTIMATED` | L2162 exacto | ✅ CONFIRMADO |
| `main.py:2163 → sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]` | L2163 exacto | ✅ CONFIRMADO |
| `main.py:2166 → value=adr_cop` (que es 420000, no 330000) | L2166 exacto | ✅ CONFIRMADO |

**Log real reproduce el síntoma** (`ejecucion-con-datos-reales.log:180`):
```
[OK] adr_cop: 420000 (verified)
```
El `confidence=verified` es **falso** porque el valor 420000 NO es del
onboarding; el flag `adr_from_onboarding_verified=True` solo verifica que
**existía** un valor en `adr_from_onboarding`, no que el `value=adr_cop`
provino de él.

### 2.6 JSON output — CONFIRMADO con hallazgo

`output/v4_complete/donalfonsohotel/v4_audit/financial_scenarios_20260722_162455.json`:
```json
{
  "input_data": {
    "rooms": 11,
    "adr_cop": 420000,        ← INCORRECTO (debería ser 330000)
    "adr_source": "handler",  ← PLACEHOLDER MUERTO (nunca actualizado)
    "occupancy_rate": 0.42424,
    "direct_channel_percentage": 0.3
  },
  ...
  "breakdown": {
    "data_sources": {
      "adr": "handler",       ← INCONSISTENTE con `input_data.adr_source` (mismo valor)
      ...
    }
  }
}
```

**Hallazgo**: `"adr_source": "handler"` es un placeholder que aparece en
2 lugares del mismo JSON (`input_data.adr_source` y `breakdown.data_sources.adr`)
y nunca se actualiza con la fuente real. Esto oculta el bug — el JSON no
permite auditar post-mortem si el ADR vino del harness, regional o user_provided.

### 2.7 Diagnostic doc — CONFIRMADO (síntoma BUG-2)

`output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260722_162501.md:88`:
```
> **¿Quiere saber su cifra exacta?** Complete el onboarding con sus datos
> reales: número de habitaciones, reservas mensuales promedio, valor promedio
> de reserva (COP) y porcentaje de canal directo.
```
Aparece **incluso cuando el log dice "Onboarding data loaded: 6 campos
confirmados"**. El bloque se construye en
`v4_diagnostic_generator.py:1259-1267` independientemente de `has_onboarding`.

**Esto NO es el bug que audita BUG-1**, pero confirma la naturaleza
sistémica del problema: la metadata de onboarding no se propaga al template
del diagnóstico.

### 2.8 Proposal doc — CONFIRMADO hallazgo H1

`output/v4_complete/02_PROPUESTA_COMERCIAL_20260722_162515.md:36`:
```
| ADR regional promedio | $420,000 COP |
```

**El proposal generator tiene su PROPIA llamada a `RegionalADRResolver`** en
`v4_proposal_generator.py:1869-1870`:
```python
resolver = RegionalADRResolver()
# rooms=0 y user_provided_adr=None para obtener solo el benchmark regional
result = resolver.resolve(region=region, rooms=0, user_provided_adr=None)
return result.adr_cop if result and result.adr_cop else None
```

Usada en `v4_proposal_generator.py:760`:
```python
_adr_value = self._get_adr_from_benchmarks(region or 'eje_cafetero')
_adr_display = f"${_adr_value:,.0f} COP" if _adr_value else "No disponible"
```

**Esto es un consumidor paralelo divergente**. El fix del harness payload
NO afecta este path. La propuesta seguirá mostrando "$420,000 COP" aunque
el diagnóstico use "$330,000 COP" del onboarding. Genera inconsistencia
entre los dos documentos que se entregan al cliente.

---

## 3. Hallazgos Sistémicos (Amplificación)

### H1 — Consumidor paralelo divergente en proposal generator

**Ubicación**: `modules/commercial_documents/v4_proposal_generator.py:1859-1873`
y uso en L760.

**Problema**: El método `_get_adr_from_benchmarks()` instancia su propio
`RegionalADRResolver` con `rooms=0` y `user_provided_adr=None`. Ignora
completamente el onboarding. Es un **bypass deliberado** documentado en el
comentario ("para obtener solo el benchmark regional").

**Impacto**: El ADR que aparece en la propuesta comercial SIEMPRE es el
benchmark regional ($420K para eje_cafetero), independientemente del
onboarding. Después del fix del harness, la propuesta y el diagnóstico
mostrarán ADRs diferentes al mismo hotel.

**Soluciones posibles**:
- (A) Reemplazar la llamada por `resolve_adr_with_shadow(user_provided_adr=adr_from_onboarding)` heredando el flag desde el orquestador.
- (B) Pasar `_adr_value` como argumento al constructor del proposal generator, calculado una sola vez en `main.py`.
- (C) Eliminar `_get_adr_from_benchmarks` y leer de `financial_scenarios.json` directamente.

### H2 — Divergencia de claves de fuente (3 vocabularios)

**Tres vocabularios distintos para "fuente del ADR"**:

| Vocabulario | Valores | Ubicación |
|-------------|---------|-----------|
| **A — `ADRSource` enum** | `"user_provided"`, `"regional_v410"`, `"legacy_hardcode"`, `"web_scraping"` | `modules/financial_engine/adr_resolution_wrapper.py:23-28` |
| **B — ValidationSummary.sources** | `["Onboarding"]`, `["Benchmark"]`, `["Default"]`, `["Audit"]` | `main.py:2151, 2163, 2175, 2187` |
| **C — JSON `input_data.adr_source`** | `"handler"`, `"onboarding"`, `"regional"`, `"web scraping"`, `"estimado: sin datos GA4"` | `main.py:1861`, `main.py:1899-1907` |

**Bug activo en discriminador del diagnostic**:
`v4_diagnostic_generator.py:1244`:
```python
if adr_source in ("user_provided", "web_scraping"):  # Vocabulario A
    adr_source_label = "datos del hotel"
elif adr_source == "regional_v410":                   # Vocabulario A
    adr_source_label = "benchmark regional"
else:
    adr_source_label = "estimado"
```

Pero `sources = field_map['adr_cop'].sources` (L1207) trae
`["Onboarding"]` o `["Benchmark"]` (Vocabulario B). **Nunca matchea los
literales del Vocabulario A**, por lo que el else siempre se ejecuta →
`adr_source_label = "estimado"`. La etiqueta "datos del hotel" (que
debería aparecer cuando el usuario proveyó onboarding) **es código muerto**.

**Soluciones posibles**:
- (A) Unificar los 3 vocabularios en una sola taxonomía (preferentemente
  `ADRSource` enum + serialización).
- (B) Cambiar el discriminador del diagnostic a aceptar ambos formatos
  (`if adr_source in ("user_provided", "Onboarding"):`).
- (C) Hacer que ValidationSummary.sources derive de `ADRSource.value`.

### H3 — Falsa confianza + falsa procedencia en ValidationSummary

**Ubicación**: `main.py:2160-2170`.

El bloque:
```python
confidence = ConfidenceLevel.VERIFIED if adr_from_onboarding_verified else ConfidenceLevel.ESTIMATED
sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]
validated_fields.append(ValidatedField(
    field_name="adr_cop",
    value=adr_cop,                    # ← Puede ser 420000 si harness ignoró onboarding
    confidence=confidence,             # ← VERIFIED por mera existencia de onboarding
    sources=sources,                   # ← ["Onboarding"] por mera existencia
    can_use_in_assets=True
))
```

**Acoplamiento incorrecto**: `confidence` y `sources` se derivan de
`adr_from_onboarding_verified` (un flag booleano que solo verifica
existencia), pero `value` viene de `adr_cop` (que puede ser regional).
**No hay invariante que ligue `value` con `sources`**: el código asume
que si `adr_from_onboarding is not None` entonces el `adr_cop` final
provino del onboarding. Esa asunción es falsa en el path actual del
harness.

**Aparición repetida en otros campos**: Misma estructura en
`rooms` (L2150-2157), `occupancy_rate` (L2174-2182),
`direct_channel_percentage` (L2186-2194). **BUG-1 es síntoma de un
patrón**: cuando hay onboarding, todo se etiqueta `VERIFIED`+`["Onboarding"]`
sin verificar que el valor final realmente provino de ahí.

**Soluciones posibles**:
- (A) Cambiar `confidence` y `sources` para que reflejen la fuente REAL
  del valor, no la mera presencia del onboarding:
  ```python
  confidence = ConfidenceLevel.VERIFIED if adr_source in ("user_provided", "Onboarding") else ConfidenceLevel.ESTIMATED
  ```
- (B) Refactorizar a un helper `build_validated_field(name, value, source)` que centralice la lógica de provenance.
- (C) Hacer que el payload del harness propague `user_provided_adr` Y que
  main.py compare `value` vs `adr_from_onboarding` antes de etiquetar.

### H4 — Tests no cubren el path end-to-end onboarding → harness → JSON

**Tests existentes** (todos aislados):
- `tests/financial_engine/test_adr_resolution_wrapper.py` — prueba el
  wrapper con `user_provided_adr` directo. ✅ Cubre el resolver.
- `tests/financial_engine/test_fallback_chain_honesto.py:144-307` —
  prueba que `user_provided_adr` gana sobre web_scraping y regional. ✅
  Cubre la cascada.
- `tests/test_onboarding.py` — prueba `load_onboarding_data`,
  `merge_with_hotel_data`, `create_onboarding_template`. ✅ Cubre el
  loader.

**Tests faltantes** (gap):
- ❌ Ningún test asserta que el `payload` del `AgentTask` incluya
  `user_provided_adr` cuando hay YAML.
- ❌ Ningún test asserta que `financial_scenarios.json:input_data.adr_cop`
  refleje el valor del YAML.
- ❌ Ningún test asserta que `financial_scenarios.json:input_data.adr_source`
  NO sea el placeholder `"handler"`.
- ❌ Ningún test asserta que `ValidationSummary` no tenga
  `confidence=VERIFIED` cuando el `value` no vino del onboarding.

**Test del archived** (`tests/_archived_broken_tests/test_fase3_harness_integration.py`):
existe referencia a `user_provided_adr` pero está archivado por roto
—no se ejecuta en CI.

**Impacto**: BUG-1 pudo entrar a producción porque ningún test cierra el
camino completo. El fix de "1 línea" sin agregar tests puede romperse
silenciosamente en el futuro.

**Solución posible**:
Agregar `tests/test_v4_onboarding_to_harness_e2e.py` que:
1. Cree un YAML de onboarding temporal.
2. Ejecute el path `main.py:1739-1814` (o su equivalente testeable).
3. Assert `result_data["adr_cop"] == 330000`.
4. Assert `financial_scenarios.json["input_data"]["adr_source"] != "handler"`.

---

## 4. Riesgos del Fix de "1 Línea"

El documento propone agregar `user_provided_adr=adr_from_onboarding` al
payload del harness (main.py:1797-1806). Riesgos reales:

| # | Riesgo | Mitigación |
|---|--------|------------|
| R1 | **NO corrige H1** — el proposal generator seguirá mostrando $420K. El cliente verá dos ADRs distintos en el mismo paquete (diagnóstico $330K, propuesta $420K). | Aplicar fix también en `v4_proposal_generator.py:1859-1873`. |
| R2 | **NO corrige H2** — la divergencia de claves seguirá produciendo `adr_source_label = "estimado"` en el diagnóstico. | Estandarizar la taxonomía de fuentes (ver H2 soluciones). |
| R3 | **NO resuelve H3 por completo** — `adr_from_onboarding_verified` aún se calcula por existencia, no por provenance. Si en el futuro el path del harness cambia y vuelve a ignorar onboarding, el bug volverá sin que se detecte. | Cambiar el cómputo de `confidence` y `sources` para reflejar fuente real. |
| R4 | **El campo semánticamente incorrecto** — el código usa `valor_reserva_cop` como si fuera `adr_cop`. Si reservas multi-noche (e.g. 2-3 noches), el `adr_cop` efectivo sería `valor_reserva_cop / noches_promedio`, no `valor_reserva_cop`. Esto puede SOBREestimar el ADR en hoteles con estancias largas. | Leer `adr_cop` del YAML si existe (L9), sino derivar de `valor_reserva_cop` con un factor. Documentar el campo canónico. |
| R5 | **El fallback `"handler"` en L1861 sigue siendo código muerto** — el JSON seguirá diciendo `"adr_source": "handler"` aunque internamente sepa la fuente real. Hace el JSON inauditable. | Cambiar L1861 a `adr_source = result_data["adr_resolution"]["source"]` o agregar el campo top-level en el handler. |
| R6 | **El YAML tiene `fecha_captura` en UTC pero `datetime.now()` se compara con offset naive** — L3362-3363: si `fecha_captura` viene sin tzinfo, se le asigna UTC, pero la diferencia se hace contra `datetime.now(timezone.utc)`. Si el YAML dice `2026-07-22T16:00:00+00:00`, la frescura es correcta; pero un YAML generado con `datetime.now()` (naive) en zona horaria local generaría drift. | Documentar contrato: `fecha_captura` debe ser ISO 8601 con offset. |
| R7 | **El fix no agrega un test que prevenga regresión** — futuros cambios al orquestador pueden reintroducir el bug. | Agregar test e2e (ver H4). |

---

## 5. Causa Raíz

El defecto NO es "olvidé pasar `user_provided_adr`". Es un **patrón
arquitectónico**: el sistema tiene 3 capas (`ADRSource` enum,
`ValidationSummary`, JSON público) que deberían compartir una taxonomía
única de provenance, pero cada una usa su propio vocabulario. El bug
de omisión en el payload del harness es el detonante visible; la causa
raíz es la **falta de invariantes entre el dato crudo (`adr_from_onboarding`),
el dato calculado (`adr_cop`), y la metadata de provenance
(`confidence`/`sources`/`adr_source`)**.

Cuando el orquestador construye el payload del harness, **no propaga
toda la información de provenance** (ADR + channel + occupancy), sino
solo los valores numéricos. El handler los recibe sin contexto. Cuando
el orquestador reconstruye la metadata (ValidationSummary), **asume que
los valores finales reflejan las fuentes originales** — asunción que el
path del harness viola.

---

## 6. Soluciones Posibles (ordenadas por costo/beneficio)

### Opción A — Mínima (la del documento)
- Agregar `"user_provided_adr": adr_from_onboarding` al payload del harness (main.py:1806).
- Agregar test que cierre el e2e.
- **Cubre**: solo el síntoma de BUG-1.
- **No cubre**: H1, H2, H3, R4, R5.

### Opción B — Mínima + H1
- Opción A + reemplazar `_get_adr_from_benchmarks` por llamada que reciba `adr_from_onboarding`.
- **Cubre**: BUG-1 + inconsistencia diagnóstico/propuesta.
- **No cubre**: H2, H3, R4, R5.

### Opción C — Robusta (recomendada)
- Aplicar Opción B.
- Unificar la taxonomía de fuentes a `ADRSource.value` (snake_case) en
  las 3 capas; cambiar `ValidationSummary.sources` para que derive de
  `ADRSource.value`.
- Cambiar la lógica de `confidence`/`sources` en ValidationSummary para
  que refleje la fuente REAL del valor (no la mera existencia de onboarding).
- Arreglar `main.py:1861` para leer `result_data["adr_resolution"]["source"]`
  en lugar de caer al placeholder `"handler"`.
- Documentar y usar `adr_cop` (semánticamente correcto) en lugar de
  `valor_reserva_cop` cuando esté disponible en el YAML.
- Agregar 3-4 tests e2e que cierren el pipeline completo.
- **Cubre**: BUG-1 + H1 + H2 + H3 + H4 + R1-R7.

### Opción D — Refactor mayor
- Opción C + extraer la lógica de construcción del payload del harness
  y la lógica de construcción de ValidationSummary a métodos
  separados y testeables.
- Centralizar `build_validated_field(name, value, raw_source)` que
  hace cumplir el invariante value ↔ sources ↔ confidence.
- Eliminar la duplicación de vocabularios.

---

## 7. Confirmaciones línea por línea del documento

| Sección del doc | Claim | Veredicto |
|-----------------|-------|-----------|
| §3 Paso 1 — `main.py:1765` extrae `valor_reserva_cop` | ✅ CONFIRMADO |
| §3 Paso 2 — payload en L1797-1806 no incluye `user_provided_adr` | ✅ CONFIRMADO |
| §3 Paso 3 — `harness_handlers.py:49` recibe None | ✅ CONFIRMADO |
| §3 Paso 4 — resolver usa benchmark regional en L65-71 | ✅ CONFIRMADO |
| §3 Paso 5 — ValidationSummary en L2160-2170 marca VERIFIED con valor incorrecto | ✅ CONFIRMADO (y la divergencia value↔sources es estructural) |
| §3 Tabla impacto cuantificado | ⚠️ PARCIALMENTE — los ratios son plausibles pero asumen OTA commission 15% constante; no se reproduce contra el JSON real. El JSON muestra `ota_commission_basis = "98 noches OTA × $420,000 ADR × 15% comisión"` y `ota_commission_cop = 6,174,000` que matchea con ADR=$420K. Con $330K sería 98×330000×0.15 = 4,851,000. La proyección §9 del doc dice $4,851,000 ✅. |
| §3 Fix Opción A | ✅ CORRECTO pero incompleto (ver §4 riesgos) |
| §3 Fix Opción B | ✅ CORRECTO pero asume que el handler ya recibe `user_provided_adr`. Después de A, sí es trivial. |
| §3 Archivos afectados | ✅ CONFIRMADO + **falta v4_proposal_generator.py:1859-1873 (H1)** |
| §6 Tabla comparativa run 1 vs run 2 | ⚠️ La tabla tiene columnas plausibles pero **no se reproduce del log** — se infiere de los dos `financial_scenarios.json`. El doc no muestra evidencia de haber leído los JSONs directamente. **Verificar**: run 2 muestra `"adr_cop": 420000` (no onboarding) y `"adr_source": "handler"` (placeholder muerto). Coherence Score 0.947 — verificable en `coherence_validation.json`. |
| §8 Ruta de código | ✅ CONFIRMADO para los puntos citados |
| §9 Proyección con ADR real | ✅ Aritmética correcta (98×330000×0.15=4,851,000) |
| §10 Checklist | ✅ Aceptable pero falta el test para `financial_scenarios.json:input_data.adr_source != "handler"` y el fix de `v4_proposal_generator.py` |

---

## 8. Resumen Ejecutivo para el Plan de Refactorización

**BUG-1 existe, es real, y su "fix de 1 línea" es necesario pero NO suficiente.**

El defecto es **sistémico** y se manifiesta en al menos 3 lugares:
1. **Harness payload** (BUG-1 doc) — el omitido original.
2. **Proposal generator** (H1) — consumidor paralelo divergente.
3. **ValidationSummary** (H3) — el bug que etiqueta como VERIFIED un valor que NO es del onboarding.

**Recomendación**: Implementar **Opción C** del §6. Si solo se puede
implementar Opción A, agregar de inmediato TODOS los tests e2e propuestos
en H4 y crear tickets separados para H1, H2, H3 antes de aceptar el fix
como completo. La entrega al cliente con datos divergentes entre
diagnóstico y propuesta es un riesgo reputacional mayor que el bug
original.

---

## Anexo A — Archivos Verificados en Esta Auditoría

- ✅ `main.py` (L1605-2220, L3324-3380) — orquestador principal
- ✅ `modules/financial_engine/harness_handlers.py` (305 líneas, leído completo)
- ✅ `modules/financial_engine/adr_resolution_wrapper.py` (L60-360)
- ✅ `modules/commercial_documents/v4_diagnostic_generator.py` (L1180-1295)
- ✅ `modules/commercial_documents/v4_proposal_generator.py` (L750-770, L1859-1875)
- ✅ `output/clientes/donalfonsohotel_onboarding.yaml` (25 líneas)
- ✅ `output/v4_complete/donalfonsohotel/v4_audit/financial_scenarios_20260722_162455.json` (52 líneas)
- ✅ `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260722_162501.md` (L88, L189)
- ✅ `output/v4_complete/02_PROPUESTA_COMERCIAL_20260722_162515.md` (L36)
- ✅ `evidence/v4complete-donalfonso/ejecucion-con-datos-reales.log` (L159, L180)
- ✅ Tests: `test_adr_resolution_wrapper.py`, `test_fallback_chain_honesto.py`, `test_onboarding.py`
- ✅ Tests archivados: `_archived_broken_tests/test_fase3_harness_integration.py`

## Anexo B — Comandos de Reproducción

```bash
# Reproducir el bug desde la línea de comandos
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py --url https://www.donalfonsohotel.com/ --output-dir output/v4_complete
# Inspeccionar el JSON generado
cat output/v4_complete/donalfonsohotel/v4_audit/financial_scenarios_*.json | \
  python3 -c "import json,sys;d=json.load(sys.stdin);print('adr_cop:',d['input_data']['adr_cop']);print('adr_source:',d['input_data']['adr_source'])"
# Esperado (bug): adr_cop: 420000, adr_source: handler
# Esperado (post-fix A): adr_cop: 330000, adr_source: user_provided
```