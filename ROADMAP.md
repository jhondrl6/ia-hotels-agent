# ROADMAP iah-cli — Evolución Agent-First con Capa Humana Mínima

> **Versión roadmap**: v3.5 (2026-05-16)
> **Estado proyecto**: v4.47.0 — ADVISORY-WARNINGS
> **Tesis estratégica**: iah-cli debe evolucionar como sistema operado principalmente por agentes, con una interfaz humana mínima, clara y suficiente.
> **Principio rector**: primero entrega confiable al cliente; después escala, automatización y crecimiento. Agentes ejecutan, validan y mantienen; humanos deciden, aprueban costos/riesgos y aportan datos reales.
> **Horizonte operativo**: 90 días. Se reevalúa semanalmente durante validación comercial y quincenalmente después.

---

## 1. Norte estratégico

iah-cli no debe evolucionar como una aplicación tradicional human-first con automatizaciones añadidas.
Debe evolucionar como una plataforma agent-first especializada en diagnóstico, propuesta y generación de assets para visibilidad digital hotelera.

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

> No se construye el segundo piso si el primero no está construido. En iah-cli, el primer piso es la entrega confiable al cliente: diagnóstico completo, oportunidad coherente, propuesta consecuente y assets específicos que resuelven las brechas detectadas.

Antes de escalar automatización comercial, outreach, monitoreo recurrente, UI, nuevos módulos o expansión del producto, el pipeline debe demostrar que puede entregar una solución autoconsistente para un hotel real.

---

## 2. Clasificación del repositorio

### 2.1 Lo que iah-cli ya es

iah-cli ya funciona como sistema híbrido:

| Capa | Estado actual | Orientación futura |
|------|---------------|-------------------|
| CLI humana | Funcional: `setup`, `v4complete`, `v4audit`, `onboard`, `execute`, `deploy`, `--doctor` | Mantener mínima y estable |
| Agent Harness | Existente: memoria, routing, handlers, timeout, skill execution | Convertir en núcleo operativo |
| Workflows `.agents/workflows/` | 16 workflows core activos | Convertir en contrato principal de ejecución |
| Documentación técnica | Abundante pero dispersa | Reorientar a navegación de agentes + resumen humano |
| Outputs comerciales | Diagnóstico, propuesta, assets, delivery zip | Mantener como producto final para humanos/clientes |
| Mantenimiento | Doctor, validations, registry, version sync | Hacerlo más automático y obligatorio para agentes |

### 2.2 Conclusión de diseño

El repo debe tratar a los humanos como operadores estratégicos y validadores, no como ejecutores paso a paso.

Interpretación comercial deseada:

> iah-cli puede evolucionar hacia un “Enrich Labs vertical para hoteles”, pero con una ventaja diferencial propia: trazabilidad, gates de calidad, evidencia y coherencia diagnóstico → propuesta → assets.

Esto no significa copiar una plataforma horizontal de marketing ni prometer ejecución 24/7 de todos los canales. Significa empaquetar, cuando exista validación comercial suficiente, los workflows y gates actuales como un equipo agéntico especializado en visibilidad digital hotelera.

Por tanto:

- No priorizar una UI compleja.
- No multiplicar documentación narrativa para humanos.
- No hacer que humanos sigan procedimientos largos si un agente puede ejecutarlos.
- Sí mantener comandos CLI simples, seguros y explicables.
- Sí fortalecer AGENTS.md, workflows, gates, doctor, memoria, evidencia y validaciones.
- Sí traducir capacidades internas en roles comerciales comprensibles cuando no comprometa la entrega confiable.

---

## 3. Estado actual verificable

Fuente de verdad de versión: `VERSION.yaml`.

Estado leído el 2026-05-14:

