# Dependencias entre Fases — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla vigente (D-PRE.1, 2026-09-15; actualizada por FASE-RELEASE)**: P4 permanece cerrada; P5 cerrada; **P6 cerrada + P6-R (remediación post-auditoría el mismo día)**; **FASE-VERIFY cerrada el 2026-09-15** (matriz de 25 ACs + integración cross-fase + greps + triaje); **FASE-RELEASE-4.77.0 cerrada el 2026-09-15 → plan 9/9 COMPLETADO** (P6-R no es fase nueva, es la corrección de P6). RELEASE ejecutó AC-V1 = verificar y citar la matriz de VERIFY (comprobación de completitud en `10-analisis` §Matriz de certificación), bump + sync + CHANGELOG/GUIA + write-back QMind pre-archivado + archivado R2.5 + tag `v4.77.0`. El push de master y del tag queda con confirmación explícita del operador. El antiguo escenario de diferimiento de P4 se conserva solo como antecedente.
> **Regla heredada**: nunca sesiones de implementación paralelas sobre el mismo working tree. P2, P3-A y P3-B compartieron `judge.py`/`main.py`/`acta_writer.py`; P5/P6 también se ejecutan secuencialmente y con baselines NR1 independientes.
> **Autorización de esta actualización**: solo documentos del plan. No ejecución de P5/P6, rotación, retirada de datos, reescritura, cambio de visibilidad ni push.

---

## Estado de la Etapa 1 (Preparación) — sesión de ajuste 2026-09-14

El executor (§Aplicación) exige que la Etapa 1 genere **todos** los prompts de fase, RELEASE incluido, y los archivos `09`/`10` desde la concepción. Al concebir el plan (2026-09-11) esto no se cumplió; la sesión de ajuste lo cierra:

| Entregable Etapa 1 | Estado |
|--------------------|--------|
| `05-prompt-inicio-sesion-fase-P1.md` | ✅ (revisado en el ajuste: citas, divisiones, escenarios) |
| `05-prompt-inicio-sesion-fase-P3-A.md` · `-P3-B.md` · `-P4.md` · `-RELEASE.md` | ✅ Creados 2026-09-14 con placeholders `⟨P1 fija⟩` donde la decisión manda |
| `05-prompt-inicio-sesion-fase-P2.md` | ✅ **Creado por FASE-P1 el 2026-09-14**, con la opción elegida (O1-cuarentena) y el contrato vinculante en su encabezado. El diferimiento estaba declarado en la fila original de esta tabla y en la cabecera del propio P1: escribir un prompt antes de conocer la opción habría producido un prompt falso, no incompleto |
| `09-documentacion-post-proyecto.md` · `10-analisis-post-implementacion.md` | ✅ Creados 2026-09-14 con estructura base; el `10-` ya registra la decisión del ajuste (D-AJUST.1–.3) |
| `05-prompt-inicio-sesion-fase-VERIFY.md` | ✅ **Creado 2026-09-15** al reabrirse la decisión (D-AJUST.4): DIRECTO, 60 iteraciones, 4 tareas / 0 comandos largos, matriz de 25 ACs + integración cross-fase de la ruta de delivery + greps residuales + triaje de Seguimientos |
| Decisión FASE-VERIFY (§4.6) | 🔁 **REABIERTA por D-AJUST.4 (2026-09-15): FASE-VERIFY SÍ activa sesión**, previa a RELEASE y con AC-V1 reducido a citar su matriz. P1 la había cerrado como no activa el 2026-09-14 sobre una premisa que P4 y P6-R desmintieron (§FASE-VERIFY abajo) |
| Escenario de cierre sin P4 | ✅ Fijado (§Cierre válido sin P4 abajo) |

---

## Decisión FASE-VERIFY (§4.6 del executor) — 🔁 **REABIERTA por D-AJUST.4 (2026-09-15): SÍ activa**

> **Estado vigente**: **FASE-VERIFY crea sesión propia**, DIRECTO y no delegable, entre P6-R y FASE-RELEASE-4.77.0. Su prompt es `05-prompt-inicio-sesion-fase-VERIFY.md` y su matriz de 25 ACs es el artefacto que RELEASE pasa a **citar**. AC-V1 deja de ser el sustituto y queda como verificación de que esa matriz existe y está completa.
>
> **Qué queda vigente de la decisión de P1**: las dos sustituciones como **piso mínimo**, no como techo — el par NR7 sigue siendo obligatorio por AC de detección/bloqueo y un AC sin su par sigue quedando ⚠️, nunca ✅. Lo que se revierte es la exclusión de la sesión, no el criterio de certificación.

### Histórico — cierre original en FASE-P1 (2026-09-14): NO activa

Los tres criterios de activación se evalúan sobre la división de fases **post-ajuste** (P1 decide; P2/P3-B son condicionales):

| Criterio §4.6 | Evaluación (al 2026-09-14) |
|---------------|------------|
| 1. ≥3 fases de implementación | **Sí**: P3-A, P3-B y P2 (Q1=sí). P4 no cuenta |
| 2. Al menos una fase con ejecución E2E | **No garantizable**: P4 depende de T3a, una precondición **comercial externa** (Q4/DA-P1.9). Atar la certificación del plan a que un hotel responda convierte el cierre en un `—` indefinido |
| 3. ACs que cruzan fases | Sí: AC-E0 (P1→P2), AC-F2↔AC-F5 (P3-A↔P3-B), AC-O0 (P4 sobre lo que deje P3-B) |

