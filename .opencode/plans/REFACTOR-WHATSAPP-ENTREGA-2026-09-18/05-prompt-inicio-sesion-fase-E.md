# FASE-E — Entrega real y revisión sin filtración

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-D completa; verificar cierre real de A–D antes de editar.
**Complejidad técnica:** ALTA: límite interno/cliente, orden temporal entre borrado y Tribunal, y dos ejes del contrato (contenido y layout).
**Scope R3:** 4 tareas, 0 comandos largos externos. Una sesión exclusivamente para E, sin v4complete real.

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §1 (filas F-P4.1 y F-P4.2), §2 y §4; `04-contrato-ejecucion.md`; `00-lecciones-capitalizadas.md`; `06-checklist-implementacion.md`; `dependencias-fases.md` y el workflow canónico.
Revalida símbolos en disco antes de editar: `DeliveryPackager.write`/`publish`/`suppress`, `_collect_files`, `_build_manifest_in_memory`, `_resolve_manifest_self_size`, `AssetResponsibilityContract.generate_delivery_template`, `run_v4_complete_mode` (borrado de diagnóstico/propuesta), `artifact_paths.resolve_latest` y los cuatro revisores del Tribunal.
**Punto de partida corregido:** F-P4.1 ya recibió corrección en P6/P6-R. E **revalida con mutación** el writer vigente e integra el asset nuevo de B; no reconstruye el writer ni afirma que hoy siempre entrega un stub.
Evidencia propia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/`. No modificar `evidence/FASE-P4/` ni históricos archivados.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | AC10 revalida el writer actual con mutantes; no se reimplementa un fix ya hecho. |
| L-V.1 | Contenido y layout reales son dos ejes distintos del contrato. | AC10 lee IMPLEMENTATION_ORDER desde el ZIP escrito por `DeliveryPackager`, no un MD fabricado en el test. |
| L-NC10 | La narrativa estática puede contradecir un ledger correcto. | AC11 cruza manifiesto interno, ledger y guía; un snapshot correcto no legitima una guía que prometa lo ausente. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | AC9/AC11 separan documento nunca generado, retenido por gate y error de lectura. |

## Tareas

1. **PRE y revalidación del writer.** Captura baseline focalizado antes de editar código o tests. Ejecuta la regresión P6-R pertinente y confirma qué garantiza hoy `asset_zip_paths`; documenta el estado real de F-P4.1 con evidencia, no con la cita del contexto. Localiza el punto exacto donde `run_v4_complete_mode` borra diagnóstico/propuesta y qué consumen después `resolve_latest` y los revisores.
2. **Snapshot interno revisable.** Conserva, antes de cualquier borrado, una copia interna **no exportable** de los documentos que el Tribunal necesita leer, con run_id explícito, ruta original, hash y momento. Los revisores y `artifact_paths` reciben rutas explícitas del mismo run_id; no se elige el archivo más reciente entre hoteles. Registra retención deliberada como `disposition=retained_by_gate` y mantiene AUSENTE lo nunca generado. El ZIP público no incluye el snapshot ni documentos internos retenidos; `write/publish/suppress` y `TribunalJudge._compute_verdict` quedan intactos.
3. **POST, ZIP real y mutaciones.** AC10: leer del ZIP real IMPLEMENTATION_ORDER con tareas no vacías, rutas ASSETS existentes, setup/guía descritos conforme a B y manifiesto coherente (incluido el nuevo asset). AC11: `review_input_manifest.json.documents` con run_id, fuente original, hash, ruta interna, `read_status` y disposition; los revisores leen ese contenido. AC12: pares permitir/bloquear del flujo real sobre `acta_revision.json.enforcement` y `package_evidence`. Mutantes: restablecer el borrado sin snapshot, perder la ruta explícita, desconectar `asset_zip_paths` o exportar el snapshot deben fallar por su aserción correspondiente.
4. **Cierre incremental.** Ejecuta el contrato de cierre completo. Actualiza AC9–AC12, PRE/POST, delta y mutaciones en evidencia de E, checklist, dependencias, 00/09/10. No certificar por tamaño de archivo ni por presencia de un string en código.

## Reglas de evidencia y límites

- El snapshot vive fuera del árbol recursivo exportado; comprobarlo con el writer real, no con una inspección visual del código.
- Una ausencia inducida por retención no se presenta como hallazgo independiente nuevo; las ausencias originales y los errores de lectura sí son hallazgos.
- Lectores nuevos o modificados publican READ_OK (incluye vacío válido), ABSENT y READ_ERROR con causa; al menos un test sobre baseline real por lector, con skip visible si falta y AC sin certificar.
- No usar el borrado como excusa para relajar enforcement, ni el snapshot para publicar material interno.
- Ninguna prueba ejecuta `main.py v4complete`; la integración real ocurre solo en E2E.

## Tests obligatorios

Suites descubiertas bajo `tests/delivery/`, `tests/quality_gates/tribunal/` y tests de integración de `main.py`, con `./venv/Scripts/python.exe`. Preferir extender archivos existentes (incluida la regresión P6-R) antes de crear suites paralelas.
`tests_baseline_pre.txt` / `tests_baseline_post.txt`: misma selección y entorno, exit code y passed/failed/skipped/xfailed/xpassed; delta explicado por adiciones y parametrizaciones de ESTA fase.
`mutation_report.json` por AC: símbolo real mutado, test, causa del rojo, exit codes y restauración; el rojo debe provenir del guard, no de syntax/import.

## Delegación viable

DIRECTA para el diseño del límite interno/cliente y el orden temporal. `delegate_task` (o `Agent` si es el equivalente disponible) solo para inventarios read-only independientes: consumidores de `artifact_paths`, lectores del Tribunal, rutas donde se escriben/borran documentos. Brief con objetivo, allowlist, prohibiciones (sin secretos, sin imports, sin red, sin fases futuras), contrato decidido y salida esperada. El principal verifica diff y artefactos; si el delegado no accede al venv, no reinstalar dependencias: el principal ejecuta imports y tests.

## Post-ejecución

Actualizar estado de este prompt, checklist, dependencias, índice del plan, 00/09/10 con las observaciones medidas que realmente existan — **sin cuota de lecciones nuevas**: la fase puede cerrar declarando «sin lecciones nuevas» (proceso común del bloque B de la orden de calidad); subsección E en CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`. Sustituir variables por datos medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E --desc "REFACTOR-WHATSAPP-ENTREGA: entrega real revalidada y revisión con snapshot interno" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico dentro del alcance autorizado; rojos ajenos o permisos faltantes implican checkpoint, no rebautizar el PRE histórico 9/10 como verde. DOMAIN_PRIMER: **regenerar** con su writer al cerrar esta fase de implementación, según la resolución de A; **verificar** con `doctor.py --context` es la otra operación y pertenece a RELEASE — dos operaciones distintas, ninguna sustituye a la otra. Write-back durable solo si está **autorizado con permiso propio** y saneado; sin autorización, checkpoint explícito. No commit, push ni release implícitos.

## Presupuesto y checklist

Referencia **60 tool_use hasta el corte que la sesión tenga autorizado**; instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`, duración de pared aparte. Con el commit de código autorizado el corte es «hasta el commit»; sin él es «hasta listo para revisión», y se declara cuál se usó. Sin transcript o con acceso denegado: **FUERA DE SERVICIO (R2.1)**, retirar la comparación y emitir auto-reporte con su unidad; nunca cumplimiento estimado. **La ausencia de commit no deja ningún corte «no consumado»**: los cinco cortes se declaran y verifican sin commit, y el commit es una acción posterior, separada y opcional con autorización explícita.

- [ ] D cerrada; PRE tomado antes de editar y POST conciliado en el mismo entorno.
- [ ] Estado real de F-P4.1 documentado con mutación, no con la cita del contexto.
- [ ] Snapshot interno no exportable, con run_id/hash y rutas explícitas a revisores.
- [ ] AC9/AC10/AC11/AC12 medidos en disco desde writer, ZIP y acta reales.
- [ ] O1, Juez, `write/publish/suppress` y umbrales intactos; sin evidencia histórica alterada.
- [ ] Cierre incremental completo y R2 medido o retirado; F será otra sesión.