| Métrica | Estado |
|---------|--------|
| Versión | v4.46.1 |
| Codename | ENCODING-SAFETY |
| Release date | 2026-05-14 |
| Archivos Python totales, incluyendo tests | 472 |
| Test files `test_*.py` | 210 |
| Scripts Python en `scripts/` | 22 |
| YAML config en `config/` | 9 |
| Workflows core en `.agents/workflows/` | 16 |
| CLI principal | `main.py` |
| Contexto global agente | `AGENTS.md` |
| Harness | `agent_harness/` |
| FASE 0 — delivery quality (bloqueante) | ✅ COMPLETADO (8 sub-fases: 0A-0H + RELEASE) |
| Módulos nuevos FASE 0 | `pain_ledger.py`, `data_derivation_layer.py`, `delivery_quality_report.py`, `human_checklist_generator.py` |
| Artifacts nuevos FASE 0 | `pain_ledger.json`, `proposal_asset_matrix.json`, `delivery_quality_report.json`, `human_checklist.md` |
| Tests nuevos FASE 0 | 60+ tests (pain_ledger, coverage_gate, proposal_asset_matrix, delivery_quality, human_checklist, data_derivation, scoring) |
| E2E coherence | ≥ 0.81 (hotelcastillareal) |
| Delivery ready post-0H | ≥ 9/12 assets ≥ 0.65 confidence |

Nota: los conteos de funciones de test pueden variar por método de medición. Para roadmap se usan conteos estructurales verificables por archivos.

---

## 4. Principios de evolución

### P1. Agent-first, human-minimal

Cada nueva capacidad debe responder primero:

- ¿Puede ejecutarla un agente con contexto suficiente?
- ¿Puede verificarse automáticamente?
- ¿Puede dejar evidencia auditable?
- ¿Puede reanudarse en otra sesión?

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

### P4. Manual antes que automático, pero solo para validar mercado

Para ventas y producto comercial, se mantiene el principio:

> Manual antes que automático, específico antes que general.

Pero para operación interna del repo, el objetivo es lo contrario:

> Si un agente puede hacerlo con seguridad y evidencia, no debe hacerlo manualmente el humano.

### P5. No construir interfaz humana pesada antes de tracción

No crear dashboard, SaaS, GUI, multiusuario o panel administrativo hasta tener validación comercial suficiente.

La interfaz humana mínima por ahora es:

```bash
python main.py setup
python main.py v4complete --url https://hotel.com
python main.py onboard --url https://hotel.com
python main.py execute --url https://hotel.com --package starter_geo
python main.py --doctor
```

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

---

## 5. Contrato de producto: quién ejecuta qué

| Actividad | Ejecutor primario | Humano interviene cuando... |
|-----------|------------------|-----------------------------|
| Diagnóstico `v4complete` | Agente / CLI | Debe aportar URL o revisar output |
| Onboarding de datos reales | Humano asistido por CLI | Siempre: son datos de negocio |
| Validación cruzada | Agente | Hay conflicto hard o dato dudoso |
| Generación de propuesta | Agente | Antes de enviar a cliente |
| Generación de assets | Agente | Si asset queda ESTIMATED o CONFLICT |
| Deploy | Agente con aprobación | Hay impacto externo real |
| Mantenimiento docs | Agente | Solo si cambia estrategia o criterio comercial |
| Actualización roadmap | Humano + agente | Cambia dirección estratégica |
| Fases de desarrollo | Agente | Humano define objetivo y límites |
| Costos/API externas | Agente con permission mode | Costo/riesgo excede umbral |

Regla comercial de costos:

> Cada Diagnóstico Express debe mantener presupuesto máximo de API/cómputo y margen mínimo esperado. Si el costo real por diagnóstico amenaza ese margen, se activa reducción de llamadas, fallback barato, `permission_mode` o revisión explícita de precio antes de escalar volumen.

---

## 6. Arquitectura objetivo

### 6.1 Capa agente

Debe ser la capa dominante.

Componentes:

- `AGENTS.md`: contexto global operativo, no manual humano.
- `.agents/workflows/`: workflows semánticos y ejecutables.
- `agent_harness/`: memoria, routing, ejecución, observación, self-healing.
- `.agent/knowledge/DOMAIN_PRIMER.md`: conocimiento regenerable del dominio/código.
- `scripts/doctor.py`: healthcheck del ecosistema agente.
- `scripts/run_all_validations.py`: gate de validación.
- `docs/contributing/*`: contrato documental para agentes.
- `tests/`: protección contra regresión.

Objetivo:

> Un agente nuevo en sesión fresca debe poder entender el estado del repo, elegir el workflow correcto, ejecutar una fase, verificarla y registrar evidencia sin depender de memoria humana.

### 6.2 Capa humana mínima

Debe ser pequeña, estable y difícil de usar mal.

Componentes:

- `README.md`: qué hace, cómo instalar, cómo ejecutar 3 comandos principales.
- CLI `main.py`: comandos claros y flags seguros.
- `setup`: credenciales.
- `onboard`: datos reales.
- outputs comerciales: diagnóstico, propuesta, assets, zip de entrega.

Objetivo:

> Un humano técnico debe poder operar el producto sin entender la arquitectura interna.

### 6.3 Capa cliente final

El cliente hotelero no opera el repo.
Recibe:

- diagnóstico,
- propuesta,
- evidencia resumida,
- assets técnicos,
- plan de acción,
- eventual reporte de seguimiento.

### 6.4 Capa de aseguramiento de entrega confiable

Esta capa debe cerrar el loop interno que hoy requiere invocación manual después de generar entregables en `output/v4_complete`.

Problema actual:

- Los módulos pueden detectar más brechas que las que aparecen en diagnóstico y oportunidad.
- La propuesta comercial puede vender soluciones que no quedan materializadas en assets concretos.
- Los assets pueden existir pero ser genéricos, estimados o desconectados del dolor específico del hotel.
- El humano debe pedir manualmente al agente que audite coherencia, cobertura y calidad después de cada entrega.

Arquitectura objetivo:

| Contrato interno | Qué debe asegurar | Evidencia esperada |
|------------------|-------------------|--------------------|
| `pain_ledger` / brechas fuente de verdad | Toda brecha detectada queda normalizada con `pain_id`, severidad, fuente y confianza | JSON rastreable en `output/v4_complete/<hotel>/` |
| Diagnóstico y oportunidad | Cobertura 1:1 o justificación explícita para cada brecha detectada | Tabla brecha → impacto → oportunidad → evidencia |
| Propuesta comercial | Cada servicio vendido responde a una o más brechas priorizadas | Matriz brecha → servicio → promesa comercial |
| Assets | Cada asset generado resuelve una brecha o servicio específico, no una plantilla genérica | Matriz servicio → asset → archivo → confidence |
| Delivery gate | Bloquea entrega si hay brechas sin explicar, servicios sin asset o assets genéricos vendidos como específicos | `delivery_quality_report.json` + estado PASS/FAIL |

Reglas obligatorias:

1. **Coverage gate**: `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`.
2. **Commercial alignment gate**: todo servicio de la propuesta debe mapear a brecha real, evidencia y asset.
3. **Asset specificity gate**: cada asset debe mencionar el hotel, el problema que resuelve y el punto de implementación; si no, queda `GENERIC_DRAFT` y no se vende como solución final.
4. **Evidence gate**: cada claim fuerte debe tener fuente: web, GBP, onboarding, benchmark o estimación declarada.
5. **No silent drop**: ninguna brecha puede desaparecer entre módulos, diagnóstico, propuesta y assets sin explicación auditable.
6. **Human review mínima**: el humano revisa excepciones y decisión comercial final, no reconstruye manualmente la coherencia.

Resultado esperado:

> `v4complete` no solo genera archivos; entrega un paquete autoconsistente donde diagnóstico, oportunidad, propuesta y assets cuentan la misma historia comercial y técnica.

---

## 7. Roadmap técnico agent-first, 90 días