> **Decisión registrada 2026-09-14 por FASE-P1**: **no se crea sesión FASE-VERIFY propia**. El criterio 2
> no se cumple y **no puede garantizarse desde la ingeniería**, así que la certificación se ancla a algo
> que sí depende de este plan. El patrón VERIFY pasa a ejecutarse como **AC-V1 dentro de FASE-RELEASE**,
> con dos sustituciones explícitas que reemplazan lo que VERIFY habría aportado:
>
> 1. La certificación **no depende de una corrida real** sino del **par NR7 por AC** (verde/rojo), obligatorio
>    en la evidencia de P2, P3-A y P3-B. Un AC sin su par queda ⚠️, nunca ✅.
> 2. Si P4 **llega** a ejecutarse, su evidencia entra a la matriz de AC-V1 y responde los 9 puntos del §5 del
>    maestro. Si no, AC-V1 certifica contra los artefactos de P2/P3-A/P3-B y **declara la ausencia de corrida
>    como límite de esta decisión**, no como fallo de la fase.
>
> Esta sección es el cierre del ítem: no se improvisa en RELEASE. Rationale completo en §7 de
> `evidence/FASE-P1/decision-enforcement.md`.

### D-AJUST.4 — Reapertura (2026-09-15, sesión dedicada por encargo del operador): **SÍ activa**

La reapertura **no improvisa en RELEASE**: la cierra una decisión registrada antes de convocar la fase, que es lo que aquella línea exigía. Tres mediciones la motivan, todas posteriores al cierre de P1:

| # | Qué se midió | Efecto sobre la decisión de P1 |
|---|--------------|--------------------------------|
| 1 | **P4 se corrió** con hotel real (Don Alfonso, `BLOQUEADO` + ZIP suprimido) y P6-R añadió `tests/test_p6r_full_flow_matrix.py` sobre el flujo real; el plan pasó de 3 a **5 fases de implementación** (P3-A, P3-B, P2, P5, P6) y de 3 a **6 familias de ACs** (25) | Cae la premisa del criterio 2 ("no garantizable desde la ingeniería") y se cumplen **los tres** criterios de §4.6, que son imperativos ("el orquestador DEBE incluir FASE-VERIFY") |
| 2 | **Dos auto-certificaciones de fase fueron falsas** y las desmintió una auditoría externa el mismo día del cierre: P5 (4/8 puntos post-ejecución, afirmación falsa en `NR7-AC-S2-green.txt`, escaneo staged **muerto** por `NameError` tragado por su propio `except`) y P6 (tarea 4 con actas a mano pese a la prohibición, `DeliveryPackager` con **0 coincidencias** en los 4 archivos nuevos, NR7 sobredichado, cláusula 2 de AC-G2 sin tocar) | El sustituto AC-V1 se apoyaba en que el par NR7 por fase bastaba. Medido: el par por fase **se declaró y no existía**. §4.6 distingue justamente esa verificación local de la de integración |
| 3 | **AC-V1 no cabía en su contenedor**: RELEASE es DELEGABLE / BAJA / 30 iteraciones para once obligaciones documentales. El precedente (VALIDADOR-URL-PROPIA) certificó **8 ACs con 41–50 iteraciones en DIRECTO**, tope 60; a esa tasa 25 ACs ≈ 140 | Brecha ≈ 4–5x **y** modo prohibido por §4.6 para esta tarea |

**Abanico evaluado** (no solo la opción preferida): **A** mantener AC-V1 tal cual (coste 0, riesgo: certificar el claim central del plan con 4–5x menos presupuesto en modo delegado) · **A'** RELEASE en DIRECTO con 60–70 iteraciones (arregla modo y presupuesto, sigue mezclando certificación y cierre documental) · **B** VERIFY completa re-verificando los 25 ACs desde cero (fiel al precedente, ~140 iteraciones, **duplica** lo que P5-R y P6-R ya midieron) · **C** VERIFY acotada con profundidad escalonada (~60 iteraciones). **Se elige C.**

**Qué se descarta de B, y por qué es legítimo**: P6-R ya curó I1–I5 con evidencia medida (matriz contra el flujo real, 5 pares por **reversión del fix** con restauración verificada por hash, converter sin defaults, fuente única de la ruta ZIP) y la remediación de P5 dejó su camino vigilado por test. Repetir esas mediciones sería inflar el presupuesto sin añadir cobertura. De ahí los niveles **RE-V / CIT / CON** de la T1 del prompt: re-verificar lo declarativo o tocado por remediación; citar con comprobación de existencia lo ya medido; y contradecir el registro donde la realidad no lo sostenga (muestreo obligatorio de ≥3 filas).

**Consecuencias**: (i) el orden pasa a P6-R → **VERIFY → RELEASE**; (ii) Tarea 1 de RELEASE se reduce a verificar que la matriz existe, está completa y está citada; (iii) el presupuesto de RELEASE vuelve a ser suficiente para lo documental; (iv) **ninguna fase de código se reabre**: un ❌ de VERIFY abre sesión de recuperación con su propio patrón (P5-R / P6-R), no un fix dentro de la certificación; (v) Tier A y el contrafactual del enforcement siguen sin observar — VERIFY los declara como **límite del plan**, igual que los declaraba AC-V1.


