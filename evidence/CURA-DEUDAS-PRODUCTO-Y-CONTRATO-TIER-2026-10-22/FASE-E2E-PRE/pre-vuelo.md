# Pre-vuelo del ensayo — FASE-E2E-PRE (CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22)

> **Medido el 2026-10-24 sobre el árbol vivo y los artefactos del baseline del 2026-10-12.** Ensayo determinista: no se ejecutó `v4complete`, no se llamó al LLM pagado, no se modificó código de producto, no se tocó `deliveries/` real ni el `output/` de la corrida.

## Checks

| # | Check | Criterio | Medido | Estado |
|---|-------|----------|--------|--------|
| 1 | Onboarding materializado | el YAML versionado vive en `output/clientes/` y el loader lo devuelve | sha256 `2990d768…` idéntico entre la copia de trabajo y `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/hotel_don_alfonso_onboarding.yaml`; `_load_latest_onboarding_data("https://www.donalfonsohotel.com/")` devuelve `Hotel Don Alfonso` por la rama `YAML_DE_DIR_CLIENTES` | ✅ |
| 2 | Fuente de las cifras operativas | rooms / adr_cop / occupancy / canal directo con productor nombrado | rooms 11 y canal 30.0 % del YAML; `adr_cop` 330000 y `occupancy_rate` 0.42424… de `financial_scenarios_20261012_165654.json → input_data` (ambas sedes coinciden) | ✅ |
| 3 | Discrepancia de dominio | documentada, sin editar `observations.json` | `observations.json` declara `https://hoteldonalfonso.com/` → normalizada `hoteldonalfonso.com`; la URL del run normaliza a `donalfonsohotel.com`; **no casan por host**. Sonda negativa: con `output/clientes` vacío el loader devuelve `None`, así que el fallback nunca alcanza al hotel | ✅ |
| 4 | Dominio confirmado por el Operador | requerido **antes de FASE-E2E**, no para este ensayo | `domain_confirmed: false`, `domain_confirmed_por: null` en `preflight.json`; antecedente: `onboarding_provenance.json` del baseline declara la URL del YAML como edición explícita del Operador (2026-10-06) | ⏳ condición para E2E |
| 5 | Render B+ sin claims absolutos | 0 ocurrencias de «Protección total»/«Transparencia total»; variantes honestas presentes; labels financieros intactos | propuesta 7.889 B y diagnóstico 8.524 B en `render/`; los dos absolutos **ausentes**; «Protección para usted» y «Transparencia en cada cifra» presentes; «Fuga total estimada» y «Total recuperación proyectada» presentes | ✅ |
| 6 | Cifras del render con fuente | cada valor trazado a un artefacto del baseline | tier `B+` por `resolver_tier_evidencia(breakdown del baseline)`; fuga 6 m 21.067.200 = 3.511.200 × 6; recuperación 6 m 4.731.342 = `calcular_recuperacion_6m(3.511.200; 0.35)`; opex 6 m 2.400.000 = 400.000 × 6; capex 2.500.000 = `packages.setup_fee_default` | ✅ |
| 7 | Revisor real | `summary.over_presentations == 0` y el revisor **leyó** los dos documentos | `review/revision_honestidad.json`: `over_presentations: 0`, 0 hallazgos `OVER_PRESENTATION`, tier resuelto `B+`, manifiesto con `read_status: OK` en `diagnostico` y `propuesta` | ✅ |
| 8 | Juez real con manifiesto reparado (H9) | acta `APROBADO-CONDICIONAL` + `conditional_reason == ANALYTICS_CEILING`; si sale `ONBOARDING_INCOMPLETE`, el ensayo se detiene | `judge/acta_revision.json`: `APROBADO-CONDICIONAL` en la primera y en la segunda pasada, `conditional_reason: ANALYTICS_CEILING`, tier `B+`, primer piso aplicado, `_has_onboarding()` = `True` (manifiesto propio con `has_onboarding: true`); **no se detuvo** | ✅ |
| 9 | `P6.5` intacta | permanece `NOT_EVALUABLE` con su dueño | cláusula `P6.5` = `NOT_EVALUABLE`, «Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a»; `T1_CERTIFIABLE_CLAUSES` no se tocó | ✅ |
| 10 | Mutante del render (R2.8) | apagar la condición → el revisor reemite los claims | `_preprocess_conditionals` forzado a tier `A` dentro del render B+: `over_presentations: 2`, los dos claims exactos («GARANTÍAS: Protección total para usted» y «Transparencia total»). Verde no vacuo: ver `review/mutante-condicion-render.txt` | ✅ |
| 11 | Paquete en temporal | ZIP real con `suppressed: false`, sha, tamaño y `member_count > 0` | `write()` deja `hotel_donalfonsohotel.com_20261024.zip.tmp` (cuarentena); `publish()` lo renombra; 6 miembros, 16.954 B, sha256 `78e9f55769b0cb09…`; copia en `package/` | ✅ |
| 12 | Flujo de supresión | un veredicto bloqueante suprime sin borrar el paquete bueno | `blocks_delivery_zip(acta del ensayo) = False`; con acta `BLOQUEADO` el predicado da `True` y `suppress()` borra solo la segunda cuarentena; el publicado sigue vivo | ✅ |
| 13 | `deliveries/` real | intacto | el directorio no existe antes ni después (0 entradas); el ensayo escribió solo bajo temporal y `evidence/…/FASE-E2E-PRE/` | ✅ |
| 14 | Evidencia congelada del baseline | sin escritura | `git status -- evidence/CURA-COSTURA-TRIBUNAL-2026-10-11` vacío | ✅ |
| 15 | Frescura del dato operativo | techo declarado por el baseline: 90 días desde `fecha_captura` | `fecha_captura: 2026-07-22` → **94 días** medidos al 2026-10-24; el baseline publicó `vence_el: 2026-10-20`. El loader no lo cortó porque `ONBOARDING_FRESHNESS_HOURS` está ausente del entorno | ⚠️ hallazgo con dueño |