### FASE 0: Primer piso — entrega confiable al cliente ✅ COMPLETADO (2026-05-13)

Objetivo: asegurar que `v4complete` entregue una solución confiable antes de construir capas superiores de automatización, comercialización o producto.

Ejecutado en 8 sub-fases (0A-0H) + RELEASE bajo `.opencode/plans/FASE-0-DELIVERY-QUALITY/`. Resultados concretos:

| ID | Entregable | Resultado | Evidencia |
|----|------------|-----------|-----------|
| 0-01 | `pain_ledger` operativo | ✅ `PainLedger` facade sobre `PainSolutionMapper` con `pain_ledger.json` — 100% pains trazables con pain_id, fuente, severidad, confianza, estado | `modules/asset_generation/pain_ledger.py` |
| 0-02 | Coverage diagnóstico/oportunidad | ✅ `CoverageGate` en `publication_gates.py` — regla `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`; 11 tests | `modules/quality_gates/publication_gates.py` |
| 0-03 | Matriz propuesta → brecha → asset | ✅ `ProposalAssetMatrix` dinámico — vínculo trazable servicio→pain_id→asset→evidencia; `proposal_asset_matrix.json` | `modules/asset_generation/proposal_asset_alignment.py` |
| 0-04 | `delivery_quality_report.json` bloqueante | ✅ `DeliveryQualityReport` — QA post-generación; FAIL bloquea ZIP; 10 tests | `modules/quality_gates/delivery_quality_report.py` |
| 0-05 | Checklist humano reducido | ✅ `HumanChecklistGenerator` — ≤10 items derivados automáticamente del reporte; `human_checklist.md` | `modules/quality_gates/human_checklist_generator.py` |
| — | G8 Root-Cause Hardening (0H) | ✅ `DataDerivationLayer` (5 derivaciones del audit) + Contrato REQUIRED/RECOMMENDED + scoring semántico; 26 tests | `modules/asset_generation/data_derivation_layer.py` |

**E2E verificado (0G)**: `v4complete` sobre hotelcastillareal — coherence 0.81, G7 PASS (0 UNTRACKED), G0 WARNING (G8 low confidence en 8/12 assets pre-0H), G8 hardening elevó delivery ready a 9/12 assets ≥0.65.

**Definición de terminado cumplida**:
> Un agente puede responder, con evidencia por archivo: qué brechas detectó, cuáles entraron al diagnóstico, qué oportunidad comercial justifican, qué se propone vender y qué assets específicos entregan esa solución.

**Pendiente post-FASE-0**: G0 requiere PASS completo (todos los assets ≥0.8 confidence) para considerar cerrado el primer piso. El hardening de 0H avanzó de 25% → 75% delivery ready, pero los assets dependientes de `hotel_data` real (onboarding humano) permanecen en `ESTIMATED`. La resolución completa de G0 depende de datos de onboarding, no de más código.

### FASE A: Baseline de robustez agente (1-2 semanas)

Objetivo: asegurar que el repo sea navegable y ejecutable por agentes sin ambigüedad, subordinado al contrato de entrega confiable de FASE 0.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| A-01 | `AGENTS.md` auditado como contexto primario agente | Zona esencial clara, rutas correctas, sin ruido excesivo | Doctor + revisión manual rápida |
| A-02 | `.agents/workflows/README.md` sincronizado con workflows reales | 16 workflows core listados, triggers claros | Script/doctor sin huérfanos |
| A-03 | Matriz de responsabilidades humano/agente documentada | El repo sabe qué pide al humano y qué ejecuta el agente | ROADMAP + AGENTS alineados |
| A-04 | Human-minimum CLI definida | README solo prioriza comandos esenciales | README no deriva en manual largo |
| A-05 | Validación de contexto fresco | Un agente nuevo puede ejecutar diagnóstico de repo sin preguntar | Prompt de smoke test pasa |

No construir:

- dashboard,
- UI web,
- wizard complejo,
- integración multiusuario,
- marketplace de skills.

