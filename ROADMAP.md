# ROADMAP iah-cli — El diagnóstico es el producto

> **Principio rector**: iah-cli es una **herramienta de diagnóstico**, no una herramienta de IA que se vende por sí misma. El producto es un hallazgo defendible sobre la fuga de reservas directas de un hotel; los agentes, gates y actas son el medio para que ese hallazgo sea correcto y verificable, nunca el objeto de venta.
> **Versión roadmap**: v4.1 (2026-09-02) — reestructurado bajo el principio rector (v4.0) y **corregido contra artefactos reales** (v4.1)
> **Regla de evidencia de este documento**: ninguna afirmación sobre el estado del pipeline se escribe aquí sin estar verificada contra código o artefactos de una corrida real. La v4.0 heredó de `.opencode/context/CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §10 varias cifras que la auditoría del 2026-09-02 refutó; la v4.1 las corrige y marca cada corrección con su fuente. Verificar citas de código **no** verifica premisas.
> **Estado del proyecto**: fuente única `VERSION.yaml`. Estado operativo regenerable: `python scripts/doctor.py --status` → `.agent/SYSTEM_STATUS.md`. Este documento no replica datos sincronizables (ver §3).
> **Convergencia**: "calidad antes que escala" no compite con el principio rector — lo garantiza. La automatización existe para que el diagnóstico sea reproducible y defendible.
> **Marco AOA**: **A**udita (tribunal) → **O**ptimiza (acta + onboarding) → **A**utomatiza (deploy + escala). Nada se automatiza sobre un paquete que el Juez no haya aprobado.
> **Horizonte operativo**: 30 días para el primer ingreso (prospección, en paralelo); 90 días para el primer piso cerrado (entrega certificada). Se reevalúa semanalmente durante validación comercial y quincenalmente después.

---

## 1. Norte estratégico

### 1.1 El producto

iah-cli vende **un diagnóstico**: la cuantificación defendible de la fuga de reservas directas de un hotel, expresada en COP, con su nivel de precisión declarado, y un paquete de assets técnicos que la recupera.

El cliente compra un hallazgo, no software. La herramienta es invisible para él: no la opera, no la ve, no la evalúa. Lo que evalúa es si la cifra es creíble, si la evidencia la sostiene y si la acción propuesta la recupera.

De esta definición se derivan los tres atributos que el roadmap debe gobernar:

| Atributo | Pregunta que responde | Principio que lo rige | Gate que lo verifica |
|---|---|---|---|
| **Corrección** | ¿La cifra de fuga es verosímil para *este* hotel? | P7 | G10 |
| **Defensibilidad** | ¿Cada claim tiene fuente, confianza y acta que lo certifique? | P3 + P6 | G3, G11 |
| **Consecuencia** | ¿Diagnóstico, propuesta y assets cuentan la misma historia? | P6 | G6, G7, G8 |

### 1.2 La forma de producirlo

iah-cli no debe evolucionar como una aplicación tradicional human-first con automatizaciones añadidas. Debe evolucionar como un sistema agent-first cuyo propósito es producir diagnósticos correctos y defendibles de forma reproducible.

La interfaz humana existe, pero no debe crecer hasta convertirse en una carga de producto.
Su función es estrictamente esencial:

1. Configurar credenciales y permisos.
2. Lanzar objetivos de negocio: diagnosticar, auditar, entregar, desplegar.
3. Proveer datos que no pueden inferirse con confianza: ADR real, habitaciones, ocupación, canal directo, WhatsApp confirmado.
4. Aprobar operaciones con costo, riesgo o impacto externo.
5. Revisar entregables comerciales antes de enviarlos al cliente.

Todo lo demás debe ser responsabilidad de agentes:

1. Interpretar contexto del repositorio.
2. Elegir workflows.
3. Ejecutar fases.
4. Validar coherencia.
5. Detectar regresiones.
6. Mantener documentación operativa.
7. Preservar memoria y trazabilidad.
8. Producir evidencia verificable.

Frase guía:

> El humano define intención y límites; el agente transforma esa intención en ejecución verificable.

Prioridad estratégica:

> No se construye el segundo piso si el primero no está construido. En iah-cli, el primer piso es la entrega confiable al cliente: diagnóstico **correcto**, oportunidad coherente, propuesta consecuente y assets específicos que resuelven las brechas detectadas.

Antes de escalar automatización comercial, outreach, monitoreo recurrente, UI, nuevos módulos o expansión del producto, el pipeline debe demostrar que puede entregar una solución autoconsistente **y verosímil** para un hotel real.

---

## 2. Clasificación del repositorio

### 2.1 Lo que iah-cli ya es

| Capa | Rol bajo el principio rector | Estado actual | Orientación futura |
|------|------------------------------|---------------|-------------------|
| **Producto: el diagnóstico** | **Lo que se vende** | Fuga cuantificada + propuesta + assets; precisión declarada en datos pero no gobernada en el roadmap | Gobernado por P7 + G10; certificado por acta |
| Outputs comerciales | Envase del producto | Diagnóstico, propuesta, assets, delivery zip, `hook-pdf` | Mantener como lo único que el cliente ve |
| CLI humana | Interfaz de lanzamiento | `setup`, `v4complete`, `v4audit`, `onboard`, `execute`, `deploy`, `hook-pdf`, `validate-guarantee`, `--doctor` | Mantener mínima y estable |
| Agent Harness | Medio de producción | Memoria, routing, handlers, timeout, skill execution | Convertir en núcleo operativo |
| Workflows `.agents/workflows/` | Contrato de ejecución | **1 workflow activo** (`phased_project_executor.md`); los 16 anteriores archivados el 2026-08-24 | Mantener como contrato, no como ecosistema |
| Documentación técnica | Contexto de agente | Abundante pero dispersa | Navegación de agentes + resumen humano |
| Mantenimiento | Salud del medio | Doctor, validations, registry, version sync | Automático y obligatorio para agentes |

### 2.2 Conclusión de diseño

El repo debe tratar a los humanos como operadores estratégicos y validadores, no como ejecutores paso a paso.

Interpretación comercial deseada:

> El mercado paga por **hallazgos accionables**, no por plataformas. Los referentes externos de agentes de marketing especializados son evidencia de que ese mercado existe; no son un modelo a imitar. iah-cli no aspira a ser una plataforma horizontal ni un equipo agéntico genérico: aspira a producir el diagnóstico más defendible del mercado hotelero vertical, y esa es su ventaja diferencial — trazabilidad, gates de calidad, evidencia, acta de revisión y coherencia diagnóstico → propuesta → assets.

Esto no significa copiar una plataforma horizontal de marketing ni prometer ejecución 24/7 de todos los canales. Significa empaquetar, cuando exista validación comercial suficiente, los workflows y gates actuales como capacidad de producir diagnósticos certificados.

Por tanto:

- No priorizar una UI compleja.
- No multiplicar documentación narrativa para humanos.
- No hacer que humanos sigan procedimientos largos si un agente puede ejecutarlos.
- No vender la herramienta: vender el hallazgo que la herramienta produce.
- Sí mantener comandos CLI simples, seguros y explicables.
- Sí fortalecer AGENTS.md, workflows, gates, doctor, memoria, evidencia y validaciones.
- Sí traducir capacidades internas en lenguaje comercial comprensible **solo cuando describan el diagnóstico**, no cuando exhiban la arquitectura.

---

## 3. Estado actual

ROADMAP es un documento estratégico y **no se sincroniza automáticamente** (deuda de herramienta #H5: decisión explícita). Por eso no replica datos que ya tienen fuente autorizada — cada snapshot copiado es un desfaso garantizado.

| Qué se necesita | Fuente autorizada | Cómo obtenerlo |
|---|---|---|
| Versión, codename, release date | `VERSION.yaml` | lectura directa |
| Estado operativo (módulos, conteos, validaciones, tests) | `.agent/SYSTEM_STATUS.md` | `python scripts/doctor.py --status` |
| Historial de fases, entregables y claims verificados | `CHANGELOG.md` + `.opencode/plans/` | lectura directa |
| Precios, tiers y pisos vigentes | `config/pricing.yaml` | lectura directa |
| Gates de publicación y su severidad | `modules/quality_gates/publication_gates.py` (docstring L4-23) | lectura directa |
| Workflows activos | `.agents/workflows/` | `ls` |
| Pipeline comercial y prospectos | `evidence/Ingresos/` | lectura directa |

**Regla**: si un dato puede desfasarse, no vive aquí; vive en su fuente y este documento la referencia.

Lo que sí pertenece al ROADMAP, porque no se deriva del código, es el **estado del primer piso** (§7.1) y el **estado de los gates de decisión** (§9).

---

## 4. Principios de evolución

### P1. Agent-first, human-minimal

Cada nueva capacidad debe responder primero:

- ¿Puede ejecutarla un agente con contexto suficiente?
- ¿Puede verificarse automáticamente?
- ¿Puede dejar evidencia auditable?
- ¿Puede reanudarse en otra sesión?

El criterio no es “automatizar más”, sino codificar contratos ejecutables:

- qué estado debe existir antes y después,
- qué artefactos son fuente de verdad,
- qué gate valida el resultado,
- qué evidencia debe quedar para reanudar en sesión fresca.

El diseño de bucles debe definir criterios de avance, reintento, fallo y handoff humano; no depender de instrucciones aisladas.

Solo después se pregunta:

- ¿Qué mínimo necesita ver o decidir un humano?

### P2. Humanos no deben cargar contexto operativo

El humano no debe tener que recordar:

- qué workflow usar,
- qué validación corre primero,
- qué documentación actualizar,
- qué gate bloquea,
- qué archivo es fuente de verdad.

Eso debe estar codificado en:

- `AGENTS.md`,
- `.agents/workflows/`,
- `docs/CONTRIBUTING.md`,
- scripts de validación,
- doctor,
- registry,
- tests.

### P3. Todo output importante debe tener evidencia

Diagnósticos, propuestas, scores, gates y assets deben poder responder:

- qué dato se usó,
- de dónde vino,
- con qué confianza,
- qué módulo lo generó,
- qué gate lo validó,
- qué archivo lo prueba.

La evidencia debe vivir en artefactos estructurados y consultables por agentes, no solo en narrativa humana.

> **P3 es condición necesaria, no suficiente.** La procedencia no garantiza la verosimilitud: una cifra puede tener fuente declarada (benchmark regional), evidencia trazable y coherencia interna perfecta, y aun así estar desviada cientos de veces de la realidad del hotel. Ese hueco lo cierra P7.

### P4. Manual antes que automático, pero solo para validar mercado

Para ventas y producto comercial, se mantiene el principio:

> Manual antes que automático, específico antes que general.

Pero para operación interna del repo, el objetivo es lo contrario:

> Si un agente puede hacerlo con seguridad y evidencia, no debe hacerlo manualmente el humano.

### P5. No construir interfaz humana pesada antes de tracción

No crear dashboard, SaaS, GUI, multiusuario o panel administrativo hasta tener validación comercial suficiente.

La interfaz humana mínima por ahora es:

```bash
python main.py setup                                          # credenciales
python main.py v4complete --url https://hotel.com             # diagnóstico completo
python main.py hook-pdf --output-dir output/v4_complete/      # gancho comercial (2 páginas)
python main.py onboard --url https://hotel.com                # datos reales → precisión
python main.py execute --url https://hotel.com --package starter_geo
python main.py validate-guarantee                             # Garantía Día 55
python main.py --doctor                                       # salud del ecosistema
```

Los siete comandos son interfaz de producto, no de plataforma: seis producen o certifican un diagnóstico y uno habilita el resto.

### P6. Coherencia comercial como contrato de entrega — primer piso obligatorio

La evolución agent-first no puede limitarse a ejecutar módulos. Debe garantizar que el producto final sea una solución confiable para el cliente.

Este principio tiene prioridad sobre cualquier segundo piso del roadmap: nuevas automatizaciones, expansión comercial, monitoreo recurrente, UI o crecimiento de features dependen de que esta capa esté resuelta.

Contrato mínimo:

1. Si los módulos detectan N brechas, el diagnóstico y oportunidad deben cubrir N brechas o justificar explícitamente cuáles se agrupan, descartan o aplazan.
2. Cada brecha priorizada debe mapearse a una recomendación comercial concreta.
3. Cada recomendación vendida en la propuesta debe tener assets correspondientes, específicos para el hotel y trazables a la brecha que resuelven.
4. Ningún asset genérico debe presentarse como solución terminada si no ataca una brecha real del hotel.
5. Si faltan datos reales, el output debe declararlo como `ESTIMATED`, `PENDING_ONBOARDING` o `CONFLICT`, no ocultarlo detrás de narrativa comercial.
6. La publicación o entrega debe bloquearse si diagnóstico, propuesta y assets se contradicen.

Este contrato debe ser ejecutado por agentes y gates, no recordado manualmente por el humano en cada entrega.

**Operationalización:** ningún diagnóstico sale sin **acta de revisión** que certifique las 6 cláusulas. Un contrato verificable, no una consigna. Ver FASE T.

> **Advertencia de estado real (verificado 2026-09-02 contra código y artefactos):** la distinción *blocking/advisory* que promete el docstring de `modules/quality_gates/publication_gates.py:4,20-23` **no está implementada**. `self.gates` (`:181-195`) es un dict plano de 13 entradas sin estructura de severidad, y el llamador de producción `check_publication_readiness` (`:1919`, invocado desde `main.py:2945`) deriva el bloqueo con `[r for r in results if not r.passed]` ⟹ **los 13 gates bloquean hoy, 0 son advisory**. `is_ready_for_publication` (`:227`) no tiene llamador de producción: aparece solo en el ejemplo del docstring (`:169`) y en tests.
>
> Lo que sí está incumplido no es la severidad sino la **agregación**: ninguna capa certifica las 6 cláusulas como un todo, y el gate que de verdad decide publicación ignora el veredicto de coherencia (§7.1). **Objetivo decidido, no aún implementado: 11 blocking + 2 advisory** (`content_quality`, `proposal_asset_alignment`); `asset_confidence` **conserva su bloqueo** porque es hoy el único mecanismo que vuelve no-entregable un paquete Tier C — relajarlo dejaría salir el 14% del histórico (4 de 29 corridas) con 100% de assets ESTIMATED. El patrón a copiar ya existe en `commercial_gate.py:99-113` (`BLOCKING_GATE_IDS` + `WARNING_GATE_IDS`). **El acta del Juez (T1) es la capa que agrega las 6 cláusulas.** Mientras T1 no exista, P6 está cumplido a medias y no debe afirmarse lo contrario.

### P7. Precisión del diagnóstico como atributo de producto

El diagnóstico es una medición. Una medición con procedencia perfecta y magnitud absurda es un producto defectuoso, y es la forma más rápida de convertir iah-cli en "tecnología de IA sin valor medible".

Reglas:

1. **Toda cifra de fuga declara su `precision_tier`** (A/B/C), derivado de la granularidad epistémica de sus fuentes — implementado en `modules/financial_engine/precision_validator.py` vía `classify_source()` + `determine_precision_tier()`. ⚠️ **Defecto vivo:** en `main.py:2149-2167` el valor se inicializa en `"C"` y la llamada al validador va dentro de un `try/except Exception: pass`. Cualquier fallo **degrada silenciosamente a Tier C sin dejar señal** — el mismo patrón que ya causó el NameError invisible del gate `tier_c`. La regla no es auditable hasta que ese `except` registre el motivo.
2. **La precisión decide la regla de render**: cifra exacta solo en Tier A; **rango + descargo** en Tier B/C. Nunca cifra exacta sobre dato inferido.
3. **Toda cifra pasa por cap de plausibilidad** antes de aparecer en un documento comercial: habitaciones × ocupación × ADR × canal directo acotan el techo posible. Una fuga que excede el techo se rechaza, no se publica.
4. **Ningún diagnóstico Tier B/C se presenta como entregable final.** Alcanza como máximo `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (T1). Coherencia interna alta no compensa precisión baja.
5. **El error se mide, no se supone**: cuando un hotel pasa por onboarding, la fuga estimada en Tier B se contrasta contra la recalculada en Tier A. La desviación es la métrica de calidad del producto (§11.1).

