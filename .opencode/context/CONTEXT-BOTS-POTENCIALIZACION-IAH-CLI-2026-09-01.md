# Contexto: Potencializar iah-cli con Bots — Diagnóstico como Producto, Entrega como Cuello de Botella

> **Fecha:** 2026-09-01 · **Reestructurado:** 2026-09-03
> **Sesión:** análisis de arquitectura de bots para escalar credibilidad y entrega
> **Propósito central:** iah-cli vende diagnóstico, NO una herramienta de IA — el diagnóstico es el producto, la herramienta es invisible para el cliente
> **Alcance desde el 2026-09-03:** este documento quedó **exclusivo de bots** (tribunal §5, capas §2, análisis Capa 4 §3). Las correcciones de severidad de gates (ex §12.1-12.6) y los hallazgos estructurales del pipeline (ex §13: A1-A6, B1-B5/punto 8, mediciones, falsos positivos) **migraron al dossier de estabilización** `/.opencode/context/Historico/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md` (§8 y §9; mapa de migración en su §10). Las precondiciones del tribunal viven ahora en **§12** de este documento.
> **Archivo retomable:** cualquier sesión futura que hable de bots, Capa 3, Capa 4, delivery, credibilidad, debottlenecking
> **Validado contra el repo (2026-09-01):** citas de código corregidas entonces (13 publication gates, `proposal_asset_alignment.py`, 1 workflow activo). ⚠️ **Dos cifras de esa validación fueron refutadas después:** los "~10 CG-*" son en realidad **12 repartidos en dos archivos**, y los "~308 .py" son en realidad **291 fuente / 284 test** (con `venv/` aportando 7.597 .py dentro del repo). El plan que esta línea anunciaba en §10 **ya no vive ahí**: está en **`ROADMAP.md` §7.2 (FASE T, v4.2)**, con equivalencia de nomenclaturas en **§10.4**.
> **Auditado contra el código vivo (2026-09-02):** la corrección de severidad advisory = 2, no 3 (`asset_confidence` conserva su bloqueo) **migró al dossier: CONTEXT-AUDITORIA §8** (decisión H10 en ROADMAP). Otras cifras de este documento fueron refutadas en la misma auditoría y están listadas en **§13**; no consumir §3 ni §8 sin leerlas antes. **§10 es ahora un stub supersedido**: §10.2 lista lo refutado, §10.3 preserva el detalle que el ROADMAP no replica, §10.4 mapea ambas nomenclaturas (las filas que apuntaban al ex §12/§13 hoy apuntan al dossier).

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
- **Existente hoy:** ~10 commercial gates (CG-*) en `modules/quality_gates/commercial_gate.py` — 6 blocking (CG-SCENARIO-ORDER, CG-SCENARIO-NEGATIVE, CG-IA-BLOCKED-CLAIM, CG-ROI-NEGATIVE, CG-CLAIM-VS-EVIDENCE, CG-EVIDENCE-TIER-CONSISTENCY) + 4 warning (CG-WHATSAPP-LEAD, CG-OTA-NARRATIVE, CG-TIER-CONSISTENCY, CG-TECH-JARGON) — y `financial_engine` generan escenarios con `EvidenceConfidence`. `DisclaimerGenerator` produce descargos. **Lo nuevo:** revisor que **lea propuesta y verifique que no sobre-presente lo que los datos soportan**, cubriendo los ~10 CG-* (no solo 4). El LLM solo *propone* hallazgos de sobre-presentación; el Juez aplica veredicto determinista contra tier labels y CG-* (ver **ROADMAP §7.2 T4**; antes §10 Etapa 4). ⚠️ El conteo "~10 CG-*" de esta línea fue refutado: son **12 repartidos en dos archivos** (§13, ROADMAP §7.2).

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
- `modules/quality_gates/publication_gates.py` — 13 publication gates. **Documentados como "10 blocking + 3 advisory" (líneas 4 y 162) pero el código no implementa la distinción: los 13 bloquean** (`check_publication_readiness:1967`). Lista advisory correcta = **2**, no 3 — corrección medida migrada al dossier: **CONTEXT-AUDITORIA §8** (decisión H10 en ROADMAP).
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
3. **Debajo del plan hay una causa raíz que §10 no ve.** El ledger resuelto tiene **3 pains** y el orquestador genera **4 assets**, de los cuales **2 son huérfanos**, y **6 de 7 servicios prometidos responden a pains que no se detectaron**. Esa única causa produce a la vez `no_breach = 6/7` **e** `is_coherent = false` (`assets_are_justified` 3/4 = 0.75). La **propuesta dinámica** — solo prometer servicios con brecha detectada — cierra ambos síntomas y hace `no_breach = 0` por construcción. Todo lo que §10 proponía (advisory, remapeos, orden de etapas) es parche sobre un contrato comercial que sigue vendiendo lo que no diagnostica. Ver ROADMAP §7.2 *"Causa raíz por debajo de T0"* y el dossier de estabilización §9.2 (ex §13.2 de este documento).

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

