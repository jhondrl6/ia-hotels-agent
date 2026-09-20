# Dependencias de fases

Fuentes de contrato: [maestro](01-plan-maestro.md), [ejecución](04-contrato-ejecucion.md) y [lecciones](00-lecciones-capitalizadas.md). Diseño congelado; ninguna fase ejecutada. **Contador v4complete: 0/1. Siguiente sesión: A.**

**Revisión 2 (2026-09-19):** doce sesiones. Se añade **FASE-0** (AC20) y **G adelanta a segunda posición** porque su verificador es el guard de las ediciones de B–F. Cadena: `A → G → 0 → B → C → D → E → F → H → E2E → VERIFY → RELEASE`.

## DAG secuencial estricto

```text
[A] -> [G] -> [0] -> [B] -> [C] -> [D] -> [E] -> [F] -> [H]
                                                        |
                                                        v
                                                     [E2E]
                                                        |
                                                        v
                                                    [VERIFY]
                                                        |
                                                        v
                                                    [RELEASE]
```

Cada nodo corresponde a una sesión nueva. Todas las aristas son obligatorias: no hay tracks de implementación paralelos. La fase siguiente exige cierre real de la anterior; un bloqueo o checkpoint INCOMPLETA mantiene cerrada la arista. Una recuperación requiere sesión y alcance autorizados, no un salto ni un segundo E2E implícito.

## Estados y condiciones de transición

| Fase | Depende de | Condición de salida prevista | Consumo v4complete | Estado |
|---|---|---|---|---|
| A | Mandato de sesión y fuentes del plan | Baseline y contratos ratificados, **incluida FASE-0, la división AC19a/AC19b y el re-anclaje de la meta E2E**; permisos centrales, identidad y vigencia resueltos o checkpoint explícito | 0 | PENDIENTE |
| G | A cerrada | Inventario AST, `wiring_report.json` en el quick y contrato muerto retirado; AC7/AC16. **Su función ahora es proteger las ediciones posteriores: debe cerrar antes de que B toque callers** | 0 | PENDIENTE |
| **0** | G cerrada | `details` del gate fundado, `findings` en el DTO del acta y `package_evidence` en la rama publish; AC20 con el contrafactual medido sobre el acta archivada | 0 | PENDIENTE |
| B | 0 cerrada | Pains y productores de promesas alineados (incluidos `nap_consistente`, generador de propuesta y `PAIN_TO_ASSET`); setup honesto; AC1/AC2/AC19a-consumo y PRE/POST | 0 | PENDIENTE |
| C | B cerrada | Campo/destino seguro, bloqueo del botón inseguro, **dos lectores de WhatsApp unificados o designados** y AC19a aditivo con alcance declarado; AC3/AC5/AC6/AC19 | 0 | PENDIENTE |
| D | C cerrada | Veredicto, causas y fail-fast persistidos; AC4/AC5/AC8/AC9 | 0 | PENDIENTE |
| E | D cerrada | **Resolvedor único para los cuatro revisores** ("no leído" ≠ OK), ZIP real y snapshot interno revisable sin filtración; AC9–AC12 | 0 | PENDIENTE |
| F | E cerrada | **Sumidero único de redacción** y verificador que cubra `output/` y `logs/`; revocación acreditada o pendiente explícito que impide certificar AC13 | 0 | PENDIENTE |
| H | F cerrada | Integración offline; binding/frescura por sucursal del loader, campos no transportados declarados, runner con hijo falso, `attempts=0` y snapshot de `.agent/memory`; AC9, AC12–AC14, AC17 offline | 0 | PENDIENTE |
| E2E | H cerrada y preflight favorable | Un proceso, exit code y evidencia saneada preservados; resultado real registrado aunque bloquee; AC20 verificado en el flujo real | 1 como máximo | PENDIENTE |
| VERIFY | E2E cerrada con evidencia preservada | Lectura directa, matriz por AC **AC1–AC20**, diff estructural, límites y triage; sin remediar ni ejecutar | 0 | PENDIENTE |
| RELEASE | VERIFY cerrada y alcance de cierre explícito | Documentación y validaciones documentales autorizadas; no declarar éxito integral si la meta quedó parcial/FALLA | 0 | PENDIENTE |

AC15 atraviesa implementación/H. Cada fila incluye el cierre incremental exigido por el contrato; no basta cumplir solo el objetivo funcional. VERIFY puede documentar un resultado fallido: eso no lo convierte en certificación favorable ni habilita una reparación dentro de RELEASE.

## Conflictos de archivos y consumidores compartidos

