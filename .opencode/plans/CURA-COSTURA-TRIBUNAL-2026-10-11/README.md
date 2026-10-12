# CURA-COSTURA-TRIBUNAL-2026-10-11

> Cura de la costura de juicio semántico viva en `v4complete` (Tribunal: `LLMPromiseExtractor` → Bot 2/Bot 4 → Juez), según el contexto `CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` (versionado en `a8c356b`). Cierra con un run único de `v4complete` para Hotel Don Alfonso y su análisis post-implementación.

## Estado

| Fase | Estado |
|------|--------|
| Preparación (esta sesión) | ✅ 2026-10-11 |
| Preparación-2 (auditoría aplicada) | ✅ 2026-10-11 — 6 fallos que rompían la ejecución + 9 de diseño corregidos en los 13 `.md`; sin código ni pytest. El commit no era parte de la tanda de edición: llegó después, el mismo 2026-10-11, en `359ac57` (empujado a `origin/master` tras una L3 con 0 hallazgos) |
| FASE-A | ✅ 2026-10-11 — contrato de cuatro estados (`extract_checked`), cache versionada sin envenenamiento con mutation check, recibo por extracción y frontera de dato en el prompt. +46 funciones de test (delta R2.3 verificado restando), quick 13/13. **Sin commit: el corte de esta sesión es «listo para revisión»** |
| FASE-B | ✅ 2026-10-11 — Bot 2 y Bot 4 consumen `extract_checked` y publican el estado de su insumo; el acta propaga el no-OK a `ReviewerStatus.INPUT_NOT_EVALUABLE` (AC17) con su etiqueta; sobre-presentación sobre texto completo (AC9/N5); patrón de CRITICAL medido y curado (AC10/N7) con tres mutantes en par rojo/verde; wrapper DEC-A1 eliminado (AC15, **cierra AC1**). Delta R2.3 **+27**, quick 13/13. **Sin commit: el corte de esta sesión es «listo para revisión»** |
| FASE-C | ✅ 2026-10-12 — `evidence_tier.py` es el símbolo único de precedencia (escenarios → MANIFEST → fallback `"C"` con `declarado=False`) y lo consumen Juez y Bot 4; Bot 4 **deja de silenciarse** bajo tier no declarado y publica `OVER_PRESENTATION_NO_EVALUABLE` (AC11/N6). El acta generada ya no niega a Bot 2 y la decisión de cláusula queda diferida con dueño (AC12). Los cuatro sitios de captura de `contradiction_engine` publican tri-estado en lugar de `print` (AC13/N8); el cableado motor→gate sigue fuera (`S-CST-1`). Delta R2.3 **+29**, quick 13/13. **Sin commit: el corte de esta sesión es «listo para revisión»** |
| FASE-C2 | ✅ **2026-10-12** — AC19 ejecutada: `verified_critical` y `verified_block` dejan de exigir `status.is_ok`, así que el CRITICAL del escaneo determinista bloquea el ZIP también bajo `INPUT_NOT_EVALUABLE`/`FALLIDO`, y `derive_corrective_actions` nombra el hallazgo en vez de la acción genérica. Fila 3 intacta (alternativa rechazada, DEC-C2). **+12** funciones (5309→5321, cero re-anclajes medidos), tribunal 331 passed / 9 skipped, quick 13/13, dos mutantes con par rojo/verde y acta generada en `evidence/…/FASE-C2/`. Métricas en `09` §D; detalle en `10-analisis` fila 17 de la matriz y su Resumen |
| FASE-E2E (run único Don Alfonso) | ⬜ |
| FASE-VERIFY | ⬜ |
| FASE-RELEASE-4.81.0 | ⬜ |

**Sello de publicación (2026-10-12)**: FASE-A `5ed960a` (+`af508cd`) y FASE-B `bf5ab2e` (+`4df81d3`) están **empujadas** con paridad `0 0`; **FASE-C quedó commiteada en `079f475`**, tanda que además registra FASE-C2 con su AC19. Las celdas de arriba que dicen «sin commit» describen el **corte declarado al cerrar la fase** (los cinco cortes del executor), no el estado actual del árbol: eso lo miden `git log` y `docs/contributing/REGISTRY.md`.

Detalles vivos: `06-checklist-implementacion.md` y `dependencias-fases.md`.

## Índice

| Archivo | Contenido |
|---------|-----------|
| `00-lecciones-capitalizadas.md` | Paso 0: consultas literales, lecciones §2 (L-T4A.x, L-VERIFY.4, L-VUP-13, S-H13, L-V.2), descartes, cobertura |
| `01-plan-maestro.md` | Objetivo, ACs AC1..18 con su artefacto de lectura (§1), causas raíz → fases (§2), fases con complejidad y presupuesto (§3), decisiones y restricciones (§4: DEC-A1..A4), deudas con dueño (§5, con `S-CST-1`) |
| `05-prompt-inicio-sesion-fase-A.md` | Contrato 4 estados + cache versionada + recibo (ALTA, directo) |
| `05-prompt-inicio-sesion-fase-B.md` | Bot 2/Bot 4 + N5 + N7 + wrapper fuera, con **orden interno obligatorio T3→T2→T1→T4** y AC17/AC18 (ALTA, directo) |
| `05-prompt-inicio-sesion-fase-C.md` | Precedencia tier + P6.2 + N8 en los cuatro sitios del motor (MEDIA-ALTA, directo) |
| `05-prompt-inicio-sesion-fase-C2.md` | AC19: enforcement del CRITICAL verificado sin exigir `is_ok` + acción correctiva nombrada; **sin subagente** (MEDIA, directo) |
| `05-prompt-inicio-sesion-fase-E2E.md` | Run único v4complete Don Alfonso vía subagente, con onboarding por YAML derivado (MEDIA, delegate_task) |
| `05-prompt-inicio-sesion-fase-VERIFY.md` | Certificación AC1..18 contra output E2E (MEDIA, directo) |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Release 4.81.0 + write-back + archivado (BAJA, delegable) |
| `06-checklist-implementacion.md` | Estados por fase y dependencias |
| `09-documentacion-post-proyecto.md` | Fuente canónica de métricas por fase (§D) |
| `10-analisis-post-implementacion.md` | Matriz de verificación, lecciones, seguimientos, decisiones |
| `dependencias-fases.md` | Diagrama, conflictos de archivos, decisiones pre-fase, riesgos |

## Reglas de oro del plan

1. Una fase por sesión (R1). El commit no es parte del cierre: requiere autorización del operador y siempre pathspec (trabajo ajeno staged en el índice).
2. El run de v4complete es ÚNICO y vive en FASE-E2E vía subagente (`notify_on_complete`).
3. Cifras: se registran una vez (`09` §D, informes, tests) y se referencian.
4. AC de detección sin par rojo/verde = ⚠️, nunca ✅ (R2.8). Delta de tests se verifica restando (R2.3).
5. Citas por símbolo, nunca `archivo:línea` (R2.2).