Dos vocabularios describen **el mismo plan**. Esta tabla es el puente; **la columna ROADMAP es la autoritativa**. Los hallazgos A/B y las mediciones citados en la columna izquierda viven desde el 2026-09-03 en el dossier de estabilización (`CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md`; mapa de migración en su §10).

| Etiqueta en este documento | Equivalente en ROADMAP v4.2 | Nota |
|---|---|---|
| §10 Etapa 1 — Juez certificador | **T1** | tramo offline |
| §10 Etapa 2 — revisores mecánicos (Bot 1, Bot 3) | **T2** | tramo offline |
| §10 Etapa 3 — onboarding (Capa 3) | **T3** | **tramo externo**: datos reales del hotel |
| §10 Etapa 4 — revisores NL (Bot 2, Bot 4) | **T4** | tramo offline (LLM mockeado en tests) |
| §10 Etapa 5 — entrega/deploy (Capa 4) | **T5** | **tramo externo**: FTP/WP + staging + deuda **P1** |
| §10 Etapa 6 — throughput + gancho (Capa 1/2) | **T6** | **tramo externo**: escala sobre T3 y T5 |
| *(inexistente en §10)* | **T0.1-T0.4** | precondiciones medidas; van **ANTES** de T1 |
| Dossier §8.3/§8.5 escenario **S2.3** (denominador = `total`) | **T0.1** | ROADMAP ya usa la etiqueta S2.3; descartado como bloqueante |
| Dossier §9.1 **A4** — doble oráculo de presencia | **T0.2** | no voltea ningún veredicto en 10/10 |
| Dossier §9.1 **A5** — skip silencioso + dos builders | **P10** extendido | trampa de falso negativo para **T0.3** |
| Dossier §9.2 bloque B — mecanismo causal de `no_breach = 6/7` | §7.2 **"Causa raíz por debajo de T0"** | dos derivaciones independientes que coinciden |
| Dossier §9.2 (B5) **N11** — el gate ignora `is_coherent` | **T0.4** + deuda **P9** | la deuda de producto más grave abierta |
| Dossier §9.1 **A1** — G9 se salta en verde | **H9** extendido | latente, no observado |
| Dossier §9.1 **A2** — oráculo de presencia no persistido | **H7** extendido | vuelve **T0.2** no retro-testeable |
| Dossier §9.1 **A3** — `promised_assets_exist` solo pre-gen | **P12** + §6.4 *"Nota pre-gen (P6.3)"* | mecanismo del Δcoherence 0.0000 |
| Dossier §9.1 **A6** — `asset_path: null` | §6.4 + **G11** + criterio de **T2** | P6.3 no verificable desde el artefacto |
| Dossier §8.3 decisión **advisory = 2, no 3** | §6.4 tabla *"Objetivo decidido"* + **H10** | `asset_confidence` **conserva** el bloqueo |
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