---

## Diagrama ASCII de dependencias

```
FASE-RELEASE-4.76.0 del predecesor ✅ cumplida 2026-09-11 (`3bdc14e`)   ← PRECONDICIÓN
        │
        ▼
FASE-P1 ✅ (2026-09-14) — Q1=sí · Q1b=escalar · Q2=O1-cuarentena · Q2b=ambas capas
                           Q3=P3→P2 · Q4=el hotel (T3a externa) · Q5=a · Q6=4 estados
                           Q7=hereda GATE_BLOCKING_ENABLED · VERIFY=no activa → 🔁 reabierta por D-AJUST.4
                           Contrato: evidence/FASE-P1/decision-enforcement.md
        │
        ▼  (orden fijado por DA-P1.3: substrato confiable antes que dientes)
FASE-P3-A ✅ (2026-09-14) (detección y fidelidad: AC-F1 dos capas ZIP-aware + AC-F2
           fuente del tier + AC-F4 primer piso en B+)  ← ejecutada; no tocó main.py
        │
        ▼
FASE-P3-B ✅ (2026-09-14) (cableado y test: AC-F5 banderas reales [disparado por Q5=a]
           + AC-F3 whitelist barreda + AC-F6 versión del acta)  ← ejecutada; **sí tocó main.py**
        │
        ▼  (P2 llega con judge.py y el resolutor de entrega ya corregidos)
FASE-P2 ✅ (2026-09-14) (O1-cuarentena: package write→revisar→decidir→publish; AC-E0…AC-E5;
         su prompt existía: 05-prompt-inicio-sesion-fase-P2.md)  ← ejecutada; tocó
         `judge.py`, `main.py`, `delivery_packager.py`, `acta_writer.py` y `asset_reviewer.py`
        │
        ▼
FASE-P4 ✅ (2026-09-14) — corrida de observación REAL con Hotel Don Alfonso  ← EJECUTADA:
         (T3a ✅ por el operador · techo `B_PLUS` con     el escenario "cierre sin P4" **no se
          dueño nombrado por AC-O0)                       invocó** — su disparador midió falso
         verdict `BLOQUEADO` → **ZIP SUPPRIMIDO** (primer caso real), 9 hallazgos con dueño
        │
        ▼
FASE-P5 ✅ (2026-09-15) — seguridad y privacidad; AC-S1…AC-S4  ← EJECUTADA:
        │ AC-S1 ✅ (sanitización de errores en providers LLM, 11 tests, NR7 green/red),
        │ AC-S2 ✅ remendada (tracked+staged con sniff NUL, NO_CUBIERTO bloqueante,
        │ │   staged vivo — el de b25b63a estaba muerto por NameError — y check de
        │ │   material de cliente separado: config/client_material_policy.yaml),
        │ AC-S3/AC-S4 ✅ (inventario de superficie pública y puerta operativa documentados)
        │ cierre técnico completado; estado operativo de AC-S4 pendiente de decisión del operador
        │ `--quick` 10/10 tras la remediación (ver REMEDIACION-auditoria-2026-09-15.md)
        ▼
FASE-P6 ✅ (2026-09-15) — generación y validación multi-hotel; AC-G1…AC-G5  ← EJECUTADA:
        │ AC-G1 ✅ (instrucciones desde la entrega real con asset_zip_paths),
        │ AC-G2 ✅ (onboarding sin dependencia de YAML ajeno — fallback independiente),
        │ AC-G3 ✅ (sha256/member_count del .zip.tmp antes de suppress),
        │ AC-G4 ✅ (matriz offline ≥3 perfiles sintéticos),
        │ AC-G5 ✅ (tres caminos causales con NR7 green/red)
        │ NR1: 4169→4189 (+20), 0 regresiones, 5 pares NR7
        │ [P6-R 2026-09-15: matriz contra flujo real + 5 pares por INVERSION del fix; NR1-P6R 4189→4196]
        ▼
FASE-VERIFY ✅ (cerrada 2026-09-15: matriz de 25 ACs + 6 cruces cross-fase + 6 greps + triaje Seguimientos)
        │
        ▼
FASE-RELEASE-4.77.0 ✅ (2026-09-15): cierre documental; AC-V1 = verificó y citó la matriz de VERIFY; tag `v4.77.0`; archivado R2.5; push con confirmación explícita

FASE-VERIFY: **SÍ crea sesión** desde D-AJUST.4 (2026-09-15). P1 la había cerrado como no activa el 2026-09-14.
```

**D-PRE.1 (2026-09-15) concreta D-P4.1 en dos sesiones:** P5 atiende F-P4.5 y la exposición de datos; P6 atiende F-P4.1, los prerrequisitos de datos F-P4.3/F-P4.7 y la huella F-P4.9. Su matriz reproducible atiende F-P4.8 y separa las causas de F-P4.2 sin cambiar la matriz de veredictos. RELEASE no recibe correcciones de código.

**Rectificación causal:** la muestra de P4 fue una corrida Don Alfonso y tres ZIP de Salento Real, no una tasa universal de bloqueo. El stub impide el control positivo de entrega válida; no vuelve imposible «gates permiten/revisor objeta». P4 no ejercitó ese caso porque los gates de coherencia ya bloqueaban antes de los revisores. P6 prueba ambos controles con el mismo input salvo el defecto plantado y registra por separado el bloqueo previo por gates.