Evidencia de por qué este principio existe: caso Hotel Luxor — 21 habitaciones, 15 reservas/mes, ADR $200K, 60% canal directo → fuga realista ~$12K COP/mes; con benchmark aplicado → ~$7.6M COP/mes. Sobreestimación ~630x en un paquete que cumplía P3, G3, G6 y G7.

---

## 5. Contrato de producto: quién ejecuta qué

| Actividad | Ejecutor primario | Humano interviene cuando... |
|-----------|------------------|-----------------------------|
| Diagnóstico `v4complete` | Agente / CLI | Debe aportar URL o revisar output |
| Precisión de la cifra (exacta vs rango) | Agente (`PrecisionValidator`, P7) | Nunca: es determinista |
| Auditoría de paquete (tribunal / acta) | Agente | Nunca: es determinista; solo lee el acta |
| Onboarding de datos reales | Humano asistido por bot de diálogo estructurado (T3) | Solo si los datos son inconsistentes entre sí |
| Validación cruzada | Agente | Hay conflicto hard o dato dudoso |
| Generación de propuesta | Agente | Antes de enviar a cliente |
| Generación de assets | Agente | Si asset queda ESTIMATED o CONFLICT |
| Garantía Día 55 / nota de crédito | Agente (`validate-guarantee`) | Aprueba el crédito si se activa |
| Deploy | Agente con aprobación, **solo tras `APROBADO-PARA-ENTREGA`** | Hay impacto externo real |
| Mantenimiento docs | Agente | Solo si cambia estrategia o criterio comercial |
| Actualización roadmap | Humano + agente | Cambia dirección estratégica |
| Fases de desarrollo | Agente | Humano define objetivo y límites |
| Costos/API externas | Agente con permission mode | Costo/riesgo excede umbral |

Regla comercial de costos:

> Cada Diagnóstico Express debe mantener presupuesto máximo de API/cómputo y margen mínimo esperado. Si el costo real por diagnóstico amenaza ese margen, se activa reducción de llamadas, fallback barato, `permission_mode` o revisión explícita de precio antes de escalar volumen.

---

## 6. Arquitectura objetivo

### 6.1 Capa agente

Es la capa dominante **en ejecución**, y está subordinada al producto **en propósito**: existe para producir diagnósticos correctos de forma reproducible, no para ser exhibida ni extendida.

Componentes:

- `AGENTS.md`: contexto global operativo, no manual humano.
- `.agents/workflows/`: workflows semánticos y ejecutables.
- `agent_harness/`: memoria, routing, ejecución, observación, self-healing y recuperación de estado.
- `.agent/knowledge/DOMAIN_PRIMER.md`: conocimiento regenerable del dominio/código.
- `scripts/doctor.py`: healthcheck del ecosistema agente.
- `scripts/run_all_validations.py`: gate de validación.
- `docs/contributing/*`: contrato documental para agentes.
- `tests/`: protección contra regresión.
- Trazas y estados de ejecución: logs, reports y snapshots mínimos para reanudar sin reconstruir contexto.

Objetivo:

> Un agente nuevo en sesión fresca debe poder entender el estado del repo, elegir el workflow correcto, ejecutar una fase, verificarla y registrar evidencia sin depender de memoria humana.

Cada ejecución debe dejar un estado mínimo: objetivo, inputs, outputs, gates, errores y siguiente acción. Si el agente cae o cambia de sesión, el siguiente debe poder retomar desde el estado, no desde la memoria humana.

