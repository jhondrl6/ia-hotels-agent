# FASE-F — Sanitización de salidas y acreditación operativa

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-E completa; verificar cierre de la cadena anterior.
**Complejidad técnica:** MEDIA-ALTA: límites de salida, prevención parcial existente y revocación externa no inferible del código.
**Scope R3:** 4 tareas, 0 comandos largos externos. Una sesión exclusivamente para F.

## Contexto e inicio

Este documento prepara una ejecución futura; requiere mandato propio. Lee `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`, checklist y workflow canónico.
Revalida el cierre de E, símbolos vivos, allowlist y estado del trabajo; preserva cambios ajenos. No ejecutar pipeline, auditorías externas ni fases siguientes.
El diseño está decidido: calificar la sanitización de `LLMMentionChecker` ya existente y cerrar brechas concretas de las salidas nuevas, no reconstruir todos los providers.
Trabaja sobre `_sanitize_text`, `_sanitize_error`, `_query_gemini`, `ValidationRunner._check_no_secrets` y consumidores/writers pertinentes descubiertos; justificar cada cambio mínimo.
Evidencia futura propia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-F/`. No modificar evidencia histórica ni examinar secretos reales.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | AC13 califica los sanitizadores existentes antes de proponer reemplazos. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | Las pruebas recorren errores y writers reales, no solo helpers aislados. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Un test no acredita revocación: separar prevención local de evidencia del operador. |

## Tareas

1. **PRE e inventario de salidas.** Medir suites focalizadas antes de editar código o tests. Inventariar consola, logs, excepciones, reportes y snapshots nuevos de D/E, distinguiendo protección existente, brecha demostrada y consumidor futuro de H. Identificar qué writers pueden persistir texto de proveedores; no abrir logs crudos históricos para buscar una key.
2. **Calificación y cierre mínimo.** Reutilizar la sanitización existente y corregir únicamente rutas descubiertas que permitan persistencia o impresión sin redacción. Definir el contrato que consumirá H, sin construir aquí su runner. Solicitar acreditación operativa de revocación mediante metadatos no secretos; registrar estado real sin rotar credenciales ni contactar servicios.
3. **POST y mutaciones offline.** Repetir selección y entorno PRE; añadir cobertura de AC13 con datos sintéticos en errores de API simulados, consola y archivos reales del writer. Desactivar el sanitizador o desconectar una llamada en aislamiento debe romper las aserciones de no propagación. Emitir informes saneados, separando pruebas locales de revocación externa.
4. **Cierre incremental.** Guardar evidencia y delta; actualizar documentación y estado conforme al contrato, ejecutar validaciones autorizadas y medir R2. Si falta acreditación operativa o falla una salida, dejar F INCOMPLETA con dueño y pendiente; no habilitar E2E ni iniciar G.

## Contrato de seguridad y evidencia

- No leer `.env`, valores del entorno con credenciales, caches ni archivos con keys reales; no imprimir URLs autenticadas, cabeceras o mensajes crudos.
- Los fixtures usan marcadores inequívocamente sintéticos, nunca una key anterior, vigente o parcialmente recuperada.
- La redacción ocurre antes de consola y disco, incluyendo mensajes de excepción, stdout/stderr de pruebas y nuevas copias de evidencia; sanear después no cumple AC13.
- Comprobar `_query_gemini` con transporte sustituido y excepciones sintéticas: la prueba no accede a red ni requiere credenciales reales.
- No reimplementar indiscriminadamente providers ni cambiar modelos, autenticación, configuración central o política de reintentos.
- `sanitization_report.json` registra ruta/canal, mecanismo, casos, resultado y límites; no contiene valores capturados ni fragmentos de secretos.
- `credential_status.json` registra estado, fecha, responsable y referencia no secreta de la comprobación del operador; no inventar campos ya ratificados en A.
- Solo evidencia operativa explícita permite acreditar revocación. Una key nueva, una llamada fallida o un test verde no demuestran que la anterior fue revocada.
- Sin evidencia suficiente: estado PENDIENTE, responsable y acción requerida; no presentar AC13 como íntegramente superado ni efectuar rotación remota.
- No copiar material del hotel o secretos a QMind ni alterar `evidence/FASE-P4/`; la prevención futura no borra una exposición histórica.

## Tests obligatorios

Descubrir suites existentes de `LLMMentionChecker`, validaciones de secretos y writers afectados; preferir extender sus archivos. Usar `./venv/Scripts/python.exe` tras comprobar el entorno.
PRE/POST: `tests_baseline_pre.txt` y `tests_baseline_post.txt`, misma selección y entorno, exit code y passed/failed/skipped/xfailed/xpassed; explicar adiciones y parametrizaciones.
Casos mínimos: texto inocuo preservado, marcador sintético en URL/error redactado, excepción saneada y ausencia del marcador tanto en consola como en archivo persistido.
Leer el reporte emitido por el writer real; comprobar que el propio informe de sanitización no vuelve a filtrar el material de prueba.
`mutation_report.json`: guard real, test, causa del rojo, exit codes y restauración; el fallo debe ser por fuga detectada, no por syntax/import ni una aserción adulterada.
Para cualquier lector nuevo: READ_OK con vacío válido, ABSENT y READ_ERROR diferenciados; baseline real sin datos sensibles o skip explícito y AC no certificado.
Conservar separación entre AC13 verificado offline en F y su integración con captura/snapshot del runner, que se prueba en H. Ninguna v4complete real.
No bajar umbrales, apagar el chequeo de secretos ni ocultar fallos PRE; el resultado histórico de quick no sustituye esta medición.

## Delegación viable

`delegate_task` solo para inventarios read-only independientes de rutas y símbolos, sin secretos; nunca para revocar, decidir arquitectura o modificar writers compartidos.
Brief obligatorio: objetivo, allowlist de código/tests, prohibidos `.env`/logs crudos/evidencia sensible, contrato decidido, salida esperada y criterios; prohibir fases futuras.
Si está disponible y permitido, `Agent` es equivalente de `delegate_task`; no inventar herramientas ni parámetros. Si no, trabajo directo.
El principal revisa el inventario, decide los cambios mínimos y verifica diff, tests y artefactos; no acepta una afirmación delegada como acreditación de revocación.

## Post-ejecución

Actualizar estado de este prompt, `06-checklist-implementacion.md`, `dependencias-fases.md` e índice del plan con resultados reales, sin marcar completos requisitos pendientes.
Actualizar `00-lecciones-capitalizadas.md`, `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`: AC13, delta, límites y al menos tres observaciones medidas.
Añadir subsección F a CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`; no cambiar VERSION ni anticipar release.
Sustituir variables por archivos y tests realmente medidos antes de ejecutar el registro propio, sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-F --desc "REFACTOR-WHATSAPP-ENTREGA: sanitización calificada y estado operativo de credencial" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico; si hay rojos fuera de alcance, checkpoint INCOMPLETA, sin modificar baselines ni permisos.
DOMAIN_PRIMER solo mediante writer y según resolución documentada en A; no editar manualmente ni resolver la divergencia cambiando contexto global.
Write-back durable solo con autorización y contenido saneado; ausencia de permiso/acceso implica checkpoint del cierre. SKIP por título no prueba frescura.
No commit, push, tag, rotación ni cambios centrales sin autorización expresa; el registro documental no declara revocación que el operador no haya acreditado.

## Presupuesto y corte

Referencia: **60 tool_use hasta el commit de código**. Instrumento: `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; registrar duración de pared aparte.
Si transcript/instrumento no es accesible o la medición es denegada: **FUERA DE SERVICIO (R2.1)** desde ese momento; retirar comparación con 60, no estimar cumplimiento ni evadir permisos.
Auto-reporte separado con su unidad; si hay medición válida, recalibrar según R2.1. Sin commit autorizado, registrar checkpoint, no fingir el corte de código.

## Checklist de completitud

- [ ] E cerrada; PRE tomado antes de cambios y POST conciliado en el mismo entorno.
- [ ] Sanitización existente calificada; solo brechas concretas modificadas, sin reconstrucción general de providers.
- [ ] AC13 cubre consola, archivos y nuevas salidas; mutantes fallan por fuga sintética real.
- [ ] Informes sin secretos; revocación acreditada por operador o F explícitamente INCOMPLETA/PENDIENTE.
- [ ] Evidencia propia, al menos tres observaciones y cierre incremental sin GAP ni regresiones ocultas.
- [ ] R2 medido o retirado explícitamente; ninguna ejecución externa ni siguiente fase iniciada.
