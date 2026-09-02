# Contexto: Potencializar iah-cli con Bots — Diagnóstico como Producto, Entrega como Cuello de Botella

> **Fecha:** 2026-09-01
> **Sesión:** análisis de arquitectura de bots para escalar credibilidad y entrega
> **Propósito central:** iah-cli vende diagnóstico, NO una herramienta de IA — el diagnóstico es el producto, la herramienta es invisible para el cliente
> **Archivo retomable:** cualquier sesión futura que hable de bots, Capa 3, Capa 4, delivery, credibilidad, debottlenecking
> **Validado contra el repo (2026-09-01):** citas de código corregidas entonces (13 publication gates, `proposal_asset_alignment.py`, 1 workflow activo). ⚠️ **Dos cifras de esa validación fueron refutadas después:** los "~10 CG-*" son en realidad **12 repartidos en dos archivos**, y los "~308 .py" son en realidad **291 fuente / 284 test** (con `venv/` aportando 7.597 .py dentro del repo). El plan que esta línea anunciaba en §10 **ya no vive ahí**: está en **`ROADMAP.md` §7.2 (FASE T, v4.2)**, con equivalencia de nomenclaturas en **§10.4**.
> **Auditado contra el código vivo (2026-09-02):** la afirmación "10 blocking + 3 advisory" es **falsa en el código** (los 13 gates bloquean) y la lista advisory correcta es de **2 miembros, no 3** — `asset_confidence` debe conservar su bloqueo. Ver **§12** para la corrección medida, la decisión y las tareas que culminan el tema en una sesión nueva. Otras cifras de este documento fueron refutadas en la misma auditoría y están listadas en **§12.7**; no consumir §3 ni §8 sin leerlas antes. **§10 es ahora un stub supersedido**: §10.2 lista lo refutado, §10.3 preserva el detalle que el ROADMAP no replica, §10.4 mapea ambas nomenclaturas.
> **Hallazgos estructurales de la misma auditoría → §13:** seis agujeros vivos (A1-A6, entre ellos G9 que se salta en verde y el oráculo de presencia que no se persiste), el mecanismo causal verificado de `no_breach = 6/7` con la doble falla de mapeo (B1-B5, insumo de la sesión de **punto 8**), tabla consolidada de todas las mediciones (13.4) y los siete falsos positivos corregidos (13.5). **Desde el 2026-09-02 los seis están registrados como deuda en `ROADMAP.md` v4.2 §13** (A1→H9 · A2→H7 · A3→P12 · A4→T0.2 · A5→P10 · A6→§6.4/G11); ya no son hallazgos sin destino.

---

## 1. Tesis central del usuario

- **iah-cli es una herramienta de diagnóstico**, no una herramienta de IA que se vende por sí misma.
- El propósito central: diagnosticar la fuga de reservas directas de un hotel y generar un paquete de assets técnicos que la recuperen.
- Los ingresos actuales son ≤ $65/mes, hay urgencia de caja, primer ingreso ≤ 30 días, tools free, bots WhatsApp Pereira.
- **Estrategia de venta:** vender el diagnóstico (con cifras de fuga en COP), no vender la plataforma.

---

## 2. Las 4 capas de potencialización con bots (análisis completo)

### Capa 1 — Throughput de diagnósticos (más hoteles diagnosticados por semana)

- `v4complete` en ~2 minutos produce diagnóstico + propuesta + assets por hotel.
- Bottleneck: si el humano tiene que orquestar cada corrida, el throughput está limitado por tiempo humano, no por el pipeline.
- **Potencialización:** un agente que recibe una lista de URLs propias de hoteles y ejecuta `v4complete` por cada uno, guardando evidencia en `evidence/fase-N/`. El humano solo revisa los PDFs gancho (`hook-pdf`) y los diagnósticos que superan coherencia ≥ 0.8.
- **Condición previa:** pipeline estable para N hoteles (gates no fallan intermitentemente, datos ESTIMATED no generan propuestas engañosas).

### Capa 2 — Primer contacto comercial automatizado (el gancho)

- `hook-pdf` genera PDF de 2 páginas con cifra de fuga, brechas principales y precios.
- **Potencialización:** agente que (1) ejecuta `v4complete`, (2) si coherence ≥ 0.8 → genera `hook-pdf`, (3) envía PDF + mensaje breve por WhatsApp con cifra de fuga en COP (no técnica, comercial), (4) queda a la espera de respuesta.
- Ataca directamente: **primer ingreso ≤ 30 días**, costo de adquisición mínimo. El bot no vende la herramienta — vende el diagnóstico que la herramienta produce.

### Capa 3 — Onboarding de datos reales (ESTIMATED → VERIFIED)

- **Riesgo crítico:** con datos benchmark (Tier B), las cifras de fuga se inflen 5-15x vs realidad (caso Hotel Luxor documentado: 21 hab, 15 reservas/mes, ADR $200K, 60% directo → fuga realista ~$12K COP/mes; benchmark aplicado → ~$7.6M COP/mes).
- `onboard` captura: rooms, occupancy_rate, direct_channel_pct, adr_from_onboarding — sube confianza ESTIMATED → VERIFIED, assets WARNING → PASSED.
- **Potencialización:** bot que, tras enviar hook-pdf, lleva diálogo de 3-4 preguntas para capturar datos operativos reales y ejecutar `onboard`. Con esos datos, re-corre `v4complete` en modo Tier A y genera propuesta con cifras verificadas.
- **Importante:** el bot no reemplaza al humano que recoge datos — es formato estructurado para que el hotel los proporcione sin friction. El humano interviene cuando datos no son consistentes.
- **Orden de prioridad según usuario:** Capa 3 es fundamental porque la calidad del diagnóstico es el eje central. Si el diagnóstico es erróneo, la credibilidad del producto se destruye.

### Capa 4 — Entrega y despliegue (CUELLO DE BOTELLA PRINCIPAL SEGUN USUARIO)

- El proceso de despliegue e inserción en la infraestructura del cliente es **totalmente manual**.
- Ejemplo concreto: `output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/hotelsalentoreal_20260831/` — paquete generado pero sin verificación de despliegue real.
- **Potencialización:** conjunto de agentes que cierran el ciclo desde decisión de entregar hasta verificación de que quedó en producción.

---

## 3. Análisis de la entrega de SalenteReal (2026-08-31)

### Estado de la entrega

| Señal | Valor |
|-------|-------|
| `evidence_tier` | **B** (datos públicos + benchmark, sin onboarding) |
| `precision_tier` | **C** (sin datos operativos reales) |
| `onboarding_used` | `false` |
| `coherence_score` | 0.913 (≥ 0.8 threshold → propuesta generada) |
| Total archivos en MANIFEST | 37 |
| Entrega tipo | Directorio expandido, no ZIP empacado |

**Coherente internamente** — diagnóstico, propuesta, assets, gates cuadran. El diagnóstico no es erróneo, pero es Tier B/C.

### Contenido del paquete

```
ASSETS/
├── analytics_setup_guide/       → guía GA4 (ESTIMATED, confidence 0.80)
├── geo_enriched/                → FAQ schema, llms.txt, robots_fix, seo_fix_kit, geo_dashboard, etc.
├── indirect_traffic_optimization/ → guía optimización (ESTIMATED, confidence 0.80)
├── llms_txt/                    → llms_20260831_122803.txt (confidence 1.00)
├── monthly_report/              → informe_mensual (confidence 1.00)
├── v4_audit/                    → 13 archivos de auditoría interna
└── research_*.json              → investigación inicial
```

- Assets con **confidence 1.00** (llms.txt, monthly_report, research.json): independientes de datos del hotel, se generan desde URL + benchmarks.
- Assets **ESTIMATED** (analytics, indirect_traffic): dependen de parámetros inferidos.

### Estado del deploy en el código

- **`execute`** (`modules/delivery/manager.py`): genera assets por paquete (`starter_geo`, `pro_aeo`, `elite`) → escribe a `output/delivery_assets/` → genera `manifest.json`, `README_DELIVERY.md`, `IMPLEMENTATION_ORDER.md` (vacío en este caso) → **no toca el servidor del cliente**.
- **`deploy`** (`modules/deployer/manager.py`): acepta `ftp` o `wp-api` → valida credenciales → build plan de acciones (upload, inject_code, create_post) → pero:
  - **FTP connector:** `upload_file` → `"no disponible en v2.5 MVP"`. `inject_code` → `"no soportada vía FTP"`.
  - **WP connector:** `inject_code` → `"requiere plugin (ej. WPCode) o endpoint habilitado. No ejecutado"`. Solo `create_post` está implementado (crea draft, no publica ni inyecta en header/footer).
  - **dry_run=True por defecto** — todo es simulación.
- **`IMPLEMENTATION_ORDER.md`** (27 líneas, vacío de contenido): el `AssetResponsibilityContract.generate_delivery_template()` no encontró `core_assets` ni `geo_assets` explícitos.
- **`site_verification_applied: false`** — nada se verificó en producción.
- **No hay registro de qué se entregó, a quién, con qué compromiso.**

### Los 3 niveles del problema de Capa 4

1. **Nivel 1 — Conector no ejecuta:** FTP/upload_file e inject_code devuelven error "no disponible en MVP". WP/inject_code requiere plugin. Solo create_post funciona (y solo draft).
2. **Nivel 2 — CMS desconocido:** el `DeployInstructionsGenerator` escribe guías para WordPress, Wix, Squarespace y genérico — pero CMS se detecta desde `hotel_data.cms_detected`. En SalenteReal, no hay evidencia de que se capturara. Sin CMS conocido, el bot no puede elegir guía correcta ni ejecutar deploy.
3. **Nivel 3 — Entrega es directorio local, no proceso con responsabilidad:** `IMPLEMENTATION_ORDER.md` vacío, `README_DELIVERY.md` dice "Week 1: Deploy..." con checkboxes para el hotel, no hay registro de entrega ni verificación post-deploy.

