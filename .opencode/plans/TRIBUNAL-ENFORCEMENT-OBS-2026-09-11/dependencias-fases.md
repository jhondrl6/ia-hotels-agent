# Dependencias entre Fases — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases previas están ✅ — **o** cuando una fase no ejecutada está **oficialmente diferida por decisión registrada** (véase §Cierre válido sin P4). Un diferimiento silencioso no cierra el paso a RELEASE.
> **Regla heredada**: nunca sesiones paralelas sobre el mismo working tree (el plan predecesor documentó sobrescritura de evidencia). P2, P3-A y P3-B comparten `judge.py`/`main.py`/`acta_writer.py` y el conteo NR1 → **secuenciales entre sí, nunca simultáneas**.

---

## Estado de la Etapa 1 (Preparación) — sesión de ajuste 2026-09-14

El executor (§Aplicación) exige que la Etapa 1 genere **todos** los prompts de fase, RELEASE incluido, y los archivos `09`/`10` desde la concepción. Al concebir el plan (2026-09-11) esto no se cumplió; la sesión de ajuste lo cierra:

| Entregable Etapa 1 | Estado |
|--------------------|--------|
| `05-prompt-inicio-sesion-fase-P1.md` | ✅ (revisado en el ajuste: citas, divisiones, escenarios) |
| `05-prompt-inicio-sesion-fase-P3-A.md` · `-P3-B.md` · `-P4.md` · `-RELEASE.md` | ✅ Creados 2026-09-14 con placeholders `⟨P1 fija⟩` donde la decisión manda |
| `05-prompt-inicio-sesion-fase-P2.md` | ✅ **Creado por FASE-P1 el 2026-09-14**, con la opción elegida (O1-cuarentena) y el contrato vinculante en su encabezado. El diferimiento estaba declarado en la fila original de esta tabla y en la cabecera del propio P1: escribir un prompt antes de conocer la opción habría producido un prompt falso, no incompleto |
| `09-documentacion-post-proyecto.md` · `10-analisis-post-implementacion.md` | ✅ Creados 2026-09-14 con estructura base; el `10-` ya registra la decisión del ajuste (D-AJUST.1–.3) |
| Decisión FASE-VERIFY (§4.6) | ✅ **CERRADA por FASE-P1: no activa** (§FASE-VERIFY abajo). AC-V1 de RELEASE es el sustituto declarado |
| Escenario de cierre sin P4 | ✅ Fijado (§Cierre válido sin P4 abajo) |

---

## Decisión FASE-VERIFY (§4.6 del executor) — **CERRADA en FASE-P1: NO activa**

Los tres criterios de activación se evalúan sobre la división de fases **post-ajuste** (P1 decide; P2/P3-B son condicionales):

| Criterio §4.6 | Evaluación |
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

---

## Diagrama ASCII de dependencias

```
FASE-RELEASE-4.76.0 del predecesor ✅ cumplida 2026-09-11 (`3bdc14e`)   ← PRECONDICIÓN
        │
        ▼
FASE-P1 ✅ (2026-09-14) — Q1=sí · Q1b=escalar · Q2=O1-cuarentena · Q2b=ambas capas
                           Q3=P3→P2 · Q4=el hotel (T3a externa) · Q5=a · Q6=4 estados
                           Q7=hereda GATE_BLOCKING_ENABLED · VERIFY=no activa
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
FASE-RELEASE-4.77.0 (cierre + tag + AC-V1 con el patrón VERIFY embebido + archivado R2.5)

FASE-VERIFY: NO crea sesión (decisión cerrada en P1, §FASE-VERIFY arriba).
```

