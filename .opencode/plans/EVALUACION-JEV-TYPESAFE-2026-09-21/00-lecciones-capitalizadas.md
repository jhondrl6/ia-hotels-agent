# Lecciones capitalizadas — EVALUACION-JEV-TYPESAFE-2026-09-21

Creado el 2026-09-21 durante la revisión de preparación, después de la primera concepción y antes de cualquier implementación. No se presenta como un Paso 0 ejecutado retroactivamente: la auditoría encontró su ausencia (`C1/AUSENTE`) y este ajuste la subsana.

## 1. Consultas ejecutadas

El índice se regeneró antes de consultarlo con `venv/Scripts/python.exe scripts/build_lesson_index.py`. Q1/Q2 se ejecutaron mediante Grep con los parámetros siguientes, sin límite de resultados; son consultas de herramienta, no comandos shell atribuidos a una ejecución que no ocurrió.

| ID | Capa | Consulta literal / parámetros | Resultado |
|---|---|---|---|
| Q1 | Índice completo del corpus | `Grep` con el JSON íntegro de Q1 debajo | Candidatos por pertinencia, proveedor y medición |
| Q2 | Índice y fuentes originales | `Grep` con el JSON íntegro de Q2 debajo, seguido de lectura de definiciones | 11 IDs contrastados |
| Q3 | Memoria del proyecto | `Read` de los tres archivos identificados en Q3 | Dos referencias relevantes, una premisa de acceso refutada |
| Q4 | QMind, corpus de lecciones | `retrieve(notebookId="01a04d98-b7bd-778c-8441-26fdc7e35f45", query="Evaluar proveedor de decisiones tipadas para pertinencia de lecciones: comparación con DeepSeek, preservar usage y modelo efectivo, distinguir fallo o no ejercitado de resultado vacío, pruebas offline y muestra humana sin fuga de evaluación.", maxResults=4)` | Cuatro fragmentos de dos fuentes |
| Q5 | QMind, corpus de lecciones | `retrieve` con la consulta literal completa de Q5 debajo | Cuatro fragmentos de dos fuentes |

**Q1 — Índice completo del corpus, por problema y superficie de medición.**

```json
{"pattern":"pertinen|proveedor|confianza|cost[oe]|medici[oó]n|muestra|denominador|vac[ií]o|ausencia|mutaci[oó]n|reproduc","path":".opencode/LECCIONES-INDEX.md","output_mode":"content","-i":true,"head_limit":0}
```

Recuperó, entre otros, L-D5, L-ENT.9, L-P6.3, L-T4A.5 y DA-C3. No se interpreta ausencia de otros términos como ausencia de lecciones.

**Q2 — Atribución exacta en el índice y lectura de las definiciones originales.**

```json
{"pattern":"\\| `(?:L-(?:R\\.3|R\\.4|D5|T4A\\.5|V2\\.1|P6\\.3|ENT\\.9|SR3|SR4|T2B\\.1)|DA-C3)`","path":".opencode/LECCIONES-INDEX.md","output_mode":"content","head_limit":0}
```

Resultado: 11 filas de IDs, ocho seleccionadas en §2 y tres descartadas en §3. La expresión se reagrupó y re-ejecutó al validar el ajuste: escribir cada prefijo junto a un punto escapado generaba falsas citas parciales en el índice; la agrupación conserva el conjunto de resultados sin inventar IDs. Se leyeron las definiciones originales, no solo los enunciados recortados del índice. La fuente Salento Real estaba en `Historico/`, no en la raíz de contextos; se localizó antes de atribuirla.

**Q3 — Memoria del proyecto.** Lectura de `MEMORY.md`, `reference-qmind-lecciones.md` y `project-edits-de-plan-vencen-el-indice-de-lecciones.md`. Dos entradas de referencia: procedencia de QMind e índice generado. La nota antigua de inaccesibilidad MCP quedó refutada por Q4/Q5 en esta sesión.

**Q4 — QMind, notebook iah-cli-lecciones.**

`retrieve(notebookId="01a04d98-b7bd-778c-8441-26fdc7e35f45", query="Evaluar proveedor de decisiones tipadas para pertinencia de lecciones: comparación con DeepSeek, preservar usage y modelo efectivo, distinguir fallo o no ejercitado de resultado vacío, pruebas offline y muestra humana sin fuga de evaluación.", maxResults=4)`

Resultado: cuatro fragmentos, dos fuentes. Algunos eran plantillas o estados históricos; no prueban el estado actual. L-D5 apareció en un registro de exclusión de write-back; su definición se verificó en disco.

**Q5 — QMind, mismo notebook.**

`retrieve(notebookId="01a04d98-b7bd-778c-8441-26fdc7e35f45", query="Un test puede pasar sin ejecutar la rama que dice certificar L-T4A.5; un proveedor configurado no es un proveedor ejercitado; matriz offline no prueba confianza estadística; medir muestra y denominador antes de activar.", maxResults=4)`