**P2 y P3-A/P3-B comparten `judge.py`/`main.py` y el conteo NR1 → secuenciales entre sí, nunca simultáneas** (regla de cabecera). El reordenamiento P3→P2 no cambia eso: lo hace más limpio, porque P2 ya no pisa el archivo que P3-A está corrigiendo.

> **Queda sin efecto**: la variante "Q1=(c) — P4 antes que P2". Q1 se respondió **sí** con refactor, y la opción (c) fue explícitamente rechazada (DA-P1.1) porque con el cableado actual la corrida no puede observar Tier A, así que "observar antes de decidir" no mostraba el caso que motiva la decisión.

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-P1 ✅ (2026-09-14) | RELEASE-4.76.0 del predecesor ✅ | P3-A, P3-B, P2, P4, RELEASE | **Contrato cerrado** en `evidence/FASE-P1/decision-enforcement.md` — Q1=sí, Q1b=escalar, Q2=O1-cuarentena, Q2b=ambas capas, Q3=P3→P2, Q5=a, Q6=4 estados, Q7=knob heredado, VERIFY=no activa (🔁 reabierta por D-AJUST.4, 2026-09-15). Lo decidido aquí obliga a las fases de código (regla §15.4.1) |
| FASE-P3-A ✅ (2026-09-14) | P1 (Q2b = las dos capas) ✅ | P3-B, P2, P4, RELEASE | **Cerrada**: AC-F1 (lectura ZIP-aware + stub estructural, 4 estados NR8 en `_impl_order_check`), AC-F2 (tier desde `financial_scenarios_*.json → breakdown.evidence_tier`, MANIFEST fallback), AC-F4 (`FIRST_FLOOR_TIERS` extendido a `"B+"`). **AC8 y AC-F2 complan el mismo resolutor** (raíz común DA-P1.5: `_resolve_delivery_dir` de Bot 3 y `_read_evidence_tier` del Juez, ambos contra un layout descomprimido). **No tocó `main.py`** (verificado con `git status`). 4 pares NR7 verde/rojo, R2.7 4.109→4.130 (+21) |
| FASE-P3-B ✅ (2026-09-14) | P1 (Q5=a) ✅ + P3-A ✅ (baseline NR1 y `acta_writer.py`) | P2, P4, RELEASE | **Cerrada**: AC-F5 **disparado y ejecutado** — hoist de `ga4_available`/`gsc_available` al `HotelFinancialData` de FASE-K (toca `main.py`); **medido**: GSC no tenía valor real que hoistear (nadie lo computaba en `v4complete`), así que hubo que calcularlo, y `gsc_configured` del MANIFEST se apuntó a la misma variable para no divergir del tier (L-SR3). AC-F3 whitelist barreda **test-only** justificada por §5.1 del contrato — **se cierra D-V.1**, la deuda que v4.76.0 publicó abierta. AC-F6 versión del acta desde `VERSION.yaml` leída en cada escritura. **Cero cambios en `judge.py`/`asset_reviewer.py`** (verificado con `git show --stat`). 6 pares NR7 verde/rojo, R2.7 4.130→4.153 (+23), 0 regresiones |
| FASE-P2 ✅ (2026-09-14) | **P3-A ✅ + P3-B ✅** + contrato P1 (Q1/Q1b/Q2/Q6/Q7) | P4, RELEASE | **Cerrada**: O1-cuarentena ejecutada — `DeliveryPackager` partido en `write()` (deja `<hotel>_<fecha>.zip.tmp`) / `publish()` (rename) / `suppress()` (unlink), con `_validate_zip` ahora sobre el `.tmp`; `reviewer_reports` tipado (`ReviewerReport`/`CorrectiveAction`/`TribunalOutcome`/`EnforcementState` en `tribunal/outcome.py`) y poblado; `_compute_verdict` con el cuarto argumento y la matriz §2.1 en su orden. **AC-E0…AC-E5** con **8 pares NR7** verde/rojo, R2.7 **4.153→4.181 = +28**, 0 regresiones, `--quick` 9/9. **Las dos verificaciones obligatorias se midieron**: el ZIP **sí** empaquetaba el acta (`ASSETS/v4_audit/acta_revision.{json,md}`, medido sobre `output/v4_complete/deliveries/hotelsalentoreal_20260911.zip`) → DA-P2.1; y el resolutor de Bot 3 veía solo `*.zip`, no la cuarentena → la **tensión heredada** (Q2b asumía ZIP publicado / Q2 pone los revisores sobre el `.zip.tmp`, registrada en Seguimientos) se cerró con un resolutor que lee un ZIP en cualquiera de los dos estados. **Cero re-decisiones de Q1/Q1b/Q2/Q5/Q6/Q7**; lo que el contrato no dejaba decidir quedó como DA-P2.1/2/3/4 con su causa |
| FASE-P4 ✅ (2026-09-14) | P2 ✅ + **T3a datos operativos** ✅ (6 hoteles resuelven por el fallback del cargador; el operador eligió **Hotel Don Alfonso** y registró consentimiento y límite de frescura en `evidence/FASE-P4/consentimiento-donalfonso.md`) | RELEASE | **Cerrada corriendo, no difiriendo**: el disparador de §Cierre válido sin P4 («no hay dato con fuente») **midió falso**. Corrida de observación real → **`verdict BLOQUEADO` y ZIP suprimido**, primer caso en el pipeline; `reviewer_reports` de longitud 4 en el artefacto; **AC-F2/AC-F4 observados en vivo**; techo `B_PLUS` con dueño nombrado (**AC-O0: analítica del hotel, no cableado**). **Quedan sin observar**: Tier A (sigue abierta **T3b**, la única precondición externa viva) y el **contrafactual** del enforcement (los gates ya bloqueaban antes). **9 hallazgos con dueño (F-P4.1…F-P4.9), cero código de producción tocado**. Informe: `evidence/FASE-P4/informe-observacion.md` |
| FASE-P5 ✅ (2026-09-15) | P4 ✅ (F-P4.5 documentado en informe de observación) | P6, RELEASE | **Cerrada**: AC-S1 ✅ (sanitización de API keys en errores/logs de providers LLM — `_query_gemini` movió key de URL a header `x-goog-api-key`, `_sanitize_text` + `_sanitize_error` en todos los except, 11 tests nuevos, NR7 green/red capturado); AC-S2 ✅ (checker `_check_no_secrets` ampliado a 13 extensiones de texto + contenido staged via `git diff --cached`, patrones de valor `AIzaSy...`/`sk-...`/`ghp_...`/`pplx-...`, allowlist documentado para `archives/`/`evidence/`/`.opencode/`, 3058 archivos escaneados, NR7 green/red capturado); AC-S3/AC-S4 ✅ (inventario de superficie pública y puerta operativa documentados en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md`, cierre técnico completado, estado operativo de AC-S4 pendiente de decisión del operador — rotación/contención con presupuesto FUERA DE SERVICIO). **NR1 baseline**: 4,145 passed (4,134 pre + 11 nuevos), 0 regresiones, 2 fallos ajenos documentados (`test_function_default_flags` flaky, `test_diagnostic_includes_geo_metrics` registrado en aba517a). **Cero cambios en `main.py`/`judge.py`/`acta_writer.py`** (verificado con `git status`). `--quick` 9/9 — **[REMEDIACIÓN 2026-09-15, auditoría forense]**: el escaneo staged de b25b63a estaba **muerto** (`re` fuera de scope → NameError tragado; L-T2C.2 en el propio checker); alcance re-estrechado a **tracked+staged** (el conteo 3058/3084 era workspace, 41 % nunca versionable); estados NR8 reales (`NO_CUBIERTO` bloqueante, verde `SIN_HALLAZGOS`); check separado de **material de cliente** (`config/client_material_policy.yaml`, 1 grandfathered con dueño AC-S4); 10 tests nuevos → **NR1 4,155 (+10)**, `--quick` **10/10** (denominador full 14). Evidencia: `evidence/FASE-P5/REMEDIACION-auditoria-2026-09-15.md`. **Iteraciones (celda que el cierre original dejó vacía — L-P5.3)**: presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); medida real auto-reportada con unidad declarada = **commits de ejecución por sesión: 1 (`b25b63a`) + 1 de remediación; corte = HEAD al cerrar**; el instrumento no alcanza el transcript (D-V2.1 reproducido, constancia en la evidencia de remediación §3) |
| FASE-P6 ✅ (2026-09-15) | P5 ✅ (cierre técnico completado) + P4 ✅ (F-P4.1/F-P4.3/F-P4.7/F-P4.9 documentados en informe de observación) | RELEASE | **Cerrada**: AC-G1 ✅ (instrucciones desde la entrega real — `asset_zip_paths` en `delivery_packager.write()` y `generate_delivery_template`, sección de assets desconocidos en `asset_responsibility_contract.py`); AC-G2 ✅ (onboarding sin dependencia de YAML ajeno — `_load_latest_onboarding_data` con fallback independiente del archivo externo); AC-G3 ✅ (identidad del paquete suprimido — `_compute_package_evidence` captura SHA256 + `member_count` del `.zip.tmp` antes de `suppress()`, rendering en `acta_writer._render_package_evidence`); AC-G4 ✅ (matriz offline ≥3 perfiles sintéticos — `test_multi_hotel_matrix` con 3 perfiles que cubren tier A/B/C); AC-G5 ✅ (tres caminos causales con NR7 — path 1: gates allow + reviewers allow → publish; path 2: gates allow + reviewers object → block; path 3: gates block by tier C → conditional + blocks=True). **NR1**: 4.169→4.189 (+20), 0 regresiones, ~~5 pares NR7 verde/rojo~~ **[ANOTACIÓN P6-R: los 5 pares originales cubrían solo AC-G4/G5 y mutaban expectativas, no revertían el fix; los pares por reversión (G1, G2×2, G3, G5) llegan en P6-R]**. **Archivos de producción tocados**: `main.py` (AC-G1/G2/G3), `delivery_packager.py` (asset_zip_paths), `asset_responsibility_contract.py` (ZIP paths + unknown assets), `acta_writer.py` (package_evidence rendering). **Cero cambios en `judge.py`** (verificado con `git status`). Presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); medida real auto-reportada con unidad declarada **[ANOTACIÓN P6-R: la celda no nombraba unidad ni corte y la fase llegó sin commitear — se cierra en P6-R]** |
| FASE-P6-R ✅ (2026-09-15) | Auditoría forense P6 (`evidence/FASE-P6/AUDITORIA-forense-2026-09-15.md`, encargo del operador) | RELEASE | **Remediación post-auditoría, mismo día (patrón P5)**: R1 matriz contra el **flujo real** (`tests/test_p6r_full_flow_matrix.py`: `packager.write()` → ZIP real → 4 Bots → Juez → publish/suppress; 5 perfiles con **B+ Don Alfonso anonimizado**, gates-ya-bloquean con causa separada, primer piso y kill switch de dos llaves); R2 **5 pares NR7 por reversión del fix** con restauración verificada por hash (`nr7_p6r_mutation_checks.py`); R3 seis falsedades anotadas sobre el registro histórico; R4 converter AC-G2 sin defaults inventados (`verified`/rooms/pct/campos_confirmados) con test migrado con causa; R5 re-escritura del acta fuera del `try` cuyo fallo publicaba el ZIP bloqueado; R6 mapeo ZIP de fuente única en el packager + disposición de `ImplementationOrderGenerator` (legacy sin consumidores). **NR1 POST-P6-R**: 4.189→**4.196** (+7), 0 regresiones. Iteraciones (unidad declarada): 1 commit de ejecución (`c31422a`) + 1 documental, corte = HEAD al cerrar; D-V2.1 reproducido |
| FASE-VERIFY ✅ (cerrada 2026-09-15) | P6-R ✅ (todas las fases de implementación cerradas) | RELEASE | **Cerrada**: matriz de certificación de los **25 ACs** con nivel RE-V/CIT/CON por fila (`evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md`), 6 cruces cross-fase (`evidence/FASE-VERIFY/T2-crosses.md`: 5 coherentes + 1 incoherente), 6 greps residuales (`evidence/FASE-VERIFY/T3-greps.md`), triaje de Seguimientos en 3 categorías (`evidence/FASE-VERIFY/T4-triaje.md`: 0 bloqueantes, 5 límite declarado, 9 plan sucesor). **2 hallazgos CON** (CON-1: docs citan switch inexistente; CON-2: cláusulas no actualizadas). **4 lecciones** (L-VERIFY.1–4). DIRECTO, no delegable, no tocó código. Prompt: `05-prompt-inicio-sesion-fase-VERIFY.md` |
| FASE-RELEASE-4.77.0 ✅ (2026-09-15) | P3-A + P3-B + P2 + **P4 ✅** + P5 + P6/P6-R + **VERIFY ✅** | — | **Cerrada**: AC-V1 = **verificó y citó** la matriz de VERIFY (25 filas con Real/Status/nivel, ningún `—`, ningún ❌ remediado en código) en `10-analisis` §Matriz de certificación; bump 4.77.0 + `sync_versions` (6 archivos) + CHANGELOG + GUIA_TECNICA + fila Tests de AGENTS.md (4.233 canónicas; D-V.1 cerrada; denominadores 10/14); CON-1/C8 cerrado como corrección documental anotada (`01`, `10`); write-back QMind **antes** del archivado; plan archivado (R2.5) con diff de `--fix` revisado a mano; tag anotado `v4.77.0` creado en el cierre. Push de master y tag: con confirmación explícita del operador |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|------------------------|--------|------------|
| `main.py` | **P2 ✅ (ordenamiento O1-cuarentena: FASE 7 escribe la cuarentena, FASE-T1b decide el rename)**; **P3-B ✅** (hoist AC-F5 de `ga4_available`/`gsc_available` sobre el bloque FASE-K + `gsc_configured` del MANIFEST leyendo la misma variable); **P6 ✅** (AC-G1 asset collection con ZIP paths, AC-G2 onboarding fallback independiente, AC-G3 `_compute_package_evidence`) | Alto | Secuencial obligatorio: P2 y P3-B nunca en la misma sesión ni en paralelo — **cumplido**: P3-B se cerró en `bad0a5e`, P2 en su propia sesión. P6 secuencia después de P5 |
| `modules/quality_gates/tribunal/judge.py` | **P2 ✅** (`_compute_verdict` con el 4º argumento tipado, `evaluate()` puebla `reviewer_reports` desde el DTO, `collect_reviewer_reports`/`enrich`/`finalize`, `_evidence_tier_source`), P3-A (✅ AC-F2/AC-F4), **P3-B: NO lo tocó** (el AC-F6 vive en `acta_writer.py`; Q6 no se reabrió) | Alto | Secuencial obligatorio — verificado con `git show --stat bad0a5e` (P3-B) y con el orden P3-A → P3-B → P2 |
| `modules/quality_gates/tribunal/asset_reviewer.py` | **P2 ✅** (`_resolve_delivery_zip` también ve `.zip.tmp`; sin eso el `.zip.tmp` de la corrida se publicaba como `ARTIFACT_MISSING`); P3-A ✅ (AC-F1 dos capas). **P3-B: NO lo tocó** — la promesa exacta de D-V.1 era edición test-only | Bajo | Línea roja cumplida: la whitelist se escribió en el test, no en el emisor (`NR7-AC-F3-a/b.txt` prueban la barra sin mutar el emisor) |
| `modules/delivery/delivery_packager.py` | **P2 ✅ (O1-cuarentena)**: `package()` = `write()` + `publish()`, nuevo `suppress()`, helpers de ruta de cuarentena, `QuarantineSuppressionError`, `_validate_zip` movido al `.tmp` y el acta excluida del paquete de cliente (DA-P2.1); **P6 ✅** (AC-G1: parámetro `asset_zip_paths` en `write()`) | Medio | **Contrato primero, tests después**: `tests/delivery/test_p2_cuarentena_zip.py` corre contra ZIP real y `package()` sigue siendo la API que usaban `execute` y los **69 tests previos de `tests/delivery/`, que no se tocaron** (78 recolectados con los 9 nuevos de esta fase, todos verdes). Tres tests ajenos al packaging sí se migraron con causa escrita en `nr1_delta_r2_7.md`: dos de `test_judge.py` (la primera pasada ya no certifica entrega) y uno de `test_acta_serialization.py` (la fuente del tier ya no es un literal del writer) |
| `modules/quality_gates/tribunal/acta_writer.py` | **P3-B ✅ (AC-F6: versión desde `VERSION.yaml`)**; **P2 ✅** (guard `if reviewer_reports:` eliminado — DA-P1.6 regla 1; secciones `Reportes de Revisores`/`Acciones correctivas`/`Enforcement`; y la fuente del primer piso deja de ser un literal del writer, que era el seguimiento que este plan asignaba a P2); **P6 ✅** (AC-G3: `_render_package_evidence` para SHA256/member_count) | Bajo | Secuencial: la segunda pata se cerró en P2 con su propio test y su mutación (`NR7-AC-E0-b.txt`) |
| `tests/quality_gates/tribunal/` | **P2 ✅** (`test_p2_veredicto_enriquecido.py`, 19 + 3 tests migrados con causa declarada), P3-A ✅, P3-B ✅ | Bajo | Archivos de test disjuntos por fase. **El `__init__.py` del paquete ya no está vacío**: P2 exportó los DTOs del contrato, así que el ritual de cierre cambia — ahora `from modules.quality_gates.tribunal import ReviewerReport` es parte de la superficie pública y queda verificado por los tests que importan del paquete |
| `test_barreda_un_solo_emisor_de_la_clave` | **P3-B ✅ (whitelist test-only, D-V.1 CERRADA)** | Bajo | Edición test-only; el emisor quedó intacto. La barra sigue siendo igualdad de conjuntos. **P2 no añadió un tercer emisor**: `outcome.py` no emite `"asset_path":` (verificado por el propio test, en verde en el POST) |
| Conteo NR1 (suma de tests) | P3-A ✅ (4.109→4.130), **P3-B ✅ (4.130→4.153)**, **P2 ✅ (4.153→4.181)**, P5 ✅ (4.155→4.169 tras remediación), **P6 ✅ (4.169→4.189)** en secuencia | Medio | Cada fase toma su snapshot `pre` y resta R2.7; nunca dos fases miden el mismo baseline — el PRE de P2 **es** el POST de P3-B (4.153), lo que encadena los tres deltas sin solapamiento. P6 PRE (4.169) incluye los +10 de la remediación de P5 |

---

## Cierre válido sin P4 (fijado en la sesión de ajuste 2026-09-14)

> **Resuelto el 2026-09-14 en FASE-P4: este escenario NO se invocó.** Medido con
> `evidence/FASE-P4/t3a_sonda_candidatos.py`, **T3a ya estaba satisfecha** para los 6 hoteles de
> `data/hotel_observations/observations.json` — el propio cargador los resuelve por URL normalizada
> vía `_observation_to_onboarding_format` —, de modo que el disparador («no hay dato con fuente») no
> se cumplió y **P4 se corrió**. La sección se conserva tal cual: es la mecánica que hereda el plan
> de analítica sucesor si ahí sí falta el dato, y L-P4.1 deja escrita la advertencia — un disparador
> redactado como pregunta de existencia hay que **medirlo contra el runtime**, no leerlo literal.

P4 depende de dos precondiciones que pueden no cerrarse nunca: **T3a** (hotel con datos operativos y fuente) y **T3b** (GA4+GSC, y bajo Q5=a además código en `main.py`). El plan **no queda bloqueado** por su incumplimiento:

| Disparador | Mecánica (idéntica en los tres casos) |
|------------|----------------------------------------|
| Q5=(c) decidida en P1 | Ya especificado en el prompt P1: README pasa a 5 sesiones, `dependencias-fases.md` aplaza P4 con la decisión registrada |
| **T3a no se cierra** (Q4 sin proveedor de datos con fuente, ni aparece después) | P4 se difiere con la misma mecánica: decisión fechada en `evidence/FASE-P1/decision-enforcement.md` o en el `10-analisis` si surge tras P1, README a 5 sesiones, y RELEASE ejecuta con P4 diferida |
| T3b no se cierra pero T3a sí | **No** difiere P4: la corrida se especifica en `B_PLUS` con límite declarado (AC-O0). Diferir sería tirar el único dato real disponible |

**Consecuencias del diferimiento** *(escenario no invocado: P4 se corrió; la consecuencia (i) quedó sin efecto por D-AJUST.4)*: (i) FASE-VERIFY pierde el criterio 2 → no activa, AC-V1 la sustituye; (ii) la decisión de enforcement Q1=(c) queda prohibida en la práctica (no hay corrida que observe) — si P1 eligió (c) y T3a luego falla, la resolución por defecto es O4 documentada, registrada como decisión; (iii) el `10-analisis` declara el régimen Tier A como **no observado por este plan**, y el sucesor de analítica hereda P4 como fase propia. Lo que NO se permite: RELEASE con P4 "en espera", ni un `—` en su fila del checklist sin decisión registrada.

---

## Dependencias externas (fuera de alcance de código)

| Sub-fase | Precondición externa | Por qué |
|----------|---------------------|---------|
| **FASE-P4 — T3a** (datos operativos) | Hotel propio: `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada (precondición T3 del ROADMAP) | Sin dato verificado, `_determine_evidence_tier` cae en `B`/`C` y el primer piso no se levanta. Su fallo **sí** difiere P4 (§Cierre válido sin P4) |
| **FASE-P4 — T3b** (analítica) — nueva, medida 2026-09-12; **su mitad de código la cerró AC-F5 en P3-B (2026-09-14)** | Credenciales y propiedad de **GA4 y GSC** configuradas. El cableado que propaga esa disponibilidad al `HotelFinancialData` del bloque FASE-K **ya existe** (Q5=a ejecutada): `ga4_available`/`gsc_available` se calculan antes de FASE-K y alimentan el tier. Lo que queda externo es el dato, no el pipeline | `_determine_evidence_tier` devuelve `A` solo con `ga4_enabled and gsc_enabled and has_verified_data`, y `_compute_verdict` exige `A` para `APROBADO-PARA-ENTREGA`. Con solo T3a el techo es `B_PLUS`. Su fallo **no** difiere P4: AC-O0. **Hecho nuevo medido en P3-B**: el pipeline **no consume** datos de GSC en `v4complete` (nadie llama `get_search_analytics()`); la regla FASE-1 decide por **conectividad**, no por dato consumido, así que un `A` con GSC configurado y sin datos leídos descansa en esa distinción — y es el punto que AC-O0 debe declarar si P4 llega a ella |
| FASE-P4 (consentimiento) | El hotel/dueño acepta que la corrida use sus datos | Es una corrida de observación, no una entrega; igual requiere autorización |
| T5 / T6 (ROADMAP) | Credenciales FTP/WP + staging / escala | Fuera de alcance de este plan (igual que en el predecesor) |

**Consecuencia**: P1–P3-A/P3-B **se ejecutaron** sin dato real. P4 queda condicionada a T3a **y** T3b; desde el 2026-09-14 ambas son puramente externas, porque la tercera pata que tenía T3b (cablear las banderas en `main.py`, Q5=a) la cerró **AC-F5 en P3-B**. Si T3b no se cierra, P4 se corre en `B_PLUS` con el límite declarado (AC-O0); si T3a no se cierra, aplica §Cierre válido sin P4. Lo que ya **no** puede alegar un `B_PLUS` en P4 es "el pipeline no propaga las banderas": esa excusa quedó cerrada, y AC-O0 obliga a nombrar el dueño real del techo (dato verificado ausente, o credenciales GA4/GSC ausentes).

---

## Nota de rutas (post-R2.5 del predecesor)

El archivado (R2.5) de TRIBUNAL-OFFLINE-2026-09-09 **ya se ejecutó** el 2026-09-11 (`3bdc14e`) y movió sólo los documentos del plan: `10-analisis-post-implementacion.md`, `06-checklist-implementacion.md` y los `05-prompt-...` viven ahora en `Archives/TRIBUNAL-OFFLINE-2026-09-09/`. La **evidencia no se mueve**: `MATRIZ-CERTIFICACION.md` sigue en `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/` y `decision-integracion.md` en `evidence/FASE-T1/` (ambos rastreados, verificado con `git ls-files`).

> **Higiene de cita (sesión de ajuste 2026-09-14)**: este archivo y los prompts del plan citaban `bd2bf57` como el commit del RELEASE. Es el duplicado pre-rebase: **no está en `origin/master`** y solo sobrevive en la rama local `backup/pre-sanidad-evidence-20260912`. El commit vivo es `3bdc14e`. Las citas históricas correctas (p. ej. "executor v2.21.0 introdujo R2.6/R2.7") se mantienen; lo que se corrigió son las afirmaciones en presente ("sin push ni tag") que el rebase y el tag `v4.76.0` (creado y empujado 2026-09-14) dejaron obsoletas.

**Convención de rutas corregida (2026-09-12)**: lo que se escribe como plantilla `<PLAN>` son las **auto-referencias** a este plan — son las que `validate_opencode_refs.py --fix` reescribe a ciegas cuando ESTE plan se archive, y las que pueden destrozar un comando documentado. Las rutas ya archivadas del predecesor (`Archives/TRIBUNAL-OFFLINE-2026-09-09/…`) **sí** se citan completas: un directorio en `Archives/` no vuelve a moverse. El checklist de RELEASE exige revisar a mano el diff de `--fix` post-archivado.

---

## Punto de partición predefinido

Si FASE-P2 agota su presupuesto (55 iteraciones):
- **P2-part1**: contrato del veredicto enriquecido implementado en `judge.py` (`_compute_verdict` consume `reviewer_reports`) + tests
- **P2-part2**: reordenamiento del flujo (`main.py` / `delivery_packager.py`) según O1/O3

El cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.