### FASE B: Ejecución de fases más confiable por agentes (2-4 semanas)

Objetivo: reducir fallos de ejecución multi-sesión.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| B-01 | `phased_project_executor.md` endurecido | Reglas de fase, presupuesto y docs cascade sin ambigüedad | Plan de prueba con fase simulada |
| B-02 | Prompts de fase estandarizados | Cada fase contiene objetivo, archivos, comandos, criterios y rollback | Template validado |
| B-03 | Evidencia post-fase obligatoria | Cada fase deja logs, tests, diff y docs tocadas | `log_phase_completion.py` usado |
| B-04 | Regla de no-doc-drift | Cambios de código que alteran comportamiento disparan docs/checks | Validación rápida pasa |
| B-05 | Modo recuperación | Si una fase falla, el siguiente agente sabe dónde retomar | Contexto de failure reproducible |

### FASE C: Operación comercial asistida por agentes (4-8 semanas)

Dependencia: no se escala esta fase si FASE 0 no está en PASS. La venta asistida por agentes solo tiene sentido si la entrega base ya es confiable.

Objetivo: que la venta inicial use agentes para investigación, diagnóstico y preparación, pero mantenga al humano en cierre y relación comercial.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| C-01 | Lista ICP de 30-40 hoteles | Prospects con criterios claros | Lista verificable |
| C-02 | `spark` o flujo express ejecutado sobre prospects | Hallazgo específico por hotel | Costo controlado |
| C-03 | Mensajes personalizados generados | Outreach con dato real, no genérico | Revisión humana antes de enviar |
| C-04 | Primer Diagnóstico Express pago | Validación de willingness-to-pay | Pago recibido |
| C-05 | Debrief estructurado | Frases reales del cliente + objeciones | Archivo de aprendizaje |

Regla:

> El agente prepara y documenta; el humano vende y decide.

### FASE D: Cierre de loop diagnóstico → propuesta → assets (8-12 semanas)

Dependencia: esta fase profundiza y productiza FASE 0. No debe tratarse como mejora tardía; FASE 0 entrega el mínimo confiable y FASE D lo convierte en estándar repetible.

Objetivo: convertir el pipeline en una unidad de entrega confiable, menos dependiente de intervención manual y capaz de demostrar que lo diagnosticado, lo vendido y lo entregado están alineados.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| D-01 | E2E v4complete por cliente pago | Diagnóstico + propuesta + assets + gates | Coherence >= 0.8 |
| D-02 | `pain_ledger` como fuente de verdad | Brechas normalizadas con ID, fuente, severidad, confianza y estado | 100% de brechas detectadas trazables |
| D-03 | Matriz diagnóstico/oportunidad | Cada brecha aparece en el diagnóstico o queda explícitamente agrupada/justificada | No silent drop |
| D-04 | Matriz propuesta → brecha → asset | Cada servicio vendido responde a brecha real y tiene asset específico | Proposal-asset alignment PASS |
| D-05 | `delivery_quality_report.json` obligatorio | QA agent-first post-generación sobre `output/v4_complete` | PASS antes de ZIP/publicación |
| D-06 | Kit de entrega profesional | ZIP + README + evidencia resumida + reporte de calidad | Cliente puede entenderlo |
| D-07 | Checklist pre-envío humano | Solo excepciones, decisiones comerciales y tono final; no debugging técnico | 5-10 min máximo |
| D-08 | Registro de caso | Antes/después, hallazgo, solución, resultado | Publicable con permiso |
| D-09 | Seguimiento básico | Revisión 30 días si aplica | Output comparable |

Criterio de éxito específico:

> Para cada hotel, el agente debe poder explicar automáticamente: “detectamos estas brechas, priorizamos estas oportunidades, vendemos estas soluciones y entregamos estos assets para resolverlas”.

---

## 8. Roadmap comercial, subordinado a validación y entrega confiable