### 6.2 Capa humana mínima

Debe ser pequeña, estable y difícil de usar mal.

Componentes:

- `README.md`: qué hace, cómo instalar, cómo ejecutar los comandos principales.
- CLI `main.py`: los 7 comandos de P5, claros y con flags seguros.
- `setup`: credenciales.
- `onboard`: datos reales (lo único que sube la precisión del producto).
- `hook-pdf` y `validate-guarantee`: instrumentos comerciales del diagnóstico y de su promesa.
- outputs comerciales: diagnóstico, propuesta, acta, assets, zip de entrega.

Objetivo:

> Un humano técnico debe poder operar el producto sin entender la arquitectura interna.

### 6.3 Capa cliente final

El cliente hotelero no opera el repo.
Recibe:

- diagnóstico,
- propuesta,
- **acta de revisión** (certificado del producto: qué se auditó, qué se encontró, con qué veredicto),
- evidencia resumida,
- assets técnicos,
- plan de acción,
- eventual reporte de seguimiento.

**Regla de visibilidad (resuelve una contradicción actual):** el acta **no es la herramienta mostrándose — es el certificado del producto**, y debe viajar al cliente. Los reports internos de gates sí se excluyen del ZIP (`modules/delivery/delivery_packager.py:337`, `_GATE_REPORT_PREFIXES`). La distinción es: *evidencia de rigor sobre el diagnóstico* viaja; *tripas del pipeline* no. Hoy el packager no distingue ambas cosas, y el acta (T1) deberá entrar por lista blanca explícita.

### 6.4 Capa de aseguramiento de entrega confiable

Esta capa debe cerrar el loop interno que hoy requiere invocación manual después de generar entregables en `output/v4_complete`.

Problema actual:

- Los módulos pueden detectar más brechas que las que aparecen en diagnóstico y oportunidad.
- La propuesta comercial puede vender soluciones que no quedan materializadas en assets concretos.
- Los assets pueden existir pero ser genéricos, estimados o desconectados del dolor específico del hotel.
- **La cifra de fuga puede ser internamente coherente y magníficamente errónea.**
- El humano debe pedir manualmente al agente que audite coherencia, cobertura y calidad después de cada entrega.

Arquitectura objetivo:

| Contrato interno | Qué debe asegurar | Evidencia esperada |
|------------------|-------------------|--------------------|
| **Cifra de fuga (P7)** | Qué número se muestra, con qué `precision_tier`, en qué formato (exacto/rango), con qué cap de plausibilidad y qué descargo | `financial_scenarios_<timestamp>.json` (**timestamped, sin índice** — §7.2) + `precision_tier` + `quality_metadata` del MANIFEST |
| `pain_ledger` / brechas fuente de verdad | Toda brecha detectada queda normalizada con `pain_id`, severidad, fuente y confianza | JSON rastreable en `output/v4_complete/<hotel>/` |
| Diagnóstico y oportunidad | Cobertura 1:1 o justificación explícita para cada brecha detectada | Tabla brecha → impacto → oportunidad → evidencia |
| Propuesta comercial | Cada servicio vendido responde a una o más brechas priorizadas | Matriz brecha → servicio → promesa comercial |
| Assets | Cada asset generado resuelve una brecha o servicio específico, no una plantilla genérica | Matriz servicio → asset → archivo → confidence |
| Harness de ejecución / trazabilidad | Qué se ejecutó, con qué inputs, qué gates corrieron, qué falló y cómo retomar | Traza mínima + logs + estado recuperable |
| Delivery gate | Bloquea entrega si hay brechas sin explicar, servicios sin asset o assets genéricos vendidos como específicos | `delivery_quality_report.json` + estado PASS/FAIL |
| **Acta de revisión (T1)** | Certifica las 6 cláusulas P6 + P7 como un todo y fija el veredicto de entrega | `acta_revision.json` + `acta_revision.md` |

Reglas obligatorias:

1. **Coverage gate**: `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`.
2. **Commercial alignment gate**: todo servicio de la propuesta debe mapear a brecha real, evidencia y asset.
   - **Gate bloqueante `tier_c_onboarding_required`**: verifica que `financial_evidence_tier ≠ "C"` para propuesta completa. Depende de datos reales del onboarding (`hotel_data`); assets con tier C en datos reales permanecen como `ESTIMATED` aunque el código esté correcto.
3. **Asset specificity gate**: cada asset debe mencionar el hotel, el problema que resuelve y el punto de implementación; si no, queda `GENERIC_DRAFT` y no se vende como solución final.
4. **Evidence gate**: cada claim fuerte debe tener fuente: web, GBP, onboarding, benchmark o estimación declarada.
5. **Precision gate (P7)**: ninguna cifra exacta sobre dato Tier B/C; cap de plausibilidad aplicado antes de render.
6. **No silent drop**: ninguna brecha puede desaparecer entre módulos, diagnóstico, propuesta y assets sin explicación auditable.
7. **Human review mínima**: el humano revisa excepciones y decisión comercial final, no reconstruye manualmente la coherencia.

**Mapeo cláusulas P6/P7 → gates reales en código, con su severidad verificada** (fuentes: `modules/quality_gates/publication_gates.py:181-195` y `:1919`; `modules/quality_gates/commercial_gate.py:740-800`):

| Cláusula | Gate en código | Bloquea hoy | Objetivo decidido | ¿Cubre la cláusula? |
|---|---|---|---|---|
| P6.1 cobertura de brechas | `coverage_no_silent_drop` | Sí | Sí (11+2) | Sí |
| P6.2 brecha → recomendación | `pain_solution_mapper` + `proposal_asset_alignment` | Sí | **advisory** | Parcial — ver nota tautología |
| P6.3 recomendación → asset | `proposal_asset_alignment` | Sí | **advisory** | **No** — el artefacto no trae la ruta (ver abajo) |
| P6.4 no asset genérico | `asset_confidence` + `content_quality` | Sí | `asset_confidence` **blocking**, `content_quality` advisory | Sí |
| P6.5 datos faltantes → ESTIMATED | `tier_c_onboarding_required` + `CG-EVIDENCE-TIER-CONSISTENCY` | Parcial | Parcial | **No del todo** — ver nota no-op |
| P6.6 entrega bloqueada si contradice | `coherence` + `hard_contradictions` | Sí, pero **ignora `is_coherent`** | Igual | **No** — ver §7.1 |
| P7.1-3 precisión y plausibilidad | `PrecisionValidator` + cap (regla de render, no gate de publicación) | **No** | No | **No** — falta G10 |
| P6 en su conjunto (agregación) | *ninguno* | **No** | **Sí** (acta T1) | **No** — falta G11 |

Gates blocking restantes no mapeados a cláusula: `evidence_coverage`, `financial_validity`, `critical_recall`, `ethics`, `doc_audit_consistency`, `pricing_compliance` (floor-aware, FASE-P0-B).

> **Nota no-op (P6.5):** `CG-EVIDENCE-TIER-CONSISTENCY` retorna `passed=True, severity="INFO"` para **todo** `evidence_tier != 'A'` (`commercial_gate.py:765-773`, mensaje "Tier {B,C} no requiere verificación GA4/GSC"). Solo bloquea cuando el documento *afirma* Tier A sin GA4/GSC reales. Por tanto **no puede certificar P6.5 para los paquetes Tier B/C**, que son exactamente los que el primer piso debe retener. Lo que hoy retiene un paquete Tier C es `asset_confidence`, no este gate.
>
> **Nota tautología (P6.2/P6.3):** `coverage_ratio = effective / (effective + unresolved)` y `passed == (unresolved == 0)` ⟹ `coverage == 1.0 ⟺ passed`. Son el mismo bit, medido en 10 configuraciones con `coverage_ratio = 1.000`. El umbral `< 0.8 → BLOCKED` es **redundante, no muerto** (3 tests lo ejercitan y disparó BLOCKED en 2 de 4 configuraciones históricas). Además `proposal_asset_matrix.json` persiste `asset_path: null` incluso en la entrada LINKED cuyo asset sí se generó ⟹ **la trazabilidad P6.3 no es verificable desde el artefacto**.

Resultado esperado:

> `v4complete` no solo genera archivos; entrega un paquete autoconsistente **y verosímil** donde diagnóstico, oportunidad, propuesta y assets cuentan la misma historia comercial y técnica, con un acta que lo certifica.

---

## 7. Roadmap técnico

### 7.1 Estado del primer piso — FASE 0 y PIPELINE-FIX completados

Detalle de entregables, claims verificados y evidencia por archivo: `CHANGELOG.md` y `.opencode/plans/FASE-0-DELIVERY-QUALITY/`.

Lo que quedó operativo y sostiene todo lo demás:

- **`pain_ledger`** (`modules/asset_generation/pain_ledger.py`) — brechas normalizadas con `pain_id`, fuente, severidad, confianza y estado; artefacto `pain_ledger.json`.
- **`delivery_quality_report`** (`modules/quality_gates/delivery_quality_report.py`) — QA post-generación; si `status == "FAIL"` **el ZIP no se crea** (verificado: `main.py:3194-3200`). ⚠️ **No es el único mecanismo**: conviven **tres rutas de bloqueo del ZIP** (`main.py:3194` por FAIL o `_claim_escalated`, `:3205`, `:3274`) más el kill switch `GATE_BLOCKING_ENABLED` (`main.py:2990-2992`, default `true`, sin auditar). T1 debe fijar cuál gobierna antes de añadir una cuarta.
- **`human_checklist`** (`modules/quality_gates/human_checklist_generator.py`) — ≤10 items derivados automáticamente del reporte.
- **`data_derivation_layer`** (`modules/asset_generation/data_derivation_layer.py`) — 5 derivaciones semánticas del audit.
- **Assessment dict bridge + fórmula `delivery_ready`** (PIPELINE-FIX) — `tier_c_onboarding_required` inyectado en el assessment; umbral `confidence_score ≥ 0.65`; `evidence_tier` propagado a `quality_metadata` del MANIFEST (`main.py:3219`).

