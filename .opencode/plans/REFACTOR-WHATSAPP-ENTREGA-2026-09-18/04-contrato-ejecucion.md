# Contrato de ejecución — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas pertinentes de `00-lecciones-capitalizadas.md`. Este archivo no reemplaza `.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

## Límites y precedencias

- Esta sesión solo prepara documentos. Cada fase posterior requiere su propia sesión y mandato de ejecución; R1 prohíbe encadenarlas.
- Fases intermedias: no cambiar VERSION.yaml, ROADMAP.md, workflow, hooks, permisos ni umbrales. No ejecutar v4complete excepto en E2E. No publicar, desplegar ni enviar material al hotel.
- La copia canónica del workflow está en el repositorio `iah-cli`, no en la ruta `iahcli` recibida inicialmente, que no existe.
- El template se adapta al executor vigente: TOTAL PASS dinámico, referencias a símbolos y delta PRE/POST. No copiar sus ejemplos obsoletos de conteos fijos ni citas de línea.
- Configuración central, rotación remota, commit, push, tag y subida a QMind requieren autorización expresa para esa acción. El plan describe pasos futuros; no los autoriza ahora. Un permiso negado no se evade.
- Si hay autorización explícita de commit: revisar diff y staged, stagear archivos concretos, commit nuevo sin saltar hooks. Sin ella, dejar checkpoint y pedirla; no declarar el corte de R2 consumado.
- No tocar `evidence/FASE-P4/` ni históricos archivados. Evidencia nueva exclusivamente bajo `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-<ID>/`.
- No leer ni imprimir valores de secretos. Los fixtures usan marcadores sintéticos. Nuevas salidas se sanean antes de disco/consola; no subir datos reales por defecto.

## Inicio de cada fase

1. Leer su prompt y estado anterior real; comprobar git status y símbolos, no heredar números de línea del contexto.
2. Verificar prerrequisitos y allowlist. Cambios ajenos se preservan; no se mezclan con el trabajo de fase.
3. Declarar hasta cuatro tareas, incluyendo validación y documentación incremental. E2E tiene tres tareas y un solo comando largo externo. No sumar otra auditoría completa o scraping independiente.
4. Tomar PRE antes de editar código o tests. Esperar terminación real del proceso; una notificación o un log parcial no constituyen resultado final.

## R2 — presupuesto e instrumento

Presupuesto de referencia por sesión: **60 tool_use hasta el commit de código**, sujeto a medición con `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`. La duración de pared se registra aparte. Los prompts no estiman cumplimiento.

Si el transcript no está disponible o su acceso es denegado, declarar desde ese momento **métrica FUERA DE SERVICIO (R2.1)**, registrar el auto-reporte con su unidad y no compararlo ni sumarlo al instrumento. No intentar evadir la denegación. Si se mide, recalibrar el presupuesto posterior con la distribución observada conforme a R2.1; un exceso produce checkpoint, no varias fases en una sesión. En fases sin código declarar el corte documental separado, nunca fingir un commit de código.

## Tests y evidencia

- Python local: `./venv/Scripts/python.exe`; comprobar existencia y entorno antes de usarlo. No reinstalar dependencias para hacer funcionar un subagente.
- PRE/POST de la misma selección pytest y entorno en `tests_baseline_pre.txt` / `tests_baseline_post.txt`; registrar exit code y sumas de passed, failed, skipped, xfailed (y xpassed si aparece). Delta de casos explicado por adiciones, bajas y parametrizaciones de ESTA fase; funciones canónicas se contabilizan aparte.
- No agregar exclusiones o cambiar expectativas para ocultar regresiones. Fallos previos requieren par medido, no la cifra histórica de AGENTS.md.
- Cada AC detector/bloqueante exige verde y rojo al mutar el símbolo real; hacer mutaciones en proceso aislado/copia temporal, sin alterar el worktree vivo durante PRE. Registrar guard, test, motivo del fallo, exit codes y restauración. No mutar la aserción del test.
- AC3 conserva su expectativa negativa: el test está verde cuando el producto bloquea el botón inseguro. Su mutante debilitado debe romper el test, no convertirse en la nueva expectativa.
- Lectores nuevos: vacío válido, artefacto ausente y lector fallido con tests separados y estados visibles. Al menos un test sobre baseline real para cada lector; si falta, skip explícito y AC sin certificar, no retorno silencioso.
- Leer JSON/MD desde el writer real y el ZIP cuando corresponda. No equiparar presencia de un string en código con evidencia de salida.