La robustez agente no reemplaza la validación comercial, pero la validación comercial tampoco debe avanzar sobre entregas inconsistentes.
El roadmap comercial se mantiene con agentes como multiplicador operativo, condicionado a FASE 0: primero entrega confiable, después escala comercial.

### Empaque comercial agéntico — corto plazo

Inspiración externa válida: Enrich Labs demuestra que el mercado entiende agentes de marketing como especialistas ejecutores, no como dashboards. Para iah-cli, la adaptación correcta es vertical hotelera y subordinada a G0.

Acciones factibles sin romper el foco:

1. Reposicionar iah-cli como equipo agéntico hotelero, no solo como CLI.
2. Convertir workflows existentes en roles comprensibles: auditor de visibilidad, SEO/GEO hotelero, generador de assets técnicos y seguimiento/reporte.
3. Preparar una capa de interacción natural — email, WhatsApp, Slack o formulario simple — solo después de 3-5 diagnósticos pagos y al menos 1 implementación cerrada.
4. Mantener como diferencial explícito: trazabilidad, gates de calidad, evidencia y coherencia diagnóstico → propuesta → assets.

No copiar todavía promesas horizontales de ejecución 24/7, publicación automática multicanal, dashboard/SaaS o personajes comerciales no anclados a workflows reales.

### Producto 1: Diagnóstico Express

Precio inicial sugerido: $120.000 COP.

Propósito:

- validar que el hotelero paga por entender su fuga digital,
- filtrar curiosos,
- generar datos reales de objeciones,
- abrir puerta a implementación.

Entregable mínimo:

- 3-5 páginas,
- hallazgo principal,
- costo de oportunidad estimado,
- evidencia visible,
- una acción inmediata,
- propuesta de siguiente paso.

### Producto 2: Implementación SEO/AEO/GEO

Precio inicial sugerido: $1.500.000–$3.500.000 COP.

Solo se ofrece a quien ya pagó o mostró intención clara.

Incluye, según confianza y datos:

- schema,
- FAQ,
- llms.txt,
- Open Graph,
- optimización GBP/GEO,
- guía de implementación,
- medición posterior.

### Producto 2.5: Reporte mensual liviano de visibilidad

No se construye como SaaS ni dashboard. Se valida primero como entregable mensual agent-generated para clientes que ya completaron diagnóstico o implementación.

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
| G0: Primer piso / entrega confiable | ¿El pipeline entrega diagnóstico, oportunidad, propuesta y assets autoconsistentes para un hotel real? | **WARNING** (2026-05-13): coherence 0.81 ≥ 0.8, G6 PASS, G7 PASS, G8 parcial (9/12 assets ≥0.65 post-0H). G0 requiere PASS completo para desbloquear FASE C comercial. Assets pending dependen de onboarding humano, no de código. |
| G1: Agent readiness | ¿Un agente fresco puede entender y ejecutar sin preguntar? | Mejorar AGENTS/workflows antes de más features |
| G2: Human minimalism | ¿El humano solo decide lo esencial? | Eliminar pasos humanos o moverlos a agente |
| G3: Evidence | ¿Cada claim comercial tiene evidencia? | Bloquear entrega o marcar ESTIMATED |
| G4: Commercial validation | ¿Alguien pagó? | No escalar automatización comercial |
| G5: Cost control | ¿API/cómputo mantiene margen mínimo por diagnóstico? | Activar `permission_mode`, reducir llamadas, usar fallback barato o revisar precio antes de escalar |
| G6: Delivery coherence | ¿Diagnóstico, oportunidad, propuesta y assets cuentan la misma historia? | Bloquear publicación |
| G7: Brecha coverage | ¿Todas las brechas detectadas aparecen, se agrupan o se justifican explícitamente? | Reabrir diagnóstico antes de generar ZIP |
| G8: Asset specificity | ¿Cada asset resuelve un problema real del hotel y no es plantilla genérica? | Marcar `GENERIC_DRAFT` o regenerar |
| G9: Documentation drift | ¿Docs críticas reflejan realidad actual? | Ejecutar docs cascade / doctor |