## 12. Precondiciones que me preceden — dossier de estabilización (2026-09-03)

El tribunal (§5) es un **revisor de artefactos**: lee outputs y produce evidencia legible, no reimplementa gates (regla arquitectónica de §5). Si los artefactos están rotos, certifica basura. Las correcciones que el tribunal necesita **antes de T1** son trabajo de pipeline y viven en el dossier de estabilización `/.opencode/context/Historico/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md`:

| Precondición | Dossier | Por qué bloquea al tribunal |
|---|---|---|
| **Punto 8** — propuesta dinámica (solo prometer servicios con brecha detectada) | §9.2 (B1-B5) | Sin él, Bot 2 marcaría SIN-BRECHA-ASOCIADA en 6/7 servicios de toda corrida: el tribunal devolvería todo paquete y no añadiría valor |
| **A2** — persistir el oráculo de presencia | §9.1 | Bot 3 no puede auditar post-hoc lo que no se escribió a disco (0 `site_presence*` en todo `output/`) |
| **A6** — poblar `asset_path` en la matriz | §9.1 | P6.3 no verificable desde el artefacto que Bot 3 debe revisar |
| **N11 / P9** — el gate decide con score, ignora `is_coherent` | §9.2 (B5) | Bot 1 debe leer `is_coherent`; el pipeline debe respetarlo primero (deuda de producto más grave abierta) |
| **H10** — severidad advisory = 2, no 3 | §8 | Bot 5 necesita saber qué gate es advisory para su veredicto; hoy hay 4 regímenes contradictorios |
| **T0.1-T0.4** — precondiciones medidas de FASE T | ROADMAP §7.2 | Ya registradas como el orden oficial antes de T1 |

El resto del dossier (ocho caídas silenciosas, blind gates, contradicciones entre módulos, pendientes de verificación) es **completitud del diagnóstico**: condición de calidad del producto, no bloqueante directo del tramo offline del tribunal. Orden acordado (2026-09-03): **estabilización primero** (dossier), **tribunal después** — la secuencia que ROADMAP §7.2 ya registró. El acta dual, su destino interno y la lista blanca del ZIP (deudas H8/P6) siguen en §9 de este documento.

---

## 13. Correcciones adyacentes de la misma auditoría — guarda de §3/§8 (2026-09-02)

> Antes "§12.7". Se queda en este documento porque corrige cifras de §3 (análisis Capa 4) y §8 (estado del proyecto), que aquí permanecen. Las correcciones de severidad y los hallazgos estructurales del pipeline migraron al dossier (CONTEXT-AUDITORIA §8-§9).

No consumir §3 ni §8 sin leer esto (§10 ya se autodescribe como stub supersedido). Todo verificado contra el código vivo y los artefactos reales el 2026-09-02.

> ⚠️ **Las referencias de línea de esta tabla que caen dentro del antiguo §10 (rango 254-361) son históricas.** Ese texto fue **eliminado** el 2026-09-02 al convertir §10 en stub, así que esas líneas ya no existen en este archivo: R3 (279), R9 (325), R10 (262), N3 (278) y R11 (275) apuntaban a las Etapas 1-5 y a las Convenciones del plan. La versión corregida de cada una vive en **`ROADMAP.md` §7.2** y el registro consolidado de lo refutado en **§10.2**. Las referencias fuera de ese rango (62, 90, 60, 146, 230, 89, 231, 182-200, 228) siguen siendo válidas **contra el snapshot 2026-09-02 del archivo**; tras la reestructuración del 2026-09-03 los números cambiaron — mapa por sección: R1→§3 (tabla Estado de la entrega) · R2→§3 (bullets de deploy) · R3→§3 y §5 (regla P6.5) · R8→§8 · R9→§3 y §8 · R13→§8 · R14→§11.

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

