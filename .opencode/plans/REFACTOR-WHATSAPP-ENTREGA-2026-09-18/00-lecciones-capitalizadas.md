# Lecciones capitalizadas — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Creado el 2026-09-18, antes del maestro y los prompts. Preparación documental; ninguna implementación ni corrida ejecutada. Actualizar al cierre de cada fase.

## 1. Consultas ejecutadas

| # | Capa | Consulta literal | Resultado |
|---|---|---|---|
| Q1 | Índice completo | `python scripts/build_lesson_index.py --check` | Índice fresco, 305 IDs antes de crear este plan. |
| Q2 | Índice completo | `Grep(pattern="L-NC6\|L23\|L19\|L-PF6\|L-PF10\|L-T4A.5\|L-VUP-5\|L-R.4\|L-NC10\|L-V.1\|L-SR5\|L-HF1", path=".opencode/LECCIONES-INDEX.md", output_mode="content")` | Se consultó el corpus completo; se contrastaron las definiciones pertinentes en sus análisis, no solo sus resúmenes. |
| Q3 | QMind, notebook iah-cli-lecciones | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "WhatsApp promesa asset sin dato requerido detect_pains caller cableado" --max-results 3 --format agent --non-interactive` | 3 resultados: fugas narrativas, RC1-RC2 y DT-4 histórico. |
| Q4 | QMind, notebook iah-cli-lecciones | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "IMPLEMENTATION_ORDER stub evidencia ZIP VERIFY mutation checks onboarding dominio" --max-results 3 --format agent --non-interactive` | 3 resultados: dos del plan de enforcement y uno del tribunal offline. Advertencia: hay correcciones P6/P6-R posteriores a P4; el código actual decide si sigue existiendo el defecto. |
| Q5 | Memoria del proyecto | `Read("C:/Users/Jhond/.qoder/projects/C--Users-Jhond-Github-iah-cli/memory/project-edits-de-plan-vencen-el-indice-de-lecciones.md")` | Regenerar índice MD+JSON tras escribir el plan; no editarlo manualmente. |
| Q6 | Memoria del proyecto | `Read("C:/Users/Jhond/.qoder/projects/C--Users-Jhond-Github-iah-cli/memory/reference-qmind-lecciones.md")` | Verificar contenido del write-back: un SKIP por título no prueba que se haya publicado el cierre actualizado. |

## 2. Lecciones capitalizadas

| ID | Enunciado | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|---|---|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | `.opencode/plans/Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` | AC1 y AC7 exigen igualdad de pains y descubrimiento de callers, incluyendo detect_pains. | Cableado y verificador AST. |
| L-NC10 | La narrativa estática puede contradecir un ledger correcto. | `.opencode/plans/Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` | AC2 y AC10 cruzan propuesta, identidad de servicio, guía y ledger; no basta quitar una entrada del catálogo. | Promesa y entrega. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | AC1 y AC6 usan entradas producibles y mutaciones del símbolo real; se prohíbe certificar la rama HTML inalcanzable. | Implementación y VERIFY. |
| L-V.1 | Contenido y layout reales son dos ejes distintos del contrato. | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | AC10 lee IMPLEMENTATION_ORDER del ZIP escrito por DeliveryPackager, no un MD fabricado. | Entrega y VERIFY. |
| L-V.4 | VERIFY registra fallos con dueño; no los remedia. | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | AC18 separa SUPERADO, FALLA y NO EJERCITADO; prohíbe reparar o repetir la corrida en VERIFY. | VERIFY. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | AC7 publica cobertura y límites del AST; AC17 limita la cuenta de ejecuciones al runner, no a comandos externos. | Verificador y corrida única. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | `.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | AC9 exige estados separados al leer evidencia; fallo de red no prueba ausencia de canal. | Preflight, análisis y cobertura de lectores (B/C). |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente. | `.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | AC9 cubre vacío, ausente y lectura fallida sin rellenar defaults ni crear pains por el parser. | Lectores y cobertura. |
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | AC10 revalida el writer actual sin reimplementar fixes ya hechos; desactivar el guard debe producir rojo. | Entrega y no-regresión. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | AC14 y AC17 verifican parser, identidad del hotel y argumentos antes de consumir la única corrida. | Onboarding, preflight y E2E. |
| L-VUP-12 | La evidencia se conserva antes de analizar. | `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | AC17 exige snapshot saneado con hashes y exit code antes del análisis; baseline P4 inmutable. | E2E. |
| L-VUP-17 | Los tests locales no certifican integración renderizada. | `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | AC18 cruza los ACs con los artefactos de la única corrida; una rama no ejercitada no se declara superada por ese hotel. | VERIFY. |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO se capitaliza como tarea de este plan |
|---|---|
| L-T4A.1 | No se introduce un protocolo de extracción LLM; modificar runtime_checkable no ataca este defecto. |
| L-T4A.2 | El parsing de cercas Markdown de respuestas LLM no forma parte de los fixes propuestos. |
| L-T4A.4 | No se cambia el matching difuso de promesas; solo se verifica que el nuevo servicio conserve identidad entre consumidores. |
| L-VUP-3 | La blocklist de plataformas no se refactoriza. La identidad exacta del hotel se valida sin introducir matching por substring. |

## 4. Cobertura declarada

Este archivo es verificado por `scripts/validate_lesson_capitalization.py`: forma, consultas, al menos tres descartes, AC existente, IDs y dueños reales, y al menos dos fuentes. **No verifica la pertinencia**, ni que los prompts hayan aplicado las lecciones. El orquestador debe revisar esto por separado.

QMind fue accesible por CLI en ambas consultas; no se publicó contenido nuevo durante la preparación. Sus snapshots no sustituyen el código vivo. Las dos consultas son recuperación, no autorización para subir datos del hotel.

`build_lesson_index.py --check` cubre frescura del índice, no calidad del diseño. El par MD+JSON se regenera después de los cambios del plan. Las futuras fases documentarán la aplicación real de cada fila y el write-back autorizado antes del archivado.