Resultado: cuatro fragmentos, dos fuentes: cierre de TRIBUNAL-OFFLINE y TRIBUNAL-ENFORCEMENT. Corroboran L-T4A.5 y L-P6.3; no añaden una medición del rendimiento de Jev. Q4/Q5 se hicieron mediante MCP `retrieve`, no mediante CLI. No se guardan enlaces de descarga firmados ni se subió contenido.

Snapshot previo a estas ediciones: índice recalculado sobre 405 Markdown, 15 análisis y 37 contextos; 320 IDs definidos y 50 sin definición. Es una medición histórica de entrada, no el tamaño que se espera después de añadir los documentos de preparación. El productor es `scripts/build_lesson_index.py::build`.

## 2. Lecciones capitalizadas

Los enunciados siguientes son síntesis de las definiciones leídas; los nombres de dueño se conservan para la validación de atribución.

| ID | Enunciado | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|---|---|---|---|---|
| L-D5 | Validar el instrumento con resultados conocidos antes de publicar un cero | `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md`, §Lecciones Aprendidas | AC10 exige casos de conteo y coste calculables a mano, incluidos denominadores vacíos, errores y usage ausente | FASE-A y FASE-B |
| DA-C3 | Vacío y ausente son contratos distintos | `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md`, §Decisiones Arquitectónicas | AC2 y AC5 separan respuesta válida negativa, abstención, proveedor ausente y ejecución fallida; un error no produce RECHAZAR | FASE-B y FASE-C |
| L-R.3 | La cobertura del verificador necesita una población explícita | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`, §FASE-RELEASE-4.76.0 | AC4 y AC10 publican recuperación, clasificación, excluidos, fallos y denominadores; un cero no representa a quienes nunca recibieron juicio | FASE-A y FASE-C |
| L-R.4 | Una regla sin verificador debe declararlo | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`, §FASE-RELEASE-4.76.0 | AC11 declara que los controles del piloto aún no existen; la rúbrica y el saneamiento siguen requiriendo revisión humana, aunque pase el checker | Preparación y todas las fases |
| L-T4A.5 | Un test verde puede no alcanzar la rama que pretende certificar | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`, §FASE-T4-A | AC9 prueba el SDK real con transporte falso y acredita que lo invocó; AC6 prueba el guard real con respuestas no vacías | FASE-B y FASE-C |
| L-V2.1 | La aserción debe identificar la causa, no solo la etiqueta del check | `.opencode/plans/Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12/10-analisis-post-implementacion.md`, §Lecciones Aprendidas nuevas | AC6, AC8 y AC9 exigen mutación del símbolo real y aserción causal; un error HTTP distinto no certifica el guard de presupuesto | FASE-B |
| L-P6.3 | Una matriz offline prueba lógica, no confianza estadística | `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/10-analisis-post-implementacion.md`, §Lecciones Aprendidas | AC3 y AC5 no convierten 60–100 pares ni un mock verde en calidad demostrada; conservan MUESTRA-INSUFICIENTE | FASE-A y FASE-C |
| L-ENT.9 | Proveedor configurado no significa proveedor ejercitado | `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md`, §Lecciones nuevas de este plan | AC4 exige DeepSeek efectivo por solicitud, sin fallback a Anthropic; AC12 distingue habilitación declarada de autenticación probada | FASE-B y FASE-C |

## 3. Candidatos evaluados y descartados

| ID | Por qué no se incorpora como requisito de este piloto |
|---|---|
| L-SR3 | La contabilidad de promesa, matriz y gate de servicios queda fuera del alcance. Su fuente es `.opencode/context/Historico/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md`; no se modifica el Tribunal para comparar pertinencia |
| L-SR4 | La confianza de assets hoteleros desde fuentes GBP/web no determina cómo interpretar Noul. No trasladar el umbral de un asset a una decisión semántica; misma fuente histórica que L-SR3 |
| L-T2B.1 | Detectar IMPLEMENTATION_ORDER como stub es un requisito de entregables ZIP, no del corpus plan–lección. Fuente: `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` |

## 4. Cobertura declarada

- `scripts/validate_lesson_capitalization.py` verifica forma, atribución y referencias a AC existentes; **no verifica la pertinencia** ni demuestra que el efecto descrito ya se haya implementado.
- §2 registra decisiones aplicadas al diseño. La implementación y las métricas semánticas permanecen PENDIENTES; se actualiza cada fila cuando su fase aporte evidencia real.
- El corpus congelado del piloto aún no existe. Los 320 IDs de la consulta no son 320 ejemplos aptos, etiquetados o autorizados para exportación.
- QMind fue accesible en estas dos consultas; sus resultados fueron acotados y no constituyen un inventario completo. Las fuentes se contrastaron con archivos locales.
- `scripts/build_lesson_index.py --check` comprueba frescura del índice generado, no saneamiento de datos ni calidad de etiquetas. Regenerar tras terminar las ediciones.
- No se ha ejecutado write-back ni archivado. Crear este documento corrige la omisión de preparación, no autoriza el piloto ni simula un cierre de fase.