---

## 10. Qué NO hacer por ahora

No construir:

- SaaS multiusuario,
- dashboard web completo,
- marketplace de skills,
- sistema comunitario de builders,
- PMS integration,
- multi-idioma,
- automatización WhatsApp productizada,
- reportes recurrentes automáticos,
- verticales fuera de hotelería.

Hasta que existan señales:

- FASE 0 en PASS para entregas reales,
- 3-5 Express pagos,
- 1 implementación cerrada,
- 5+ debriefs reales,
- objeciones repetidas,
- flujo de entrega confiable repetido 10 veces.

---

## 11. Métricas 90 días

### Métricas agent-first

| Métrica | Umbral | Objetivo | Actual (2026-05-14) |
|---------|--------|----------|---------------------|
| Workflows core sincronizados con README | 100% | 100% | 100% |
| Ejecución de fase sin contexto humano adicional | 1 caso | 3 casos | ✅ 8 fases ejecutadas (0A-0H) |
| Validaciones rápidas post-cambio | Pasa | Pasa consistentemente | 4/5 PASS (doc integration pre-existing) |
| Outputs con evidencia rastreable | 90% | 95%+ | ✅ pain_ledger, coverage_gate, proposal_asset_matrix, delivery_quality_report |
| Brechas detectadas cubiertas o justificadas | 95% | 100% | ✅ 100% (0 UNTRACKED en E2E 0G) |
| Servicios vendidos con asset específico | 90% | 100% | ✅ proposal_asset_matrix vinculado |
| Assets marcados correctamente (`VERIFIED`/`ESTIMATED`/`CONFLICT`/`GENERIC_DRAFT`) | 95% | 100% | 75% (9/12 ≥0.65 post-0H; 3 en ESTIMATED por falta de hotel_data) |
| Docs críticas sin drift visible | AGENTS/README/CONTRIBUTING | + ROADMAP alineado | ✅ (actualizado 2026-05-14) |
| Tiempo humano pre-envío | <= 15 min | <= 10 min | ✅ checklist ≤10 items |

### Métricas comerciales

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Entrevistas de validación | 3 | 5 |
| Prospects ICP-filtrados | 20 | 40 |
| Mensajes personalizados enviados | 20 | 40 |
| Conversaciones comerciales reales | 2 | 5 |
| Diagnósticos Express pagos | 1 | 5 |
| Clientes de implementación | 0 | 1 |
| Debriefs documentados | 1 | 5 |

---

## 12. Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| El repo acumula documentación humana que los agentes no usan | Alta | Alto | AGENTS/workflows como fuente operativa primaria |
| El humano vuelve a ejecutar pasos manuales largos | Alta | Alto | Convertir procedimientos en workflows/gates |
| Agentes ejecutan sin suficiente contexto | Media | Alto | Contexto global + prompts de fase completos |
| Drift entre docs, código y outputs | Alta | Alto | Doctor, validation scripts, docs cascade |
| Hoteleros no pagan por diagnóstico | Alta | Alto | Validación Express antes de automatizar más |
| Costos API/modelo erosionan margen del Diagnóstico Express | Media | Alto | Presupuesto máximo por diagnóstico, margen mínimo, `permission_mode`, fallback barato y revisión de precio antes de escalar |
| Se construye UI antes de tracción | Media | Alto | Gate explícito: no UI pesada hasta 10+ entregas manuales |
| Outputs estimados se venden como verificados | Media | Alto | Taxonomía VERIFIED/ESTIMATED/CONFLICT obligatoria |
| Brechas detectadas desaparecen del diagnóstico final | Media | Alto | Coverage gate y `pain_ledger` obligatorio |
| Propuesta promete servicios que los assets no materializan | Media | Alto | Matriz propuesta → brecha → asset bloqueante |
| Assets genéricos erosionan confianza del cliente | Media | Alto | Asset specificity gate + etiqueta `GENERIC_DRAFT` |