---

## 4. Qué NO resolvería un bot (límites honestos)

- **No puede desplegar sin credenciales** — si el hotel no da acceso, deploy es manual o lo hace el hotel con la guía. No es bug, es límite del modelo.
- **No puede garantizar que el hotel mantenga los assets** — si reemplaza sitio, cambia de CMS, o nunca instala, el bot detecta pero no resuelve.
- **No puede vender por ti** — primer contacto, negociación, aprobación de deploy son humanos. Bot potencializa ejecución, no cierre.
- **No puede mejorar calidad del diagnóstico más allá de lo que permiten los datos** — si hotel no da datos reales, diagnóstico sigue siendo Tier B. Bot puede invitar al onboarding, no inventar datos.
- **No valida si el diagnóstico es correcto en absoluto** — solo verifica coherencia interna. Corrección viene de datos reales (onboarding, Tier A) y verificación contra sitio vivo.

---

## 5. Concepto: Tribunal de Revisión Multi-Bot (para credibilidad)

### Tesis
Un grupo de bots de revisión es la capa de credibilidad que falta entre "paquete generado" y "paquete entregable con responsabilidad." No es "un bot hace todo" — es "cada bot revisa una capa con criterio explícito, y un bot juez decide si el paquete pasa o devuelve."

### Los 5 bots del tribunal

#### Bot 1 — Revisor de Diagnóstico Interno
- **Entrada:** `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` + `coherence_validation.json` + `pain_ledger.json` + `pain_ledger_resolved.json`
- **Revisa:** brechas diagnosticadas aparecen en pain_ledger con pain_id trazable; cada brecha tiene fuente declarada; cifras de fuga calculadas desde inputs declarados; diagnóstico no afirma cosas que gates no pudieron validar; brechas críticas con prioridad correcta.
- **Salida:** `revision_diagnostico.json` con hallazgos por severidad + veredicto (APROBADO / DEVOLVER-PRUEBAS / BLOQUEAR).
- **Existente hoy:** `coherence_validation.json` + `pain_ledger` son los artefactos. Lógica de validación cruzada en `modules/data_validation/cross_validator.py` y `modules/auditors/`. Lo nuevo: agente que **lea esos artefactos y produzca reporte de hallazgos en lenguaje humano + JSON**, no solo pass/fail del gate.

#### Bot 2 — Revisor de Alineación Diagnóstico → Propuesta
- **Entrada:** `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` + `02_PROPUESTA_COMERCIAL.md` + `proposal_asset_matrix.json` + `pain_ledger_resolved.json`
- **Revisa:** cada servicio vendido responde a una brecha diagnosticada (o oportunidad derivada); no hay servicios sin brecha asociada; cada brecha tiene al menos una recomendación o se explica por qué se descarta; precios consistentes con costos estimados; narrativa de impacto coherente con base de cálculo.
- **Salida:** `revision_alineacion.json` con matriz servicio → brecha → pain_id (ALINEADO / SIN-BRECHA-ASOCIADA / BRECHA-SIN-PROPUESTA) + veredicto.
- **Existente hoy:** `modules/asset_generation/proposal_asset_alignment.py` genera la matriz servicio→pain_id (artefacto `proposal_asset_matrix.json`). Gates incluyen `proposal_asset_alignment` (uno de los 13 publication gates). **Lo nuevo:** revisor que **lea propuesta en lenguaje natural y verifique que lo prometido verbalmente corresponda a la matriz** (la propuesta puede prometer algo que no quedó en la matriz).

#### Bot 3 — Revisor de Completitud de Assets
- **Entrada:** `asset_generation_report.json` + `delivery_quality_report.json` + `MANIFEST.json` + archivos reales en `ASSETS/`
- **Revisa:** cada servicio de propuesta tiene al menos un asset generado o presente en producción; assets no son genéricos (mencionan hotel, brecha específica, punto de implementación); assets con `can_use: false` o `preflight_status: BLOCKED` no se presentan como entregables listos; assets `ESTIMATED` están explícitamente etiquetados en README; no hay assets huérfanos.
- **Salida:** `revision_assets.json` con cobertura por servicio (CON-ASSET / SIN-ASSET / ASSET-GENERICO / ASSET-ESTIMATED-NO-ETIQUETADO) + veredicto.
- **Existente hoy:** `delivery_quality_report.json` + gates G8 (asset_confidence, asset_specificity). `DeliveryContext` clasifica assets por estado. **Lo nuevo:** revisor independiente que **produzca reporte legible antes de entrega**, no solo gate interno.

#### Bot 4 — Revisor de Honestidad Comercial
- **Entrada:** `financial_scenarios.json` + `commercial_gates_report.json` + `02_PROPUESTA_COMERCIAL.md` + `quality_metadata` del MANIFEST
- **Revisa:** cifras de fuga y proyecciones tienen `evidence_tier` declarado; propuesta no presenta ESTIMATED como verificado; escenarios son los 3 declarados (70/20/10), no solo el favorable; claims de "recuperación en X meses" tienen base de cálculo visible; no hay contradicciones entre propuesta y gates financieros.
- **Salida:** `revision_honestidad.json` con hallazgos de presentación engañosa + veredicto.
- **Existente hoy:** ~10 commercial gates (CG-*) en `modules/quality_gates/commercial_gate.py` — 6 blocking (CG-SCENARIO-ORDER, CG-SCENARIO-NEGATIVE, CG-IA-BLOCKED-CLAIM, CG-ROI-NEGATIVE, CG-CLAIM-VS-EVIDENCE, CG-EVIDENCE-TIER-CONSISTENCY) + 4 warning (CG-WHATSAPP-LEAD, CG-OTA-NARRATIVE, CG-TIER-CONSISTENCY, CG-TECH-JARGON) — y `financial_engine` generan escenarios con `EvidenceConfidence`. `DisclaimerGenerator` produce descargos. **Lo nuevo:** revisor que **lea propuesta y verifique que no sobre-presente lo que los datos soportan**, cubriendo los ~10 CG-* (no solo 4). El LLM solo *propone* hallazgos de sobre-presentación; el Juez aplica veredicto determinista contra tier labels y CG-* (ver **ROADMAP §7.2 T4**; antes §10 Etapa 4). ⚠️ El conteo "~10 CG-*" de esta línea fue refutado: son **12 repartidos en dos archivos** (§12.7, ROADMAP §7.2).

#### Bot 5 — Juez / Agregador
- **Entrada:** 4 reportes de revisión + gate_report + delivery_quality_report
- **Hace:** determina si paquete pasa para entrega, requiere corrección, o está bloqueado; produce **acta de revisión** legible (no solo JSON) que puede incluirse en entrega o presentarse al hotel como evidencia de rigor; identifica qué hallazgos son bloqueantes vs consultivos; propone acciones correctivas específicas.
- **Salida:** `acta_revision.json` + `acta_revision.md` con veredicto final (APROBADO-PARA-ENTREGA / **APROBADO-CONDICIONAL-PENDING-ONBOARDING** / DEVOLVER-CORRECCIONES / BLOQUEADO), resumen ejecutivo, hallazgos por severidad con referencia al bot detectador, acciones correctivas recomendadas con prioridad.
- **Regla determinista de primer piso (P6.5 + gap G0):** si `evidence_tier ∈ {B, C}` (datos benchmark, sin onboarding), el veredicto máximo es `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; **nunca** `APROBADO-PARA-ENTREGA`. Coherencia interna alta (ej. SalenteReal 0.9133) NO basta: el primer piso solo cierra con datos reales (Tier A, assets ≥ 0.8). Sin LLM.

### Qué añade el tribunal que el sistema actual no hace

| Lo que existe hoy | Lo que añade el tribunal |
|-------------------|--------------------------|
| Gates internos que deciden publicar o no | Reportes explícitos de **qué se revisó y qué se encontró**, legibles por humano y cliente |
| `delivery_quality_report.json` interno | Acta de revisión que puede ir en la entrega como evidencia de rigor |
| Coherencia verificada por módulos en pipeline | **Auditoría independiente** — revisores no son los mismos módulos que generaron contenido |
| Gate bloqueando ZIP si hay problemas | Veredicto granular: bloquear, devolver para corrección, o aprobar con observaciones |
| Cifras con `evidence_tier` en datos | Revisor que verifica que **presentación al cliente respeta nivel de confianza** |

La diferencia clave: hoy el pipeline genera y valida internamente. Con el tribunal, hay una **capa de accountable review** que produce evidencia explícita de que el diagnóstico es coherente, la propuesta responde a brechas reales, y los assets cierran lo prometido.

> **Regla arquitectónica inviolable (no re-ejecutar gates):** el tribunal **NO reimplementa lógica de gates**. Los 13 publication gates + ~10 CG-* ya codifican las 6 cláusulas de P6 (mapeo abajo). El tribunal *lee los outputs* (`gate_report.json`, `commercial_gates_report.json`, `delivery_quality_report.json`, `pain_ledger*.json`, `proposal_asset_matrix.json`) como revisor independiente y produce evidencia legible. Re-implementar checks que ya existen en `publication_gates.py` / `commercial_gate.py` reproduciría el drift de fuente-única que se resolvió en FASE-SR-B. El valor del tribunal = **independencia + legibilidad + verificación de lenguaje natural** (lo único que ningún gate cubre: promesas verbales fuera de la matriz, sobre-presentación de ESTIMATED como verificado).

### Mapeo P6 ↔ Bots ↔ Gates (fuente única de responsabilidad)

| Cláusula P6 (ROADMAP línea 195) | Gate que YA la ejecuta | Bot responsable |
|---|---|---|
| P6.1 N brechas cubiertas o justificadas | `coverage_no_silent_drop` | Bot 1 |
| P6.2 brecha priorizada → recomendación comercial | `pain_solution_mapper` + `proposal_asset_alignment` | Bot 2 |
| P6.3 recomendación vendida → asset específico trazable | `proposal_asset_alignment` | Bot 3 |
| P6.4 ningún asset genérico como solución terminada | `asset_confidence` | Bot 3 |
| P6.5 datos faltantes → ESTIMATED/PENDING/CONFLICT | `tier_c_onboarding_required` + `CG-EVIDENCE-TIER-CONSISTENCY` | Bot 4 |
| P6.6 entrega bloqueada si se contradicen | `coherence` + `hard_contradictions` | Bot 5 (Juez) |

### Orden de construcción

El orden **ya no es mecánico-first**. Está anclado en el principio P6 del ROADMAP ("primer piso obligatorio") y se detalla en **`ROADMAP.md` §7.2 (FASE T)** — antes §10 de este documento, hoy stub supersedido: primero las **precondiciones medidas T0.1-T0.4**, luego el Juez certificador del contrato P6 (T1), después los revisores que alimentan cláusulas P6 específicas, descendiendo hasta onboarding, deploy y escala. Equivalencia Etapa↔T en **§10.4**.

---

## 6. Artefactos existentes relevantes para el tribunal

### Para Bot 1 (diagnóstico interno)
- `output/<corrida>/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/coherence_validation.json`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/pain_ledger.json`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/pain_ledger_resolved.json`

### Para Bot 2 (alineación diagnóstico-propuesta)
- `output/<corrida>/v4_complete/02_PROPUESTA_COMERCIAL_*.md`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/proposal_asset_matrix.json`
- `modules/asset_generation/proposal_asset_alignment.py` (genera el artefacto `proposal_asset_matrix.json`)