| Superficie compartida | Fases que la consumen o modifican según su allowlist | Riesgo de interferencia | Orden obligatorio |
|---|---|---|---|
| `main.py` | G, 0, B, C, D, E, H | Cableado de pains, precedencia WhatsApp, causas/fail-fast, retención, firmas; en 0 también `package_evidence` de la rama publish y el writer del reporte | G antes de 0 antes de B antes de C antes de D antes de E; nunca ediciones concurrentes. En `run_v4_complete_mode`, los pares `_diag_var`/`_prop_var` + `locals()` resuelven rutas por lookup de `locals()`: frágil, E debe reemplazarlo por variables explícitas |
| Tribunal y gates de entrega: `publication_gates.py`, `tribunal/outcome.py`, `tribunal/diagnosis_reviewer.py`, `judge.py` | **0 es dueña del cambio**; D/E/H consumen su contrato | Un cambio de severidad o de `BLOCKING_VERDICTS` compraría el verde ocultando un bloqueo real | 0 cierra la serialización **sin tocar la regla de decisión**; D y E no vuelven a escribir sobre esas claves |
| Mapper y catálogo: `PainSolutionMapper`, `PAIN_SOLUTION_MAP`, `asset_catalog.py` | B es dueño del cambio; C/E/G consumen su contrato | Una promesa residual o identidad distinta rompe specs, narrativa y entrega | B congela identidades; consumidores posteriores prueban el mismo contrato |
| Productores asociados: `ConditionalGenerator.PAIN_TO_ASSET`, `get_assets_for_pain`, `_solutions_to_asset_specs` | B; C consume/gobierna seguridad del botón | Quitar una constante no elimina promesas en otras rutas | B alinea productores antes del guard de C |
| Coherencia: `CoherenceValidator`, reporte y callers | G, C, D | G verifica firmas/cableado **antes** de que C toque los callers; C elimina boost de presencia; D consume veredicto y causas | G antes de C antes de D; no reintroducir rutas paralelas |
| Lectores de presencia: `site_presence_checker.py`, `site_presence_adapter.py` y los 8 consumidores del reporte canónico | C (19a, aditivo); B consume el estado; **la migración tri-estado ya no está en ninguna fase: es AC19b diferido** | Cambiar la forma canónica rompe 4 asserts de igualdad exacta y exige redefinir `site_verified`/`PRODUCTION_PRESENT_STATUSES` en 8 sitios | C solo agrega claves; cualquier consumidor que necesite el tri-estado espera a AC19b con su propia sesión |
| Delivery y revisores: writer, manifiesto interno, rutas de artefactos | E; H integra y prueba | Snapshot exportado por accidente o lectura del archivo equivocado | E define el límite interno/cliente; H no rehace enforcement |
| Sanitización y captura de salidas | F; H integra runner | Persistencia previa a redacción o fuga en stdout/stderr | F antes de H; solo secretos sintéticos en pruebas |
| Tests de integración, onboarding derivado y runner del plan | H | Gastar el intento desde un test o inventar flags de producción | H trabaja en tests/runner y preparación aislada: sin nuevos flags CLI ni nueva edición de `main.py` |
| Índice, checklist, dependencias y cierre documental | Todas, por turno | Estados inconsistentes o cierres anticipados | Un único cierre de fase a la vez; respetar permisos de cada sesión |

La tabla no amplía allowlists. Si un cambio exige otra superficie, detener y resolver alcance. No hay edición concurrente de ningún archivo compartido. Los inventarios read-only permitidos no autorizan ejecución de fases en paralelo ni escrituras por otro actor sobre esos archivos.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Bloqueantes y decisiones pendientes reales

