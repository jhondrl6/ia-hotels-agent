# CURA-COSTURA-TRIBUNAL-2026-10-11

> Cura de la costura de juicio semántico viva en `v4complete` (Tribunal: `LLMPromiseExtractor` → Bot 2/Bot 4 → Juez), según el contexto `CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` (versionado en `a8c356b`). Cierra con un run único de `v4complete` para Hotel Don Alfonso y su análisis post-implementación.

## Estado

| Fase | Estado |
|------|--------|
| Preparación (esta sesión) | ✅ 2026-10-11 |
| Preparación-2 (auditoría aplicada) | ✅ 2026-10-11 — 6 fallos que rompían la ejecución + 9 de diseño corregidos en los 13 `.md`; sin código, sin pytest, sin commit |
| FASE-A | ⬜ |
| FASE-B | ⬜ |
| FASE-C | ⬜ |
| FASE-E2E (run único Don Alfonso) | ⬜ |
| FASE-VERIFY | ⬜ |
| FASE-RELEASE-4.81.0 | ⬜ |

Detalles vivos: `06-checklist-implementacion.md` y `dependencias-fases.md`.

## Índice

| Archivo | Contenido |
|---------|-----------|
| `00-lecciones-capitalizadas.md` | Paso 0: consultas literales, lecciones §2 (L-T4A.x, L-VERIFY.4, L-VUP-13, S-H13, L-V.2), descartes, cobertura |
| `01-plan-maestro.md` | Objetivo, ACs AC1..18 con su artefacto de lectura (§1), causas raíz → fases (§2), fases con complejidad y presupuesto (§3), decisiones y restricciones (§4: DEC-A1..A4), deudas con dueño (§5, con `S-CST-1`) |
| `05-prompt-inicio-sesion-fase-A.md` | Contrato 4 estados + cache versionada + recibo (ALTA, directo) |
| `05-prompt-inicio-sesion-fase-B.md` | Bot 2/Bot 4 + N5 + N7 + wrapper fuera, con **orden interno obligatorio T3→T2→T1→T4** y AC17/AC18 (ALTA, directo) |
| `05-prompt-inicio-sesion-fase-C.md` | Precedencia tier + P6.2 + N8 en los cuatro sitios del motor (MEDIA-ALTA, directo) |
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