## Veredicto del ensayo

**`LISTO_PARA_E2E`** — las cuatro tareas del ensayo pasan sobre artefactos reales del baseline con el código corregido.

Condiciones abiertas para la corrida, con dueño declarado (ninguna es un fallo de este ensayo):

| Condición | Dueño | Qué decide |
|-----------|-------|------------|
| Confirmación del dominio `www.donalfonsohotel.com` vs `hoteldonalfonso.com` | Operador | `preflight.json` de FASE-E2E no debe emitirse con `domain_confirmed: false` |
| El dato operativo tiene 94 días y el baseline publicó un techo de 90 | Operador | re-capturar el onboarding o declarar el techo vencido en el pre-vuelo de E2E; el loader no lo aplica porque la variable de entorno está ausente |

## Instrumento de iteraciones

R2.7/R2.8: `evidence/FASE-D/measure_iterations.py` lee transcripts de otro runtime, así que **no es comparable**. Auto-reporte en unidad `tool_use`: la sesión combinó la verificación de política de subagentes, la cura de los dos prompts, la investigación de los packs de briefing y este ensayo; la unidad publicada es conteo propio de esta sesión, no comparable con las rondas de otras sesiones.

## Lo que este ensayo NO prueba

- No ejercita la extracción ni la inferencia pagada: `MockPromiseExtractor([])` deja `promesas_leidas: 0` y el escáner estructural sigue activo (por eso el mutante da 2).
- No sustituye AC7: la pérdida honesta, las 11 brechas re-medidas y el ZIP real en `deliveries/` se certifican con la corrida.
- No re-certifica los otros tres revisores: sus informes son los del baseline (`revision_*.json`), y `alignment_reviewer` sigue publicando `DEVOLVER-PRUEBAS` con 33 advertencias y 0 críticos.
