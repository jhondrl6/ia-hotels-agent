# Dependencias de fases

Fuentes de contrato: [maestro](01-plan-maestro.md), [ejecución](04-contrato-ejecucion.md) y [lecciones](00-lecciones-capitalizadas.md). Diseño congelado; ninguna fase ejecutada. **Contador v4complete: 0/1. Siguiente sesión: A.**

## DAG secuencial estricto

```text
[A] -> [B] -> [C] -> [D] -> [E] -> [F] -> [G] -> [H]
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
| A | Mandato de sesión y fuentes del plan | Baseline y contratos ratificados; permisos centrales, identidad y vigencia resueltos o checkpoint explícito | 0 | PENDIENTE |
| B | A cerrada | Pains y productores de promesas alineados; setup honesto; AC1/AC2/AC19-consumo y PRE/POST | 0 | PENDIENTE |
| C | B cerrada | Campo/destino seguro, bloqueo del botón inseguro y lector de presencia con alcance declarado; AC3/AC5/AC6/AC19 | 0 | PENDIENTE |
| D | C cerrada | Veredicto, causas y fail-fast persistidos; AC4/AC5/AC8/AC9 | 0 | PENDIENTE |
| E | D cerrada | Writer/ZIP real y snapshot interno revisable sin filtración; AC9–AC12 | 0 | PENDIENTE |
| F | E cerrada | Salidas saneadas y revocación acreditada, o pendiente explícito que impide certificar AC13 | 0 | PENDIENTE |
| G | F cerrada | Inventario AST, callers cubiertos y contrato muerto retirado; AC7/AC16 | 0 | PENDIENTE |
| H | G cerrada | Integración offline; binding/frescura y loader real; runner probado con hijo falso y attempts=0 | 0 | PENDIENTE |
| E2E | H cerrada y preflight favorable | Un proceso, exit code y evidencia saneada preservados; resultado real registrado aunque bloquee | 1 como máximo | PENDIENTE |
| VERIFY | E2E cerrada con evidencia preservada | Lectura directa, matriz por AC, diff estructural, límites y triage; sin remediar ni ejecutar | 0 | PENDIENTE |
| RELEASE | VERIFY cerrada y alcance de cierre explícito | Documentación y validaciones documentales autorizadas; no declarar éxito integral si la meta quedó parcial/FALLA | 0 | PENDIENTE |

AC15 atraviesa implementación/H. Cada fila incluye el cierre incremental exigido por el contrato; no basta cumplir solo el objetivo funcional. VERIFY puede documentar un resultado fallido: eso no lo convierte en certificación favorable ni habilita una reparación dentro de RELEASE.

## Conflictos de archivos y consumidores compartidos

| Superficie compartida | Fases que la consumen o modifican según su allowlist | Riesgo de interferencia | Orden obligatorio |
|---|---|---|---|
| `main.py` | B, C, D, E, G | Cableado de pains, precedencia WhatsApp, causas/fail-fast, retención y firmas | B antes de C antes de D antes de E antes de G; nunca ediciones concurrentes |
| Mapper y catálogo: `PainSolutionMapper`, `PAIN_SOLUTION_MAP`, `asset_catalog.py` | B es dueño del cambio; C/E/G consumen su contrato | Una promesa residual o identidad distinta rompe specs, narrativa y entrega | B congela identidades; consumidores posteriores prueban el mismo contrato |
| Productores asociados: `ConditionalGenerator.PAIN_TO_ASSET`, `get_assets_for_pain`, `_solutions_to_asset_specs` | B; C consume/gobierna seguridad del botón | Quitar una constante no elimina promesas en otras rutas | B alinea productores antes del guard de C |
| Coherencia: `CoherenceValidator`, reporte y callers | C, D, G | C elimina boost de presencia; D consume veredicto y causas; G verifica firmas/cableado | C antes de D antes de G; no reintroducir rutas paralelas |
| Delivery y revisores: writer, manifiesto interno, rutas de artefactos | E; H integra y prueba | Snapshot exportado por accidente o lectura del archivo equivocado | E define el límite interno/cliente; H no rehace enforcement |
| Sanitización y captura de salidas | F; H integra runner | Persistencia previa a redacción o fuga en stdout/stderr | F antes de H; solo secretos sintéticos en pruebas |
| Tests de integración, onboarding derivado y runner del plan | H | Gastar el intento desde un test o inventar flags de producción | H trabaja en tests/runner y preparación aislada: sin nuevos flags CLI ni nueva edición de `main.py` |
| Índice, checklist, dependencias y cierre documental | Todas, por turno | Estados inconsistentes o cierres anticipados | Un único cierre de fase a la vez; respetar permisos de cada sesión |

La tabla no amplía allowlists. Si un cambio exige otra superficie, detener y resolver alcance. No hay edición concurrente de ningún archivo compartido. Los inventarios read-only permitidos no autorizan ejecución de fases en paralelo ni escrituras por otro actor sobre esos archivos.

## Bloqueantes y decisiones pendientes reales

| Tema | Hecho de partida | Dueño / fase | Condición para resolverlo sin falsear evidencia |
|---|---|---|---|
| Version Sync (quick 9/10) | Medido 2026-09-19: `sync_versions.py --check` y `version_consistency_checker.py` exit 0 sobre los 7 campos gobernados; el check del quick compara contra `full_version: 4.77.2.0`. Es un desacuerdo entre verificador y escritor, no documentos desincronizados, y no bloquea el pre-commit | Operador/quality gates; A | Decidir cuál de los dos expresa el contrato y alinear el otro con su propio writer. No reescribir AGENTS.md/.cursorrules/GUIA a mano ni declarar TOTAL PASS antes de esa decisión |
| Privacidad F-B / D1 | Transporte WhatsApp por warehouse diferido; no es la fase B de este DAG | Producto/privacidad y onboarding; A ratifica la exclusión | No añadir PII ni modificar formulario/esquema sin decisión escrita. El setup puede resolver una promesa falsa, no el transporte de contacto |
| Frescura de observación | Fuente del 2026-07-22 (59 días al 2026-09-19) y `ONBOARDING_FRESHNESS_HOURS` sin definir, medido hoy: ningún verificador mecánico actúa | Operador; A decide vigencia, H comprueba entorno | Consentimiento datado sobre la URL viva con límite escrito, como en FASE-P4. Contrastar el entorno; reconfirmación real como fuente aparte, nunca fecha artificial, bypass o defaults |
| Binding de hotel | Medido 2026-09-19: la URL del warehouse no resuelve (NXDOMAIN) y la solicitada responde 200 con redirección observable; el fixture versionado ya usa la URL viva | A/H | Procedencia con ambas URLs, la evidencia de que una no resuelve y atribución de la corrección al operador. Sin edición del warehouse sin instrucción expresa y sin alias universal |
| Key expuesta | La prevención parcial en código no demuestra revocación operativa | Operador; F/H | Evidencia sin secreto de revocación o estado pendiente explícito. Key nueva y tests verdes no bastan; no ejecutar rotación remota sin permiso |
| Cierre documental central | Hay divergencia sobre regeneración de DOMAIN_PRIMER por implementación o solo RELEASE | Responsable documental; A | Resolver mandato antes de aplicarlo, sin modificar reglas centrales para silenciar la divergencia |
| QMind/write-back | QMind accesible para consulta según `00-lecciones-capitalizadas.md`; upload no autorizado | Responsable documental/operador | La consulta no concede permiso de subida. Si se exige write-back, dejar checkpoint hasta autorización y comprobar contenido/frescura; SKIP por título no prueba actualización |

Estas condiciones no se consideran satisfechas por existir un plan. La preparación no ejecuta validaciones, consultas de red, cambios de configuración ni operaciones sobre credenciales.

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

Estado actual de validación y medición de estas sesiones: **PENDIENTE / no ejecutado**. No se ha consumido el intento ni autorizado subida, commit, push o release operativo.