## delegate_task

Usar `delegate_task` únicamente donde el prompt lo permita: búsqueda independiente acotada, tracks sin archivos compartidos, comandos externos y documentación. Si el cliente ofrece `Agent` en lugar de `delegate_task`, usar `Agent` como equivalente disponible; no inventar parámetros de timeout ni herramientas inexistentes. Para procesos largos usar notificación de término (`run_in_background` en el cliente actual).

Brief obligatorio: objetivo, archivos permitidos/prohibidos, lectura o escritura, contrato ya decidido, salida esperada, criterios y prohibición de ejecutar fases futuras. El principal conserva decisiones de arquitectura y verifica diff/artefactos al integrar. En entorno WSL con venv Windows inaccesible al delegado, el principal ejecuta imports y tests. VERIFY no se delega.

## Cierre incremental obligatorio de cada fase

Esta sección forma parte de T4 (T3 en E2E). No se difiere a RELEASE.

1. Guardar evidencia saneada y actualizar el estado real de su prompt, `06-checklist-implementacion.md`, `dependencias-fases.md` y el índice del plan. Marcar INCOMPLETA si falta un requisito.
2. Actualizar `09-documentacion-post-proyecto.md` (A/B/D/E), `10-analisis-post-implementacion.md` (métricas, ACs, lecciones, seguimientos) y `00-lecciones-capitalizadas.md` (aplicación efectiva). Conservar al menos tres observaciones medidas por fase, sin fabricar lecciones.
3. Añadir subsección de esa fase en CHANGELOG.md bajo versión vigente y nota en docs/GUIA_TECNICA.md; no anticipar nueva versión. Ejecutar el comando `log_phase_completion.py` incluido en el prompt, con archivos y tests realmente medidos. No usar el flag de release en fases intermedias. Confirmar REGISTRY y ausencia de GAP.
4. Regenerar DOMAIN_PRIMER solo con su writer y según el mandato vigente del repositorio; no editar a mano. El contexto global lo reserva a RELEASE mientras el executor/CONTRIBUTING indican cada implementación: resolver explícitamente esa divergencia en A antes de aplicarla, no cambiar ambos documentos para silenciarla. En RELEASE ejecutar también doctor context/status.
5. Para write-back durable autorizado: `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload REFACTOR-WHATSAPP-ENTREGA-2026-09-18`. Revisar lo que sube: no material del hotel ni secretos. SKIP por título no prueba frescura; si cambió el aporte, verificar snapshot y acordar título nuevo antes de subir. Si no hay autorización/acceso, checkpoint del cierre y motivo, no simular éxito.
6. Regenerar `./venv/Scripts/python.exe scripts/build_lesson_index.py`, comprobar `--check` y ejecutar `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` más `scripts/validate_document_integration.py`. Resolver los rojos dentro del alcance o mantener fase incompleta. No modificar baselines de validadores para absorber errores nuevos.
7. Medir R2 al corte autorizado, revisar git diff y finalizar la sesión. No iniciar la siguiente fase. Si la fase no acabó, guardar checkpoint con lo pendiente y sin volver a ejecutar lo ya completado.

## Corrida única y límites de certificación

Solo E2E puede iniciar `main.py v4complete`. El contador se consume al crear el proceso, incluso si falla. Un timeout del delegado no autoriza lanzar otro proceso; verificar PID y checkpoint. No usar reintentos de proceso, loops ni una segunda corrida con flags distintos. Las llamadas internas normales del pipeline no equivalen a una segunda invocación CLI.

VERIFY y RELEASE no ejecutan v4complete. Si la corrida falla por red, credenciales, datos insuficientes o un defecto nuevo, conservar el resultado, registrar causa y dueño, y pedir una modificación de alcance en otra sesión. Una sola muestra no certifica todos los hoteles ni todas las ramas; declarar por separado el régimen offline y lo realmente ejercitado.
