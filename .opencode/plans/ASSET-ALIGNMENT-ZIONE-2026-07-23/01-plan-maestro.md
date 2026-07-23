# Plan Maestro: ASSET-ALIGNMENT-ZIONE-2026-07-23

> **Fecha**: 2026-07-23
> **Contexto origen**: `.opencode/context/ZIONE-PROPOSAL-ASSET-ALIGNMENT-BLOCK-2026-07-23.md`
> **Hotel de prueba**: Zi One Luxury (https://zione.co/)
> **Datos reales**: `data/hotel_observations/observations.json` (entry: Zi One Luxury, Tier A, confidence 0.95)
> **Estado base**: v4.62.0, 136 tests relevantes ejecutados (1 pre-existing failure)
> **Convención**: 1 fase = 1 sesión. Sin excepciones.

---

## 1. Resumen Ejecutivo

La ejecución v4complete para Zi One Luxury completó 11/11 publication gates evaluados, pero
**proposal_asset_alignment** (Gate 9) marcó **BLOCKED** (75% efectivo, umbral 80%) porque 2 servicios
prometidos en la propuesta comercial (SEO Local → optimization_guide, Meta Tags Sociales → open_graph)
no tienen assets generados correspondientes. La auditoría exhaustiva contra código vivo reveló una
**cadena de bypass de 3 capas** que permite entregar el ZIP a pesar del bloqueo, más 11 hallazgos
adicional de severidad variable (14 hallazgos total tras la ampliación del gap del generador).

Este plan implementa la **solución híbrida recomendada** (Opciones A + C + E + F del contexto):
reparar el bypass de seguridad, cerrar los gaps Pain→Asset, hacer la propuesta condicional como
safety net, unificar las fuentes de verdad divergentes, y corregir bugs de presentación. La
validación final es una única ejecución de v4complete para zione.co con análisis post-implementación.

## 2. Hallazgos a Corregir

| ID | Hallazgo | Severidad | Sección contexto | Fase |
|----|----------|-----------|-----------------|------|
| 9.1 | delivery_quality_report ignora resultado real de Gate 9 (key "proposal_asset" vs "proposal_asset_alignment") | 🔴 CRÍTICO | §9.1 | FASE-1 |
| 9.2 | GATE_BLOCKING_ENABLED=False por default en main.py:2814 | 🔴 CRÍTICO | §9.2 | FASE-1 |
| 3.1 | PainSolutionMapper no tiene pain `low_seo_score` → optimization_guide nunca se planifica | 🔴 CRÍTICO | §3.1 | FASE-2 |
| 3.2 | Pain `no_og_tags` no se activa cuando sitio YA tiene OG tags (sin modo enhance_existing) | 🟠 ALTO | §3.2 | FASE-2 |
| 3.2b | OpenGraphGenerator produce tags desde cero — duplica OG tags existentes en vez de optimizarlos | 🟠 ALTO | §3.2 L148-149 | FASE-2 |
| 9.5 | Clave duplicada en PAIN_TO_ASSET (conditional_generator.py:250-251) | 🟠 ALTO | §9.5 | FASE-2 |
| 9.6 | 3 fuentes de verdad divergentes para servicios (PROPOSAL_SERVICE_TO_ASSET vs SERVICE_CATALOG vs SERVICE_TO_ASSET_LOOKUP) | 🟠 ALTO | §9.6 | FASE-3 |
| Opción C | Propuesta promete servicios sin asset generado (sin safety net) | 🟡 MEDIO | §7.C | FASE-3 |
| 9.4 | Template "Tier C" hardcodeado en propuesta_v6_template.md:102 (debería ser variable) | 🟡 MEDIO | §9.4 | FASE-4 |
| 9.7 | proposal_asset_matrix.json muestra todo como NO_BREACH (serialización dicts vs objetos) | 🟡 MEDIO | §9.7 | FASE-4 |
| 9.8 | MANIFEST (38) y README (38) desincronizados del ZIP real (40 archivos) | 🟡 MEDIO | §9.8 | FASE-4 |
| 9.9 | README_DELIVERY.md referencia boton_whatsapp.html que no existe en el ZIP | 🟡 MEDIO | §9.9 | FASE-4 |
| 9.10 | $7,192,000 etiquetado "Fuga mensual por comisiones OTA" es engañoso (no es la comisión OTA verificable $20,880,000) | 🟡 MEDIO | §9.10 | FASE-4 |
| 9.11 | Test roto: test_publication_gates.py:1191 path hardcodeado a amaziliahotel | 🟢 BAJO | §9.11 | FASE-4 |

## 3. Dependencias entre fases

```
FASE-1 (bypass de seguridad) ──→ FASE-2 (gaps Pain→Asset)
                            ──→ FASE-3 (propuesta condicional + unificación)
FASE-2 + FASE-3             ──→ FASE-4 (correcciones de presentación + bugs menores)
FASE-4                      ──→ FASE-5 (v4complete + análisis post-implementación)
FASE-5                      ──→ FASE-RELEASE-4.63.0 (cierre y documentación)
```

FASE-1 es prerequisito de todas las demás: sin reparar el bypass, los fixes de FASE-2
no serían detectados por el gate. FASE-2 y FASE-3 son independientes entre sí pero ambas
dependen de FASE-1. FASE-4 depende de FASE-2+FASE-3 porque algunas correcciones de
presentación interactúan con los cambios de PainSolutionMapper y la propuesta condicional.

## 4. Complejidad técnica por fase

| Fase | Complejidad | Justificación |
|------|-------------|---------------|
| FASE-1 | MEDIA | 2 archivos, cambios localizados. delivery_quality_report.py:238 (fix key lookup) + main.py:2814 (env default). Lógica clara del contexto. |
| **FASE-2** | **ALTA (MAYOR)** | **Toque arquitectónico en PainSolutionMapper: agregar pain type nuevo + modificar lógica de detección existente (no_og_tags de binario a graduated) + extender OpenGraphGenerator con modo enhance_existing (no produce duplicados). 4 archivos, cascada semántica pain→asset→generador. El modo enhance_existing para OG tags es un cambio conceptual, no mecánico.** |
| FASE-3 | MEDIA-ALTA | Unificar 3 fuentes de verdad divergentes + hacer propuesta condicional. Mucha surface area pero cambios mayormente mecánicos. |
| FASE-4 | MEDIA | 6 correcciones de baja complejidad individual, pero alto conteo. Mecánicas, sin razonamiento arquitectónico. |
| FASE-5 | MEDIA | v4complete (5-10 min runtime) + verificación de 13 hallazgos + análisis post-implementación. Presupuesto de iteraciones ajustado. |
| FASE-RELEASE | BAJA | Mechanical: version bump, changelog, docs. No modifica código fuente. |

## 5. delegate_task — Matriz de viabilidad

| Fase | ¿Viable? | Tipo | Razón |
|------|----------|------|-------|
| FASE-1 | ✅ SÍ | SUBAGENTE | Spec completa del contexto (§9.1, §9.2), 2 archivos, cambios localizados con líneas exactas. |
| FASE-2 | ✅ SÍ | SUBAGENTE | Spec completa con código ANTES/DESPUÉS del contexto (§3.1, §3.2, §9.5). Requiere razonamiento pero auto-contenido. |
| FASE-3 | ✅ SÍ | SUBAGENTE | Cambios mecánicos de unificación + condicionales. Spec del contexto (§9.6, §7.C). |
| FASE-4 | ✅ SÍ | SUBAGENTE | 6 fixes mecánicos con líneas exactas del contexto (§9.4, §9.7-9.11). Baja complejidad individual. |
| FASE-5 | ⚠️ PARCIAL | MIXTO | v4complete → delegate_task subagente (timeout 900s). Análisis post-implementación → agente principal directo (requiere contexto completo del plan). |
| FASE-RELEASE | ✅ SÍ | SUBAGENTE | Mechanical: version bump, changelog, sync_versions, doctor. Solo YAML/MD + scripts, sin imports del proyecto. |

## 6. Fase de mayor complejidad técnica: FASE-2

**FASE-2** es la fase de mayor complejidad técnica porque:

1. **Modifica lógica de detección de pains (no solo agregar entradas)**: El pain `no_og_tags`
   actualmente se activa solo cuando `seo_elements.open_graph == False`. El fix requiere un
   modo "enhance_existing" que evalúe si los OG tags existentes son mejorables (no solo
   presencia/ausencia). Esto cambia el contrato de `detect_pains()` de binario a graduated.

2. **Agrega un pain type nuevo con validación de campos**: `low_seo_score` necesita un
   trigger (`seo_local_score < 40`), `validation_fields` que deben existir en el audit_report,
   y mapeo a assets. El PainSolutionMapper tiene invariante de que todo pain en PAIN_SOLUTION_MAP
   debe tener sus validation_fields disponibles en el audit — si no, el pain se silencia.

3. **Cascada semántica pain→asset→proposal**: Agregar `low_seo_score` → optimization_guide
   hace que el asset se planifique, pero el asset_catalog ya tiene `promised_by` entries
   que referencia pains que no se activan. Hay que verificar consistencia entre
   `promised_by` en asset_catalog y `assets` en PAIN_SOLUTION_MAP.

4. **Eliminación de clave duplicada (9.5) puede romper consumidores**: La clave duplicada
   en conditional_generator.py:250-251 causa que `whatsapp_conflict` mapee a lista, no
   string. Eliminar la duplicada puede romper consumidores que esperan string.

5. **Extensión del generador OpenGraphGenerator (gap 3.2b)**: El generador produce tags
   HTML desde cero (L248-338) sin recibir information sobre los tags existentes. Para
   hoteles que ya tienen OG tags (como Zi One Luxury con 8 tags), el generador produciría
   tags duplicados. El fix requiere pasar los tags existentes al generador y que este
   genere solo los faltantes — un cambio en la interfaz del generador, no solo en el
   detector de pains.

**Mitigaciones**: prompt auto-contenido con snippets ANTES/DESPUÉS del contexto, verificación
post-patch con grep de invariantes, y tests de regresión incluidos en la misma fase.

## 7. Definition of Done (DoD) global

- [ ] delivery_quality_report.py consume resultado real de Gate 9 (no hardcodea passed=True)
- [ ] GATE_BLOCKING_ENABLED=True por default en main.py
- [ ] PainSolutionMapper tiene pain `low_seo_score` → optimization_guide
- [ ] Pain `no_og_tags` se activa en modo enhance_existing (OG tags presentes pero mejorables)
- [ ] OpenGraphGenerator soporta modo enhance_existing (genera tags faltantes, no duplica existentes)
- [ ] Clave duplicada en conditional_generator.py:250-251 eliminada
- [ ] Propuesta solo promete servicios con asset generado o present_in_production
- [ ] SERVICE_TO_ASSET_LOOKUP derivado de PROPOSAL_SERVICE_TO_ASSET (fuente única)
- [ ] Template "Tier C" reemplazado por variable ${financial_evidence_tier}
- [ ] proposal_asset_matrix.json muestra BREACH correctos (no todo NO_BREACH)
- [ ] README_DELIVERY.md dinámico basado en assets reales del ZIP
- [ ] Test roto test_publication_gates.py:1191 corregido
- [ ] v4complete ejecutado para Zi One Luxury (zione.co) con Gate 9 PASSED (alignment ≥ 80%)
- [ ] Análisis post-implementación: 13 hallazgos superados + lecciones aprendidas
- [ ] RELEASE: CHANGELOG + version sync 4.62.0 → 4.63.0 + pre-commit

## 10. Opciones de solución descartadas (evaluación deliberada)

El contexto (§7) presenta 6 opciones (A-F) más una híbrida recomendada (A+C+E+F).
El plan implementa la híbrida recomendada. Las opciones descartadas se documentan
aquí con su justificación, para trazabilidad de la decisión.

### Opción B: Agregar `promised_by: "always"` al asset_catalog — DESCARTADA (parcialmente)

**Qué propone**: Para assets que la propuesta SIEMPRE promete, generarlos sin depender de
un pain. Patrón ya usado para `monthly_report` (asset_catalog.py:336).

**Evaluación**:

| Asset | ¿Prometido siempre? | ¿Descartar? | Razón |
|-------|-------------------|-------------|-------|
| `optimization_guide` (SEO Local) | Sí (en PROPOSAL_SERVICE_TO_ASSET) | ✅ SÍ | La propuesta lo promete, pero el score SEO Local varía por hotel. Si el hotel tiene SEO Local ≥ 80, no hay justificación de pain. `low_seo_score` (Opción A) es más preciso: solo se activa cuando SEO < 40. `promised_by="always"` generaría el asset incluso para hoteles con buen SEO, degradando la confianza del gate `asset_confidence`. |
| `open_graph` (Meta Tags) | Sí (en PROPOSAL_SERVICE_TO_ASSET) | ⚠️ PARCIAL | La propuesta SIEMPRE lo promete, pero el valor del asset depende de si el sitio ya tiene OG tags. Para sitios sin OG tags, el pain `no_og_tags` (Opción A) es el mapeo correcto. Para sitios CON OG tags incompletos, el modo `enhance_existing` (Opción A modificada) es el correcto. `promised_by="always"` generaría tags duplicados para sitios que ya tienen OG tags completos, lo que es peor que no generar nada. |

**Decisión**: Descartar `promised_by="always"` para `optimization_guide` y `open_graph`.
Mantener `low_seo_score` (Opción A) como mecanismo de activación para `optimization_guide`.
Mantener `no_og_tags` con modo `enhance_existing` (Opción A modificada) para `open_graph`.

**Deuda técnica registrada**: Si en el futuro se detecta que la propuesta promete un servicio
que NO tiene un pain type correspondiente Y el servicio es siempre aplicable (ej: un nuevo
servicio transversal), evaluar `promised_by="always"` con la documentación de causalidad
que usa `monthly_report` como patrón (asset_catalog.py:337-346).

### Opción D: Gate 9 como WARNING en vez de BLOCKING — DESCARTADA

**Qué propone**: Cambiar Gate 9 de BLOCKING a WARNING para que no impida publication.

**Evaluación**: El riesgo es que el cliente reciba una propuesta con servicios que no tiene.
El plan logra lo contrario: hace que el gate funcione correctamente (Opción E + F) y cierra
los gaps para que el gate pase (Opción A + C). Cambiar a WARNING sería enmascarar el problema
en vez de resolverlo.

**Decisión**: Descartar. El plan repara el bypass (FASE-1) y cierra los gaps (FASE-2) para
que el gate pase legítimamente, no para degradar el gate.

### Opción B complemento: Modo enhance_existing en el generador (no solo en el detector)

**Gap detectado en revisión del plan**: El plan original FASE-2 Tarea 2 modificaba el detector
de pains (`detect_pains()`) para activar `no_og_tags` cuando OG tags existen pero son
incompletos. PERO no modificaba el generador `OpenGraphGenerator` — el generador produce
tags HTML desde cero (L248-338) sin recibir information sobre los tags existentes.

Para Zi One Luxury (que ya tiene 8 OG tags: og:locale, og:type, og:title, og:description,
og:url, og:site_name, og:image), el generador produciría tags DUPLICADOS, no optimizaría
los existentes. El texto comercial "Sus fotos brillan cuando alguien comparte su link en
redes" implica optimización, no creación desde cero.

**Solución mejorada (incorporada al plan)**: FASE-2 ahora incluye modificar
`OpenGraphGenerator` para soportar un modo `enhance_existing` que:
1. Reciba los OG tags existentes del audit report (seo_elements.og_tags_list o similar)
2. Genere solo los tags FALTANTES (no duplique los existentes)
3. Incluya una nota HTML explicando que estos tags complementan los existentes
4. Si los tags existentes ya están completos, el asset se marca como
   `present_in_production` en vez de generar un archivo duplicado

Esto es mejor que el plan original porque:
- El detector de pains (FASE-2) Y el generador (FASE-2) trabajan en conjunto
- No produce archivos duplicados que confunden al cliente
- Respeta el trabajo ya hecho en el sitio (mejora, no reemplaza)
- El gate `asset_confidence` no se degrada con assets redundantes

## 8. Datos de prueba esperados (Zi One Luxury)

| Campo | Valor esperado post-fix | Valor actual (bug) |
|-------|------------------------|-------------------|
| Gate 9 status | PASSED | BLOCKED |
| Gate 9 alignment | ≥ 80% | 75% (efectivo), 66.7% (raw) |
| optimization_guide generado | ✅ SÍ | ❌ NO |
| open_graph generado | ✅ SÍ (tags faltantes, no duplicados) | ❌ NO |
| open_graph mode | enhance_existing (complementa) | — (no se activa) |
| delivery_quality_report proposal_asset_gate | passed=False si Gate 9 falla | passed=True (hardcodeado) |
| GATE_BLOCKING_ENABLED | True (default) | False (default) |
| Servicios en ZIP vs prometidos | 8/8 (o justificados) | 4/8 |

## 9. Estructura del plan

```
.opencode/plans/ASSET-ALIGNMENT-ZIONE-2026-07-23/
├── 01-plan-maestro.md                    # Este archivo
├── 02-prompt-fase-1.md                    # Bypass de seguridad (CRÍTICO)
├── 03-prompt-fase-2.md                    # Gaps Pain→Asset (MAYOR COMPLEJIDAD)
├── 04-prompt-fase-3.md                    # Propuesta condicional + unificación fuentes
├── 05-prompt-fase-4.md                    # Correcciones de presentación + bugs menores
├── 06-prompt-fase-5.md                    # v4complete + análisis post-implementación
├── 07-prompt-fase-6-release.md            # RELEASE 4.63.0
├── 08-checklist-implementacion.md         # Tracking
├── 09-documentacion-post-proyecto.md     # Acumulativo para RELEASE
├── dependencias-fases.md                  # Dependencias
└── README.md                              # Índice del plan
```
