# ROADMAP iah-cli — Evolución Agent-First con Capa Humana Mínima

> **Versión roadmap**: v3.0 (2026-05-12)
> **Estado proyecto**: v4.45.0 — TERMALES-GATE-HARDENING
> **Tesis estratégica**: iah-cli debe evolucionar como sistema operado principalmente por agentes, con una interfaz humana mínima, clara y suficiente.
> **Principio rector**: agentes ejecutan, validan y mantienen; humanos deciden, aprueban costos/riesgos y aportan datos reales.
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

Por tanto:

- No priorizar una UI compleja.
- No multiplicar documentación narrativa para humanos.
- No hacer que humanos sigan procedimientos largos si un agente puede ejecutarlos.
- Sí mantener comandos CLI simples, seguros y explicables.
- Sí fortalecer AGENTS.md, workflows, gates, doctor, memoria, evidencia y validaciones.

---

## 3. Estado actual verificable

Fuente de verdad de versión: `VERSION.yaml`.

Estado leído el 2026-05-12:

| Métrica | Estado |
|---------|--------|
| Versión | v4.45.0 |
| Codename | TERMALES-GATE-HARDENING |
| Release date | 2026-05-12 |
| Archivos Python totales, incluyendo tests | 463 |
| Test files `test_*.py` | 203 |
| Scripts Python en `scripts/` | 22 |
| YAML config en `config/` | 9 |
| Workflows core en `.agents/workflows/` | 16 |
| CLI principal | `main.py` |
| Contexto global agente | `AGENTS.md` |
| Harness | `agent_harness/` |

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

---

## 7. Roadmap técnico agent-first, 90 días

### FASE A: Baseline de robustez agente (1-2 semanas)

Objetivo: asegurar que el repo sea navegable y ejecutable por agentes sin ambigüedad.

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

Objetivo: convertir el pipeline en una unidad de entrega más confiable y menos dependiente de intervención manual.

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| D-01 | E2E v4complete por cliente pago | Diagnóstico + propuesta + assets + gates | Coherence >= 0.8 |
| D-02 | Kit de entrega profesional | ZIP + README + evidencia resumida | Cliente puede entenderlo |
| D-03 | Checklist pre-envío humano | Solo decisiones comerciales, no debugging técnico | 5-10 min máximo |
| D-04 | Registro de caso | Antes/después, hallazgo, solución, resultado | Publicable con permiso |
| D-05 | Seguimiento básico | Revisión 30 días si aplica | Output comparable |

---

## 8. Roadmap comercial, subordinado a validación

La robustez agente no reemplaza la validación comercial.
El roadmap comercial se mantiene, pero con agentes como multiplicador operativo.

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
| G1: Agent readiness | ¿Un agente fresco puede entender y ejecutar sin preguntar? | Mejorar AGENTS/workflows antes de más features |
| G2: Human minimalism | ¿El humano solo decide lo esencial? | Eliminar pasos humanos o moverlos a agente |
| G3: Evidence | ¿Cada claim comercial tiene evidencia? | Bloquear entrega o marcar ESTIMATED |
| G4: Commercial validation | ¿Alguien pagó? | No escalar automatización comercial |
| G5: Cost control | ¿API/cómputo sigue barato? | Activar permission_mode / reducir llamadas |
| G6: Coherence | ¿Diagnóstico, propuesta y assets coinciden? | Bloquear publicación |
| G7: Documentation drift | ¿Docs críticas reflejan realidad actual? | Ejecutar docs cascade / doctor |

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

- 3-5 Express pagos,
- 1 implementación cerrada,
- 5+ debriefs reales,
- objeciones repetidas,
- flujo de entrega manual repetido 10 veces.

---

## 11. Métricas 90 días

### Métricas agent-first

| Métrica | Umbral | Objetivo |
|---------|--------|----------|
| Workflows core sincronizados con README | 100% | 100% |
| Ejecución de fase sin contexto humano adicional | 1 caso | 3 casos |
| Validaciones rápidas post-cambio | Pasa | Pasa consistentemente |
| Outputs con evidencia rastreable | 90% | 95%+ |
| Docs críticas sin drift visible | AGENTS/README/CONTRIBUTING | + ROADMAP alineado |
| Tiempo humano pre-envío | <= 15 min | <= 10 min |

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
| Costos API crecen con automatización | Media | Medio | `permission_mode`, presupuestos y modo fallback |
| Se construye UI antes de tracción | Media | Alto | Gate explícito: no UI pesada hasta 10+ entregas manuales |
| Outputs estimados se venden como verificados | Media | Alto | Taxonomía VERIFIED/ESTIMATED/CONFLICT obligatoria |

---

## 13. Deuda técnica estratégica

1. `spark` está marcado como deprecado, pero puede ser útil para outreach barato. Decisión: mantenerlo solo si se usa comercialmente 10+ veces.
2. Consolidar el rol de `.agents/workflows/` como capa ejecutable, no solo documentación.
3. Reducir duplicación entre README, AGENTS y docs. README debe ser humano-mínimo; AGENTS debe ser agente-operativo.
4. Fortalecer recuperación de fases fallidas para agentes en sesiones frescas.
5. Formalizar smoke test de agent-readiness: un agente nuevo debe poder entender estado, ejecutar validación y explicar siguiente acción.
6. Mantener ROADMAP como documento estratégico manual. No incluirlo en cascadas automáticas salvo solicitud explícita.

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

Grafo de hoteles, competidores, regiones, activos digitales y benchmarks.

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
