# ROADMAP iah-cli — El diagnóstico es el producto, y se implementa

> **Principio rector**: iah-cli es una **herramienta de diagnóstico**, no una herramienta de IA que se vende por sí misma. El producto es un hallazgo defendible sobre la fuga de reservas directas de un hotel; los agentes, gates y actas son el medio para que ese hallazgo sea correcto y verificable, nunca el objeto de venta. La promesa comercial incluye **implementación gestionada**: los assets contratados se instalan y verifican bajo responsabilidad del operador, no se delegan al hotel sin contrato de alcance.
> **Versión roadmap**: v4.3 (2026-09-21) — reestructurado bajo el principio rector (v4.0), corregido contra artefactos reales (v4.1), completado con tramos de FASE T y agujeros vivos (v4.2), **actualizado contra la sesión 2026-09-21** (v4.3): Tribunal implementado con enforcement observado en corridas reales, implementación gestionada incorporada a Producto 2, y estados/deudas re-anclados con fecha de última verificación.
> **Regla de evidencia de este documento**: ninguna afirmación sobre el estado del pipeline se escribe aquí sin estar verificada contra código o artefactos de una corrida real. Lo verificado en esta revisión lleva fecha 2026-09-21; lo no revalidado se marca **[sin revalidar]** con su fecha anterior. Verificar citas de código **no** verifica premisas.
> **Qué añade la v4.3** (verificado el 2026-09-21 salvo marca contraria): **(1)** FASE T tramo offline **implementado y certificado** (planes `TRIBUNAL-OFFLINE-2026-09-09` y `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`, release v4.77.0; enforcement con dientes observado en P4 2026-09-14 y TAREA7 2026-09-19). **(2)** **Implementación gestionada** incorporada a Producto 2 con contrato de alcance, aprobación y verificación post-cambio; `site_verification_applied` re-anclado a su productor real (`len(self.skipped_assets) > 0`, `modules/asset_generation/v4_asset_orchestrator.py:168`) — **no acredita instalación**. **(3)** Evidencia nueva: TAREA7 (`READY_FOR_PUBLICATION` + 13/13 gates + veredicto `BLOQUEADO` + `EXIT=0`), corrección offline AC20 (aprobación condicional en contrafactual, E2E pendiente), techo Tier B/B+ por analítica ausente (AC-O0). **(4)** Deuda **P6 cerrada por decisión de diseño** (acta excluida del ZIP); P2 parcialmente trabajada por AC10; H7 parcialmente cerrada (snapshot de presencia persistido); H9 parcialmente cerrada (escape del enforcement declarado en el acta). **(5)** Referencias históricas rotas corregidas (`context/Historico/`, `plans/Archives/`).
> **Estado del proyecto**: fuente única `VERSION.yaml`. Estado operativo regenerable: `python scripts/doctor.py --status` → `.agent/SYSTEM_STATUS.md`. Este documento no replica datos sincronizables (ver §3) y se edita manualmente (H5).
> **Convergencia**: "calidad antes que escala" no compite con el principio rector — lo garantiza. La automatización existe para que el diagnóstico sea reproducible, defendible e instalable sin ambigüedad.
> **Marco AOA**: **A**udita (tribunal) → **O**ptimiza (acta + onboarding) → **A**utomatiza (implementación + escala). Nada se instala sobre un paquete que el Juez no haya aprobado, y nada se declara instalado sin comprobación posterior.
> **Horizonte operativo**: 30 días para el primer ingreso (prospección, en paralelo); 90 días para el primer piso cerrado (entrega certificada + primera implementación gestionada verificada). Se reevalúa semanalmente durante validación comercial y quincenalmente después.

---

## 1. Norte estratégico

### 1.1 El producto

iah-cli vende **un diagnóstico**: la cuantificación defendible de la fuga de reservas directas de un hotel, expresada en COP, con su nivel de precisión declarado, un paquete de assets técnicos que la recupera y, contratada aparte, su **implementación gestionada** en el sitio del hotel.

El cliente compra un hallazgo y su materialización, no software. La herramienta es invisible para él. Lo que evalúa es si la cifra es creíble, si la evidencia la sostiene, si la acción propuesta la recupera y si los cambios quedaron realmente aplicados.

Cadena de estados que este roadmap mantiene separadas en todos sus contratos:

> **Generado ≠ aprobado ≠ instalado ≠ verificado ≠ resultado comercial observado.**

De esta definición se derivan los atributos que el roadmap gobierna:

| Atributo | Pregunta que responde | Principio que lo rige | Gate que lo verifica |
|---|---|---|---|
| **Corrección** | ¿La cifra de fuga es verosímil para *este* hotel? | P7 | G10 |
| **Defensibilidad** | ¿Cada claim tiene fuente, confianza y acta que lo certifique? | P3 + P6 | G3, G11 |
| **Consecuencia** | ¿Diagnóstico, propuesta y assets cuentan la misma historia? | P6 | G6, G7, G8 |
| **Materialización** | ¿Lo prometido quedó instalado y comprobado en el sitio correcto? | T5 / §8 | G0, G12 (verificación post-cambio) |

### 1.2 La forma de producirlo

iah-cli evoluciona como sistema agent-first cuyo propósito es producir diagnósticos correctos, defendibles, reproducibles e implementables. La interfaz humana es esencial y mínima:

1. Configurar credenciales, permisos y accesos delegados del hotel.
2. Lanzar objetivos de negocio: diagnosticar, auditar, entregar, implementar.
3. Proveer datos que no pueden inferirse con confianza: ADR real, habitaciones, ocupación, canal directo, WhatsApp confirmado, políticas y servicios.
4. Aprobar operaciones con costo, riesgo o impacto externo (incluido cada cambio en el sitio del cliente).
5. Revisar entregables comerciales antes de enviarlos al cliente.

Todo lo demás debe ser responsabilidad de agentes bajo el operador. Frase guía:

> El humano define intención y límites; el agente transforma esa intención en ejecución verificable.

Prioridad estratégica:

> No se construye el segundo piso si el primero no está construido. En iah-cli, el primer piso es la entrega confiable al cliente: diagnóstico **correcto**, oportunidad coherente, propuesta consecuente, assets específicos y su instalación verificada.

Antes de escalar automatización comercial, outreach, monitoreo recurrente, UI, nuevos módulos o expansión del producto, el pipeline debe demostrar que puede entregar una solución autoconsistente, verosímil e instalada para un hotel real.

---

## 2. Clasificación del repositorio

### 2.1 Lo que iah-cli ya es

| Capa | Rol bajo el principio rector | Estado actual (2026-09-21) | Orientación futura |
|------|------------------------------|---------------|-------------------|
| **Producto: el diagnóstico** | **Lo que se vende** | Fuga cuantificada + propuesta + assets + acta; techo real Tier B/B+ sin analítica | Gobernado por P7 + G10; certificado por acta; Tier A exige GA4+GSC verificados (`modules/financial_engine/scenario_calculator.py:508`) |
| Outputs comerciales | Envase del producto | Diagnóstico, propuesta, assets, delivery zip con cuarentena, `hook-pdf` | Mantener como lo único que el cliente ve |
| Implementación en sitio | Extensión del servicio | **MVP**: WP crea posts borrador; FTP no conecta; sin aprobación/hash/rollback binding (§13 P1) | Contrato de implementación gestionada (T5 + Refuerzo §3.3) |
| CLI humana | Interfaz de lanzamiento | `setup`, `v4complete`, `v4audit`, `onboard`, `execute`, `deploy`, `hook-pdf`, `validate-guarantee`, `--doctor` | Mantener mínima y estable |
| Agent Harness | Medio de producción | Memoria, routing, handlers, timeout, skill execution; `v4complete` se ejecuta principalmente desde `main.py` (`:1462`, `:1663`, `:1757`) | Convertir en núcleo operativo sin duplicar contratos |
| Tribunal `modules/quality_gates/tribunal/` | Certificación de entrega | **Operativo**: Juez determinista + 4 revisores + acta dual + cuarentena O1 + enforcement (`main.py:3345`, `judge.py:464`) | Ampliar cláusulas certificables; no duplicar gates |
| Workflows `.agents/workflows/` | Contrato de ejecución | **1 workflow activo** (`phased_project_executor.md`); los 16 anteriores archivados el 2026-08-24 | Mantener como contrato, no como ecosistema |
| Documentación técnica | Contexto de agente | Abundante pero dispersa | Navegación de agentes + resumen humano |
| Mantenimiento | Salud del medio | Doctor, validations, registry, version sync | Automático y obligatorio para agentes |