**NO OBSTACULIZA — pero sí reordena (D-P4.1, decidida al cerrar P4 el 2026-09-14):** la sesión
siguiente a P4 **no** es RELEASE. Se abre una fase propia de remediación de los hallazgos de la
corrida — **F-P4.1** (el stub `IMPLEMENTATION_ORDER.md` que bloquea toda corrida real y hace
inobservable el contrafactual de Q1), **F-P4.5** (cobertura del barrido de secretos: hoy solo `*.py`
con 4 patrones de asignación) y **F-P4.9** (`suppress()` borra el ZIP que los revisores leyeron) —,
con sus ACs y su par NR7. RELEASE (AC-V1 + bump + tag + R2.5) se ejecuta después de esa fase.

**P2 y P3-A/P3-B comparten `judge.py`/`main.py` y el conteo NR1 → secuenciales entre sí, nunca simultáneas** (regla de cabecera). El reordenamiento P3→P2 no cambia eso: lo hace más limpio, porque P2 ya no pisa el archivo que P3-A está corrigiendo.

> **Queda sin efecto**: la variante "Q1=(c) — P4 antes que P2". Q1 se respondió **sí** con refactor, y la opción (c) fue explícitamente rechazada (DA-P1.1) porque con el cableado actual la corrida no puede observar Tier A, así que "observar antes de decidir" no mostraba el caso que motiva la decisión.

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-P1 ✅ (2026-09-14) | RELEASE-4.76.0 del predecesor ✅ | P3-A, P3-B, P2, P4, RELEASE | **Contrato cerrado** en `evidence/FASE-P1/decision-enforcement.md` — Q1=sí, Q1b=escalar, Q2=O1-cuarentena, Q2b=ambas capas, Q3=P3→P2, Q5=a, Q6=4 estados, Q7=knob heredado, VERIFY=no activa. Lo decidido aquí obliga a las fases de código (regla §15.4.1) |
| FASE-P3-A ✅ (2026-09-14) | P1 (Q2b = las dos capas) ✅ | P3-B, P2, P4, RELEASE | **Cerrada**: AC-F1 (lectura ZIP-aware + stub estructural, 4 estados NR8 en `_impl_order_check`), AC-F2 (tier desde `financial_scenarios_*.json → breakdown.evidence_tier`, MANIFEST fallback), AC-F4 (`FIRST_FLOOR_TIERS` extendido a `"B+"`). **AC8 y AC-F2 complan el mismo resolutor** (raíz común DA-P1.5: `_resolve_delivery_dir` de Bot 3 y `_read_evidence_tier` del Juez, ambos contra un layout descomprimido). **No tocó `main.py`** (verificado con `git status`). 4 pares NR7 verde/rojo, R2.7 4.109→4.130 (+21) |
| FASE-P3-B ✅ (2026-09-14) | P1 (Q5=a) ✅ + P3-A ✅ (baseline NR1 y `acta_writer.py`) | P2, P4, RELEASE | **Cerrada**: AC-F5 **disparado y ejecutado** — hoist de `ga4_available`/`gsc_available` al `HotelFinancialData` de FASE-K (toca `main.py`); **medido**: GSC no tenía valor real que hoistear (nadie lo computaba en `v4complete`), así que hubo que calcularlo, y `gsc_configured` del MANIFEST se apuntó a la misma variable para no divergir del tier (L-SR3). AC-F3 whitelist barreda **test-only** justificada por §5.1 del contrato — **se cierra D-V.1**, la deuda que v4.76.0 publicó abierta. AC-F6 versión del acta desde `VERSION.yaml` leída en cada escritura. **Cero cambios en `judge.py`/`asset_reviewer.py`** (verificado con `git show --stat`). 6 pares NR7 verde/rojo, R2.7 4.130→4.153 (+23), 0 regresiones |
| FASE-P2 ✅ (2026-09-14) | **P3-A ✅ + P3-B ✅** + contrato P1 (Q1/Q1b/Q2/Q6/Q7) | P4, RELEASE | **Cerrada**: O1-cuarentena ejecutada — `DeliveryPackager` partido en `write()` (deja `<hotel>_<fecha>.zip.tmp`) / `publish()` (rename) / `suppress()` (unlink), con `_validate_zip` ahora sobre el `.tmp`; `reviewer_reports` tipado (`ReviewerReport`/`CorrectiveAction`/`TribunalOutcome`/`EnforcementState` en `tribunal/outcome.py`) y poblado; `_compute_verdict` con el cuarto argumento y la matriz §2.1 en su orden. **AC-E0…AC-E5** con **8 pares NR7** verde/rojo, R2.7 **4.153→4.181 = +28**, 0 regresiones, `--quick` 9/9. **Las dos verificaciones obligatorias se midieron**: el ZIP **sí** empaquetaba el acta (`ASSETS/v4_audit/acta_revision.{json,md}`, medido sobre `output/v4_complete/deliveries/hotelsalentoreal_20260911.zip`) → DA-P2.1; y el resolutor de Bot 3 veía solo `*.zip`, no la cuarentena → la **tensión heredada** (Q2b asumía ZIP publicado / Q2 pone los revisores sobre el `.zip.tmp`, registrada en Seguimientos) se cerró con un resolutor que lee un ZIP en cualquiera de los dos estados. **Cero re-decisiones de Q1/Q1b/Q2/Q5/Q6/Q7**; lo que el contrato no dejaba decidir quedó como DA-P2.1/2/3/4 con su causa |
| FASE-P4 ✅ (2026-09-14) | P2 ✅ + **T3a datos operativos** ✅ (6 hoteles resuelven por el fallback del cargador; el operador eligió **Hotel Don Alfonso** y registró consentimiento y límite de frescura en `evidence/FASE-P4/consentimiento-donalfonso.md`) | RELEASE | **Cerrada corriendo, no difiriendo**: el disparador de §Cierre válido sin P4 («no hay dato con fuente») **midió falso**. Corrida de observación real → **`verdict BLOQUEADO` y ZIP suprimido**, primer caso en el pipeline; `reviewer_reports` de longitud 4 en el artefacto; **AC-F2/AC-F4 observados en vivo**; techo `B_PLUS` con dueño nombrado (**AC-O0: analítica del hotel, no cableado**). **Quedan sin observar**: Tier A (sigue abierta **T3b**, la única precondición externa viva) y el **contrafactual** del enforcement (los gates ya bloqueaban antes). **9 hallazgos con dueño (F-P4.1…F-P4.9), cero código de producción tocado**. Informe: `evidence/FASE-P4/informe-observacion.md` |
| FASE-VERIFY | — | — | **No activa** (decisión cerrada en P1 arriba). AC-V1 de RELEASE la sustituye como patrón declarado |
| FASE-RELEASE-4.77.0 | P3-A + P3-B + P2 + **P4 ✅ o diferida por decisión registrada** | — | Cierre documental + tag anotado + **AC-V1** (certificación contra artefactos de fase + pares NR7) |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|------------------------|--------|------------|
| `main.py` | **P2 ✅ (ordenamiento O1-cuarentena: FASE 7 escribe la cuarentena, FASE-T1b decide el rename)**; **P3-B ✅** (hoist AC-F5 de `ga4_available`/`gsc_available` sobre el bloque FASE-K + `gsc_configured` del MANIFEST leyendo la misma variable) | Alto | Secuencial obligatorio: P2 y P3-B nunca en la misma sesión ni en paralelo — **cumplido**: P3-B se cerró en `bad0a5e`, P2 en su propia sesión |
| `modules/quality_gates/tribunal/judge.py` | **P2 ✅** (`_compute_verdict` con el 4º argumento tipado, `evaluate()` puebla `reviewer_reports` desde el DTO, `collect_reviewer_reports`/`enrich`/`finalize`, `_evidence_tier_source`), P3-A (✅ AC-F2/AC-F4), **P3-B: NO lo tocó** (el AC-F6 vive en `acta_writer.py`; Q6 no se reabrió) | Alto | Secuencial obligatorio — verificado con `git show --stat bad0a5e` (P3-B) y con el orden P3-A → P3-B → P2 |
| `modules/quality_gates/tribunal/asset_reviewer.py` | **P2 ✅** (`_resolve_delivery_zip` también ve `.zip.tmp`; sin eso el `.zip.tmp` de la corrida se publicaba como `ARTIFACT_MISSING`); P3-A ✅ (AC-F1 dos capas). **P3-B: NO lo tocó** — la promesa exacta de D-V.1 era edición test-only | Bajo | Línea roja cumplida: la whitelist se escribió en el test, no en el emisor (`NR7-AC-F3-a/b.txt` prueban la barra sin mutar el emisor) |
| `modules/delivery/delivery_packager.py` | **P2 ✅ (O1-cuarentena)**: `package()` = `write()` + `publish()`, nuevo `suppress()`, helpers de ruta de cuarentena, `QuarantineSuppressionError`, `_validate_zip` movido al `.tmp` y el acta excluida del paquete de cliente (DA-P2.1) | Medio | **Contrato primero, tests después**: `tests/delivery/test_p2_cuarentena_zip.py` corre contra ZIP real y `package()` sigue siendo la API que usaban `execute` y los **69 tests previos de `tests/delivery/`, que no se tocaron** (78 recolectados con los 9 nuevos de esta fase, todos verdes). Tres tests ajenos al packaging sí se migraron con causa escrita en `nr1_delta_r2_7.md`: dos de `test_judge.py` (la primera pasada ya no certifica entrega) y uno de `test_acta_serialization.py` (la fuente del tier ya no es un literal del writer) |
| `modules/quality_gates/tribunal/acta_writer.py` | **P3-B ✅ (AC-F6: versión desde `VERSION.yaml`)**; **P2 ✅** (guard `if reviewer_reports:` eliminado — DA-P1.6 regla 1; secciones `Reportes de Revisores`/`Acciones correctivas`/`Enforcement`; y la fuente del primer piso deja de ser un literal del writer, que era el seguimiento que este plan asignaba a P2) | Bajo | Secuencial: la segunda pata se cerró en P2 con su propio test y su mutación (`NR7-AC-E0-b.txt`) |
| `tests/quality_gates/tribunal/` | **P2 ✅** (`test_p2_veredicto_enriquecido.py`, 19 + 3 tests migrados con causa declarada), P3-A ✅, P3-B ✅ | Bajo | Archivos de test disjuntos por fase. **El `__init__.py` del paquete ya no está vacío**: P2 exportó los DTOs del contrato, así que el ritual de cierre cambia — ahora `from modules.quality_gates.tribunal import ReviewerReport` es parte de la superficie pública y queda verificado por los tests que importan del paquete |
| `test_barreda_un_solo_emisor_de_la_clave` | **P3-B ✅ (whitelist test-only, D-V.1 CERRADA)** | Bajo | Edición test-only; el emisor quedó intacto. La barra sigue siendo igualdad de conjuntos. **P2 no añadió un tercer emisor**: `outcome.py` no emite `"asset_path":` (verificado por el propio test, en verde en el POST) |
| Conteo NR1 (suma de tests) | P3-A ✅ (4.109→4.130), **P3-B ✅ (4.130→4.153)**, **P2 ✅ (4.153→4.181)** en secuencia | Medio | Cada fase toma su snapshot `pre` y resta R2.7; nunca dos fases miden el mismo baseline — el PRE de P2 **es** el POST de P3-B (4.153), lo que encadena los tres deltas sin solapamiento |

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

**Consecuencias del diferimiento**: (i) FASE-VERIFY pierde el criterio 2 → no activa, AC-V1 la sustituye; (ii) la decisión de enforcement Q1=(c) queda prohibida en la práctica (no hay corrida que observe) — si P1 eligió (c) y T3a luego falla, la resolución por defecto es O4 documentada, registrada como decisión; (iii) el `10-analisis` declara el régimen Tier A como **no observado por este plan**, y el sucesor de analítica hereda P4 como fase propia. Lo que NO se permite: RELEASE con P4 "en espera", ni un `—` en su fila del checklist sin decisión registrada.

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