**Definición de terminado cumplida**:
> Un agente puede responder, con evidencia por archivo: qué brechas detectó, cuáles entraron al diagnóstico, qué oportunidad comercial justifican, qué se propone vender y qué assets específicos entregan esa solución.

**Lo que falta para cerrar el primer piso**: la **coherencia** está demostrada en score (E2E Castilla Real 0.8261; SalenteReal **0.88** — verificado 2026-09-02 en `asset_generation_report.json`: `coherence_score_pre/post/final = 0.88` y `coherence_report.overall_score = 0.88`). La **corrección** no: ambos paquetes son Tier B/C, producidos sin onboarding.

> **Hallazgo bloqueante de premisa (verificado contra artefactos reales, 2026-09-02):** los **cuatro** artefactos de la corrida SalenteReal 2026-08-31 dicen **`is_coherent: false`** (`coherence_report` y `final_coherence_report`) y aun así el paquete salió **`READY_FOR_PUBLICATION`** y produjo `hotelsalentoreal_20260831.zip` (46.552 bytes; 37 archivos expandidos). No es bug de lectura: `publication_gates._coherence_gate` decide con **solo** `coherence_score >= threshold`, mientras `coherence_gate.py` — que sí usa `passed = report.is_coherent` — **no tiene llamador de producción** (huérfano, igual que `publication_state.py`). Causa del `false`: `assets_are_justified` da 3/4 = 0.75 → `severity=error`; el asset injustificado es `monthly_report` (always-on, sin pain que lo respalde).
>
> **Consecuencia para el plan:** como el gate que decide publicación lee solo `overall_score`, **agregar errores al reporte de coherence no bloquea nada**. Ningún acta (T1) que se alimente de ese reporte heredará el veredicto real. Corregir esto es condición previa a T1, no parte de T1.
>
> La cifra **0.9133** que circulaba en documentos previos es el `pre_coherence_score` **no canónico** (regresión DT4-N4, doble fuente de coherence). No citarla como score de SalenteReal.

El primer piso no cierra con coherencia interna — cierra con Tier A, assets ≥ 0.8 y acta `APROBADO-PARA-ENTREGA` (G0, §9). La resolución depende de datos reales y del tribunal, no de más código de pipeline.

### 7.2 FASE T: Tribunal certificador del contrato P6 + P7 ← **máxima prioridad**

Ancla: P6 ("primer piso obligatorio") y P7. Fuente del plan: `.opencode/context/CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §10 — ⚠️ **parcialmente refutado** por la auditoría del 2026-09-02 (14 refutaciones factuales + 10 defectos vivos que el doc no ve). Las correcciones verificadas contra código y artefactos están incorporadas abajo; no citar §10 como fuente de verdad sin contrastar.

Convierte el contrato en un agente que certifica y produce un acta. Es la capa que hoy no existe: nadie certifica las cláusulas **como un todo**, y el gate que decide publicación ignora el veredicto de coherencia (§7.1).

**Regla arquitectónica inviolable**: el tribunal **no re-ejecuta lógica de gates**. Lee los outputs ya generados como revisor independiente. Reimplementar checks reproduciría el drift de fuente-única ya resuelto en FASE-SR-B. Su valor es **independencia + legibilidad + verificación de lenguaje natural**, lo único que ningún gate cubre.

⚠️ **Pero leer outputs exige resolver tres problemas reales de nomenclatura** (verificados sobre `output/FASE-D_salentoreal_post_guard/.../v4_audit/`):

1. **No hay nombres fijos.** `gate_report` y `financial_scenarios` son **timestamped** (`gate_report_20260831_122803.json`, `financial_scenarios_20260831_122757.json`) y **no existe índice** que permita resolver cuál corresponde a la corrida. Un revisor que lea outputs necesita un paso previo de resolución de nombre, o un manifiesto de artefactos.
2. **El reporte comercial está partido en dos y el que falla es el que nadie lee.** `commercial_gates_report.json` contiene **3** gates (todos en verde); los otros **9** viven en `commercial_gates_report_diagnostic_20260831_122803.json`, y ahí está el único gate que falló en la corrida real: **`CG-WHATSAPP-LEAD` (WARNING, `passed: false`)**. Leer solo el archivo de nombre canónico produce un falso "todo pasó".
3. `pain_ledger.json` **no serializa la clave `assets`** (`pain_ledger_resolved.json` trae `assets: null` en las 3 entradas) ⟹ la matriz no es reproducible desde disco.

Integración: módulo gate-family `modules/quality_gates/tribunal/` (**aún no existe** — nada de FASE T está implementado). El doc fuente propone orquestarlo desde `modules/orchestration_v4/two_phase_flow.py` como **FASE 5.5**, pero ese módulo **no es el orquestador de producción**: lo único que lo importa es `onboarding_controller.py` (que sí se instancia en `main.py:1697`, pero usa de allí solo los tipos `Phase1Result`/`Phase2Result`/`HotelInputs`), el `__init__` del paquete y tests. **Elegir un anfitrión real es precondición de T1.** El punto natural es `main.py` junto a `delivery_quality_report` (FASE 7, `:3178-3200`), que es donde hoy ya se decide el ZIP.

#### T0 — Precondiciones medidas (van ANTES de T1)

La secuencia T1→T6 del doc fuente **invierte el orden correcto**. Mediciones empíricas del 2026-09-02 sobre los artefactos reales (10 configuraciones: 5 variantes de registro × 2 oráculos de presencia) muestran que el cambio de denominador de `coverage_ratio` **no es un fix, es un interruptor global**:

| # | Acción | Evidencia medida |
|---|---|---|
| **T0.1** | Convertir `coverage_ratio` en **divulgación advisory** y dejar el veredicto bloqueante en `unresolved` | Con denominador = `total` (S2.3) **bloquea en 10/10 configuraciones**, rango 0.125-0.714, todo bajo 0.8. **Insatisfacible por medios honestos**: solo 3 pains detectados de ~22 en el mapper ⟹ máximo 3 servicios LINKED; pasar 0.8 con total=7 exige `effective ≥ 6` y hoy hay 4. Llegar a 6 obligaría a remapear servicios a assets ajenos — semánticamente falso |
| **T0.2** | Arreglar el **doble oráculo de presencia** | Un mismo resultado afirma que `Schema Hotel` y `Schema Organization` están en `details.missing` **y** en `alignment.present_assets`, a 4 claves de distancia. El oráculo permisivo (`_presence_resolved`, acepta `exists_with_issues`) gana y decide `coverage_ratio`/`unresolved`; el estricto solo escribe el `message`. **No voltea ningún veredicto en 10/10** — es higiénico, no crítico |
| **T0.3** | Recién entonces tocar el **registro de servicios** | Unificar 7→8 cuesta **exactamente 0.0000 en coherence** (dos candados estructurales: score `1.0` hardcoded en la rama de éxito; denominador por unión en la de fallo) pero **empeora alignment 0.571 → 0.500**. Hacerlo antes de T0.1 es pagar el costo sin recibir el beneficio |
| **T0.4** | Corregir el gate de coherence para que lea `is_coherent`, no solo el score | §7.1: los 4 artefactos dicen `false` y el paquete salió con ZIP. Sin esto, el acta de T1 hereda un veredicto que no es el real |

**Causa raíz por debajo de T0** (verificada entrada por entrada sobre artefactos reales): el ledger resuelto tiene **3 pains** y el orquestador genera **4 assets**, de los cuales **2 son huérfanos** (se generan y entregan sin que ningún servicio prometido mapee a ellos) y **6 de 7 servicios prometidos responden a pains que no se detectaron**. Esa única causa produce a la vez `no_breach = 6/7` e `is_coherent = false` (`assets_are_justified` 3/4 = 0.75). **La propuesta dinámica — solo prometer servicios con brecha detectada — cierra ambos síntomas a la vez** y hace `no_breach = 0` por construcción. Todo lo demás (advisory, S2.3, remapeos) es parche sobre un contrato comercial que sigue vendiendo lo que no diagnostica. Requiere decidir antes **cuál de los seis registros de identidad de servicios manda** (`service_catalog` 8 · `PROPOSAL_SERVICE_TO_ASSET` 7 · `ASSET_CATALOG` 25 · `PAIN_SOLUTION_MAP` 22 · runtime 4 · contract registry 3+3; ninguno canónico).

| ID | Sub-fase | Qué se construye | Cláusula | LLM | Criterio de aceptación |
|----|----------|------------------|----------|-----|------------------------|
| **T1** | Juez certificador | `tribunal/judge.py` — determinista. Emite `acta_revision.json` + `acta_revision.md`. El veredicto debe **alimentar una de las tres rutas de bloqueo del ZIP ya existentes**, no añadir una cuarta (§7.1). `publication_state.py` está **huérfano**: o se le da llamador o no se cita como destino. Regla de primer piso: `evidence_tier ∈ {B,C}` → máximo `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | P6 (las 6) + P7 | No | Corrido sobre la entrega real `hotelsalentoreal_20260831` (Tier B, coherence canónico **0.88**, `is_coherent: false`, ZIP de 46.552 B / 37 archivos) → acta con veredicto condicional, 6 cláusulas evaluadas contra artefactos reales **resueltos por timestamp**, `CG-WHATSAPP-LEAD` detectado en el archivo diagnóstico, `IMPLEMENTATION_ORDER.md` vacío señalado. Test determinista verde |
| **T2** | Revisores mecánicos | `tribunal/asset_reviewer.py` (CON-ASSET / SIN-ASSET / ASSET-GENERICO / ASSET-ESTIMATED-NO-ETIQUETADO) y `tribunal/diagnosis_reviewer.py` (brecha→`pain_id` trazable, fuente declarada) | P6.1, P6.3, P6.4 | No | El acta de SalenteReal incluye hallazgos por severidad y señala que `proposal_asset_matrix.json` trae `asset_path: null` (P6.3 no verificable desde el artefacto); `IMPLEMENTATION_ORDER.md` vacío detectado como asset incompleto. Tests de contrato verdes |
| **T3** | Onboarding como precondición | Bot de diálogo estructurado (3-4 preguntas: rooms, occupancy_rate, direct_channel_pct, adr) que ejecuta `main.py onboard` y re-corre `v4complete` en Tier A | P6.5, P7.4 | No | Paquete con onboarding completo alcanza `evidence_tier: A`, assets ≥ 0.8 (G0 cerrado) y el Juez emite `APROBADO-PARA-ENTREGA` |
| **T4** | Revisores de lenguaje natural | `tribunal/alignment_reviewer.py` (promesas verbales de la propuesta vs matriz) y `tribunal/honesty_reviewer.py` (sobre-presentación vs tier labels y los **12 `CG-*` reales repartidos en dos archivos**, no "los ~10" ni "solo 4" del doc fuente) | P6.2, P6.5 | Sí, acotado | Test con propuesta que promete verbalmente un servicio ausente de la matriz → marcado. Test con ESTIMATED presentado como verificado → marcado. Debe leer **ambos** reportes comerciales. LLM mockeado en tests |
| **T5** | Entrega y deploy gateados | (1) Fix del `IMPLEMENTATION_ORDER.md` vacío — causa raíz en `modules/geo_enrichment/asset_responsibility_contract.py` y `modules/delivery/generators/implementation_order_gen.py`; (2) CMS detection desde `hotel_data.cms_detected`; (3) conectores fuera de `dry_run` (FTP `upload_file`, WP `inject_code`) con aprobación humana | AOA "automatiza" | No | Paquete Tier A aprobado → `IMPLEMENTATION_ORDER.md` con contenido real; deploy de prueba a staging verificado en producción (`site_verification_applied: true`) |
| **T6** | Throughput + gancho | Agente que recibe lista de URLs propias y ejecuta `v4complete` + tribunal por cada una; agente de primer contacto que envía `hook-pdf` + mensaje con cifra de fuga en COP | escala | Sí | N hoteles/semana con acta sin intervención humana por corrida; costo por diagnóstico dentro del margen (§5) |

