# FASE-P3-B · Constancia Q5 — el condicional de la Tarea 3 quedó **disparado**

> **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Fecha**: 2026-09-14
> **Para qué sirve este archivo**: `05-prompt-inicio-sesion-fase-P3-B.md` condiciona la Tarea 3
> (AC-F5) a la decisión Q5 de FASE-P1. La constancia registra qué rama del condicional corrió
> y con qué fuente, para que la presencia o ausencia de la tarea sea auditable sin reabrir la
> decisión (restricción "NO re-decidir Q5", L-VUP-6).

---

## 1. La decisión, citada de su fuente

| Campo | Valor |
|-------|-------|
| Pregunta | Q5 — ¿Tier A inalcanzable por construcción? |
| Decisión | **(a) Propagar las banderas**, como par inseparable con AC-F2 |
| Dueño de la ejecución | **P3-B (AC-F5)** + P3-A (AC-F2) |
| Fuente | `evidence/FASE-P1/decision-enforcement.md` §0 (tabla de decisiones) y DA-P1.8 |
| Fecha de la decisión | 2026-09-14 |

## 2. Rama que corrió

**Rama (a) → la Tarea 3 SÍ se ejecutó.** No aplica la constancia de no-ejecución.

Consecuencias que esto tuvo sobre el presupuesto y la complejidad de la fase, ambas
anunciadas por el propio prompt de fase:

- Presupuesto: **25 iteraciones** (15 si Q5 ≠ (a)).
- Complejidad técnica: **MEDIA** (era BAJA; "Q5=a la sube") porque toca `main.py`.
- El punto 3 de la matriz de completitud del prompt ("Si Q5=a: AC-F5 con sus dos tests
  de tier y hoist sin `except` ancho") queda exigible, no condicional.

## 3. Qué se ejecutó efectivamente

| Elemento | Estado |
|----------|--------|
| Hoist de `ga4_available` / `gsc_available` sobre el bloque FASE-K de `main.py` | Hecho |
| `HotelFinancialData(..., ga4_enabled=ga4_available, gsc_enabled=gsc_available)` | Hecho (antes: dos literales `False`) |
| Test de tier `A` con analítica | Hecho — `TestReglaFASE1SigueViva::test_tier_a_con_analitica_disponible` |
| Test de tier `B+` sin analítica | Hecho — `test_tier_b_mas_sin_analitica`, más dos con una sola bandera |
| Sin `NameError` en régimen `generate_proposal=False` | Hecho — se **amplió** `test_s_e2_generate_proposal_false.py` con `TestAnalyticsFlagsReachableWithoutProposal` (5 tests), tal como pedían DA-P1.8 y el checklist |
| Hoist fuera de todo `except` ancho (L-T2C.2) | Hecho — `test_hoist_fuera_de_todo_except_ancho`, mutado y verificado en `NR7-AC-F5-b.txt` |
| Delta NR1 con par pre/post | Hecho — ver `nr1_delta_r2_7.md` |
| CHANGELOG declara el cambio de tier | Pendiente de publicación — acumulado en `09-documentacion-post-proyecto.md` §E, que es el dueño del CHANGELOG de 4.77.0 |

## 4. Dos hechos nuevos que la decisión Q5 no contemplaba (medidos, no asumidos)

El plan dio por sentado que "la disponibilidad real se calcula más abajo" cubría **ambas**
fuentes. Medido en `main.py`:

1. **GSC jamás se calculaba en `v4complete`.** `AnalyticsStatus()` nace con
   `gsc_available: bool = False` y en el flujo nadie lo asigna, así que no existía un valor
   real que hoistear: hubo que **computarlo**
   (`GoogleSearchConsoleClient().is_configured()`), reutilizando el precedente de
   `modules/analytics/guarantee_validator.py`. Sin esto, propagar solo GA4 dejaba el Tier A
   **igual de inalcanzable** (la regla FASE-1 exige `ga4_enabled and gsc_enabled`) y AC-F5
   habría sido un fix que no arregla lo que nombra.

2. **`gsc_configured` del MANIFEST leía ese mismo campo jamás asignado.** Antes de la fase,
   tier y MANIFEST coincidían por las dos ramas del error (ambos decían "sin GSC"). Tras
   propagar la bandera real, dejar el MANIFEST leyendo `analytics_status.gsc_available` habría
   creado la divergencia que este plan denuncia (L-SR3: una sola fuente de verdad por hecho).
   Se apuntó a la misma variable hoisteada, en analogía simétrica con `ga4_configured`, que ya
   la usaba.

### Divergencia que NO se cierra en esta fase (deuda registrada, con dueño)

`analytics_status.gsc_available` sigue sin asignarse, y por tanto el **diagnóstico**
(`AnalyticsStatus.summary_for_template()` / `gsc_status_for_template()`) puede decir
"GSC: No configurado" mientras el tier dice `A`. No se toca aquí porque el texto del template
afirma "datos de búsqueda orgánica **incluidos**", y el pipeline **no consume** datos de GSC en
`v4complete`: asignar la bandera sin consumir el dato convertiría un "no configurado" honesto
en una afirmación falsa. La cura es doble (consumir GSC o reescribir el texto del template) y
excede a P3-B.

- **Dueño propuesto**: plan de analítica (T3b), o FASE-RELEASE si se decide abrir un AC propio.
- **Por qué no se calló**: el acta del tribunal no consume `analytics_status`, y el MANIFEST ya
  no diverge; la divergencia restante es diagnóstico↔tier y queda documentada aquí y en
  `10-analisis-post-implementacion.md`.

## 5. Techo de tier observado en este entorno (entrada para AC-O0)

`verify_probe_ac_f5_techo_tier.py` sobre el artefacto real de FASE-I:

- Cableado: `ga4_available=False`, `gsc_available=False` (sin credenciales en este entorno).
- El tier de esa corrida es **B con las cuatro combinaciones de banderas**, porque sus fuentes
  son `adr=regional_v410`, `direct_channel=default`: la regla FASE-1 exige además
  `has_verified_data`. **El techo de esa corrida lo pone el dato, no el cableado.**
- Para FASE-P4: el techo `A` exige (i) credenciales GA4+GSC y (ii) onboarding verificado.
  Declarar solo "B+ por cableado" sería atribuir al pipeline un límite que es comercial (T3a/T3b).