### Para Bot 3 (completitud de assets)
- `output/<corrida>/v4_complete/<hotel>/v4_audit/asset_generation_report.json`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/delivery_quality_report.json`
- `output/<corrida>/v4_complete/deliveries/<hotel>_<fecha>/MANIFEST.json`
- Archivos reales en `output/<corrida>/v4_complete/deliveries/<hotel>_<fecha>/ASSETS/`

### Para Bot 4 (honestidad comercial)
- `output/<corrida>/v4_complete/<hotel>/v4_audit/financial_scenarios_*.json`
- `output/<corrida>/v4_complete/<hotel>/v4_audit/commercial_gates_report.json` (si existe)
- `modules/commercial_documents/` (DisclaimerGenerator)
- `modules/financial_engine/scenario_calculator.py`

### Módulos base del pipeline (para entender qué ya valida)
- `modules/data_validation/cross_validator.py` — validación cruzada de datos
- `modules/quality_gates/publication_gates.py` — 13 publication gates. **Documentados como "10 blocking + 3 advisory" (líneas 4 y 162) pero el código no implementa la distinción: los 13 bloquean** (`check_publication_readiness:1967`). Lista advisory correcta = **2**, no 3. Ver §12.
- `modules/quality_gates/commercial_gate.py` — ~10 commercial gates CG-* (6 blocking + 4 warning)
- `modules/quality_gates/delivery_quality_report.py` — QA post-generación
- `modules/quality_gates/human_checklist_generator.py` — checklist ≤10 items
- `modules/asset_generation/pain_ledger.py` — PainLedger facade
- `modules/asset_generation/data_derivation_layer.py` — 5 derivaciones del audit

---

## 7. Riesgos de potencialización sin cerrar primero la calidad

1. **Tier B con mismatch de perfil** — bot diagnostica hoteles con benchmark y presenta cifras infladas. El diagnóstico pierde credibilidad, el producto vuelve a ser "tecnología de IA sin valor medible." El `onboard` es obligatorio antes de vender, no después.
2. **Commercial gates ocultos** — ~10 CG-* gates corren en segundo plano (6 blocking + 4 warning, ver §5 Bot 4). Un bot que solo revisa `gate_report.json` pasa por alto los 4 warning (CG-WHATSAPP-LEAD, CG-OTA-NARRATIVE, CG-TIER-CONSISTENCY, CG-TECH-JARGON) que afectan lo comercial.
3. **Costo por diagnóstico** — cada corrida usa APIs (Places, serp, LLM). Si potencializas volumen sin controlar costo, margen del diagnóstico se desvanece. Roadmap: "si costo real por diagnóstico amenaza margen, reducir llamadas / fallback barato / revisión de precio."
4. **Evidencia, no narrativa** — cualquier bot que frote diagnósticos debe dejar evidencia en `evidence/` y `output/v4_complete/<hotel>/v4_audit/` para que se pueda auditar qué se vendió y con qué confianza.

---

## 8. Estado del proyecto relevante (v4.74.1, 31 Agosto 2026)

- **FASE 0 completada** — delivery quality capaz de bloquear entregas incoherentes (8 sub-fases 0A-0H + RELEASE)
- **PIPELINE-FIX completada** — assessment dict bridge + delivery_ready formula corregidos
- E2E Hotel Castilla Real: coherence **0.8261**, coverage PASS, 10/12 assets ≥ 0.65
- Pendiente: G0 requiere todos los assets ≥ 0.8 para cerrar primer piso; algunos dependen de datos reales de onboarding, no de código
- 24 módulos, 10 configs YAML, 1 workflow activo (`phased_project_executor.md`; los 16 restantes archivados el 2026-08-24), ~308 archivos Python sin tests (604 con tests)
- `IMPLEMENTATION_ORDER.md` vacío en entregas actuales (bug del `AssetResponsibilityContract` cuando no recibe core_assets/geo_assets explícitos)
- `modules/deployer/` en MVP v2.5 — solo validación de credenciales, sin ejecución real de upload/inject_code (dry_run por defecto)
- Roadmap v3.6 (2026-06-09): agent-first, human-minimal; principio "el humano define intención y límites; el agente transforma esa intención en ejecución verificable"

---

## 9. Preguntas abiertas — resueltas por el plan (hoy `ROADMAP.md` §7.2; antes §10)

> ⚠️ Las cinco resoluciones siguen siendo la respuesta correcta a la pregunta que las originó, pero **dos quedaron parcialmente refutadas por la auditoría del 2026-09-02** en su mecanismo de implementación: la **2** (el anfitrión `two_phase_flow.py` / FASE 5.5 no existe como orquestador de producción) y la **3** (`publication_state.py` está huérfano). Están marcadas en su lugar. Equivalencias en **§10.4**.

1. **Capa 3 primero o Capa 4 primero?** — El usuario enfatizó que calidad del diagnóstico es el eje central (Capa 3), pero identificó Capa 4 como cuello de botella real. El orden de ejecución afecta cuál es el primer bot a construir.
   → **Resolución (§10):** Capa 3 (Etapa 3) va ANTES que Capa 4 (Etapa 5). Justificación P6: un paquete Tier B/C no cierra el primer piso y desplegar assets no verificados viola P6.5. Para el primer ingreso ≤30 días la restricción real es **credibilidad**, no volumen de deploy.
2. **¿El tribunal de revisión es un agente orquestado por el AgentHarness existente, o un conjunto de scripts independientes?** — Determina la arquitectura de implementación.
   → **Resolución (§10):** módulo gate-family (`modules/quality_gates/tribunal/`) orquestado por `orchestration_v4` como **FASE 5.5** post-`delivery_quality_report`; NO scripts sueltos (evita drift, reutiliza loaders, la evidencia cae en `v4_audit/`). Cada bot = clase revisora independiente y testeable.
   → ⚠️ **Parcialmente refutada (2026-09-02):** la decisión de *gate-family, no scripts sueltos* y el destino de la evidencia en `v4_audit/` **siguen en pie**. El **anfitrión no**: `orchestration_v4/two_phase_flow.py` no es el orquestador de producción (solo lo importan `onboarding_controller.py` por sus tipos, el `__init__` y tests), así que la FASE 5.5 no existe como punto de integración. **Elegir anfitrión real es precondición de T1**; el natural es `main.py` junto a `delivery_quality_report` (FASE 7, `:3178-3200`), que es donde hoy ya se decide el ZIP. Ver ROADMAP §7.2 y deuda **H8**.
3. **¿El acta de revisión va en la entrega al hotel como evidencia de rigor, o es solo un gate interno?** — Cambia el diseño del Bot 5 y el valor comercial del tribunal.
   → **Resolución (§10):** **dual** — gate interno (alimenta `publication_state`, puede bloquear ZIP) Y documento cliente-facing (evidencia de rigor vendible: "diagnóstico auditado con acta firmada").
   → ⚠️ **Parcialmente refutada (2026-09-02):** el **acta dual sigue en pie** y es la decisión correcta. El destino interno no: `publication_state.py` está **huérfano** (sin importadores fuera de sí mismo) ⟹ o se le da llamador real o no se cita como destino (deuda **H8**). Y el bloqueo del ZIP **no es un punto único**: hoy existen **tres rutas** (`main.py:3194`, `:3205`, `:3274`) más el kill switch `GATE_BLOCKING_ENABLED` (`:2990-2992`); el veredicto del Juez debe **alimentar una de las tres, no añadir una cuarta** (deuda **H9**). Que el acta viaje al ZIP del cliente requiere además lista blanca explícita — `delivery_packager.py:337` excluye reports internos por prefijo (deuda **P6**).
4. **¿Qué nivel de inferencia es aceptable para Bot 2 y Bot 4?** — Verificar alineación propuesta-brecha requiere leer lenguaje natural. ¿Se puede hacer con prompts estructurados al LLM del pipeline, o requiere lógica adicional?
   → **Resolución (§10, Etapa 4):** **híbrido acotado** — el LLM solo *extrae* promesas/claims en lenguaje natural; una capa determinista los *verifica* contra artefactos (matriz, tier labels, CG-*). El LLM propone hallazgos, el Juez aplica veredicto. Nunca es juez de registro (preserva auditabilidad P3).
5. **¿El primer ingreso objetivo (≤30 días, ≤$65/mes actual) cambia si el tribunal añade un paso de revisión antes de entregar?** — Afecta la urgencia y el diseño del flujo.
   → **Resolución (§10):** no, si el tribunal es de costo marginal ~0: Bots 1/3/5 son deterministas (sin LLM); solo Bot 2/4 usan LLM barato + cache. El `hook-pdf` de prospección corre en paralelo (es pre-contrato, no entrega). El tribunal **acelera** el primer ingreso al volver el diagnóstico defendible.

---

## 10. Plan de implementación — SUPERSEDIDO por ROADMAP §7.2 (FASE T)

> ⚠️ **Esta sección ya no es el plan de registro.** El 2026-09-02 fue sustituida por **`ROADMAP.md` §7.2 "FASE T: Tribunal certificador del contrato P6 + P7"** (v4.2), que incorpora las correcciones verificadas contra código vivo y artefactos reales. ROADMAP §7.2 ya advertía que este §10 estaba parcialmente refutado; **el enlace ahora es simétrico**.
>
> **Para ejecutar, leer ROADMAP §7.2.** Lo que sigue se conserva por dos motivos y solo dos: registrar **qué fue refutado** (§10.2, para no reutilizarlo) y preservar el **detalle de implementación que el ROADMAP no replica** (§10.3). El diseño por bot sigue vivo en **§5** de este documento, que no fue refutado.

### 10.1 Por qué dejó de ser el plan

Tres cambios de fondo, todos medidos el 2026-09-02 sobre los artefactos de la corrida SalenteReal 2026-08-31:

1. **El orden estaba invertido.** §10 proponía Etapa 1 → Etapa 6 sin precondiciones. ROADMAP §7.2 establece **T0.1-T0.4 ANTES de T1**. Medido: tocar el denominador de `coverage_ratio` antes de convertirlo en divulgación advisory **bloquea en 10/10 configuraciones** (rango 0.125-0.714) y es insatisfacible por medios honestos; y unificar el registro 7→8 antes de eso **empeora alignment 0.571 → 0.500** a cambio de **Δcoherence = 0.0000 exacto**. Hacerlo en el orden de §10 era pagar el costo sin recibir el beneficio.
2. **FASE T no es una fase lineal.** ROADMAP v4.2 la parte en **tramo offline** (T0/T1/T2/T4 — certificable ya contra los artefactos de SalenteReal, sin nada externo) y **tramo externo** (T3 datos operativos reales del hotel · T5 credenciales FTP/WP + staging · T6 escala sobre los dos). §10 no hacía la distinción, así que se leía como deuda de implementación lo que en realidad es **falta de acceso**.
3. **Debajo del plan hay una causa raíz que §10 no ve.** El ledger resuelto tiene **3 pains** y el orquestador genera **4 assets**, de los cuales **2 son huérfanos**, y **6 de 7 servicios prometidos responden a pains que no se detectaron**. Esa única causa produce a la vez `no_breach = 6/7` **e** `is_coherent = false` (`assets_are_justified` 3/4 = 0.75). La **propuesta dinámica** — solo prometer servicios con brecha detectada — cierra ambos síntomas y hace `no_breach = 0` por construcción. Todo lo que §10 proponía (advisory, remapeos, orden de etapas) es parche sobre un contrato comercial que sigue vendiendo lo que no diagnostica. Ver ROADMAP §7.2 *"Causa raíz por debajo de T0"* y §13.2 de este documento.

### 10.2 Claims de esta sección que fueron refutados — no reutilizar

| §10 decía | Verificado contra código/artefactos el 2026-09-02 | Dónde vive ahora |
|---|---|---|
| Anclaje en "ROADMAP §P6 (**línea 195**)" | La reestructura v4.1/v4.2 movió todo el documento. **Referir por sección, nunca por línea** | ROADMAP §4 (P6), §7.2 |
| Integración desde `two_phase_flow.py` como **FASE 5.5** | Ese módulo **no es el orquestador de producción**: solo lo importan `onboarding_controller.py` (que usa únicamente sus tipos), el `__init__` del paquete y tests. **Elegir anfitrión real es precondición de T1**; el natural es `main.py` junto a `delivery_quality_report` (FASE 7, `:3178-3200`) | ROADMAP §7.2 |
| El Juez lee `gate_report.json` y `commercial_gates_report.json` con "**~10 CG-***" | Los nombres son **timestamped y sin índice** (`gate_report_20260831_122803.json`). El reporte comercial está **partido en 3 + 9**: el archivo de nombre canónico trae 3 gates en verde y el único que falló en la corrida real (**`CG-WHATSAPP-LEAD`**, WARNING) está en el diagnóstico que §10 no leía. Conteo real: **12 `CG-*`** | ROADMAP §7.2 + deuda **H7** |
| El veredicto **alimenta `publication_state.py`** | Módulo **huérfano**, sin importadores fuera de sí mismo (igual que `coherence_gate.py`) | ROADMAP §9 + deuda **H8** |
| Coherence de SalenteReal **0.9133** | Es el `pre_coherence_score` **no canónico** (regresión DT4-N4). El canónico es **0.88** (`coherence_score_pre/post/final` en `asset_generation_report.json`) | ROADMAP §7.1 |
| "**37 archivos**" como el paquete entregado | El ZIP pesa **46.552 bytes**; los 37 archivos son el **directorio expandido** | ROADMAP §7.1 |
| `pain_ledger.json` como fuente suficiente para el Bot 1 | **No serializa la clave `assets`** (`pain_ledger_resolved.json` trae `assets: null` en las 3 entradas) ⟹ la matriz **no es reproducible desde disco** | ROADMAP §7.2 + **H7** |
| **Definition of Done única** (a)-(e) | **Insatisfacible en este repo**: la cláusula (c) depende de infraestructura del cliente (T5 + deuda P1), así que un Done único vuelve incerificable también el tramo offline | ROADMAP §7.2 **DoD-técnico / DoD-comercial** |
| Margen de costo en "ROADMAP **línea 229-231**" | Referencia por línea, stale | ROADMAP §5 |
| Etapa 3 cierra el primer piso | Cierra **una** precondición. G0 exige además `evidence_tier: A` + assets ≥ 0.8 + acta `APROBADO-PARA-ENTREGA`, y hoy está **NO CERRADO** | ROADMAP §9 (G0) |

### 10.3 Detalle de implementación que el ROADMAP no replica

Único contenido de la §10 original que sigue siendo útil y **no** está en ROADMAP §7.2:

- **Tests:** `tests/quality_gates/tribunal/`, con contrato I/O explícito por bot.
- **Convención de evidencia:** todo artefacto del tribunal cae en `output/<corrida>/v4_complete/<hotel>/v4_audit/` (principio P3).
- **Rutas de módulo para T3 (onboarding):** `modules/orchestration_v4/onboarding_controller.py` y `modules/onboarding/`; el humano interviene solo si los datos son inconsistentes.
- **Rutas de módulo para T5 (deploy):** CMS detection en `modules/delivery/generators/deploy_instructions_gen.py`; conectores en `modules/deployer/connectors/ftp_connector.py` (`upload_file`) y `wordpress_connector.py` (`inject_code`).
- **Vocabulario de Bot 2:** marca `promesa-sin-matriz` y `SIN-BRECHA-ASOCIADA` — el segundo no está nombrado en ROADMAP T4.
- **Regla de dependencia fina:** Bot 1 y Bot 3 enchufan al acta del Juez, así que T1 debe tener contrato de acta estable antes de T2/T4 (ROADMAP lo da por supuesto en el orden de la tabla).
- **Diseño completo de Bot 1-5** (responsabilidad, entradas, salidas, qué añade cada uno): **§5** de este documento. No fue refutado.

### 10.4 Equivalencias de nomenclatura — este documento ↔ ROADMAP v4.2

Dos vocabularios describen **el mismo plan**. Esta tabla es el puente; **la columna ROADMAP es la autoritativa**.

| Etiqueta en este documento | Equivalente en ROADMAP v4.2 | Nota |
|---|---|---|
| §10 Etapa 1 — Juez certificador | **T1** | tramo offline |
| §10 Etapa 2 — revisores mecánicos (Bot 1, Bot 3) | **T2** | tramo offline |
| §10 Etapa 3 — onboarding (Capa 3) | **T3** | **tramo externo**: datos reales del hotel |
| §10 Etapa 4 — revisores NL (Bot 2, Bot 4) | **T4** | tramo offline (LLM mockeado en tests) |
| §10 Etapa 5 — entrega/deploy (Capa 4) | **T5** | **tramo externo**: FTP/WP + staging + deuda **P1** |
| §10 Etapa 6 — throughput + gancho (Capa 1/2) | **T6** | **tramo externo**: escala sobre T3 y T5 |
| *(inexistente en §10)* | **T0.1-T0.4** | precondiciones medidas; van **ANTES** de T1 |
| §12.3 / §12.5 escenario **S2.3** (denominador = `total`) | **T0.1** | ROADMAP ya usa la etiqueta S2.3; descartado como bloqueante |
| §13.1 **A4** — doble oráculo de presencia | **T0.2** | no voltea ningún veredicto en 10/10 |
| §13.1 **A5** — skip silencioso + dos builders | **P10** extendido | trampa de falso negativo para **T0.3** |
| §13.2 bloque B — mecanismo causal de `no_breach = 6/7` | §7.2 **"Causa raíz por debajo de T0"** | dos derivaciones independientes que coinciden |
| §12.7 **N11** — el gate ignora `is_coherent` | **T0.4** + deuda **P9** | la deuda de producto más grave abierta |
| §13.1 **A1** — G9 se salta en verde | **H9** extendido | latente, no observado |
| §13.1 **A2** — oráculo de presencia no persistido | **H7** extendido | vuelve **T0.2** no retro-testeable |
| §13.1 **A3** — `promised_assets_exist` solo pre-gen | **P12** + §6.4 *"Nota pre-gen (P6.3)"* | mecanismo del Δcoherence 0.0000 |
| §13.1 **A6** — `asset_path: null` | §6.4 + **G11** + criterio de **T2** | P6.3 no verificable desde el artefacto |
| §12.3 decisión **advisory = 2, no 3** | §6.4 tabla *"Objetivo decidido"* + **H10** | `asset_confidence` **conserva** el bloqueo |
| §10 Definition of Done única | **DoD-técnico / DoD-comercial** | partida en v4.2 |
| §9 preguntas abiertas 1-5 | resueltas en ROADMAP §4, §6.4, §7.2, §8, §9 | ⚠️ las resoluciones 2 y 3 de §9 quedaron refutadas (§10.2) |
| §8 estado del proyecto v4.74.1 | `VERSION.yaml` + `python scripts/doctor.py --status` | fuente única; no replicar |

---

## 11. Referencias rápidas

- Proyecto: `/mnt/c/Users/Jhond/Github/iah-cli`
- Entrega analizada: `output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/hotelsalentoreal_20260831/`
- README: `README.md` (inicio rápido, comandos, escenarios financieros, arquitectura del repo)
- ROADMAP: `ROADMAP.md` (estrategia agent-first, norte, clasificación repositorio, contrato de producto, 90 días)
- DOMAIN_PRIMER: `.agent/knowledge/DOMAIN_PRIMER.md` (módulos, clases clave, referencias)
- Skills (referencia histórica — NO verificadas como artefacto vivo en el repo; solo aparecen en este doc y en plans archivados): `iah-cli-v4complete-workflows`, `iah-cli-execution-conventions`, `iah-cli-v4complete-delivery-validation`
- Config: 10 archivos YAML en `config/` (`pricing.yaml`, `scenarios.yaml`, `financial_defaults.yaml`, `fallbacks.yaml`, `commercial.yaml`, `regional_benchmarks.yaml`, `certificates.yaml`, `provider_registry.yaml`, `settings.yaml`, `url_blocklist.yaml`)

---

## 12. Corrección medida — la lista advisory es de 2, no de 3 (auditado 2026-09-02)

> **Estado:** decisión tomada, **no implementada**. Ningún archivo de código fue modificado durante la auditoría. Esta sección es autocontenida: una sesión nueva puede ejecutarla sin leer la conversación que la produjo.

### 12.1 El hecho a corregir

El repo dice cosas incompatibles sobre la severidad de sus 13 publication gates:

| Lugar | Qué afirma | Realidad |
|---|---|---|
| `AGENTS.md` (tabla "Módulos Activos", fila `quality_gates/`) | 10 blocking + **3 advisory** (`content_quality`, `asset_confidence`, `proposal_asset_alignment`) | Falso en el código |
| `publication_gates.py:4` (docstring de módulo) | "13 publication gates (10 blocking + 3 advisory)" | Falso |
| `publication_gates.py:162` (docstring de clase) | "manages 10 blocking gates and 3 advisory gates" | Falso |
| `publication_gates.py:1967-1968` `check_publication_readiness` | — | `blocking_gates = [r for r in results if not r.passed]` / `ready = len(blocking_gates) == 0` → **los 13 bloquean**; el concepto advisory no existe |
| `publication_gates.py:239-249` `get_blocking_gates` | — | `return [r for r in results if not r.passed]` — idéntico, vestigial |
| `delivery_quality_report.py:289` | `BLOCKING_GATE_NAMES = ("coherence", "coverage", "evidence", "proposal_asset_alignment")` | **Tercer régimen**: aquí `proposal_asset_alignment` SÍ es bloqueante explícito |

Resultado: **cuatro regímenes contradictorios** para la misma severidad. El único lugar del repo donde la distinción blocking/advisory está realmente implementada es `commercial_gate.py:99-113` (`BLOCKING_GATE_IDS` de 6 + `WARNING_GATE_IDS` de 4) — **ese es el patrón a copiar**.

### 12.2 Evidencia medida — por qué `asset_confidence` no puede ser advisory

Corpus completo de corridas históricas en `output/`: **29 corridas únicas, 10 hoteles**.

**4 de 29 (14%) tienen 100% de assets ESTIMATED** — exactamente el caso que `asset_confidence` bloquea en `publication_gates.py:802-820`:

| Hotel | Fecha | ESTIMATED / total | `coherence_score_final` |
|---|---|---|---|
| `hotel_visperas` | 2026-04-05 | 9/9 | `None` |
| `hotelvisperas` | 2026-04-04 | 9/9 | `None` |
| `hotel_vísperas` | 2026-03-26 | 6/6 | `None` |
| `hotelvisperas` | 2026-03-25 | 6/6 | `None` |

Las cuatro comparten `coherence_score_final = None`: no hay score canónico que las rescate. Si `asset_confidence` fuera advisory, **el 14% del histórico saldría a entrega sin un solo dato real** — el escenario exacto que la cláusula P6.5 y el primer piso del Juez (§5, regla determinista) existen para impedir.

Distribución de `ESTIMATED/total` en las 29 corridas: 0.00→1, 0.50→4, 0.54→3, 0.55→4, 0.56→2, 0.62→3, 0.67→1, 0.75→1, 0.77→1, 0.80→1, 0.86→1, 0.88→1, 0.90→2, **1.00→4**.

El bloque duro de `asset_confidence` (`all_estimated` → `GateStatus.BLOCKED`, mensaje *"Delivery bloqueado hasta onboarding o datos reales"*) es hoy **el único mecanismo** que convierte un paquete Tier C en no-entregable. No hay sustituto.

### 12.3 Decisión

- Lista advisory = **2 miembros**: `content_quality` y `proposal_asset_alignment`.
- `asset_confidence` **conserva su bloqueo**.
- La documentación correcta es **"11 blocking + 2 advisory"**. Hay que corregir `AGENTS.md` y `publication_gates.py:4,162` hacia esta decisión — **no al revés**: el código no debe relajarse para coincidir con un docstring que nunca fue implementado.

Fundamento de que `proposal_asset_alignment` sí puede ser advisory: su bloqueo actual es redundante. `alignment_result.py:105-108` define `passed = (unresolved == 0)` y `alignment_result.py:268-269` define `actionable = max(total - no_breach, 0)` / `coverage = (generated + present) / actionable if actionable > 0 else 1.0`.

**La tautología es demostrable algebraicamente, no solo medible.** La misma llamada `_presence_resolved` que resuelve una entrada NO_BREACH la saca de `no_breach` (L259-263, encoge el denominador) y la mete en `present` (L251-255, agranda el numerador). Si `unresolved == 0`, las entradas se particionan en `generated + present + no_breach == total` ⟹ `generated + present == total - no_breach == actionable` ⟹ **`coverage == 1.0` siempre que `passed == True`**. Numerador y denominador se mueven juntos por construcción.

Por eso el umbral `< 0.8` de `publication_gates.py:1156` no añade protección *independiente* sobre `unresolved`. Ojo con la lectura: es **redundante, no muerto** — sí disparó BLOCKED en 2 de las 4 configuraciones históricas y 3 tests lo ejercitan. Medido en **10 configuraciones** (5 variantes de registro × 2 oráculos de presencia): `coverage_ratio = 1.000` en las 10 y `unresolved = 0` en las 10, con ambos oráculos. Demoterlo no pierde cobertura y **gana** coherencia con lo que los docs ya prometen. Ver §13.2 para el mecanismo completo.

### 12.4 Tareas para la sesión que culmina el tema

1. **Implementar la distinción** en `publication_gates.py`: estructura explícita (`ADVISORY_GATE_NAMES` / `BLOCKING_GATE_NAMES`) copiando `commercial_gate.py:99-113`, y consumirla en `check_publication_readiness:1967-1968` y en `get_blocking_gates:239-249`. Los advisory fallidos deben reportarse con estado WARNING pero no impedir `ready = True`. Dos requisitos inseparables de esa tarea:
   - **Piso explícito (riesgo B).** Advisory sin umbral mínimo deja pasar en silencio coberturas de 0.125 (medido, ver §13.2). Definir un piso bajo el cual el advisory degrada a blocking, o justificar por escrito por qué no hace falta.
   - **Divulgación con consumidor nombrado (riesgo C).** El WARNING debe aterrizar en `human_checklist_generator.py` (≤10 items) y en el `acta_revision.md` del Bot 5 (§5). Un advisory que no entra en un artefacto que el humano lee es indistinguible de un advisory que no existe.
2. **Corregir `AGENTS.md`** (tabla Módulos Activos, fila `quality_gates/`, y el bloque FASE 4.5 del flujo v4) **y `publication_gates.py:4` y `:162`** a "11 blocking + 2 advisory".
3. **NO tocar `delivery_quality_report.py:289`** (`BLOCKING_GATE_NAMES`). Ese tuple rige el ZIP (`main.py:3198` "⛔ ZIP ABORTED") y pertenece a un régimen distinto — delivery, no publicación. Unificarlos es una decisión separada con su propio radio de impacto.
4. **Añadir candado de regresión**: hoy **0 tests** referencian `BLOCKING_GATE_NAMES` y ningún test de `tests/regression/` ni `tests/e2e/` fija la lista advisory. Sin candado, el cuarto régimen reaparece.
5. **Cerrar el ciclo en el plan de registro, no en este documento.** Una vez implementado, actualizar **ROADMAP §6.4** (la columna "Objetivo decidido" de la tabla de severidad pasa a "Implementado") y dar de baja la deuda **H10**. La redacción original de este item —"actualizar §8 y §10 de este documento"— quedó **sin objeto** desde el 2026-09-02: §10 es un stub supersedido (§10.2 lista lo refutado) y §8 es estado histórico del proyecto cuya fuente única es `VERSION.yaml` + `python scripts/doctor.py --status` (ROADMAP §3: no replicar datos sincronizables).

### 12.5 Qué NO hacer

- **No demoter `asset_confidence`** — ver §12.2 (14% del histórico).
- **No implementar S2.3** (cambiar el denominador de `coverage_ratio` de `actionable_total` a `promised_services_total`). Es **revertir la decisión D-PF1** de FASE-SR-B (`alignment_result.py:115-123`, *"los servicios 'sin costo (fallback)' no comprometidos no cuentan como deuda de entrega"*). Efecto medido: convierte un 0.571 BLOCKED en 1.000 WARNING. Bloquearía **3 de las 4 configuraciones históricas de alignment (75%)**. En 3 de esas 4, `no_breach = None` ⟹ históricamente `coverage == coverage/total`: S2.3 no corrige nada real, penaliza una deuda que D-PF1 decidió explícitamente no contar.
- **No añadir todavía el octavo servicio al registro.** `PROPOSAL_SERVICE_TO_ASSET` tiene 7 entradas (`monthly_report` comentado en `proposal_asset_alignment.py:27-29`, FASE-3 BUG-10), mientras `service_catalog` declara 8 y el comentario de L35-37 dice "All 8". Medido: **Δcoherence = +0.0000 exacto** (la rama de éxito hardcodea `score=1.0` en `coherence_validator.py:689-700` y solo pone el tamaño del registro en el mensaje; la rama de fallo usa una **UNIÓN** en L703 donde `monthly_report` ya está en `promised_types`), pero **`promise_coverage` cae 0.571 → 0.500** porque el pain `no_monthly_report` no se detecta. Neutro en coherencia, negativo en coverage: no vale la pena sin el punto 8.
- **No tratar el punto 8 como opcional.** La causa raíz es que la propuesta es **estática**: promete los 7-8 servicios del registro haya o no brecha detectada. Una **propuesta dinámica que solo prometa servicios con brecha detectada** hace `no_breach = 0` por construcción ⟹ `total == actionable` ⟹ los denominadores convergen y toda la discusión anterior se disuelve. Advisory es un parche legítimo; el punto 8 es la cura.
- Datos de sensibilidad útiles si se toca coherencia: pesos en `coherence_validator.py:101-108` (1.5/1.0/1.5/0.5/1.0/2.0, total 7.5) ⟹ sensibilidad 0.2667 por unidad; headroom actual 0.08; score mínimo de un check para mantener overall ≥ 0.8 = **0.7000** (M=3 de 10 faltantes).

### 12.6 Criterio de aceptación

- **Baseline antes de tocar nada:** 140 passed, 1 skipped, 8 warnings en ~1.23s sobre los 7 archivos de tests de alignment/gates (141 tests, 32 asserts de bloqueo).
- **Costo esperado:** ~6 tests específicos de alignment a actualizar. No hay candados en `tests/regression/` ni `tests/e2e/`.
- **Verificación:**
  ```bash
  python -m pytest tests/quality_gates tests/asset_generation -q
  python scripts/run_all_validations.py --quick
  python scripts/validate_agents_md.py    # gate de coherencia AGENTS.md (conteo de gates)
  ```
- **Definición de hecho:** un gate advisory fallido produce WARNING visible en el acta y `ready` sigue siendo `True`; un gate blocking fallido produce `ready = False`; `AGENTS.md`, `publication_gates.py:4`, `:162` y el código dicen los mismos 11 + 2; existe al menos un test que fija ambas listas.

### 12.7 Correcciones adyacentes — otras cifras de este documento refutadas en la misma auditoría

No consumir §3 ni §8 sin leer esto (§10 ya se autodescribe como stub supersedido). Todo verificado contra el código vivo y los artefactos reales el 2026-09-02.

> ⚠️ **Las referencias de línea de esta tabla que caen dentro del antiguo §10 (rango 254-361) son históricas.** Ese texto fue **eliminado** el 2026-09-02 al convertir §10 en stub, así que esas líneas ya no existen en este archivo: R3 (279), R9 (325), R10 (262), N3 (278) y R11 (275) apuntaban a las Etapas 1-5 y a las Convenciones del plan. La versión corregida de cada una vive en **`ROADMAP.md` §7.2** y el registro consolidado de lo refutado en **§10.2**. Las referencias fuera de ese rango (62, 90, 60, 146, 230, 89, 231, 182-200, 228) siguen siendo válidas.

| # | Línea(s) | Afirmación del doc | Realidad medida |
|---|---|---|---|
| R1 | 62 | "Entrega tipo: directorio expandido, no ZIP empacado" | Falso. Existe `deliveries/hotelsalentoreal_20260831.zip` (**46,552 bytes**, verificado 2026-09-02); los 37 archivos son del directorio expandido. Ambas cosas coexisten |
| R2 | 90 | "`site_verification_applied: false` — nada se verificó en producción" | Semántica invertida. Ver `v4_asset_orchestrator.py:150-162`: el flag indica si la verificación *se aplicó al flujo*, no si el sitio fue verificado |
| R3 | 60, 146, ~~279~~ | `coherence_score` 0.913 / 0.9133 | Ese es `pre_coherence_score` (`main.py:3228`), **no canónico**. El canónico DT4-N4 es **0.88**. La ocurrencia en 279 (criterio de aceptación de la antigua Etapa 1) **fue eliminada con el stub**; `ROADMAP.md` §7.2 T1 trae el valor correcto |
| R8 | 230 | "~308 .py" / "604" | Real: **291 archivos fuente**, **284 de test** |
| R9 | 89, 231, 325 | `IMPLEMENTATION_ORDER.md` vacío porque `generate_delivery_template()` no encontró `core_assets` ni `geo_assets` | Causa raíz mal atribuida. La real es doble: `main.py:3239-3255` (derivación NF-6) + `asset_responsibility_contract.py:316-317` donde `core_assets = core_assets or []` **destruye el centinela `None`** |
| R10 | 262 | `two_phase_flow.py` como base del flujo | No tiene ningún llamador en producción |
| N3 | 278 | `publication_state.py` como artefacto de Etapa 1 | Es un **huérfano**: Etapa 1 apunta a código muerto |
| R11 | 182-200, 275 | Nombres fijos de artefactos | No existen con nombre fijo: son **timestamped** (`audit_report_20260831_122757.json`, `gate_report_20260831_122803.json`, `financial_scenarios_20260831_122757.json`) |
| R13 | 228 | Castilla Real 0.8261 | Evidencia **archivada** del 2026-05-28, no corrida viva |
| R14 | 363 | `/mnt/c/Users/Jhond/Github/iah-cli` | Ruta WSL; la plataforma real es `win32` → `C:\Users\Jhond\Github\iah-cli` |
| — | §5, ROADMAP §7.2 | `modules/quality_gates/tribunal/` | **No existe.** Ninguno de los 5 bots del tribunal está implementado; §5 y ROADMAP §7.2 son **plan, no estado** (antes §10, hoy stub) |

**Hallazgo adicional (N11), crítico para el Bot 1 del tribunal:** el gate de coherencia **ignora `is_coherent`**. `publication_gates.py` `_coherence_gate` (~L458-520) decide con `passed = coherence_score >= self.config.coherence_threshold` — solo el score, nunca `report.is_coherent`. Los artefactos reales de SalenteReal dicen `is_coherent: false` en cuatro lugares y aun así el gate PASÓ. Añadir errores no bloquea nada. Causa única del `is_coherent=False`: `_check_assets_are_justified` = 3/4 = 0.75 → `severity="error"` (`coherence_validator.py:255-309`), porque `monthly_report` es always-on y no tiene pain que lo justifique. Contraste: `coherence_gate.py:289` sí usa `passed = report.is_coherent` (más estricto) pero **no tiene llamador en producción** — es huérfano. El Bot 1 debe leer `is_coherent`, no el score.

---

## 13. Hallazgos estructurales de la auditoría 2026-09-02 (no cubiertos por §12)

> **Propósito:** preservar medición verificada para evitar reproceso. Nada de esto está implementado y ningún archivo de código fue modificado durante la auditoría. §12 resuelve la severidad de los gates; §13 documenta lo que la auditoría encontró *alrededor*, que necesitan (a) la sesión del **punto 8** —propuesta dinámica, causa raíz en ROADMAP §7.2— y (b) la del **tribunal** (§5 para el diseño por bot, **ROADMAP §7.2** para el plan). Los seis agujeros A1-A6 ya están registrados como deuda en ROADMAP v4.2 §13 — ver la equivalencia en **§10.4**.
> **Corpus de referencia:** `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/` (corrida 2026-08-31 12:28:03), re-verificado el 2026-09-02.

### 13.1 Seis agujeros vivos (bloque A)

Verificados contra código vivo y artefactos reales el 2026-09-02. Al momento del hallazgo **ninguno estaba documentado en el repo**; desde **ROADMAP v4.2** los seis están registrados como deuda o precondición — A1→**H9**, A2→**H7**, A3→**P12**, A4→**T0.2**, A5→**P10**, A6→§6.4/**G11**. Se conservan aquí con su evidencia por archivo.

**A1 — G9 se salta en verde.**
- *Qué:* si no existe `proposal_asset_matrix.json`, el gate de alignment de delivery se marca como pasado.
- *Evidencia:* `delivery_quality_report.py:250-257` → `{"passed": True, "gate": "G9", "skipped": True, "reason": "proposal_asset_matrix.json not found"}`. El summary (`:310-319`) cuenta `passed_count` sobre `gate_results.values()` ⟹ **un gate saltado se cuenta como gate pasado**. Hay además un **segundo default independiente** en `:325` (`{"passed": True, "gate": "G9"}`) para cuando la clave no existe.
- *Consecuencia:* un paquete sin matriz pasa el gate de delivery de forma vacuamente verde. Dos defaults para la misma clave = dos fuentes de verdad.
- *Requisito:* `skipped` no debe contar como `passed`; debe ser `NOT_EVALUATED` y visible en el acta. Unificar los dos defaults.

**A2 — El oráculo de presencia no se persiste.**
- *Qué:* `site_presence_report` es la entrada que decide `present_in_production` y por tanto `no_breach`, `unresolved`, `coverage_ratio` y G9. No se escribe a disco.
- *Evidencia:* `find output -iname "*site_presence*"` → **0 resultados** en todo el histórico. Para medir hubo que reconstruir el snapshot a mano.
- *Consecuencia:* el número más decisivo del gate de alignment **no es auditable post-hoc**. El Bot 3 del tribunal (§5) no puede revisar lo que no existe y ninguna corrida pasada puede re-evaluarse bajo un oráculo distinto.
- *Requisito:* persistir el snapshot canónico — el concepto ya existe (`main.py:2535` lo pasa como `site_presence_snapshot`, DT4-R2); falta escribirlo junto a los demás artefactos de `v4_audit/`.

**A3 — `promised_assets_exist`, el check más pesado, solo corre pre-gen.**
- *Qué:* el cross-check contra el registro estático se ejecuta únicamente cuando no hay assets generados.
- *Evidencia:* `coherence_validator.py:670` `if not generated_assets:`, con comentario H6 FIX explícito (*"With real generated_assets, we trust the orchestrator's actual output"*). El acoplamiento oculto con el registro está en `:622`.
- *Consecuencia:* el check de peso **2.0** (el mayor de los 6, sobre total 7.5) devuelve `score=1.0` **hardcoded** en la rama de éxito (`:689-700`); el tamaño del registro solo entra al *mensaje*. Post-generación —que es cuando importa— el check confía en el orquestador sin re-verificar el contrato. Esto explica por qué Δcoherence = 0.0000 al cambiar el registro (B5).
- *Requisito:* si el Bot 1 va a certificar P6.3, no puede apoyarse en este check tal como está.

**A4 — Doble oráculo de presencia: decisión y narrativa divergen.**
- *Qué:* un mismo resultado de gate puede afirmar que un asset falta y a la vez listarlo como presente en producción.
- *Evidencia:* reproducido con nombres reales sobre SalenteReal — el resultado dice que **Schema Hotel** está `missing` y simultáneamente lo incluye en `present_assets`. Mecanismo: el oráculo **permisivo** (`PRODUCTION_PRESENT_STATUSES = ("exists", "exists_with_issues")`, `site_presence_checker.py:73`, decisión FASE-SR-E H7/L-SR3) es el que **decide**; el **estricto** es el que **escribe el mensaje**.
- *Consecuencia:* el humano (y el Bot 3) lee una narrativa que no corresponde con la decisión tomada. Misma forma de defecto que R2 (`site_verification_applied`).
- *Requisito:* un solo oráculo para decidir y para narrar, o narrativa derivada de la decisión.

**A5 — Parámetro fantasma y skip silencioso en los dos builders de matriz.**
- *Qué:* hay dos constructores de matriz y ambos tienen rutas de silencio.
- *Evidencia:* `AssetAlignmentMatrix.build` (`proposal_asset_alignment.py:748-789`) declara `delivery_context` como fuente de verdad preferida en su docstring, pero **lo ignora** cuando `generated_assets is not None` (L779-789). `ProposalAssetMatrix.build` (`:575-659`) hace **skip silencioso** en `:610-612` (`if not expected_asset: continue`): un servicio sin asset esperado desaparece de la matriz sin dejar rastro. Medido: los dos builders son **empíricamente idénticos en las 5 variantes probadas**.
- *Consecuencia:* hoy no divergen, pero hay dos rutas por las que un servicio puede esfumarse sin señal. Duplicación sin divergencia es deuda latente, no seguridad.
- *Requisito:* un solo builder; el skip de `:610-612` debe dejar una entrada con estado explícito (`NO_ASSET_MAPPED`), no desaparecer.

**A6 — La matriz persistida pierde el puntero al artefacto.**
- *Qué:* `asset_path` se serializa como `null` incluso para la entrada LINKED cuyo asset sí se generó.
- *Evidencia* (entrada real de `proposal_asset_matrix.json`, versión 2.0):
  ```json
  {"alignment": "linked", "asset_path": null, "asset_type": "llms_txt",
   "confidence": 1.0, "pain_ids": ["ai_crawler_blocked"],
   "service_name": "Optimización para IA Generativa", "status": "LINKED"}
  ```
- *Consecuencia:* la trazabilidad P6.3 (*"recomendación vendida → asset específico trazable"*) **no se puede verificar desde el artefacto**: no hay ruta al archivo. El Bot 3 tendría que adivinar el nombre.
- *Requisito:* poblar `asset_path` cuando el asset existe; es el campo que hace auditable P6.3.

### 13.2 Mecanismo causal de `no_breach = 6/7` (bloque B)

Esto es lo que necesita una sesión de **punto 8**. Sin esto se vuelve a medir desde cero.

**B1 — La matriz real, verificada entrada por entrada.** 7 servicios: **6 NO_BREACH + 1 LINKED**, `delivery_ready: True`.

| Servicio prometido | `asset_type` | Estado | conf | `pain_ids` |
|---|---|---|---|---|
| SEO Local | `optimization_guide` | NO_BREACH | 0.0 | `[]` |
| Botón de WhatsApp | `whatsapp_button` | NO_BREACH | 0.0 | `[]` |
| Schema Hotel | `hotel_schema` | NO_BREACH | 0.0 | `[]` |
| Schema Organization | `org_schema` | NO_BREACH | 0.0 | `[]` |
| Página de FAQ | `faq_page` | NO_BREACH | 0.0 | `[]` |
| Meta Tags Sociales (Open Graph) | `open_graph` | NO_BREACH | 0.0 | `[]` |
| **Optimización para IA Generativa** | `llms_txt` | **LINKED** | 1.0 | `["ai_crawler_blocked"]` |

Y el ledger resuelto tiene **exactamente 3 entradas**, las tres MEDIUM y ASSET_GENERATED: `no_analytics_configured`, `low_organic_visibility`, `ai_crawler_blocked`.

**La doble falla de mapeo, que es la causa raíz:**
- `low_organic_visibility` **sí se detectó** y produjo `indirect_traffic_optimization` (`pain_solution_mapper.py:179`; `asset_catalog.py:300-313` IMPLEMENTED) — pero **ningún servicio prometido mapea a ese asset**: es un **huérfano**. Se genera, se entrega y no responde a nada vendido.
- `no_analytics_configured` produjo `analytics_setup_guide` — **segundo huérfano**, mismo mecanismo (`pain_solution_mapper.py:170`).
- "SEO Local" promete `optimization_guide`, que solo se mapea desde `low_citability` (`pain_solution_mapper.py:207-215`) — pain que **no se detectó**. El servicio prometido queda NO_BREACH.

⟹ **El registro promete por pains que no aparecieron, y los pains que aparecieron producen assets que nadie promete.** Los dos extremos del contrato comercial están desalineados por construcción del mapper, no por los datos del hotel. De 4 assets generados, **2 son huérfanos** y 1 (`monthly_report`) no tiene pain.

**B2 — Brecha runtime vs estática.** El registro estático `PROPOSAL_SERVICE_TO_ASSET` está **completo: 7/7 con asset implementado**. El problema no es el registro. En runtime se generan **4 assets** (`asset_generation_report.json`: `analytics_setup_guide` WARNING, `indirect_traffic_optimization` WARNING, `llms_txt` PASSED, `monthly_report` PASSED; `total_assets = 4`, `estimated = 2`, `delivery_ready_percentage = 100.0`) y la **intersección prometido ∩ generado = {`llms_txt`}** — un solo elemento. `monthly_report` se genera pero **no está en el registro** (comentado en `proposal_asset_alignment.py:27-29`, FASE-3 BUG-10).
⟹ Quien confunda "registro completo" con "cobertura real" llega a la conclusión opuesta. Fue un falso positivo de esta misma auditoría (§13.5, #3).

**B3 — Los seis registros de identidad de servicios.** Punto 8 es imposible sin decidir cuál manda.

| Registro | Ubicación | Tamaño | Rol |
|---|---|---|---|
| `service_catalog` | config | **8** | lo que se declara vendible |
| `PROPOSAL_SERVICE_TO_ASSET` | `proposal_asset_alignment.py:22-33` | **7** | lo que la propuesta promete → asset |
| `ASSET_CATALOG` | `asset_catalog.py` | **25** | lo que se sabe generar |
| `PAIN_SOLUTION_MAP` | `pain_solution_mapper.py` | **22 mapeables** | pain → asset |
| Output runtime del orquestador | `asset_generation_report.json` | **4** | lo que de hecho se generó |
| Contract registry | `asset_responsibility_contract.py` | **3 CORE + 3 GEO** | responsabilidad de deploy |

Seis fuentes, ninguna canónica. `ALL_PROMISED_SERVICES = list(PROPOSAL_SERVICE_TO_ASSET.keys())` (`:45`) hace que el registro de 7 mande sobre el de 8, mientras el comentario de `:35-37` dice "All 8".

**B4 — Palancas medidas sobre la cobertura.** Bajo el régimen actual `coverage_ratio` = **1.000 en las 10 configuraciones** (tautología, §12.3). Lo que varía es el resultado bajo **S2.3** (denominador = `promised_services_total`):

| Configuración | coverage bajo S2.3 |
|---|---|
| Rango en las 10 (5 registros × 2 oráculos) | **0.125 – 0.714** |
| Registro actual (7), oráculo permisivo | **0.571** (4/7) |
| Registro actual + S1.2 (añadir `monthly_report`) | **0.500** — *empeora*, porque el pain `no_monthly_report` no se detecta |
| **R8c** (remapear "SEO Local" → `indirect_traffic_optimization`) | **0.714** (5/7) — única palanca que sube |
| R8 (8 servicios), oráculo estricto | **0.125** |

- **S2.3 bloquea en las 10** (ninguna alcanza 0.8) ⟹ por eso §12.5 lo descarta.
- `unresolved = 0` y **G9 = PASS en las 10** ⟹ **S2.4 no tiene efecto alguno**.
- **Ninguna variante de registro llega a 1.0 sin punto 8.** La mejor (R8c) se queda en 0.714.

**B5 — Δcoherence medido, y por qué es cero.**

| Cambio de registro | Δ coherence_score | Mecanismo |
|---|---|---|
| 7 → 8 servicios (añadir `monthly_report`) | **+0.0000 exacto** | Dos candados independientes: (1) la rama de éxito hardcodea `score=1.0` (`coherence_validator.py:689-700`) y el tamaño del registro solo entra al mensaje; (2) la rama de fallo usa una **UNIÓN** (`:703`, `total_checked = len(promised_types \| set(PROPOSAL_SERVICE_TO_ASSET.values()))`) y `monthly_report` ya está en `promised_types` ⟹ la unión vale 10 para R7 y para R8 |
| R22 (vocabulario completo de 22 del mapper) | **−0.0121** (0.88 → 0.8679) | Único cambio que sí mueve el score. Causa: `direct_booking_campaign` es **MANUAL_ONLY** en `asset_catalog.py` ⟹ `is_asset_implemented` False ⟹ entra a `missing_service_assets` |

- **Sensibilidad:** pesos `1.5/1.0/1.5/0.5/1.0/2.0` (total 7.5, `coherence_validator.py:101-108`) ⟹ **0.2667 por unidad**. Headroom actual **0.08**. Score mínimo de un check para mantener overall ≥ 0.8 = **0.7000** (M=3 de 10 faltantes).
- **Landmine:** unificar los registros con el vocabulario del mapper (22) cuesta 0.0121 de coherencia por un asset MANUAL_ONLY. Unificar no es gratis.
- **Cierre con N11:** el gate decide con `coherence_score`, **nunca con `is_coherent`**; los artefactos dicen `is_coherent: false` en cuatro lugares y el gate PASÓ. Causa única: `_check_assets_are_justified` = **3/4 = 0.75** → `severity="error"` (`coherence_validator.py:255-309`). **Ese 3/4 está confirmado por el artefacto real**: 4 assets generados, 3 con pain en el ledger, 1 (`monthly_report`) always-on sin pain. ⟹ **La misma falla estructural de B1 (assets sin pain y pains sin servicio) produce a la vez el `no_breach = 6/7` y el `is_coherent = false`.** Punto 8 elimina las dos.

### 13.3 Costos comparados (bloque C)

| Cambio | Tests a tocar | Candados de regresión | Δ protección real |
|---|---|---|---|
| Advisory 2 (§12.4) | **~6** de alignment | 0 hoy; hay que crearlos (§12.4, item 4) | **0** — coverage es 1.000 siempre; no se pierde nada |
| S2.3 (denominador) | **~41 tests / 152 asserts** | 0 | **Negativo** — revierte D-PF1 y bloquea 3 de 4 configuraciones históricas (75%) |

Baseline medido antes de tocar nada: **140 passed, 1 skipped, 8 warnings, ~1.23s** sobre los 7 archivos de tests de alignment/gates (141 tests, 32 asserts de bloqueo). **0 tests** referencian `BLOCKING_GATE_NAMES`.

### 13.4 Tabla consolidada de mediciones (para no re-medir)

| Magnitud | Valor | Dónde |
|---|---|---|
| Corridas históricas únicas en `output/` | **29** (10 hoteles) | §12.2 |
| Corridas con 100% assets ESTIMATED | **4 (14%)** — `hotel_visperas`/`hotel_vísperas`, 2026-03-25 → 2026-04-05, todas con `coherence_score_final = None` | §12.2 |
| Configuraciones únicas de alignment en el histórico | **4**, con `no_breach = None` en 3 | §12.5 |
| Matriz SalenteReal | 7 entradas: 6 NO_BREACH + 1 LINKED, `delivery_ready: True`, versión 2.0 | B1 |
| Ledger resuelto | **3 pains**, todos MEDIUM / ASSET_GENERATED | B1 |
| Assets generados en runtime | **4** (2 WARNING, 2 PASSED), `estimated = 2`, `delivery_ready_percentage = 100.0` | B2 |
| Intersección prometido ∩ generado | **{`llms_txt`}** — 1 elemento; 2 assets huérfanos | B1/B2 |
| `coverage_ratio` (régimen actual) | **1.000** en 10/10 | §12.3 |
| `coverage_ratio` bajo S2.3 | **0.125 – 0.714**, bloquea en 10/10 | B4 |
| `unresolved` / G9 | **0** / **PASS** en 10/10 ⟹ S2.4 sin efecto | B4 |
| Δcoherence 7→8 | **+0.0000** | B5 |
| Δcoherence R22 | **−0.0121** (0.88 → 0.8679) | B5 |
| coherence canónico SalenteReal | **0.88** (DT4-N4); `0.9133` es `pre_coherence_score`, **no canónico** | §12.7 R3 |
| `is_coherent` | **false** en 4 lugares del artefacto; el gate PASÓ igual. Causa: 3/4 = 0.75 | N11 / B5 |
| Sensibilidad de coherence | **0.2667**/unidad; headroom **0.08**; mínimo por check **0.7000** | B5 |
| ZIP de la entrega | `hotelsalentoreal_20260831.zip`, **46,552 bytes**; directorio expandido **37 archivos** | §12.7 R1 |
| Artefactos `site_presence*` persistidos | **0** en todo `output/` | A2 |
| Tests que fijan la lista advisory | **0** | §12.4 |

### 13.5 Falsos positivos de esta auditoría (corregidos, para no repetirlos)

Siete afirmaciones que se hicieron durante el análisis y que la medición refutó. Se listan porque son las trampas naturales de este código:

1. "Dos rutas de veredicto independientes desde un mismo DTO" → **algebraicamente redundantes** (§12.3).
2. "S2.4 volteaba G9 → ZIP ABORTED" → **falso en SalenteReal**: hay cero MISSING_ASSET en la matriz.
3. "La intersección prometido × generado es solo `{llms_txt}`" → cierto **en runtime**, falso **para el registro estático** (7/7 completo). Ver B2.
4. "Los dos builders de matriz divergen" → **empíricamente idénticos** en las 5 variantes. Ver A5.
5. "El umbral de coverage es código muerto" → **impreciso: redundante, no muerto** (3 tests lo ejercitan, disparó en 2 de 4 configuraciones históricas).
6. "S2.3 es insatisfacible" → **refinado**: insatisfacible bajo el régimen de SalenteReal; una configuración histórica sí lo pasa.
7. "El 0.88 canónico no es estable bajo S1.2" → **refutado**: Δ = 0.0000 exacto.

**Lección de forma:** en este pipeline, revalidar citas de código **no** revalida premisas. Las siete afirmaciones de arriba eran coherentes con el código leído y falsas contra el artefacto real. Todo hallazgo de §13 está anclado a un artefacto o a una corrida, no a una lectura.

---

*Contexto generado 2026-09-01 y convertido en plan implementable (§10) ese mismo día; auditado contra el código vivo el 2026-09-02 (§12 decisión advisory + §13 hallazgos estructurales). Esa auditoría **migró el plan a `ROADMAP.md` §7.2 (FASE T, v4.2)** y dejó §10 como stub supersedido: §10.2 lo refutado, §10.3 el detalle de implementación preservado, §10.4 la equivalencia de nomenclaturas. Retomar cuando la sesión aborde: bots para iah-cli, credibilidad de diagnóstico, Capa 3 onboarding, Capa 4 delivery/deploy, tribunal de revisión multi-bot, debottlenecking del proceso de entrega, ejecución del plan anclado en P6 (**punto de entrada: ROADMAP §7.2 T0.1-T0.4, y solo después T1 = Juez certificador**; el tramo offline T0/T1/T2/T4 es certificable ya, el tramo externo T3/T5/T6 depende de datos reales del hotel y credenciales FTP/WP), culminar la corrección de la lista advisory de gates — 2, no 3 (§12.4 + ROADMAP **H10**), **o abordar la causa raíz del punto 8 — propuesta dinámica (§13.2 = ROADMAP §7.2 "Causa raíz por debajo de T0", que además cierra N11 = T0.4/**P9**).*