Regla de LLM: el LLM **propone** hallazgos, el **Juez aplica veredicto determinista**. Nunca es juez de registro — preserva la auditabilidad de P3.

Costo marginal: T1/T2/T3/T5 deterministas; solo T4/T6 usan LLM barato con cache. El tribunal **acelera** el primer ingreso al volver el diagnóstico defendible.

**Definition of Done de FASE T**: (a) ningún paquete sale sin `acta_revision.md` que certifique P6 + P7; (b) ningún paquete Tier B/C recibe `APROBADO-PARA-ENTREGA`; (c) ningún deploy se ejecuta sin veredicto de aprobación; (d) el tribunal no duplica lógica de gates; (e) costo marginal dentro del margen comercial.

### 7.3 FASE A: Baseline de robustez agente (colapsada — 2-3 días)

FASE A se diseñó para sanear un ecosistema de 16 workflows. Ese ecosistema fue archivado el 2026-08-24: hoy hay **1 workflow activo**. Los entregables originales A-01 a A-04 perdieron objeto y se reducen a una sola tarea de higiene documental; solo conserva valor propio la validación de contexto fresco.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| A-05 | Validación de contexto fresco | Un agente nuevo puede ejecutar diagnóstico de repo sin preguntar | Smoke test pasa **y el diagnóstico resultante declara `precision_tier` y produce acta** |
| A-06 | Higiene documental única | `AGENTS.md` auditado como contexto primario, README humano-mínimo, matriz humano/agente alineada | `python scripts/validate_agents_md.py` PASS + `validate_document_integration.py` PASS |

No construir: dashboard, UI web, wizard complejo, integración multiusuario, marketplace de skills.

### 7.4 FASE B: Ejecución de fases más confiable por agentes (2-4 semanas)

Objetivo: reducir fallos de ejecución multi-sesión. Es la infraestructura que hace el diagnóstico **reproducible**, y sin reproducibilidad no hay tasa de error medible (P7.5).

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| B-01 | `phased_project_executor.md` endurecido | Reglas de fase, presupuesto y docs cascade sin ambigüedad | Plan de prueba con fase simulada |
| B-02 | Bucles de fase estandarizados | Cada bucle contiene objetivo, estado inicial, acciones permitidas, criterios de avance, gates de verificación, rollback y handoff humano cuando corresponda | Checklist de bucle validado |
| B-03 | Evidencia post-fase obligatoria | Cada fase deja logs, tests, diff y docs tocadas | `log_phase_completion.py` usado; **el acta del tribunal cuenta como evidencia de fase** |
| B-04 | Regla de no-doc-drift | Cambios de código que alteran comportamiento disparan docs/checks | Validación rápida pasa |
| B-05 | Estado ejecutable de fase | Cada fase deja inputs, outputs, gates, errores y siguiente acción | Traza mínima + estado recuperable |
| B-06 | Modo recuperación | Si una fase falla, el siguiente agente sabe dónde retomar | Contexto de failure reproducible |

### 7.5 FASE C: Prospección inmediata y venta asistida por agentes

**Cambio de secuencia.** La prospección **no espera** a la robustez agente: el gancho es actividad **pre-contrato** — no entrega un diagnóstico certificado, entrega una hipótesis de fuga para abrir conversación. Puede correr desde la semana 1, en paralelo a FASE T. Lo que sí está gateado por el acta es la **escala de entregas** (T6).

Dependencia: C-01 a C-03 no tienen dependencia. C-04 en adelante requiere que la entrega certificada exista (T1-T3).

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| C-01 | Lista ICP de 30-40 hoteles | Prospects con criterios claros y **URL propia validada** | `own_site_guard` PASS (v4.74.0 + blocklist v2) |
| C-02 | `v4complete` + `hook-pdf` sobre prospects | PDF gancho de **2 páginas** con cifra de fuga en COP, lenguaje comercial no técnico | Costo controlado (G5) + **cifra en rango si `precision_tier` B/C** (G10) |
| C-03 | Mensajes personalizados generados | Outreach con dato real, no genérico | Revisión humana antes de enviar |
| C-04 | Primer Diagnóstico Express pago | Validación de willingness-to-pay | Pago recibido |
| C-05 | Debrief estructurado | Frases reales del cliente + objeciones | Archivo de aprendizaje |

`spark` queda **retirado** del roadmap (deuda cerrada, §13.3): está marcado Deprecado en `AGENTS.md:130` y el instrumento real del gancho es `hook-pdf` (`main.py:52`).

Regla:

> El agente prepara y documenta; el humano vende y decide.

### 7.6 FASE D: Cierre de loop diagnóstico → propuesta → assets → garantía (8-12 semanas)

Dependencia: profundiza y productiza FASE 0, y se ejecuta **junto a FASE T** (T2, T3 y T5 son sub-fases de este cierre). No debe tratarse como mejora tardía.

Objetivo: convertir el pipeline en una unidad de entrega confiable, menos dependiente de intervención manual y capaz de demostrar que lo diagnosticado, lo vendido y lo entregado están alineados. Cada ejecución de cliente debe quedar como un estado recuperable y auditable, no como una secuencia de acciones olvidables.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| D-01 | E2E `v4complete` por cliente pago | Diagnóstico + propuesta + assets + gates + acta | Coherence ≥ 0.8 **y acta `APROBADO-PARA-ENTREGA`** |
| D-02 | `pain_ledger` como fuente de verdad | Brechas normalizadas con ID, fuente, severidad, confianza y estado | 100% de brechas detectadas trazables |
| D-03 | Matriz diagnóstico/oportunidad | Cada brecha aparece en el diagnóstico o queda explícitamente agrupada/justificada | No silent drop |
| D-04 | Matriz propuesta → brecha → asset | Cada servicio vendido responde a brecha real y tiene asset específico | Proposal-asset alignment PASS **y bloqueante vía acta** |
| D-05 | `delivery_quality_report.json` obligatorio | QA agent-first post-generación sobre `output/v4_complete` | PASS antes de ZIP/publicación |
| D-06 | Kit de entrega profesional | ZIP + README + **acta de revisión** + evidencia resumida + reporte de calidad | Cliente puede entenderlo; el acta viaja en lista blanca (§6.3) |
| D-07 | Checklist pre-envío humano | Solo excepciones, decisiones comerciales y tono final; no debugging técnico | 5-10 min máximo |
| D-08 | Registro de caso | Antes/después, hallazgo, solución, resultado | Publicable con permiso |
| D-09 | **Garantía Día 55 operativa** | Baseline Día 0 capturado en onboarding; comparación de KPIs GSC en Día 55 (impresiones, clics, posición promedio); si la mejora es menor al threshold → `CREDIT_NOTE.md` + `billing_adjustment.yaml` | `validate-guarantee` ejecutable sobre entrega real + G12 PASS |
| D-10 | **Contraste estimado vs real** | Para cada hotel con onboarding: fuga Tier B (pre) vs fuga Tier A (post) → desviación registrada | Alimenta la métrica de producto (§11.1) |

Criterio de éxito específico:

> Para cada hotel, el agente debe poder explicar automáticamente: “detectamos estas brechas, priorizamos estas oportunidades, vendemos estas soluciones, entregamos estos assets para resolverlas **y esta es la precisión con la que pudimos afirmar la cifra**”.

---

## 8. Roadmap comercial, subordinado a validación y entrega confiable