**N11 — el gate de coherencia ignora `is_coherent` — migró al dossier** (mecanismo completo: CONTEXT-AUDITORIA §9.2, B5; deuda P9/T0.4 en ROADMAP). Lo único que importa aquí para el diseño del tribunal: **el Bot 1 debe leer `is_coherent`, no el score** (§5), y el pipeline debe respetar `is_coherent` antes de que ese check sea certificable.

---

## 14. Adendum (2026-09-05) — estabilización COMPLETADA: precondiciones §12 cerradas, residuos heredados y reglas de concepción

> Registrado por la sesión post-release v4.75.0. No reescribe §12: registra qué cerró el plan
> **ESTABILIZACION-PRE-TRIBUNAL-2026-09-03** (v4.75.0 publicada 2026-09-04; 11/11 sesiones + HOTFIX;
> ACs 11 ✅ / 1 ⚠️ con dueño; NRs 10 ✅ / 1 ⚠️ / 1 ❌ con decisión) sobre las precondiciones de esa
> tabla. Fuentes: `10-analisis-post-implementacion.md` del plan (§2.2, §4, §5, §10) y
> `09-documentacion-post-proyecto.md`. Leer §14 ANTES de concebir el plan del tribunal.

### 14.1 Precondiciones §12 — estado tras la estabilización (certificado sobre artefacto, no sobre string)

| Precondición §12 | Estado | Evidencia en artefacto de la corrida real (FASE-I) |
|---|---|---|
| Punto 8 — propuesta dinámica | ✅ Cerrado | `no_breach` **6→0** en `proposal_asset_matrix.json`; exclusión auditable vía `summary.not_promised` (AC5) |
| A2 — oráculo de presencia persistido | ✅ Cerrado | `v4_audit/site_presence_snapshot.json` (1.421 B, 5 servicios) **dentro del ZIP** (AC9) |
| A6 — `asset_path` poblado | ✅ Cerrado | entrada LINKED trae ruta real; `null` solo donde no hay asset (AC9) |
| N11/P9 — gate respeta `is_coherent` | ✅ Cerrado | `coherence_verdict_passes()` única definición; corpus F4: 0 liberadas, 4 flips READY→NOT_READY (AC12) |
| H10 — severidad 11 blocking + 2 advisory | ✅ Cerrado | `BLOCKING_GATE_NAMES`/`ADVISORY_GATE_NAMES` + `gate_blocks_publication()`; `severity` serializado 13/13 en `gate_report` tras HOTFIX (AC7/AC8) |
| T0.2 (A4) — doble oráculo de presencia | ✅ Cerrado | `missing_count` == `alignment.unresolved` sobre artefacto; criterio canónico `is_present_in_production` (AC10; residuo → S-HF1, 14.2) |
| T0.3 (A5) — skip silencioso en builders | ✅ Cerrado | `classify_promised_services()` única partición compartida; builders idénticos por test |

### 14.2 Residuos heredados al tribunal (dueño asignado en `10-analisis` §5; ninguno a fases documentales, DA-V5)