| Tema | Hecho de partida | Dueño / fase | Condición para resolverlo sin falsear evidencia |
|---|---|---|---|
| **Nueva (revisión 2): supresión determinista del ZIP en la ruta viva** | Medido sobre `output/TAREA7-2026-09-19/`: readiness `READY_FOR_PUBLICATION` con 13/13 gates verdes y **aun así** `BLOQUEADO` + ZIP suprimido, por un único CRITICAL `VACUOUS_RECALL` originating en un hueco de serialización del gate (la rama PASSED de `PublicationGatesOrchestrator._critical_recall_gate` más el `return 1.0` de `_extract_critical_recall`). No es un bloqueo legítimo del producto: el recall estaba fundado y el acta no puede decirlo porque `ReviewerReport.to_dict()` no serializa hallazgos | Quality gates/tribunal; **FASE-0** | Cerrar AC20 antes de consumir el intento E2E. Prohibido el verde barato: bajar severidades, editar `DiagnosisReviewer._check_vacuous_recall` para que no denuncie, o desactivar `GATE_BLOCKING_ENABLED`. Evidencia exigida: el contrafactual `BLOQUEADO → APROBADO-CONDICIONAL` sobre el acta archivada |
| Version Sync (quick) | Resuelto por re-medición: 9/10 el 2026-09-18 por cuatro documentos sucios en el árbol; 10/10 el 2026-09-19 con esos archivos ya idénticos a HEAD. `_check_version_sync` solo invoca `sync_versions.py --check` | Operador; A | Ninguna autorización pendiente. A re-mide el quick al inicio y no arrastra el rojo como prerrequisito |
| Privacidad F-B / D1 | Transporte WhatsApp por warehouse diferido; no es la fase B de este DAG | Producto/privacidad y onboarding; A ratifica la exclusión | No añadir PII ni modificar formulario/esquema sin decisión escrita. El setup puede resolver una promesa falsa, no el transporte de contacto |
| Frescura de observación | Fuente del 2026-07-22 (59 días al 2026-09-19) y `ONBOARDING_FRESHNESS_HOURS` sin definir, medido hoy: ningún verificador mecánico actúa | Operador; A decide vigencia, H comprueba entorno | Consentimiento datado sobre la URL viva con límite escrito, como en FASE-P4. Contrastar el entorno; reconfirmación real como fuente aparte, nunca fecha artificial, bypass o defaults |
| Binding de hotel | Medido 2026-09-19: la URL del warehouse no resuelve (NXDOMAIN) y la solicitada responde 200 con redirección observable; el fixture versionado ya usa la URL viva | A/H | Procedencia con ambas URLs, la evidencia de que una no resuelve y atribución de la corrección al operador. Sin edición del warehouse sin instrucción expresa y sin alias universal |
| Key expuesta | La prevención parcial en código no demuestra revocación operativa | Operador; F/H | Evidencia sin secreto de revocación o estado pendiente explícito. Key nueva y tests verdes no bastan; no ejecutar rotación remota sin permiso |
| Cierre documental central | Hay divergencia sobre regeneración de DOMAIN_PRIMER por implementación o solo RELEASE | Responsable documental; A | Resolver mandato antes de aplicarlo, sin modificar reglas centrales para silenciar la divergencia |
| QMind/write-back | QMind accesible para consulta según `00-lecciones-capitalizadas.md`; upload no autorizado | Responsable documental/operador | La consulta no concede permiso de subida. Si se exige write-back, dejar checkpoint hasta autorización y comprobar contenido/frescura; SKIP por título no prueba actualización |

Estas condiciones no se consideran satisfechas por existir un plan. La preparación no ejecuta validaciones, consultas de red, cambios de configuración ni operaciones sobre credenciales.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Único intento y aislamiento de la evidencia

- H prepara el runner acotado al plan, con reserva persistente exclusiva, hashes y preflight `attempts=0`; lo prueba con hijo falso, no con v4complete.
- Solo E2E invoca ese runner. El único proceso hijo autorizado es v4complete para `https://www.donalfonsohotel.com/`, Hotel Don Alfonso, con el output aislado del plan y flags existentes.
- El intento se consume al crear el proceso, incluso si falla o termina por timeout. La vigilancia de un PID existente no es un relanzamiento; no ejecutar además el comando manual, loops ni reintentos.
- No invocar una auditoría preliminar externa en A–H, ni force, deploy o desactivación del Tribunal para forzar READY.
- Snapshot saneado, exit code, inventario y hashes se preservan antes del análisis. No copiar secretos, `.env` o logs históricos crudos ni conservar un ZIP suprimido contra O1.
- VERIFY trabaja directamente sobre esa evidencia: no delega, modifica código, ejecuta tests ni repite la corrida. RELEASE se limita al cierre documental autorizado.

## Control de avance y R2

PRE/POST de cada implementación usan la misma selección y entorno; mutantes prueban el guard real y no errores de import/sintaxis. Los lectores distinguen READ_OK, ABSENT y READ_ERROR; retención deliberada se registra aparte. Umbrales, blocking y `write/publish/suppress` no se debilitan.

R2 conserva la referencia de **60 tool_use hasta el commit de código autorizado**, medida con el instrumento del contrato y corte temporal. Sin transcript o ante acceso denegado: **FUERA DE SERVICIO (R2.1)**, auto-reporte con unidad separado y sin comparaciones inventadas. Sin autorización de commit no se declara ese corte consumado; sin código se usa corte documental. Agotar presupuesto exige checkpoint y nueva sesión, nunca adelantar otra fase.

**Cierre de sesión (preparación 2026-09-18 y revisión 2 2026-09-19):** documentación y validaciones, sin código de producto; cerrado con commit y push autorizados en su turno, lo que no prueba ninguna fase A–H.

Estado actual de validación y medición de estas sesiones: **PENDIENTE / no ejecutado** para A–H. Las doce fases siguen pendientes y el contador v4complete en 0/1; lo ya ejecutado y publicado es la medición y el cierre documental de la preparación y de la revisión 2, con validaciones locales en verde y su push a `origin/master`. Sigue sin autorización e implícitamente no hecho: subida de datos, release operativo y cualquier auditoría externa preliminar.