La robustez agente no reemplaza la validación comercial, pero la validación comercial tampoco debe avanzar sobre entregas inconsistentes.
El roadmap comercial se mantiene con agentes como multiplicador operativo, condicionado al primer piso: primero entrega confiable, después escala comercial.

### Distinción obligatoria: prospección vs entrega

| | Prospección (pre-contrato) | Entrega (post-contrato) |
|---|---|---|
| Qué es | Gancho: hipótesis de fuga para abrir conversación | Producto: diagnóstico certificado |
| Instrumento | `hook-pdf` + mensaje breve | Paquete completo + acta |
| Precisión exigida | Rango declarado (P7.2) | Tier A para `APROBADO-PARA-ENTREGA` |
| ¿Requiere acta? | No | **Sí, siempre** |
| ¿Puede automatizarse ya? | **Sí, desde la semana 1** | Solo tras T1-T3 en PASS |
| ¿Puede automatizarse por WhatsApp? | Sí (envío del gancho) | **No** — prohibido (§10) |

Esta distinción resuelve la contradicción entre "no automatizar WhatsApp" y "usar WhatsApp como canal de gancho": lo prohibido es automatizar **la entrega y el deploy**, no el primer contacto.

### Empaque comercial — corto plazo

Acciones factibles sin romper el foco:

1. Reposicionar iah-cli por lo que produce: **el diagnóstico de fuga de reservas directas**, no la CLI ni el equipo agéntico.
2. Preparar una capa de interacción natural — email, WhatsApp, Slack o formulario simple — para **prospección** de inmediato; para **entrega**, solo después de 3-5 diagnósticos pagos y al menos 1 implementación cerrada.
3. Mantener como diferencial explícito: trazabilidad, gates de calidad, evidencia, **acta de revisión** y coherencia diagnóstico → propuesta → assets.
4. Usar el acta como argumento de venta: "diagnóstico auditado con acta de revisión" es evidencia de rigor que el cliente puede ver.

No copiar promesas horizontales de ejecución 24/7, publicación automática multicanal, dashboard/SaaS ni personajes comerciales no anclados a workflows reales.

### Producto 1: Diagnóstico Express

Precio: fuente única `config/pricing.yaml` → `express_price`. No hardcodear aquí.

Propósito:

- validar que el hotelero paga por entender su fuga digital,
- filtrar curiosos,
- generar datos reales de objeciones,
- abrir puerta a implementación.

**Especificación de producto** (lo que hace que el entregable sea vendible y no un riesgo):

- **2 páginas** — instrumento: `hook-pdf` (`python main.py hook-pdf --output-dir output/v4_complete/`),
- hallazgo principal,
- **cifra de fuga en COP con `precision_tier` declarado; en rango si Tier B/C, nunca cifra exacta sobre dato inferido** (P7.2),
- costo de oportunidad con base de cálculo visible y cap de plausibilidad aplicado (P7.3),
- evidencia visible,
- una acción inmediata,
- propuesta de siguiente paso (onboarding para pasar de rango a cifra verificada),
- **acta de revisión cuando el Express evoluciona a entrega certificada**.

### Producto 2: Implementación SEO/AEO/GEO

Precio: fuente única `config/pricing.yaml` → tiers `boutique` / `standard` / `large`, con `floor_price` como piso y `monthly_default` como componente recurrente. Estructura comercial vigente: `evidence/Ingresos/04_Estructura_Precios.md`. No hardcodear rangos aquí — divergen de la fuente única.

Solo se ofrece a quien ya pagó o mostró intención clara.

Incluye, según confianza y datos:

- schema,
- FAQ,
- llms.txt,
- Open Graph,
- optimización GBP/GEO,
- guía de implementación,
- medición posterior (**Garantía Día 55**, D-09).

### Producto 2.5: Reporte mensual liviano de visibilidad

Precio: fuente única `config/pricing.yaml` → `monthly_default`.

No se construye como SaaS ni dashboard. Se valida primero como entregable mensual **generado por agente con revisión humana**, para clientes que ya completaron diagnóstico o implementación. "Generado por agente con revisión" no es "automático": la prohibición de §10 aplica a reportes automáticos sin revisión, no a este producto.

Hipótesis:

- score de visibilidad digital vs. benchmark regional,
- nuevas brechas detectadas desde el último reporte,
- top 3 acciones recomendadas,
- evidencia resumida desde web, GBP, benchmarks y datos aportados por el cliente.

Disparador:

- 1-3 clientes piden seguimiento después de una entrega real,
- costo por reporte mantiene margen mínimo,
- el reporte puede generarse sin que el humano reconstruya manualmente la evidencia.

### Producto 3: Seguimiento recurrente

No se vende hasta tener repetición manual.

Disparadores:

- 5+ clientes activos,
- 10+ diagnósticos entregados,
- demanda explícita de monitoreo,
- costo operativo controlado.

---

## 9. Gates de decisión

| Gate | Pregunta | Si falla |
|------|----------|----------|
| **G0: Primer piso / entrega confiable** | ¿El pipeline entrega un diagnóstico **correcto y consecuente** para un hotel real? Coherencia interna es **necesaria pero no suficiente**: un paquete puede ser autoconsistente y magníficamente erróneo. | **NO CERRADO** (2026-09-02). Score de coherencia demostrado (Castilla Real 0.8261, SalenteReal **0.88** canónico) pero **el veredicto real del paquete es `is_coherent: false`** y el gate lo ignora (§7.1); ambos son Tier B/C, sin onboarding, y SalenteReal salió con ZIP. G0 cierra solo con `evidence_tier: A` + assets ≥ 0.8 + acta `APROBADO-PARA-ENTREGA`. Bloquea la escala de entregas (T6), no la prospección |
| G1: Agent readiness | ¿Un agente fresco puede entender y ejecutar sin preguntar? | Mejorar AGENTS/workflows antes de más features |
| G2: Human minimalism | ¿El humano solo decide lo esencial? | Eliminar pasos humanos o moverlos a agente |
| G3: Evidence | ¿Cada claim comercial tiene evidencia y fuente declarada? | Bloquear entrega o marcar ESTIMATED |
| G4: Commercial validation | ¿Alguien pagó? | No escalar automatización comercial |
| G5: Cost control | ¿API/cómputo mantiene margen mínimo por diagnóstico? | Activar `permission_mode`, reducir llamadas, usar fallback barato o revisar precio antes de escalar |
| G6: Delivery coherence | ¿Diagnóstico, oportunidad, propuesta y assets cuentan la misma historia? | Bloquear publicación |
| G7: Brecha coverage | ¿Todas las brechas detectadas aparecen, se agrupan o se justifican explícitamente? | Reabrir diagnóstico antes de generar ZIP |
| G8: Asset specificity | ¿Cada asset resuelve un problema real del hotel y no es plantilla genérica? | Marcar `GENERIC_DRAFT` o regenerar |
| G9: Documentation drift | ¿Docs críticas reflejan realidad actual? | Ejecutar docs cascade / doctor |
| **G10: Precisión (P7)** | ¿La cifra de fuga es **verosímil** para este hotel y declara su `precision_tier`? ¿Pasó el cap de plausibilidad? | **Renderizar rango, nunca cifra exacta.** Si excede el techo plausible, rechazar la cifra y recalcular. G3 no cubre esto: una cifra puede tener fuente y estar cientos de veces desviada |
| **G11: Acta de revisión** | ¿Existe `acta_revision.md` certificando las 6 cláusulas P6 + P7? | **No se entrega.** No es que los gates sean advisory (los 13 bloquean hoy, §6.4): es que **ninguna capa agrega las 6 cláusulas como un todo**, y P6.3 no es verificable desde el artefacto (`asset_path: null`). El acta cierra ambos |
| **G12: Garantía medible** | ¿La Garantía Día 55 puede medirse: baseline Día 0 capturado y deploy verificado en producción? | **No se promete garantía.** Una promesa unverificable es pasivo comercial, no argumento de venta |

**Veredictos del Juez (T1) y su correspondencia con `PublicationState`** (`modules/quality_gates/publication_state.py:14-27`). ⚠️ **El módulo está huérfano**: no tiene ningún importador fuera de sí mismo (verificado 2026-09-02), igual que `coherence_gate.py`. Esta tabla es una correspondencia *de diseño*; para que tenga efecto hay que darle llamador real, y ese es el mismo anfitrión que debe elegirse antes de T1 (§7.2).