| Residuo | Qué es | Por qué toca al tribunal |
|---|---|---|
| **S-HF1** (AC10 ⚠️) | `message «4/4»` vs `details.total_services = 1` en el mismo gate | Bot 2/3 leen ese artefacto; decidir qué mide `total_services` es criterio de narración, no serialización |
| **S-I1** (NR2 ❌) | `critical_recall = 1.0` con `details: {}` pese a 1 crítico registrado | Bot 1 debe distinguir recall fundado de vacuo; decisión tomada: `details` declara siempre `critical_issues_count` + `recall_basis` |
| **P12 estructura** | `promised_assets_exist` con `score=1.0` hardcode en `coherence_validator.py` (el mensaje stale ya se corrigió en HOTFIX) | P6.3 es la cláusula de Bot 3; el check sigue dando 1.0 incondicional |
| **S-C4** | tabla de assets técnicos sigue imprimiendo catálogo incondicional | tercera superficie de promesa; decide qué invariante manda (contrato C1 vs tests S-B10) |
| S-E2 · S9 · S-I3 · S-V7 · S-V8 · S-H2 | NameError latente con `generate_proposal=False`; `INVALID_MAPPINGS` (#14); clave canónica por artefacto; nombres timestamped; kill switch H9; eje de performance caído sin pain | limpieza/precondición del tramo offline T1/T2 |
| **S-V10** (B4) | banda de palancas 0.125-0.714 no re-medible | exige corpus ≥3 hoteles — incompatible con «una sola corrida» por diseño |

### 14.3 Reglas de concepción que la certificación dejó medidas (aplicar al concebir FASE T)

1. **Cada AC declara artefacto + clave donde se lee su valor** (L-V1/DA-V3): los 4 ⚠️ del plan tuvieron la misma forma — régimen correcto en código, invisible o contradictorio en el JSON. Un AC no legible en el artefacto no es certificable.
2. **Presupuesto de iteraciones** (DA-V6): las 9 fases medibles excedieron (≥1.219 vs ≤440; R2 ≤60/fase). Recalibrar ×3 o retirar la métrica del executor, fijando el corte «hasta el commit de código».
3. **Candados de serialización como patrón** (`test_gate_report_severity_artifact.py`, `test_matrix_coverage_artifact.py`, `test_promised_assets_message_artifact.py`): cubren S-I2 y la mitad serializable de S-V3 sin decisiones de negocio.
4. **Regla de sincronización = patrón que su validador ejecuta** (L-R2.4): un mensaje «in sync» sobre una forma que ya no existe es el fallo silencioso más caro; el baseline de citas del plan se re-fija con acto visible, no reescribiendo registros.

### 14.4 Baseline de arranque para FASE T

- **v4.75.0** «Estabilización pre-tribunal» (`VERSION.yaml`); 3.934 funciones de test / 298 archivos; validadores del ecosistema 8/8; batería de contratos A-D 180/0.
- Corrida de referencia: **FASE-I** (`evidence/FASE-I/` — coherence 0.8333 ≥ 0.80, `is_coherent: true`, 5 pains en ledger) + baseline `output/FASE-D_salentoreal_post_guard/` (solo lectura) para deltas.
- Suite ancha post-release: los 6 grupos de fallos quedaron resueltos (31 tests recuperados, commits `7826084`…`43e2bf9`); el único rojo restante es el fallo de encoding **preexistente documentado desde FASE-H**. Mediciones por archivo, sin re-corrida completa.

---

*Contexto generado 2026-09-01; auditado contra el código vivo el 2026-09-02 (plan migrado a `ROADMAP.md` §7.2, FASE T v4.2); reestructurado el 2026-09-03 como documento **exclusivo de bots** — la corrección de severidad de gates (ex §12.1-12.6) y los hallazgos estructurales del pipeline (ex §13: A1-A6, B1-B5/punto 8, mediciones, falsos positivos con su lección de forma) viven ahora en el dossier de estabilización `/.opencode/context/Historico/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md` (§8-§9; mapa de migración en su §10). Retomar cuando la sesión aborde: bots para iah-cli, credibilidad de diagnóstico, Capa 3 onboarding, Capa 4 delivery/deploy, tribunal de revisión multi-bot, debottlenecking del proceso de entrega, ejecución del plan anclado en P6 — **punto de entrada: §14 (adendum 2026-09-05: precondiciones §12 cerradas por la estabilización v4.75.0, residuos heredados y reglas de concepción) y ROADMAP §7.2 T0.1-T0.4, y solo después T1 = Juez certificador**; el tramo offline T0/T1/T2/T4 es certificable ya, el tramo externo T3/T5/T6 depende de datos reales del hotel y credenciales FTP/WP.*