### 2.2 Conclusión de diseño

El repo debe tratar a los humanos como operadores estratégicos y validadores, no como ejecutores paso a paso.

Interpretación comercial deseada:

> El mercado paga por **hallazgos accionables y aplicados**, no por plataformas. iah-cli no aspira a ser una plataforma horizontal ni un equipo agéntico genérico: aspira a producir el diagnóstico más defendible del mercado hotelero vertical y a dejarlo instalado, y esa es su ventaja diferencial — trazabilidad, gates de calidad, evidencia, acta de revisión, coherencia diagnóstico → propuesta → assets e instalación verificada.

Por tanto:

- No priorizar una UI compleja.
- No multiplicar documentación narrativa para humanos.
- No hacer que humanos sigan procedimientos largos si un agente puede ejecutarlos.
- No vender la herramienta: vender el hallazgo y su implementación.
- Sí mantener comandos CLI simples, seguros y explicables.
- Sí fortalecer AGENTS.md, workflows, gates, doctor, memoria, evidencia y validaciones.
- Sí traducir capacidades internas en lenguaje comercial **solo cuando describan el diagnóstico y su implementación**, no cuando exhiban la arquitectura.

---

## 3. Estado actual

ROADMAP es un documento estratégico y **no se sincroniza automáticamente** (deuda de herramienta #H5: decisión explícita). Por eso no replica datos que ya tienen fuente autorizada — cada snapshot copiado es un desfaso garantizado.

| Qué se necesita | Fuente autorizada | Cómo obtenerlo |
|---|---|---|
| Versión, codename, release date | `VERSION.yaml` | lectura directa |
| Estado operativo (módulos, conteos, validaciones, tests) | `.agent/SYSTEM_STATUS.md` | `python scripts/doctor.py --status` |
| Historial de fases, entregables y claims verificados | `CHANGELOG.md` + `.opencode/plans/` | lectura directa |
| Precios, tiers y pisos vigentes | `config/pricing.yaml` | lectura directa |
| Gates de publicación y su severidad | `modules/quality_gates/publication_gates.py` (docstring) | lectura directa |
| Workflows activos | `.agents/workflows/` | `ls` |
| Pipeline comercial y prospectos | `evidence/Ingresos/` | lectura directa |
| Contexto de refuerzo y prioridades de sesión | `.opencode/context/Refuerzo.md` | lectura directa |

**Regla**: si un dato puede desfasarse, no vive aquí; vive en su fuente y este documento la referencia.

Lo que sí pertenece al ROADMAP es el **estado del primer piso** (§7.1), el **estado de FASE T** (§7.2), el **estado de los gates de decisión** (§9) y el **contrato de implementación** (§8, Producto 2).

---

## 4. Principios de evolución

### P1. Agent-first, human-minimal

Cada nueva capacidad debe responder primero:

- ¿Puede ejecutarla un agente con contexto suficiente?
- ¿Puede verificarse automáticamente?
- ¿Puede dejar evidencia auditable?
- ¿Puede reanudarse en otra sesión?

El criterio no es "automatizar más", sino codificar contratos ejecutables: estado antes/después, artefactos fuente de verdad, gate que valida el resultado, evidencia para reanudar. Los bucles definen criterios de avance, reintento, fallo y handoff humano; no dependen de instrucciones aisladas. Solo después se pregunta qué mínimo necesita decidir un humano.

### P2. Humanos no deben cargar contexto operativo

El humano no debe recordar qué workflow usar, qué validación corre primero, qué documentación actualizar, qué gate bloquea o qué archivo es fuente de verdad. Eso vive en `AGENTS.md`, `.agents/workflows/`, `docs/CONTRIBUTING.md`, scripts de validación, doctor, registry y tests.

### P3. Todo output importante debe tener evidencia

Diagnósticos, propuestas, scores, gates, assets, cambios instalados y verificaciones deben poder responder: qué dato se usó, de dónde vino, con qué confianza, qué módulo lo generó, qué gate lo validó y qué archivo lo prueba. La evidencia vive en artefactos estructurados, no solo en narrativa.

> **P3 es condición necesaria, no suficiente.** La procedencia no garantiza la verosimilitud: una cifra puede tener fuente declarada, evidencia trazable y coherencia interna perfecta, y aun así estar desviada cientos de veces de la realidad del hotel. Ese hueco lo cierra P7. Y una salida HTTP exitosa no acredita una instalación: esa brecha la cierra T5.

### P4. Manual antes que automático, pero solo para validar mercado

Para ventas y producto comercial: manual antes que automático, específico antes que general. Para operación interna: si un agente puede hacerlo con seguridad y evidencia, no debe hacerlo manualmente el humano.

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

Los siete comandos son interfaz de producto, no de plataforma: seis producen o certifican un diagnóstico y uno habilita el resto. El despliegue sigue `deploy` con `--dry-run` por defecto y `--no-dry-run` explícito (§8).

### P6. Coherencia comercial como contrato de entrega — primer piso obligatorio

La evolución agent-first no puede limitarse a ejecutar módulos: debe garantizar que el producto final sea una solución confiable para el cliente.

Contrato mínimo:

1. Si los módulos detectan N brechas, el diagnóstico y oportunidad deben cubrir N brechas o justificar explícitamente cuáles se agrupan, descartan o aplazan.
2. Cada brecha priorizada debe mapearse a una recomendación comercial concreta.
3. Cada recomendación vendida debe tener assets correspondientes, específicos y trazables a la brecha que resuelven.
4. Ningún asset genérico se presenta como solución terminada.
5. Si faltan datos reales, el output lo declara como `ESTIMATED`, `PENDING_ONBOARDING` o `CONFLICT`.
6. La publicación o entrega se bloquea si diagnóstico, propuesta y assets se contradicen.
7. Ningún cambio se instala en el sitio del cliente sin la aprobación definida en §8.

**Operationalización (actualizada 2026-09-21):** ningún paquete sale sin **acta de revisión**; el Juez determinista existe (`judge.py`) y su veredicto consume los reportes de los 4 revisores (`_compute_verdict`, `judge.py:464-522`). Estado real de la agregación: **4 cláusulas certificables** (`T1_CERTIFIABLE_CLAUSES = P6.1/P6.3/P6.4/P6.6`, `judge.py:43`); **P6.2 y P6.5 permanecen `NOT_EVALUABLE`** (`judge.py:269-279`, verificado 2026-09-21) aunque los revisores corren y aportan hallazgos. El acta gatea el rename del ZIP (cuarentena O1) y el enforcement `GATE_BLOCKING_ENABLED` se hereda con escape declarado en el acta (`outcome.py`; verificado en `acta_revision.json` de TAREA7). P6 está **parcialmente certificado**: mejor que la fotografía de v4.2 (0/6), aún no 6/6.

### P7. Precisión del diagnóstico como atributo de producto

El diagnóstico es una medición. Una medición con procedencia perfecta y magnitud absurda es un producto defectuoso.

Reglas:

1. **Toda cifra de fuga declara su `precision_tier`** (A/B+/B/C), derivado de la granularidad epistémica de sus fuentes. La cascada vigente (`scenario_calculator.py:486-520`, verificado 2026-09-21): Tier A solo con GA4+GSC habilitados y datos verificados; **B+** con onboarding verificado sin analítica (nuevo desde TRIBUNAL-ENFORCEMENT); C con ≥2 fuentes de baja calidad; default B. ⚠️ **[sin revalidar]** El defecto de degradación silenciosa por `try/except Exception: pass` en `main.py:2149-2167` se registró el 2026-09-02; revalidar antes de usarlo como bloqueante (P11).
2. **La precisión decide la regla de render**: cifra exacta solo en Tier A; **rango + descargo** en Tier B/B+/C. Nunca cifra exacta sobre dato inferido.
3. **Toda cifra pasa por cap de plausibilidad** antes de aparecer en un documento comercial. Una fuga que excede el techo (habitaciones × ocupación × ADR × canal directo) se rechaza, no se publica.
4. **Ningún diagnóstico sin analítica verificada se presenta como entregable final sin condiciones.** Con `evidence_tier ∈ {B, B+, C}` la regla de primer piso capa el veredicto a `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (`judge.py:38`, `:450-462`).
5. **El error se mide, no se supone**: con onboarding, la fuga estimada se contrasta contra la recalculada en Tier A. La desviación es la métrica de calidad del producto (§11.1, D-10).

Evidencia del riesgo: caso Hotel Luxor — sobreestimación ~630x en un paquete que cumplía P3, G3, G6 y G7. Evidencia del techo actual: AC-O0 (2026-09-14) midió `B+` como máximo con `ga4_available=False`/`gsc_available=False`; el dueño del techo es la analítica del hotel, no el cableado.

---

## 5. Contrato de producto: quién ejecuta qué

| Actividad | Ejecutor primario | Humano interviene cuando... |
|-----------|------------------|-----------------------------|
| Diagnóstico `v4complete` | Agente / CLI | Debe aportar URL o revisar output |
| Precisión de la cifra (exacta vs rango) | Agente (`PrecisionValidator`, P7) | Nunca: es determinista |
| Auditoría de paquete (tribunal / acta) | Agente | Nunca: es determinista; solo lee el acta |
| Onboarding de datos reales | Humano asistido por bot estructurado (T3) | Solo si los datos son inconsistentes entre sí |
| Validación cruzada | Agente | Hay conflicto hard o dato dudoso |
| Generación de propuesta | Agente | Antes de enviar a cliente |
| Generación de assets | Agente | Si asset queda ESTIMATED o CONFLICT |
| **Plan de implementación (qué cambia, dónde, con qué hash)** | Agente, para aprobación del operador | **Siempre: aprueba el cambio externo** |
| **Instalación en sitio (T5)** | Ejecutor técnico bajo el operador | Aprobación previa; acceso delegado del hotel |
| **Verificación post-cambio** | Agente con comprobación fresca | Revisión de evidencia antes de dar por aceptado |
| Garantía Día 55 / nota de crédito | Agente (`validate-guarantee`) | Aprueba el crédito si se activa; nunca sobre KPIs simulados |
| Deploy | Agente con aprobación, **solo tras `APROBADO-PARA-ENTREGA`** | Hay impacto externo real |
| Mantenimiento docs | Agente | Solo si cambia estrategia o criterio comercial |
| Actualización roadmap | Humano + agente | Cambia dirección estratégica |
| Fases de desarrollo | Agente | Humano define objetivo y límites |
| Costos/API externas | Agente con permission mode | Costo/riesgo excede umbral |

Reglas comerciales de costos:

> Cada Diagnóstico Express mantiene presupuesto máximo de API/cómputo y margen mínimo esperado. El margen del servicio completo incluye **preparación de contenido, instalación, verificación y retrabajo**, no solo la generación: las tarifas teóricas o estimaciones del permission gate no sustituyen el coste observado (Refuerzo §3.5).

---

## 6. Arquitectura objetivo

### 6.1 Capa agente

Es la capa dominante **en ejecución**, subordinada al producto **en propósito**.

Componentes: `AGENTS.md` (contexto global), `.agents/workflows/` (contrato), `agent_harness/` (memoria, routing, ejecución, observación, recuperación acotada), `.agent/knowledge/DOMAIN_PRIMER.md`, `scripts/doctor.py`, `scripts/run_all_validations.py`, `docs/contributing/*`, `tests/`, y trazas/estados mínimos para reanudar sin reconstruir contexto.

Objetivo:

> Un agente nuevo en sesión fresca debe poder entender el estado del repo, elegir el workflow correcto, ejecutar una fase, verificarla y registrar evidencia sin depender de memoria humana.

Cada ejecución deja estado mínimo: objetivo, inputs, outputs, gates, errores y siguiente acción. Límites medidos que deben respetarse: la memoria del harness es historial y referencias, no checkpoint reanudable; los índices y cachés comparten archivos entre ejecuciones; la concurrencia no está demostrada como segura — mantener ejecución serial hasta medirlo.

### 6.2 Capa humana mínima

`README.md` humano-mínimo; CLI `main.py` con los 7 comandos de P5; `setup` (credenciales); `onboard` (datos reales, lo único que sube la precisión); `hook-pdf` y `validate-guarantee` (instrumentos comerciales); outputs comerciales (diagnóstico, propuesta, acta, assets, zip de entrega, evidencia de instalación).

> Un humano técnico debe poder operar el producto sin entender la arquitectura interna.

### 6.3 Capa cliente final

El cliente hotelero no opera el repo. Recibe: diagnóstico, propuesta, **acta de revisión** (certificado del producto), evidencia resumida, assets técnicos, plan de acción, evidencia de instalación y eventual reporte de seguimiento.

**Regla de visibilidad (actualizada 2026-09-21, decisión DA-P1.4):** el acta **es el certificado del producto y se comparte con el cliente desde `v4_audit/`**, pero **no viaja dentro del ZIP** (`modules/delivery/delivery_packager.py:442`, `_INTERNAL_DOC_PREFIXES = ("acta_revision",)`): empaquetar el acta pre-veredicto dentro del paquete que esa acta decide es el círculo de fe que el contrato prohíbe. Los reports internos de gates también se excluyen (`:435`). La entrega del certificado es un paso explícito del kit (D-06), no una incrustación.

### 6.4 Capa de aseguramiento de entrega confiable

Cierre del loop interno entre generación y entrega. Contratos vigentes:

| Contrato interno | Qué asegura | Evidencia esperada |
|------------------|-------------|--------------------|
| **Cifra de fuga (P7)** | Número, `precision_tier`, formato exacto/rango, cap de plausibilidad y descargo | `financial_scenarios_<ts>.json` + `quality_metadata` del MANIFEST |
| `pain_ledger` / brechas fuente de verdad | Brecha normalizada con `pain_id`, severidad, fuente y confianza | JSON rastreable en `output/v4_complete/<hotel>/` |
| Diagnóstico y oportunidad | Cobertura 1:1 o justificación explícita | Tabla brecha → impacto → oportunidad → evidencia |
| Propuesta comercial | Cada servicio vendido responde a brechas priorizadas | Matriz brecha → servicio → promesa |
| Assets | Cada asset resuelve una brecha o servicio específico | Matriz servicio → asset → archivo → confidence |
| Harness / trazabilidad | Qué se ejecutó, gates, fallos y cómo retomar | Traza mínima + logs + estado recuperable |
| Delivery gate (`delivery_quality_report`) | Bloquea entrega con brechas sin explicar o assets genéricos | `delivery_quality_report.json` PASS/FAIL |
| **Acta de revisión (T1)** | Certifica las cláusulas P6 + P7 alcanzables y fija el veredicto; gatea el ZIP | `acta_revision.json` + `acta_revision.md` |
| **Verificación post-cambio (T5, nueva)** | Los cambios aprobados quedaron aplicados en el sitio y entorno indicados | Evidencia antes/después ligada al plan de implementación y sus hashes |

Reglas obligatorias:

1. **Coverage gate**: `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`.
2. **Commercial alignment gate**: todo servicio de la propuesta mapea a brecha real, evidencia y asset.
3. **Asset specificity gate**: asset sin hotel/problema/punto de implementación queda `GENERIC_DRAFT`.
4. **Evidence gate**: todo claim fuerte con fuente declarada.
5. **Precision gate (P7)**: ninguna cifra exacta sobre dato Tier B/B+/C; cap antes de render.
6. **No silent drop**: ninguna brecha desaparece sin explicación auditable.
7. **Human review mínima**: el humano revisa excepciones y decisión comercial, no reconstruye coherencia.
8. **Install gate (nueva)**: deploy exige acta aprobatoria, hash del paquete vinculado y plan de cambios aprobado; el deployer actual **no** los exige todavía (P1).

**Mapeo cláusulas P6/P7 → estado verificado 2026-09-21** (notas de detalle de 2026-09-02 marcadas **[sin revalidar]**):

| Cláusula | Veredicto la consume | Estado |
|---|---|---|
| P6.1 cobertura de brechas | Sí (gate `critical_recall`) | Certificable; detalles de recall serializados desde AC20 (2026-09-20) |
| P6.2 brecha → recomendación | No — `NOT_EVALUABLE` (`judge.py:269`) | Revisor de alineación corre y aporta hallazgos; la cláusula no entra al veredicto |
| P6.3 recomendación → asset | Sí | Certificable vía `asset_generation_report`; revisor de assets lee el ZIP |
| P6.4 no asset genérico | Sí | Certificable |
| P6.5 datos faltantes → ESTIMATED | No — `NOT_EVALUABLE` (`judge.py:226-230`) | Reservada al revisor de honestidad; no agregada al veredicto |
| P6.6 entrega bloqueada si contradice | Sí | Certificable |
| P6 en su conjunto | Acta + cuarentena + enforcement | **4/6 cláusulas certificables**; veredicto consume `reviewer_reports` (CRITICAL verificado → `BLOQUEADO`) |

Gates blocking sin mapeo directo a cláusula: `evidence_coverage`, `financial_validity`, `critical_recall`, `ethics`, `doc_audit_consistency`, `pricing_compliance`, `asset_confidence` (y advisory `content_quality`, `proposal_asset_alignment` según docstring vigente **[sin revalidar en código]**).

Resultado esperado:

> `v4complete` entrega un paquete autoconsistente y verosímil, con acta que certifica lo certificable, y la implementación gestionada deja los cambios instalados y verificados — cada etapa con su evidencia propia.

---

## 7. Roadmap técnico

### 7.1 Estado del primer piso — FASE 0 y PIPELINE-FIX completados; enforcement observado

Detalle histórico: `CHANGELOG.md` (release 4.46.0, DELIVERY-QUALITY-RELEASE, línea ~2217) y `CHANGELOG.md` + planes para el resto.

Lo que quedó operativo y sostiene todo lo demás:

- **`pain_ledger`** (`modules/asset_generation/pain_ledger.py`) — brechas normalizadas con `pain_id`, fuente, severidad, confianza y estado; artefacto `pain_ledger.json`.
- **`delivery_quality_report`** (`modules/quality_gates/delivery_quality_report.py`) — QA post-generación; FAIL bloquea el ZIP.
- **`human_checklist`** (`modules/quality_gates/human_checklist_generator.py`) — ≤10 items derivados automáticamente.
- **`data_derivation_layer`** (`modules/asset_generation/data_derivation_layer.py`) — 5 derivaciones semánticas del audit.
- **Assessment dict bridge + fórmula `delivery_ready`** — `tier_c_onboarding_required` inyectado; `evidence_tier` propagado al MANIFEST.
- **Tribunal + cuarentena O1 + enforcement** (desde v4.77.0) — el veredicto gatea el rename del ZIP; `package_evidence` (sha256 + member_count) se registra en **ambas** ramas (publicar y suprimir; verificado en `acta_revision.json` de TAREA7 y en la remediación FASE-0 del 2026-09-20).

**Evidencia de corridas reales (2026-09):**

| Corrida | Resultado | Lección de contrato |
|---|---|---|
| FASE-P4 (2026-09-14) | `BLOQUEADO`, ZIP suprimido, 4 revisores con CRITICAL | Primera vez que los dientes mordieron en el pipeline real |
| TAREA7 (2026-09-19) | `READY_FOR_PUBLICATION` + 13/13 gates + veredicto `BLOQUEADO` (VACUOUS_RECALL) + ZIP suprimido + `EXIT=0` | **Exit 0, readiness y gates preliminares no certifican entrega** |
| FASE-0 offline (2026-09-20) | Contrafactual sobre el acta archivada: `BLOQUEADO` → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` con anotación fundada del recall | Corrección verificada **offline**; no re-aprueba archivos ni acredita instalación |

**Lo que falta para cerrar el primer piso**: onboarding real con analítica (Tier A), certificación E2E de la corrección AC20 sobre una corrida nueva, y los datos del hotel. No es más código de pipeline.

### 7.2 FASE T: Tribunal certificador — tramo offline completado; restante externo

Ancla: P6 + P7. Diseño por bot: `.opencode/context/Historico/CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §5. Planes de ejecución archivados: `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/` y `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/` (release v4.77.0; matriz de 25 ACs en `evidence/FASE-VERIFY/`).

**Regla arquitectónica inviolable (vigente)**: el tribunal **no re-ejecuta lógica de gates**; lee outputs como revisor independiente. El LLM **propone** hallazgos; el **Juez aplica veredicto determinista** (`judge.py:464`).

Componentes operativos (verificado 2026-09-21): `judge.py` (veredicto determinista, regla del primer piso con `FIRST_FLOOR_TIERS = {B, B+, C}`), `outcome.py` (DTOs: `ReviewerReport`/`CorrectiveAction`/`TribunalOutcome`/`EnforcementState`; `blocks_publish = blocks ∧ GATE_BLOCKING_ENABLED`), `acta_writer.py` (acta dual JSON+MD con enforcement, corrective_actions y package_evidence), 4 revisores que leen el ZIP en cuarentena (`.zip.tmp`), `artifact_paths.py` y `llm_extractor.py` (protocolo: el LLM propone, el Juez decide).

#### T0 — Precondiciones medidas (2026-09-02; **[sin revalidar]** contra HEAD)

Las mediciones T0.1–T0.4 (coverage_ratio como interruptor global, doble oráculo de presencia, registro de servicios, gate de coherence vs `is_coherent`) siguen siendo el orden correcto **si** sus deudas (P9/P10/P12, H7) siguen abiertas: revalidar cada una antes de ampliar la certificación del Juez. El hallazgo que las originó (SalenteReal 2026-08-31: `is_coherent: false` con ZIP publicado) es evidencia archivada con fecha; no citarla como estado actual sin re-medir.

#### Estado por sub-fase

| ID | Sub-fase | Estado (2026-09-21) | Pendiente |
|----|----------|---------------------|-----------|
| T0 | Precondiciones | **[sin revalidar]** — mediciones del 2026-09-02; P9/P10/P12 abiertas según §13 | Revalidar antes de certificar más cláusulas |
| T1 | Juez certificador | **OPERATIVO** — veredicto determinista + acta dual + primer piso (B/B+/C → condicional) + enforcement | Certificar E2E de AC20 en corrida nueva |
| T2 | Revisores mecánicos | **OPERATIVOS** — diagnóstico y assets leen el ZIP en cuarentena | Cerrar residuales P6.3 (`asset_path` en matriz **[sin revalidar]**) |
| T3 | Onboarding como precondición | **PENDIENTE (externo)** — requiere datos operativos reales de un hotel | Tier A + assets ≥ 0.8 + `APROBADO-PARA-ENTREGA` |
| T4 | Revisores de lenguaje natural | **OPERATIVOS** — alineación y honestidad con `LLMPromiseExtractor` | Agregar P6.2/P6.5 al veredicto del Juez (hoy `NOT_EVALUABLE`) |
| T5 | Implementación gestionada | **PENDIENTE (externo + código)** — ver §8 Producto 2 y §13 P1 | Conector(es) reales, aprobación/hash binding, respaldo/reversión, verificación post-cambio |
| T6 | Throughput + gancho | **PENDIENTE** — gateado por T3+T5 (AOA) | Escala con margen verificado |

#### Tramos

| Tramo | Sub-fases | Estado |
|---|---|---|
| **Offline** | T0, T1, T2, T4 | **COMPLETADO y certificado** (2026-09-15, release v4.77.0); T0 revalidable contra HEAD |
| **Externo** | T3 | Datos operativos reales de un hotel (ninguna corrida pública produce Tier A) |
| **Externo** | T5 | Accesos reales del hotel (CMS confirmado, staging, permisos) + completar conectores |
| **Externo** | T6 | T3 y T5 en PASS + URLs propias + margen verificado |

**DoD-técnico (offline)**: (a) ningún paquete sale sin acta; (b) ningún paquete sin analítica recibe `APROBADO-PARA-ENTREGA`; (d) el tribunal no duplica lógica de gates; (e) costo marginal dentro del margen. **Cumplido y certificado el 2026-09-15** (matriz 25 ACs). Pendiente de reforzar: (b) mantiene vigencia con cada cambio de tier.

**DoD-comercial (externo)**: (c) ningún deploy se ejecuta sin veredicto de aprobación **y plan de cambios aprobado**; disparador: primera implementación gestionada con instalación, reversión y verificación post-cambio evidenciadas. **No mezclar ambos Done.**

### 7.3 FASE A: Baseline de robustez agente (colapsada)

El ecosistema de 16 workflows fue archivado el 2026-08-24; queda 1 workflow activo. A-05 (validación de contexto fresco) y A-06 (higiene documental con `validate_agents_md.py` + `validate_document_integration.py`) **sin fecha de cierre registrada** — revalidar si siguen vigente antes de tratarla como pendiente o cumplida.

No construir: dashboard, UI web, wizard complejo, integración multiusuario, marketplace de skills.

### 7.4 FASE B: Ejecución de fases más confiable por agentes

Infraestructura de reproducibilidad; sin ella no hay tasa de error medible (P7.5). Evidencia parcial ya existente en planes activos (B-05/B-06: estado recuperable y modo recuperación se ejercitan en `dependencias-fases.md` y checklists de los planes vigentes).

| ID | Entregable | Gate |
|----|------------|------|
| B-01 | `phased_project_executor.md` endurecido | Plan de prueba con fase simulada |
| B-02 | Bucles de fase estandarizados (objetivo, estado, límites, criterios, gates, rollback, handoff) | Checklist validado |
| B-03 | Evidencia post-fase obligatoria | `log_phase_completion.py`; el acta cuenta como evidencia de fase |
| B-04 | Regla de no-doc-drift | Validación rápida pasa |
| B-05 | Estado ejecutable de fase | Traza mínima + estado recuperable |
| B-06 | Modo recuperación | Contexto de fallo reproducible |

### 7.5 FASE C: Prospección inmediata y venta asistida por agentes

La prospección **no espera** a la robustez agente: el gancho es pre-contrato (hipótesis de fuga para abrir conversación). Puede correr desde la semana 1, en paralelo a FASE T. La escala de entregas (T6) sí queda gateada por el acta.

Materiales vigentes: listas de prospectos y guiones en `evidence/Ingresos/` (fuente autorizada del pipeline comercial).

| ID | Entregable | Gate |
|----|------------|------|
| C-01 | Lista ICP de 30-40 hoteles con URL propia validada | `own_site_guard` PASS |
| C-02 | `v4complete` + `hook-pdf` sobre prospects | Costo controlado (G5) + cifra en rango si Tier B/B+/C (G10) |
| C-03 | Mensajes personalizados | Revisión humana antes de enviar |
| C-04 | Primer Diagnóstico Express pago | Pago recibido |
| C-05 | Debrief estructurado | Archivo de aprendizaje |

`spark` sigue retirado (§13.3). Regla:

> El agente prepara y documenta; el humano vende y decide.

### 7.6 FASE D: Cierre de loop diagnóstico → propuesta → assets → implementación → garantía

Profundiza FASE 0 junto a FASE T (T3 y T5 son sub-fases de este cierre). Objetivo: unidad de entrega confiable donde lo diagnosticado, lo vendido, lo entregado y lo instalado estén alineados, cada ejecución como estado recuperable y auditable.

| ID | Entregable | Gate |
|----|------------|------|
| D-01 | E2E `v4complete` por cliente pago | Coherence ≥ 0.8 y acta no bloqueante según tier |
| D-02 | `pain_ledger` como fuente de verdad | 100% brechas trazables |
| D-03 | Matriz diagnóstico/oportunidad | No silent drop |
| D-04 | Matriz propuesta → brecha → asset | Alignment PASS vía acta |
| D-05 | `delivery_quality_report.json` obligatorio | PASS antes de ZIP |
| D-06 | Kit de entrega profesional | ZIP + README + **acta adjunta fuera del ZIP** (§6.3) + evidencia resumida |
| D-07 | Checklist pre-envío humano | 5-10 min máximo |
| D-08 | Registro de caso | Publicable con permiso |
| D-09 | **Garantía Día 55 operativa** | Baseline Día 0 + KPIs GSC reales (`is_simulated: false`; nunca decidir crédito sobre modo simulación) |
| D-10 | **Contraste estimado vs real** | Desviación registrada → §11.1 |
| D-11 | **Primera implementación gestionada verificada** | Plan de cambios aprobado → instalación → comprobación post-cambio → aceptación del cliente |

Criterio de éxito:

> Para cada hotel, el agente explica automáticamente: brechas detectadas, oportunidades, soluciones vendidas, assets entregados, precisión de la cifra y **estado de instalación de los cambios**.

---

## 8. Roadmap comercial, subordinado a validación y entrega confiable

### Distinción obligatoria: prospección vs entrega vs implementación

| | Prospección (pre-contrato) | Entrega (post-contrato) | Implementación gestionada (post-contrato) |
|---|---|---|---|
| Qué es | Gancho: hipótesis de fuga | Producto: diagnóstico certificado | Cambios instalados en el sitio del hotel |
| Instrumento | `hook-pdf` + mensaje breve | Paquete completo + acta | Plan de cambios + ejecutor + verificación |
| Precisión exigida | Rango declarado (P7.2) | Tier A para `APROBADO-PARA-ENTREGA` | Contenido validado + datos confirmados |
| ¿Requiere acta? | No | **Sí, siempre** | Sí, la del paquete + aprobación del cambio |
| ¿Puede automatizarse ya? | **Sí, desde la semana 1** | Solo tras T1-T3 en PASS | Parcial, según T5; siempre con aprobación |
| ¿Automatizable por WhatsApp? | Sí (gancho) | **No** — prohibido (§10) | **No** — prohibido (§10) |

Lo prohibido es automatizar **la entrega y el deploy** sin el circuito de aprobación; no el primer contacto. El deploy técnico supervisado de T5 está contemplado y requiere aprobación humana del cambio.

### Empaque comercial — corto plazo

1. Reposicionar iah-cli por lo que produce: **el diagnóstico de fuga y su implementación**, no la CLI ni el equipo agéntico.
2. Capa de interacción natural (email, WhatsApp, Slack, formulario) para **prospección** de inmediato; para **entrega**, solo después de 3-5 diagnósticos pagos y al menos 1 implementación cerrada.
3. Diferencial explícito: trazabilidad, gates, evidencia, **acta de revisión**, coherencia y **instalación verificada**.
4. El acta como argumento de venta: "diagnóstico auditado con acta de revisión".

No copiar promesas horizontales de ejecución 24/7, publicación automática multicanal, dashboard/SaaS ni personajes comerciales no anclados a workflows reales.

### Producto 1: Diagnóstico Express

Precio: fuente única `config/pricing.yaml` → `express_price`. No hardcodear.

Especificación: 2 páginas vía `hook-pdf`; hallazgo principal; cifra en COP con `precision_tier` declarado (rango si Tier B/B+/C); costo de oportunidad con base de cálculo y cap de plausibilidad; evidencia visible; una acción inmediata; propuesta de siguiente paso (onboarding); acta cuando evoluciona a entrega certificada.

### Producto 2: Implementación SEO/AEO/GEO — con implementación gestionada

Precio: fuente única `config/pricing.yaml` → tiers `boutique`/`standard`/`large`, con `floor_price` como piso y `monthly_default` como componente recurrente. Estructura vigente: `evidence/Ingresos/04_Estructura_Precios.md`.

Solo se ofrece a quien ya pagó o mostró intención clara. Incluye, según confianza y datos: schema, FAQ, llms.txt, Open Graph, optimización GBP/GEO, guía de implementación y medición posterior (Garantía Día 55, D-09).

**Contrato de implementación gestionada (T5 + Refuerzo §3.3, incorporado 2026-09-21):**

1. **El operador asume la ejecución técnica; el hotel aporta datos, accesos delegados y aprobaciones.** No delegar la instalación al hotel sin contrato: el riesgo (errores, inacción, insatisfacción) es real aunque su frecuencia no esté medida.
2. **Alcance delimitado por escrito**: accesos (CMS/hosting/analytics con permiso mínimo), cambios exactos incluidos y excluidos, entorno (staging/producción), criterios de aceptación. **Antipatrón medido**: la propuesta de TAREA7 dice "nosotros implementamos todo / no necesita hacer nada técnico" sin delimitar accesos ni aceptación (`output/TAREA7-2026-09-19/v4_complete/02_PROPUESTA_COMERCIAL_20260919_150131.md:42`) — no repetirlo sin contrato.
3. **Flujo**: paquete aprobado y datos confirmados → plan de cambios por dominio/entorno/asset con hashes → respaldo y staging → aprobación vinculada al plan → instalación controlada → **comprobación fresca del sitio publicado** → evidencia y aceptación.
4. **Seguridad del cambio**: registro de objetos gestionados (actualizar, no duplicar), reversión selectiva de lo propio, detención ante fallos parciales, secretos nunca en actas/logs/paquetes.
5. **Piloto primero**: un CMS confirmado, un staging, pocos cambios vinculados a brechas reales. No soportar varios CMS antes de medir el primero.
6. **Herramientas**: la necesidad primera son conectores ejecutores + comprobaciones HTTP/de navegador. `n8n` es candidata a **coordinador** (accesos pendientes, aprobaciones, ejecución, seguimiento) después de definir el circuito; no sustituye conectores ni certifica éxito. LangGraph, RAG y voz no resuelven esta brecha (Refuerzo §4).
7. **Semántica prohibida**: no usar `site_verification_applied` como comprobante de instalación (su productor real es `len(self.skipped_assets) > 0`, `v4_asset_orchestrator.py:168`); un HTTP 200 o la presencia previa no acreditan el cambio; generado no es aprobado; aprobado no es instalado; instalado no es verificado; verificado no es resultado comercial.

### Producto 2.5: Reporte mensual liviano de visibilidad

Precio: fuente única `config/pricing.yaml` → `monthly_default`. No se construye como SaaS ni dashboard: entregable mensual generado por agente **con revisión humana**, para clientes con diagnóstico o implementación completados. La prohibición de §10 aplica a reportes automáticos sin revisión, no a este producto.

Disparador: 1-3 clientes piden seguimiento; costo con margen; generación sin reconstrucción manual de evidencia.

### Producto 3: Seguimiento recurrente

No se vende hasta tener repetición manual. Disparadores: 5+ clientes activos, 10+ diagnósticos entregados, demanda explícita, costo controlado.

---

## 9. Gates de decisión

| Gate | Pregunta | Si falla |
|------|----------|----------|
| **G0: Primer piso / entrega confiable** | ¿El pipeline entrega un diagnóstico correcto y consecuente para un hotel real? | **NO CERRADO (re-anclado 2026-09-21).** Enforcement operativo y bloqueos reales observados (P4, TAREA7); corrección AC20 verificada offline sin certificación E2E; techo Tier B/B+ por analítica ausente (AC-O0). G0 cierra con `evidence_tier: A` + assets ≥ 0.8 + acta `APROBADO-PARA-ENTREGA` + certificación E2E de la corrida nueva. Bloquea la escala (T6), no la prospección |
| G1: Agent readiness | ¿Un agente fresco puede entender y ejecutar sin preguntar? | Mejorar AGENTS/workflows antes de más features |
| G2: Human minimalism | ¿El humano solo decide lo esencial? | Eliminar pasos humanos o moverlos a agente |
| G3: Evidence | ¿Cada claim comercial tiene evidencia y fuente declarada? | Bloquear entrega o marcar ESTIMATED |
| G4: Commercial validation | ¿Alguien pagó? | No escalar automatización comercial |
| G5: Cost control | ¿API/cómputo mantiene margen por diagnóstico **y por implementación**? | Activar `permission_mode`, reducir llamadas, fallback barato o revisar precio antes de escalar |
| G6: Delivery coherence | ¿Diagnóstico, oportunidad, propuesta y assets cuentan la misma historia? | Bloquear publicación |
| G7: Brecha coverage | ¿Todas las brechas aparecen, se agrupan o se justifican? | Reabrir diagnóstico antes de generar ZIP |
| G8: Asset specificity | ¿Cada asset resuelve un problema real y no es plantilla? | Marcar `GENERIC_DRAFT` o regenerar |
| G9: Documentation drift | ¿Docs críticas reflejan la realidad actual? | Ejecutar docs cascade / doctor (esta revisión v4.3 es el ejemplo del arreglo) |
| **G10: Precisión (P7)** | ¿La cifra es verosímil, declara su `precision_tier` y pasó el cap? | Renderizar rango, nunca cifra exacta sobre dato inferido |
| **G11: Acta de revisión** | ¿Existe acta certificando lo certifiable? | **No se entrega.** Vigente: 4/6 cláusulas certificables; P6.2/P6.5 `NOT_EVALUABLE`; el veredicto consume los reportes de los 4 revisores |
| **G12: Garantía medible** | ¿Baseline Día 0 capturado y KPIs reales (no simulados) medibles? | **No se promete garantía.** `validate-guarantee` cae a modo simulación sin GSC (`is_simulated: true`, `guarantee_validator.py:165-197`): nunca emitir crédito sobre datos simulados |
| **G13: Instalación verificada (nueva, 2026-09-21)** | ¿Los cambios aprobados quedaron instalados y comprobados en el sitio y entorno correctos, con reversión disponible? | No declarar "implementado"; re-trabajar o escalar. La evidencia es la comprobación post-cambio, no el exit del deploy ni `site_verification_applied` |

**Veredictos del Juez y `PublicationState`** **[re-validado 2026-09-21]**: el módulo `publication_state.py` citado por v4.2 **ya no existe en el árbol**; los literales de estado (`READY_FOR_CLIENT`, `DRAFT_INTERNAL`, etc.) sobreviven en `modules/quality_gates/coherence_gate.py`, sin llamador de producción confirmado. La correspondencia siguiente es de **diseño**, no de cableado: `APROBADO-PARA-ENTREGA` → `READY_FOR_CLIENT`; `APROBADO-CONDICIONAL-PENDING-ONBOARDING` → **sin estado propio** (decisión pendiente: estado nuevo o mapeo explícito, deuda P5); `DEVOLVER-CORRECCIONES` → `DRAFT_INTERNAL`; `BLOQUEADO` → `BLOCKED`. Antes de citar estados como cableados: decidir el destino del módulo (H8).

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
- reportes recurrentes **automáticos sin revisión humana** (Producto 2.5 con revisión sí está autorizado),
- ecosistema de skills extensible por terceros,
- verticales fuera de hotelería,
- **migración del pipeline o Tribunal a frameworks externos** (LangGraph/LangChain): no hay beneficio medido frente a los contratos vigentes (Refuerzo §4),
- cualquier feature cuyo criterio de éxito sea "la plataforma hace más cosas" en vez de "el diagnóstico es más correcto y su implementación verificable".

Hasta que existan señales:

- G0 cerrado con certificación E2E,
- 3-5 Express pagos,
- 1 implementación cerrada **con verificación post-cambio evidenciada**,
- 5+ debriefs reales,
- objeciones repetidas,
- flujo de entrega confiable repetido 10 veces,
- tasa de error del producto medida y dentro de umbral (§11.1, D-10).

---

## 11. Métricas

### 11.1 Métricas de producto — ¿qué tan bueno es el diagnóstico?

| Métrica | Umbral | Objetivo | Fuente |
|---------|--------|----------|--------|
| Diagnósticos con `precision_tier` A (cifra exacta permitida) | ≥ 30% | ≥ 70% | `quality_metadata` del MANIFEST |
| **Desviación fuga Tier B (estimada) vs Tier A (real post-onboarding)** | ≤ 3x | ≤ 1.5x | D-10 — la métrica del caso Luxor (~630x) |
| Cifras que pasan el cap de plausibilidad | 100% | 100% | `PrecisionValidator` + P7.3 |
| Paquetes entregados con `acta_revision.md` | 100% | 100% | T1 / G11 |
| Paquetes sin analítica que recibieron `APROBADO-PARA-ENTREGA` | **0** | **0** | Primer piso — invariante, no objetivo |
| Garantías Día 55 medidas con KPIs reales / créditos emitidos | 100% medidas | < 20% créditos | `validate-guarantee` / G12 |
| `hook-pdf` con cifra defendible (rango si B/B+/C) | 100% | 100% | G10 |

### 11.2 Métricas de aseguramiento — ¿el producto es consecuente?

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Outputs con evidencia rastreable | 90% | 95%+ |
| Brechas detectadas cubiertas o justificadas | 95% | 100% |
| Servicios vendidos con asset específico | 90% | 100% |
| Assets marcados correctamente | 95% | 100% |
| Cláusulas P6 certificables por el Juez | **4/6** (P6.2/P6.5 `NOT_EVALUABLE`, verificado 2026-09-21) | 6/6 |
| **Cambios gestionados con comprobación post-cambio evidenciada** | 100% | 100% (G13) |

### 11.3 Métricas comerciales

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Entrevistas de validación | 3 | 5 |
| Prospects ICP-filtrados con URL propia validada | 20 | 40 |
| Mensajes personalizados enviados | 20 | 40 |
| Conversaciones comerciales reales | 2 | 5 |
| Diagnósticos Express pagos | 1 | 5 |
| Clientes de implementación (con aceptación verificada) | 0 | 1 |
| Debriefs documentados | 1 | 5 |

Las métricas de salud operativa viven en `.agent/SYSTEM_STATUS.md` (regenerable con `python scripts/doctor.py --status`). Este cuadro solo lleva producto, aseguramiento y comercial.

---

## 12. Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **La cifra está magníficamente equivocada y destruye la credibilidad en la primera reunión** | **Alta** | **Crítico** | P7 completo: `precision_tier`, render en rango, cap, onboarding (T3), G10. Evidencia: Luxor ~630x |
| El producto se vende como plataforma de IA en vez de como diagnóstico + implementación | Media | Alto | Principio rector; §1, §2.2, §8, §10, §15 |
| **Promesa "implementamos todo" sin contrato de alcance → expectativas incumplidas, insatisfacción, el trabajo queda en diagnóstico** | **Alta (antipatrón ya publicado en TAREA7)** | Alto | Contrato de alcance del Producto 2 (accesos, exclusiones, aceptación); separación diagnóstico/implementación/seguimiento; G13 |
| Outputs estimados se venden como verificados | Media | Alto | Taxonomía VERIFIED/ESTIMATED/CONFLICT + revisor de honestidad |
| Un paquete sale ready con gates verdes pero veredicto bloqueante, y una integración lo envía igual | **Media (observado en TAREA7: EXIT=0 + READY + BLOQUEADO)** | Alto | La decisión de entrega es el veredicto + enforcement + package_evidence; ninguna integración usa exit code o readiness como permiso (Refuerzo §3.2) |
| Deploy sin acta/hash/aprobación binding (estado actual del deployer) | Media | Alto | P1 + G13: exigir binding antes de cualquier `--no-dry-run` real |
| `site_verification_applied` o un HTTP 200 se citan como instalación | Media | Alto | Re-anclado del productor (§8.7); verificación post-cambio separada |
| Crédito de garantía decidido sobre KPIs simulados | Media | Alto | G12: `is_simulated` obliga a revisión; sin GSC real no se emite crédito |
| Brechas detectadas desaparecen del diagnóstico final | Media | Alto | Coverage gate + `pain_ledger` |
| Propuesta promete servicios que los assets no materializan | Alta | Alto | Propuesta dinámica + acta; 6/7 servicios con pains no detectados fue causa raíz medida del 2026-09-02 **[sin revalidar]** |
| Assets genéricos erosionan confianza | Media | Alto | Specificity gate + `GENERIC_DRAFT` + revisor de assets |
| Deploy en sitio daña trabajo ajeno o no es reversible | Media | Alto | Registro de objetos gestionados, respaldo, reversión selectiva, staging (Producto 2.4) |
| Hoteleros no pagan por diagnóstico | Alta | Alto | Validación Express antes de automatizar más |
| Costos erosionan margen | Media | Alto | Presupuesto por diagnóstico **y por implementación**; coste observado, no teórico |
| Se automatiza la escala antes de que el diagnóstico sea correcto | Media | Alto | AOA: T6 gateado por T3+T5; §10 exige G0 y tasa de error medida |

---

## 13. Deuda técnica estratégica

### 13.1 Deuda de producto

1. **P1 — Deployer sin binding de aprobación ni ciclo de cambio.** Verificado 2026-09-21: WP crea solo posts borrador (`wordpress_connector.py:123`); `upload_file`/`inject_code` devuelven fallo explícito (`:88`, `:103`); FTP no conecta (`ftp_connector.py:47`); el plan solo cubre 4 nombres legacy (`manager.py:381`); no exige acta aprobatoria ni hash del paquete; sin idempotencia, respaldo, reversión ni verificación remota; tests con `FakeConnector` (`tests/test_deploy_execute_actions.py:13`). ⚠️ **Corrección v4.3**: la frase de v4.2 "consecuencia: `site_verification_applied: false`" era incorrecta — el flag nunca midió deploy (ver §8.7). Se resuelve en T5 + Producto 2.
2. **P2 — `IMPLEMENTATION_ORDER.md` vacío en entregas reales.** Stub detectado en P4 (2026-09-14) sobre ZIP real. AC10 del plan `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` trabaja el writer real (estado PENDIENTE al 2026-09-20). Revalidar contra HEAD antes de cerrar.
3. **P3 — CMS detectado con confianza estimada.** TAREA7 registró `cms_detected: "wordpress"` con `confidence: "estimated"` (`audit_report_20260919_150111.json:198`): la detección existe; falta confirmación por accesos (hosting, plugins, permisos) antes de elegir conector.
4. **P4 — No existe contraste entre fuga estimada y fuga real.** Sigue abierta; es la deuda de mayor valor relativo (D-10, §11.1).
5. **P5 — Sin estado de publicación para el veredicto condicional.** **[Re-validado 2026-09-21]**: el módulo `publication_state.py` ya no existe; la decisión pendiente es dónde vive el estado de publicación (reconstruir el módulo, usar `coherence_gate.py` o el anfitrión del pipeline) y si `APROBADO-CONDICIONAL-PENDING-ONBOARDING` recibe estado propio (§9).
6. **P6 — CERRADA (2026-09-14, DA-P1.4).** El acta no viaja en el ZIP por decisión de diseño: el círculo acta→paquete prohibido se evita excluyéndola (`delivery_packager.py:442`); el certificado se comparte desde `v4_audit/` (§6.3). La deuda original ("requiere lista blanca para entrar al ZIP") quedó resuelta en dirección opuesta y deliberada.
7. **P7 — Resolver G0 completo.** Requiere T3 (datos reales) + certificación E2E de AC20. Depende de datos, no de más código de pipeline.
8. **P8 — Endurecer G8 para hoteles atípicos.** Las 5 derivaciones cubren el audit estándar.
9. **P9 — El gate de publicación ignora `is_coherent`.** **[sin revalidar]** — hallazgo del 2026-09-02 sobre SalenteReal; revalidar en HEAD antes de usar como bloqueante de T0.4/certificación.
10. **P10 — Seis registros de identidad de servicios, ninguno canónico; skip silencioso en el builder.** **[sin revalidar]**; precondición de la propuesta dinámica.
11. **P11 — `precision_tier` degrada en silencio** (`main.py:2149-2167`, `try/except: pass`). **[sin revalidar]**; P7.1 no es auditable hasta registrar el motivo.
12. **P12 — El check de coherencia de mayor peso solo corre pre-gen.** **[sin revalidar]**; lo que AC20 cerró (2026-09-20) fue la serialización de evidencia del veredicto (details del recall, findings en el acta, package_evidence en ambas ramas), no la re-verificación post-gen del contrato de assets. T2/Bot 3 no puede certificar P6.3 más allá de lo que este check declara.

### 13.2 Deuda de herramienta

1. **H1 — Reducir duplicación README/AGENTS/docs.** README humano-mínimo; AGENTS agente-operativo.
2. **H2 — Recuperación de fases fallidas**: estado, causa, artefactos y siguiente acción segura por fallo.
3. **H3 — Smoke test de agent-readiness formalizado.**
4. **H4 — Taxonomía de fuentes y contrato de tipos del payload** (3 vocabularios ADR coexisten). Toca producto: la fuente determina `precision_tier`. Fuente: `.opencode/plans/Archives/BUGS-ONBOARDING-ADR-2026-07-22/01-plan-maestro.md` §9.
5. **H5 — ROADMAP manual, fuera de cascadas** (reafirmada v4.3; esta revisión se hizo a mano). Restricción: `scripts/validate_agents_md.py` exige las cadenas `pain_ledger`, `delivery_quality_report`, `human_checklist`, `data_derivation_layer` — preservadas en §7.1. Nota: el patrón antiguo `.agent/patterns/doc_sync_post_release.md` está **superado** por esta regla; no usarlo para re-sincronizar.
6. **H6 — El análisis Enrich Labs es evidencia de mercado, no modelo de producto.** Fuente: `.opencode/context/Historico/roadmap-enrichlabs-vertical-hotels-strategy.md`.
7. **H7 — Artefactos timestamped sin índice; oráculo de presencia.** **Parcialmente cerrada (2026-09-19)**: `site_presence_snapshot.json` ya se persiste en `v4_audit/` (TAREA7). Pendiente: índice/manifiesto que resuelva artefactos por corrida y reproducibilidad de la matriz desde disco (`pain_ledger` sin clave `assets` **[sin revalidar]**).
8. **H8 — Módulos huérfanos y eliminados.** **[Re-validado 2026-09-21]**: `publication_state.py` fue eliminado del árbol (ya no existe; sus literales sobreviven en `coherence_gate.py`); `coherence_gate.py` sigue sin llamador de producción confirmado **[sin revalidar]**; `two_phase_flow.py` solo se consume por sus tipos (verificado 2026-09-21). Regla vigente: decidir por módulo conectar o eliminar; un huérfano que parece vivo es peor que uno ausente.
9. **H9 — Rutas de bloqueo del ZIP y kill switch.** **Parcialmente cerrada (2026-09-14)**: el enforcement hereda `GATE_BLOCKING_ENABLED` con escape declarado en el acta (`enforcement.suppressed_by_operator`; verificado en TAREA7). Pendiente **[sin revalidar]**: converger rutas de bloqueo, auditar el switch, y el gate G9 que se salta en verde cuando falta la matriz.
10. **H10 — Docstring de severidades (11 blocking + 2 advisory) vs código.** **[sin revalidar en código]**; la documentación (AGENTS.md) ya declara el objetivo decidido.

### 13.3 Cerradas

- **`spark`**: retirado (v4.0); el instrumento del gancho es `hook-pdf`.
- **"Consolidar `.agents/workflows/` como capa ejecutable"**: sin objeto; 1 workflow activo.
- **"Monitorear discoverability agent-to-agent/MCP"**: demorada sin fecha; reevaluar solo por petición de cliente.
- **"Elevar QA post-generación a contrato nativo" + "consolidar `delivery_quality_report.json`"**: resueltas en FASE-0.
- **P6 (acta al ZIP)**: cerrada por decisión de diseño opuesta (2026-09-14) — ver §13.1.
- **Fases T offline (T1/T2/T4 + enforcement + multi-hotel + certificación 25 ACs)**: completadas el 2026-09-15 (release v4.77.0), planes archivados.

---

## 14. Visión 12-24 meses

Solo se activa si el modelo comercial valida. **H** = horizonte (no colisiona con las sub-fases **T**).

### H1: Agentic delivery engine

iah-cli entrega diagnósticos y assets con implementación gestionada verificada y mínima intervención humana.

Disparadores: 5+ diagnósticos pagos; 1+ implementación cerrada con aceptación verificada; flujo E2E repetible con acta y comprobación post-cambio.

### H2: Monitoring recurrente

Agentes revisan periódicamente hoteles activos y generan reportes comparables con revisión humana antes de enviar.

Disparadores: 5+ clientes activos; solicitud explícita; costo controlado; G12 pasando con KPIs reales.

### H3: Motor de precisión — grafo de hoteles y benchmarks

Horizonte de mayor valor bajo el principio rector: el aprendizaje agregado desde `pain_ledger` sube el `precision_tier` sin depender del onboarding de cada hotel. Ataca la causa raíz del caso Luxor.

Objetivos en orden de valor: mejorar benchmarks y recomendaciones; detectar brechas recurrentes por región/tipo; convertir diagnósticos en inteligencia comercial; preservar privacidad (agregación, anonimización, permiso explícito).

Disparadores: 20+ hoteles con permiso de uso agregado; tasa de error (D-10) medida en ≥10 casos. No se construye como capa de producto visible ni como proyecto de RAG: es infraestructura de precisión.

---

## 15. Resumen ejecutivo

iah-cli vende un diagnóstico: cuánto dinero pierde un hotel por reservas directas fugadas, con la precisión con que esa cifra puede afirmarse, los assets que la recuperan y —contratado aparte— su instalación gestionada y verificada.

Todo lo demás — agentes, gates, workflows, harness, actas, tribunal, conectores — es el medio para que ese diagnóstico sea **correcto, defendible, reproducible e implementable**. El acta viaja al cliente porque certifica el hallazgo; la evidencia de instalación viaja porque certifica el cambio. Nada se automatiza sobre un paquete que el Juez no aprobó, y nada se declara instalado sin comprobación posterior.

El humano queda en las decisiones de mayor valor: qué cliente perseguir, qué riesgo aceptar, qué dato confirmar, qué propuesta enviar, qué cambio autorizar en el sitio y qué aprendizaje incorporar. El agente se encarga del resto: investigación, ejecución, validación, documentación, coherencia, trazabilidad, instalación controlada y verificación.

La secuencia no es negociable (AOA): **auditar** el paquete antes de optimizarlo, **optimizar** su precisión con datos reales antes de instalarlo, e **implementar/automatizar** solo lo aprobado — midiendo el resultado observado, no solo el exit del comando.

Principio final:

> iah-cli vende un diagnóstico defendible sobre la fuga de reservas directas de un hotel, y lo convierte en cambios instalados y verificados. Los agentes, gates y actas son el medio para que eso sea correcto y verificable — no el producto.