| Veredicto del acta | Estado existente | Nota |
|---|---|---|
| `APROBADO-PARA-ENTREGA` | `READY_FOR_CLIENT` | Mapeo directo |
| `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | **sin estado propio** | `REQUIRES_REVIEW` es lo más cercano, pero su semántica documentada es "solo soft conflicts/warnings", no "tier insuficiente". Decisión pendiente: nuevo estado o mapeo explícito con regla de transición (deuda de producto #P5) |
| `DEVOLVER-CORRECCIONES` | `DRAFT_INTERNAL` | Mapeo directo |
| `BLOQUEADO` | `BLOCKED` | Mapeo directo |

---

## 10. Qué NO hacer por ahora

No construir:

- SaaS multiusuario,
- dashboard web completo,
- marketplace de skills,
- sistema comunitario de builders,
- PMS integration,
- multi-idioma,
- **entrega ni deploy automatizados por WhatsApp** (el **gancho de prospección** por WhatsApp sí está autorizado: es pre-contrato, ver §8),
- reportes recurrentes **automáticos sin revisión humana** (el reporte mensual agent-generated con revisión, Producto 2.5, sí está autorizado),
- ecosistema de skills extensible por terceros,
- verticales fuera de hotelería,
- cualquier feature cuyo criterio de éxito sea "la plataforma hace más cosas" en vez de "el diagnóstico es más correcto".

Hasta que existan señales:

- G0 cerrado: **diagnóstico en Tier A con acta `APROBADO-PARA-ENTREGA`** para entregas reales,
- 3-5 Express pagos,
- 1 implementación cerrada,
- 5+ debriefs reales,
- objeciones repetidas,
- flujo de entrega confiable repetido 10 veces,
- **tasa de error del producto medida y dentro de umbral** (§11.1, D-10).

---

## 11. Métricas

### 11.1 Métricas de producto — ¿qué tan bueno es el diagnóstico?

Estas son las métricas que el principio rector exige. Sin ellas no se puede afirmar que el producto funciona.

| Métrica | Umbral | Objetivo | Fuente |
|---------|--------|----------|--------|
| Diagnósticos con `precision_tier` A (cifra exacta permitida) | ≥ 30% | ≥ 70% | `quality_metadata` del MANIFEST |
| **Desviación fuga Tier B (estimada) vs Tier A (real post-onboarding)** | ≤ 3x | ≤ 1.5x | D-10 — la métrica del caso Luxor (~630x) |
| Cifras de fuga que pasan el cap de plausibilidad | 100% | 100% | `PrecisionValidator` + P7.3 |
| Paquetes entregados con `acta_revision.md` | 100% | 100% | T1 / G11 |
| Paquetes Tier B/C que recibieron `APROBADO-PARA-ENTREGA` | **0** | **0** | T1 / G0 — invariante, no objetivo |
| Garantías Día 55 medidas / créditos emitidos | 100% medidas | < 20% créditos | `validate-guarantee` / G12 |
| `hook-pdf` con cifra defendible (rango declarado si B/C) | 100% | 100% | G10 |

### 11.2 Métricas de aseguramiento — ¿el producto es consecuente?

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Outputs con evidencia rastreable | 90% | 95%+ |
| Brechas detectadas cubiertas o justificadas | 95% | 100% |
| Servicios vendidos con asset específico | 90% | 100% |
| Assets marcados correctamente (`VERIFIED`/`ESTIMATED`/`CONFLICT`/`GENERIC_DRAFT`) | 95% | 100% |
| Cláusulas P6 certificadas **como un todo** (acta agregada) | 0/6 hoy — los 13 gates bloquean por separado, nadie agrega | 6/6 tras T1 |

### 11.3 Métricas comerciales

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Entrevistas de validación | 3 | 5 |
| Prospects ICP-filtrados y con URL propia validada | 20 | 40 |
| Mensajes personalizados enviados | 20 | 40 |
| Conversaciones comerciales reales | 2 | 5 |
| Diagnósticos Express pagos | 1 | 5 |
| Clientes de implementación | 0 | 1 |
| Debriefs documentados | 1 | 5 |

Las métricas de salud operativa del ecosistema (workflows sincronizados, validaciones rápidas, docs sin drift, tiempo humano pre-envío) **no se listan aquí**: viven en `.agent/SYSTEM_STATUS.md`, regenerable con `python scripts/doctor.py --status`. Este cuadro solo lleva lo que mide producto y aseguramiento.

---

## 12. Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **La cifra de fuga está magníficamente equivocada (benchmark vs realidad) y destruye la credibilidad en la primera reunión — el producto pasa a ser "tecnología de IA sin valor medible"** | **Alta** | **Crítico** | **P7 completo: `precision_tier` declarado, render en rango para Tier B/C, cap de plausibilidad, onboarding como precondición comercial (T3), G10. Evidencia del riesgo: caso Luxor ~630x** |
| El producto se describe y vende como plataforma/herramienta de IA en vez de como diagnóstico | Media | Alto | Principio rector encabezando este documento; §1.1, §2.2, §8 y §15 alineados; criterio explícito en §10 |
| Outputs estimados se venden como verificados | Media | Alto | Taxonomía VERIFIED/ESTIMATED/CONFLICT obligatoria + Bot 4 (T4) sobre los **12 `CG-*` reales repartidos en dos archivos** (§7.2) |
| El paquete sale `READY_FOR_PUBLICATION` con **`is_coherent: false`** y ZIP: el gate de publicación lee solo `overall_score` e ignora el veredicto real | **Crítica** | Crítico | §7.1 hallazgo bloqueante; T0.4 corrige el gate antes de T1; G11 acta agregada. Verificado sobre la corrida real SalenteReal 2026-08-31 |
| Ninguna capa certifica las 6 cláusulas P6 como un todo, y P6.3 no es verificable desde el artefacto (`asset_path: null`) | **Alta** | Alto | §6.4 tabla con severidad verificada; G11 acta bloqueante; no afirmar el cumplimiento hasta T1 |
| Brechas detectadas desaparecen del diagnóstico final | Media | Alto | Coverage gate y `pain_ledger` obligatorio |
| Propuesta promete servicios que los assets no materializan | **Alta — ya ocurre** | Alto | La matriz **ya bloquea** (`proposal_asset_alignment`), pero 6 de 7 servicios prometidos responden a pains **no detectados** y caen en `NO_BREACH`, que el gate excluye por diseño; además `asset_path: null` impide verificar la ruta (§6.4, §7.2 causa raíz). Mitigación real: propuesta dinámica + acta del Juez |
| Assets genéricos erosionan confianza del cliente | Media | Alto | Asset specificity gate + etiqueta `GENERIC_DRAFT` + Bot 3 (T2) |
| Se promete la Garantía Día 55 sin poder medirla (deploy en `dry_run`) | Alta | Alto | G12; deuda de producto #P1 |
| El repo acumula documentación humana que los agentes no usan | Alta | Alto | AGENTS/workflows como fuente operativa primaria |
| El humano vuelve a ejecutar pasos manuales largos | Alta | Alto | Convertir procedimientos en workflows/gates |
| Agentes ejecutan sin suficiente contexto | Media | Alto | Contexto global + bucles de fase con estado, criterios de continuación y handoff definidos |
| Drift entre docs, código y outputs | Alta | Alto | Doctor, validation scripts, docs cascade, y §3: ROADMAP no replica datos sincronizables |
| Hoteleros no pagan por diagnóstico | Alta | Alto | Validación Express antes de automatizar más |
| Costos API/modelo erosionan margen del Diagnóstico Express | Media | Alto | Presupuesto máximo por diagnóstico, margen mínimo, `permission_mode`, fallback barato y revisión de precio antes de escalar |
| Se construye UI antes de tracción | Media | Alto | Gate explícito: no UI pesada hasta 10+ entregas manuales |
| Se automatiza la escala antes de que el diagnóstico sea correcto | Media | Alto | Marco AOA: T6 gateado por T1-T3; §10 exige G0 cerrado y tasa de error medida |

---

## 13. Deuda técnica estratégica

### 13.1 Deuda de producto (la que afecta lo que se vende)

1. **P1 — Deployer en MVP v2.5, `dry_run` por defecto.** FTP `upload_file` e `inject_code` devuelven "no disponible en v2.5 MVP"; WP `inject_code` requiere plugin no ejecutado; solo `create_post` funciona y genera draft. Consecuencia directa: `site_verification_applied: false` en entregas reales y **la Garantía Día 55 no puede medirse** → G12 no puede pasar. Fuente: `modules/deployer/connectors/`. Se resuelve en T5.
2. **P2 — `IMPLEMENTATION_ORDER.md` vacío en entregas reales.** Causa raíz: `AssetResponsibilityContract.generate_delivery_template()` (`modules/geo_enrichment/asset_responsibility_contract.py`) y `modules/delivery/generators/implementation_order_gen.py` cuando no reciben `core_assets`/`geo_assets` explícitos. Independiente del tribunal; se arregla primero en T5.
3. **P3 — CMS del cliente no detectado de forma confiable.** `DeployInstructionsGenerator` escribe guías para WordPress, Wix, Squarespace y genérico, eligiendo desde `hotel_data.cms_detected`; sin CMS capturado, ni la guía ni el deploy pueden ser correctos.
4. **P4 — No existe contraste entre fuga estimada y fuga real.** El pipeline produce ambos números cuando hay onboarding (Tier B pre, Tier A post) y nadie los compara. Sin esto el producto **no puede conocer su propia tasa de error** ni mejorar sus benchmarks. Es la deuda de mayor valor relativo: barata de instrumentar y es la única que convierte "creemos que el diagnóstico es bueno" en "sabemos cuánto se desvía". Se resuelve en D-10.
5. **P5 — `PublicationState` no tiene estado para `APROBADO-CONDICIONAL-PENDING-ONBOARDING`.** Los 4 estados existentes (`READY_FOR_CLIENT`, `DRAFT_INTERNAL`, `REQUIRES_REVIEW`, `BLOCKED`) no cubren el veredicto más frecuente del primer piso. Decidir: estado nuevo o mapeo con regla de transición explícita (§9).
6. **P6 — El acta no tiene vía de entrada al ZIP del cliente.** `modules/delivery/delivery_packager.py:337` excluye reports internos por prefijo, sin distinguir "tripas del pipeline" de "certificado del producto". Requiere lista blanca explícita (§6.3, D-06).
7. **P7 — Resolver G0 completo.** Los assets en `ESTIMATED` por falta de `hotel_data` requieren onboarding real para alcanzar ≥ 0.8 confidence. Es la última milla del primer piso y depende de datos, no de código. Se resuelve en T3.
8. **P8 — Endurecer G8 para nuevos tipos de hotel.** El `DataDerivationLayer` cubre 5 derivaciones del audit estándar; hoteles con estructuras atípicas pueden necesitar derivaciones adicionales.
9. **P9 — El gate de publicación ignora `is_coherent`.** `publication_gates._coherence_gate` decide con solo `coherence_score >= threshold`; `coherence_gate.py`, que sí usa `passed = report.is_coherent`, no tiene llamador de producción. Consecuencia verificada: la corrida SalenteReal 2026-08-31 salió `READY_FOR_PUBLICATION` con ZIP y los cuatro artefactos en `is_coherent: false`. **Es la deuda de producto más grave abierta**: el sistema certifica coherencia que su propio reporte niega. Condición previa a T1 (§7.2 T0.4).
10. **P10 — Seis registros de identidad de servicios, ninguno canónico.** `service_catalog` 8 (config) · `PROPOSAL_SERVICE_TO_ASSET` 7 (`proposal_asset_alignment.py:22-33`) · `ASSET_CATALOG` 25 · `PAIN_SOLUTION_MAP` 22 mapeables · runtime 4 · contract registry 3 CORE + 3 GEO. `ALL_PROMISED_SERVICES` (`:45`) hace que el de 7 mande sobre el de 8 mientras el comentario de `:35-37` dice "All 8". **Decidir cuál manda es precondición de la propuesta dinámica**, que es la única palanca que cierra a la vez `no_breach = 6/7` e `is_coherent = false` (§7.2 causa raíz).
11. **P11 — `precision_tier` degrada en silencio.** `main.py:2149-2167` inicializa en `"C"` y envuelve la llamada al validador en `try/except Exception: pass`: un fallo deja Tier C **sin señal**, y Tier C es justo el valor que P7 usa para decidir el render. Repite el patrón del NameError invisible del gate `tier_c`. P7.1 no es auditable hasta registrar el motivo.

### 13.2 Deuda de herramienta (la que afecta cómo se produce)

1. **H1 — Reducir duplicación entre README, AGENTS y docs.** README debe ser humano-mínimo; AGENTS debe ser agente-operativo.
2. **H2 — Fortalecer recuperación de fases fallidas** para agentes en sesiones frescas: cada fallo debe dejar estado, causa probable, artefactos tocados y siguiente acción segura.
3. **H3 — Formalizar smoke test de agent-readiness:** un agente nuevo debe poder entender estado, ejecutar validación, explicar siguiente acción y retomar desde bucles de fase con estado, criterios de continuación y handoff definidos.
4. **H4 — Unificación total de taxonomía de fuentes y contrato de tipos del payload del harness.** El plan BUGS-ONBOARDING-ADR-2026-07-22 aplicó la Opción C (3 bugs puntuales + CTAs centralizados en `_build_onboarding_cta`), pero los 3 vocabularios incompatibles (`ADRSource` enum, `ValidationSummary.sources`, `JSON adr_source`) siguen existiendo. `build_validated_field(name, value, source)` centralizado y migración del payload a `TypedDict`/dataclass quedan pendientes. Riesgo: un nuevo campo validado puede cometer el mismo error por construcción. Nota: esta deuda **toca producto**, porque la fuente de un dato determina su `precision_tier` (P7.1). Fuente: `.opencode/plans/BUGS-ONBOARDING-ADR-2026-07-22/01-plan-maestro.md` §9.
5. **H5 — Mantener ROADMAP como documento estratégico manual**, fuera de cascadas automáticas salvo solicitud explícita. Verificado: no participa en `scripts/sync_versions.py` ni en `scripts/validate_document_integration.py`. §3 depende de esta decisión. **Restricción conocida:** `scripts/validate_agents_md.py:170-187` exige que este archivo mencione `pain_ledger`, `delivery_quality_report`, `human_checklist` y `data_derivation_layer` — preservar esos nombres en §7.1.
6. **H6 — Preservar el análisis Enrich Labs como evidencia de mercado, no como modelo de producto.** Fuente: `.opencode/context/roadmap-enrichlabs-vertical-hotels-strategy.md`. Su valor es demostrar que existe mercado para agentes especializados; **no** define hacia qué debe evolucionar iah-cli (§2.2).
7. **H7 — Artefactos timestamped sin índice.** `gate_report_<ts>.json` y `financial_scenarios_<ts>.json` no tienen nombre fijo ni manifiesto que resuelva cuál pertenece a la corrida; `pain_ledger.json` no serializa `assets`, así que la matriz no es reproducible desde disco. Todo revisor externo (incluido el tribunal) necesita un paso de resolución de nombres antes de leer. Bloquea la regla "el tribunal lee outputs" (§7.2).
8. **H8 — Módulos huérfanos.** `publication_state.py` (sin importadores fuera de sí mismo) y `coherence_gate.py` (sin llamador de producción) implementan exactamente lo que el pipeline necesita y no está conectado. `two_phase_flow.py` solo se usa por sus tipos. Decidir por módulo: **conectar o eliminar**. Un módulo huérfano que parece vivo es peor que uno ausente, porque los planes lo citan como si funcionara.
9. **H9 — Tres rutas de bloqueo del ZIP y un kill switch sin auditar.** `main.py:3194` (FAIL o `_claim_escalated`), `:3205`, `:3274`, más `GATE_BLOCKING_ENABLED` (`:2990-2992`, default `true`). Converger en un único punto de decisión antes de que T1 añada el suyo; auditar el kill switch, que hoy permite desactivar todo el bloqueo por variable de entorno sin dejar rastro.
10. **H10 — Corregir el docstring de `publication_gates.py:4` y `:162` hacia 11 blocking + 2 advisory**, no al revés: el código nunca implementó la distinción que promete (`check_publication_readiness` bloquea con los 13). El mismo error está en `AGENTS.md` (tabla Módulos Activos y bloque FASE 4.5). Patrón a copiar: `commercial_gate.py:99-113`. **No tocar `delivery_quality_report.py:289` `BLOCKING_GATE_NAMES`** — rige el ZIP, es régimen de delivery, no de publicación.

### 13.3 Cerradas en la revisión v4.0 (2026-09-02)

- **`spark`**: retirada del roadmap. Marcada Deprecado en `AGENTS.md:130`; el instrumento del gancho es `hook-pdf`. La condición "mantenerla solo si se usa comercialmente 10+ veces" quedó resuelta en los hechos.
- **"Consolidar `.agents/workflows/` como capa ejecutable"**: sin objeto. Queda 1 workflow activo tras el archivado del 2026-08-24.
- **"Monitorear discoverability agent-to-agent/MCP"**: demorada sin fecha. Hacer la herramienta consumible por otros agentes la expone como producto, dirección opuesta al principio rector. Se reevalúa solo si un cliente pide integración explícita.
- **"Elevar el QA post-generación a contrato nativo"** y **"consolidar `delivery_quality_report.json` como evidencia obligatoria"**: resueltas en FASE-0 / FASE-0E. La deuda resuelta se borra de la lista, no se archiva tachada dentro de ella.

---

## 14. Visión 12-24 meses

Solo se activa si el modelo comercial valida. Se nombra **H** (horizonte) para no colisionar con las sub-fases **T** de FASE T.

### H1: Agentic delivery engine

iah-cli entrega diagnósticos y assets de forma confiable con mínima intervención humana.

Disparador:

- 5+ diagnósticos pagos,
- 1+ implementación cerrada,
- flujo E2E repetible con acta.

### H2: Monitoring recurrente

Agentes revisan periódicamente hoteles activos y generan reportes comparables, con revisión humana antes de enviar.

Disparador:

- 5+ clientes activos,
- solicitud explícita de seguimiento,
- costo controlado,
- G12 pasando (garantía medible).

### H3: Motor de precisión — grafo de hoteles y benchmarks

**Es el horizonte de mayor valor bajo el principio rector, y su justificación es de producto, no de plataforma.** El aprendizaje agregado desde `pain_ledger` existe para **subir el `precision_tier` de los diagnósticos sin depender de que cada hotel entregue sus datos operativos**. Ataca la causa raíz del caso Luxor: hoy un hotel sin onboarding cae a benchmark grueso y la cifra se dispara; con benchmarks regionales finos por tipo de hotel, el Tier B se vuelve defendible.

Objetivos, en orden de valor:

- **mejorar benchmarks y recomendaciones sin depender de intuición manual** (efecto directo sobre P7),
- detectar brechas recurrentes por región y tipo de hotel,
- convertir diagnósticos repetidos en inteligencia comercial reutilizable,
- preservar privacidad mediante agregación, anonimización y permiso explícito de uso.

Disparador:

- 20+ hoteles activos o diagnosticados con permiso de uso agregado,
- tasa de error del producto (D-10) medida en al menos 10 casos.

No se construye como capa de producto visible ni como grafo expuesto al cliente: es infraestructura de precisión.

---

## 15. Resumen ejecutivo

iah-cli vende un diagnóstico: cuánto dinero pierde un hotel por reservas directas fugadas, con la precisión con que esa cifra puede afirmarse y los assets que la recuperan.

Todo lo demás en este documento — agentes, gates, workflows, harness, actas, tribunal — es el medio para que ese diagnóstico sea **correcto, defendible y reproducible**. Ninguno de esos componentes es el producto, y ninguno debe volverse visible para el cliente salvo cuando certifica el hallazgo: el acta viaja porque es el certificado del diagnóstico, no porque exhiba la arquitectura.

El humano debe quedar en las decisiones de mayor valor:

- qué cliente perseguir,
- qué riesgo aceptar,
- qué dato confirmar,
- qué propuesta enviar,
- qué aprendizaje comercial incorporar.

El agente debe encargarse del resto:

- investigación,
- ejecución,
- validación,
- documentación,
- coherencia,
- trazabilidad,
- mantenimiento.

La secuencia no es negociable y se resume en el marco AOA: **auditar** el paquete antes de optimizarlo, **optimizar** su precisión con datos reales antes de automatizar su entrega, y **automatizar** solo lo que ya fue aprobado. Escalar sobre un diagnóstico no certificado no acelera el ingreso: lo destruye, porque convierte la primera reunión comercial en la prueba de que la cifra no se sostiene.

Principio final:

> iah-cli vende un diagnóstico defendible sobre la fuga de reservas directas de un hotel. Los agentes, gates y actas son el medio para que ese diagnóstico sea correcto y verificable — no el producto.