---

## 13. Deuda técnica estratégica

1. `spark` está marcado como deprecado, pero puede ser útil para outreach barato. Decisión: mantenerlo solo si se usa comercialmente 10+ veces.
2. Consolidar el rol de `.agents/workflows/` como capa ejecutable, no solo documentación.
3. Reducir duplicación entre README, AGENTS y docs. README debe ser humano-mínimo; AGENTS debe ser agente-operativo.
4. Fortalecer recuperación de fases fallidas para agentes en sesiones frescas.
5. Formalizar smoke test de agent-readiness: un agente nuevo debe poder entender estado, ejecutar validación y explicar siguiente acción.
6. ~~Elevar el QA post-generación de `output/v4_complete` a contrato nativo del pipeline: coverage de brechas, alineación comercial y especificidad de assets.~~ ✅ Resuelto en FASE-0-DELIVERY-QUALITY: `delivery_quality_report.json` + `coverage_gate` + `proposal_asset_matrix` + `pain_ledger.json`.
7. ~~Consolidar `delivery_quality_report.json` como evidencia obligatoria antes de empaquetar o enviar entregables.~~ ✅ Resuelto en FASE-0E: FAIL bloquea ZIP.
8. Mantener ROADMAP como documento estratégico manual. No incluirlo en cascadas automáticas salvo solicitud explícita.
9. Monitorear discoverability agent-to-agent/MCP como radar 12-18 meses. No priorizarlo antes de validación comercial y entrega confiable repetible.
10. Resolver G0 completo: los 3 assets en `ESTIMATED` por falta de `hotel_data` requieren onboarding real para alcanzar ≥0.8 confidence. Es la última milla del primer piso.
11. Endurecer G8 para nuevos tipos de hotel: el DataDerivationLayer cubre 5 derivaciones del audit estándar; hoteles con estructuras atípicas pueden necesitar derivaciones adicionales.
12. Preservar el análisis Enrich Labs vertical para hoteles como contexto estratégico, no como copia de producto horizontal. Fuente: `.opencode/context/roadmap-enrichlabs-vertical-hotels-strategy.md`.

---

## 14. Visión 12-24 meses

Solo se activa si el modelo comercial valida.

### Etapa 1: Agentic delivery engine

iah-cli entrega diagnósticos y assets de forma confiable con mínima intervención humana.

Disparador:

- 5+ diagnósticos pagos,
- 1+ implementación cerrada,
- flujo E2E repetible.

### Etapa 2: Monitoring recurrente

Agentes revisan periódicamente hoteles activos y generan reportes comparables.

Disparador:

- 5+ clientes activos,
- solicitud explícita de seguimiento,
- costo controlado.

### Etapa 3: Hotel graph / intelligence layer

Grafo de hoteles, competidores, regiones, activos digitales, benchmarks y aprendizaje agregado desde `pain_ledger` / `evidence_ledger`.

Objetivo:

- detectar brechas recurrentes por región y tipo de hotel,
- mejorar benchmarks y recomendaciones sin depender de intuición manual,
- convertir diagnósticos repetidos en inteligencia comercial reutilizable,
- preservar privacidad mediante agregación, anonimización y permiso explícito de uso.

Disparador:

- 20+ hoteles activos o diagnosticados con permiso de uso agregado.

### Etapa 4: Ecosistema de skills hoteleros

Solo después de validar repetición interna.

Disparador:

- 3+ builders o clientes piden extensibilidad,
- skills internas estables,
- documentación agente-first madura.

---

## 15. Resumen ejecutivo

La dirección correcta no es hacer iah-cli más cómodo para que humanos operen cada detalle.
La dirección correcta es hacerlo más robusto para que agentes ejecuten con seguridad, evidencia y continuidad.

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

Principio final:

> iah-cli debe ser una máquina de entrega agéntica para hoteles, no una herramienta manual con scripts.
