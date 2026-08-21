# CONTEXT — Validación Comercial contra Código Vivo (INFORME-VALIDACION-COMERCIAL-2026-08-19)

> **Fecha**: 2026-08-19
> **Alcance**: Evaluación comercial del repositorio iah-cli (v4.71.0) — si puede crear valor comercial cuantificable, presentarse como evaluación remunerada y convertir oportunidades en trabajo continuo. Tres bucles de validación: (1) diagnóstico comercial inicial, (2) validación exhaustiva contra código vivo, (3) bucle de fallos por causa raíz hasta certeza factual.
> **Método**: Verificación contra código vivo (grep/read), corrida E2E real como evidencia (`evidence/FASE-F/`, hotel Zione, 2026-08-05), inspección programática del ZIP de entrega, análisis de configs y docs comerciales. **Sin modificaciones de código** (análisis de solo lectura conforme a instrucción explícita).
> **Resultado**: 12 claims verificados (8 confirmados, 4 corregidos/refutados), 1 falso positivo propio descartado, 10 fallos nuevos F1-F10 con causa raíz, estrategia corregida v2 (priorización P0-P3). Nivel de certeza declarado: ~95% factual con 3 incógnitas explícitas.
> **Adenda §6 (misma fecha, sesión posterior)**: decisiones del propietario (v4complete queda a nivel interno; concepción Hook/Express de dos momentos mantenida con reframe "un diagnóstico en dos etapas" — §6.7), evidencia Tier A vs benchmarks runtime, fallo nuevo F11 (continuidad Hook→Express), refinación de causa raíz F8. Inventario accionable: 23 elementos.

---

## Veredicto Ejecutivo

El repositorio **SÍ puede crear valor comercial cuantificable**. La evidencia no es teórica: existe una corrida E2E real (`evidence/FASE-F/`, hotel Zione 2026-08-05) con coherence 0.9237, 11/12 gates PASSED y estado READY_FOR_PUBLICATION, con kit de entrega bien estructurado (53 archivos en ZIP con README, MANIFEST e IMPLEMENTATION_ORDER).

**PERO** el diagnóstico comercial está comprometido por **10 fallos (F1-F10)** que afectan la credibilidad numérica frente al primer cliente: 5 fuentes de pricing contradictorias, 3 valores de ADR para la misma región, un fallback de región que infla la fuga hasta 3.2x, y encoding corrupto en artefactos de salida. La tesis estratégica se mantiene, pero la **unificación de credibilidad numérica es prerrequisito del primer cliente**, no una mejora posterior.

**El evento transformador del negocio es el primer Express pagado ($120K COP)**: valida willingness-to-pay (hoy cero evidencia) y desbloquea el modelo de 3 niveles. Todo lo demás (deployer, Express 5 páginas, monitoreo automatizado) es post-validación.

---

## 1. Parte 1 — Matriz de Verificación Factual (12 claims)

### 1.1 Claims CONFIRMADOS (8)

| # | Claim | Evidencia verificada | Status |
|---|-------|---------------------|--------|
| C1 | Hook PDF existe y es funcional | `modules/commercial_documents/hook_pdf_generator.py` (641 líneas: extract_data → validate_data → render_html → generate), tests `tests/commercial_documents/test_hook_pdf_generator.py` (427 líneas), comando CLI `hook-pdf` en main.py, templates `hook_template.md` + `hook_styles.css` | ✅ CONFIRMADO |
| C2 | Motor financiero produce escenarios reales | `evidence/FASE-F/financial_scenarios_20260805_154855.json`: 34 habitaciones, ADR $290K (user_provided), escenarios conservador/realista/optimista 70/20/10 | ✅ CONFIRMADO |
| C3 | 12 publication gates operan en producción | `evidence/FASE-F/gate_report_20260805_154910.json`: 11 PASSED + 1 WARNING (asset_confidence: review_plan y review_widget a 0.5 < 0.7); overall READY_FOR_PUBLICATION, coherence 0.9237 | ✅ CONFIRMADO |
| C4 | Deployer es MVP funcional limitado | `modules/deployer/` con soporte FTP/WP-API básico, sin despliegue real verificado | ✅ CONFIRMADO |
| C5 | Cero evidencia de willingness-to-pay | No existe ningún cliente pagado registrado en evidence/, docs ni configs; corridas son propias (Zione, Don Alfonso, Luxor) | ✅ CONFIRMADO |
| C6 | Kit comercial existe | `docs/PRECIOS_PAQUETES.md`, `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` (472 líneas), `evidence/Ingresos/04_Estructura_Precios.md`, `config/pricing.yaml`, `config/commercial.yaml` | ✅ CONFIRMADO |
| C7 | Monitoring es dashboard interno, no monitoreo de clientes | `modules/monitoring/` = health dashboard del sistema; no hay producto de monitoreo mensual para hoteles | ✅ CONFIRMADO |
| C8 | Express 5 páginas no existe | Ni template ni generador para paquete Express; el Express actual es solo el reporte diagnóstico | ✅ CONFIRMADO |

### 1.2 Claims CORREGIDOS/REFUTADOS (4)

| # | Claim original | Corrección factual | Evidencia |
|---|---------------|--------------------|-----------| 
| C9 | "~5 min por hotel" | **Parcialmente refutado**: la corrida real duró 16 segundos (15:48:55 → 15:49:11) PERO fue **cacheada** ("Análisis previo encontrado: output\v4_verify_4.70.0\v4_complete"). El tiempo de una corrida fresh es **desconocido** | `evidence/FASE-F/v4complete_run.log` |
| C10 | Plan semana 3-4: "contactar 10 prospectos" | **Refutado como ejecutable**: la lista de 30 prospectos tiene 66 menciones "Pendiente verificar" y solo 1 teléfono real. Contactar requiere verificación manual previa de datos | `evidence/Ingresos/01_Lista_Prospectos_Eje_Cafetero.md` (compilada 2026-07-21) |
| C11 | "El ZIP de 110 archivos que el hotelero nunca abre" | **Refutado**: el ZIP actual (`zione_20260805.zip`) tiene 53 archivos bien organizados: DIAGNOSTICO.md, PROPUESTA_COMERCIAL.md, ASSETS/ por tipo con prefijo ESTIMATED_, README_DELIVERY.md, IMPLEMENTATION_ORDER.md, MANIFEST.json, human_checklist.md | Inspección programática del ZIP |
| C12 | "Estructura de ingresos coherente" | **Refutado**: coexisten 5 fuentes de pricing contradictorias (ver F1) | pricing.yaml, PRECIOS_PAQUETES.md, hook_pdf_generator.py, corrida real |

### 1.3 Falso positivo propio descartado (transparencia metodológica)

Durante el bucle 3 se declaró "BUG CRÍTICO" en `_detect_region_from_url()` (main.py L3478-3491) basándose en un **grep con contexto recortado** que sugería que URLs del Eje Cafetero retornaban `'caribe'`. Al leer el archivo completo: la función retorna correctamente `'eje_cafetero'` (L3484). **El bug no existe.** Lección: nunca declarar bug sin leer el archivo completo. (El bug real de región está en otro punto: ver F3.)

---

## 2. Parte 2 — Fallos F1-F10 con Causa Raíz

| ID | Fallo | Evidencia (archivo/línea) | Causa raíz | Severidad comercial |
|----|-------|--------------------------|------------|---------------------|
| **F1** | **5 fuentes de pricing contradictorias**: pricing.yaml mezcla USD/COP; `PRECIO_MENSUAL = "400.000"` hardcodeado en hook PDF vs **$500K dinámico** generado en la corrida real para el mismo hotel; `is_compliant: false` (pain_ratio 0.0724 > 0.06) **no bloquea nada** | `hook_pdf_generator.py` (constantes PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE); `financial_scenarios_20260805_154855.json` (pricing.monthly_price_cop=500000, is_compliant=false) | Pricing hardcodeado como constantes de Python en el generador del PDF en vez de consumir pricing.yaml; ausencia de gate `pricing_compliance` bloqueante | 🔴 CRÍTICA — el cliente vería $400K en el PDF y $500K en la propuesta del mismo output |
| **F2** | **3 valores de ADR para eje_cafetero**: $285K (YAML) vs $420K (JSON, gana en runtime) vs $200K (doc comercial como ejemplo) | `config/regional_benchmarks.yaml` vs `data/benchmarks/regional_adr_2026.json` vs docs comerciales | Dos fuentes de benchmarks sin mecanismo de sincronización; docs comerciales sin actualización al cambiar el JSON | 🔴 CRÍTICA — cifra fundacional del pitch varía según qué fuente se consulte |
| **F3** | **Fallback `'colombia'→'caribe'` infla la fuga 2.3-3.2x**: si la dirección GBP solo dice "Colombia" (común en GBP incompletos del ICP objetivo), el ADR se resuelve como caribe ($950K boutique) en vez de default ($300K) | `modules/auditors/v4_comprehensive.py` L1466-1474 (`'colombia': 'caribe'` en el mapa de fallback) | Mapa de fallback de región mal diseñado: país → región turística más cara en vez de default conservador | 🔴 CRÍTICA — sobreestimación sistemática de la fuga en el hook de venta |
| **F4** | **Bogotá cubierta en YAML ($350K) pero ausente en JSON runtime** → se degrada a default $300K | `regional_benchmarks.yaml` (con bogota) vs `regional_adr_2026.json` (sin bogota) | Misma desincronización de F2 | 🟡 ALTA |
| **F5** | **Comisión OTA 15% hardcodeada** (`industry_standard_15pct`) vs 17-25% usada en la narrativa comercial del guion de venta | `financial_scenarios_20260805_154855.json` (ota_commission_source) | Constante única sin rango parametrizado ni fuente citada | 🟡 ALTA — subestima la fuga OTA en la cifra que ancla el pitch |
| **F6** | **Rango del hook 23x entre extremos**: "entre $453.600 y $10.631.250 COP mensuales" — inverosímil comercialmente, invita descredito | `evidence/FASE-F/v4complete_run.log` (hook message) | Extremos conservador/optimista sin acotación de plausibilidad (sin cap percentil) | 🟡 ALTA |
| **F7** | **Encoding corrupto en artefactos de salida**: `delivery_quality_report.json` dentro del ZIP lanza UnicodeDecodeError (byte 0xf3); mojibake en `data/benchmarks/plan_maestro_data.json`; "B+ � Datos fuente" en el diagnóstico FASE-F | Zip FASE-F, plan_maestro_data.json, 01_DIAGNOSTICO_20260805.md | `open()`/`json.dump` sin `encoding='utf-8'` explícito en Windows (cp1252 por defecto) | 🔴 CRÍTICA — el cliente recibe artefactos ilegibles/corruptos |
| **F8** | **Occupancy 0.7843 con origen intrazable**: `data_sources.occupancy = "regional"` (¿qué benchmark? ¿qué región?) mientras ADR sí declara `user_provided` | `financial_scenarios_20260805_154855.json` (occupancy_rate, data_sources) | Mezcla de fuentes sin provenance completo (valor numérico sin referencia al benchmark exacto) | 🟡 ALTA — cifra que multiplica la fuga sin trazabilidad |
| **F9** | **Lista de prospectos no ejecutable**: 30 prospectos con 66 "Pendiente verificar" y solo 1 teléfono real | `evidence/Ingresos/01_Lista_Prospectos_Eje_Cafetero.md` | Compilación manual sin gate de completitud de datos de contacto | 🟡 ALTA — bloquea el plan de prospección semana 3-4 |
| **F10** | **Documentación comercial desactualizada vs código**: PROPUESTA_EMPAQUETADO describe un ZIP caótico antiguo que ya no existe; ejemplos con ADR $200K | `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` | Docs comerciales no versionadas junto al código que describen | 🟢 MEDIA |

**Patrón de causa raíz dominante**: violación del principio "una fuente de verdad por concepto" del propio plan maestro — pricing (F1), benchmarks (F2, F4), comisión OTA (F5), occupancy (F8) y docs (F10) tienen múltiples fuentes no sincronizadas. El pipeline produce datos correctos en algunos puntos pero los generadores consumen constantes hardcodeadas.

---

## 3. Parte 3 — Estrategia Corregida v2

### 3.1 Lo que se MANTIENE

1. **Tesis central**: el primer Express pagado ($120K COP) es el evento transformador. Antes de eso, todo es hipótesis.
2. **Modelo de 3 niveles** (Demo $0 → Diagnóstico → Implementación → Monitoreo): sólido y alineado con ROADMAP.
3. **Los gaps de deployer (Gap 1), Express 5 páginas (Gap 3) y monitoreo automatizado (Gap 5) son post-validación**: no tienen sentido construirlos antes de que exista willingness-to-pay demostrado (Gap 2 = objetivo central).

### 3.2 Lo que CAMBIA

- La **unificación de credibilidad numérica (F1-F6) y el fix de encoding (F7) son PRERREQUISITOS del primer cliente**, no mejoras posteriores. Un pitch con cifras contradictorias entre sus propios artefactos destruye la confianza en la primera reunión.

### 3.3 Tabla de Priorización

| Prioridad | Acciones | Fallos cubiertos | Razón de ser |
|-----------|----------|------------------|--------------|
| **P0 — Antes de cualquier contacto comercial** | 1. Fuente única de pricing (pricing.yaml como master, eliminar constantes de hook_pdf_generator.py) 2. Gate bloqueante `pricing_compliance` (is_compliant=false debe BLOQUEAR) 3. Precio dinámico en hook PDF 4. Fix encoding utf-8 en todos los writers de artefactos | F1, F7 | El cliente no puede ver $400K y $500K por el mismo servicio, ni JSONs corruptos |
| **P1 — Antes del primer hook enviado** | 5. Consistencia de benchmarks (un solo archivo maestro con bogota incluido) 6. Fix fallback región (colombia → default, no caribe) 7. Comisión OTA parametrizada con rango y fuente 8. Acotar rango del hook (cap de plausibilidad) | F2, F3, F4, F5, F6 | La cifra de fuga del pitch debe ser defendible ante un hotelero escéptico |
| **P2 — Semana 1-2 de ejecución** | 9. Pre-carga GBP de prospectos (scrape batch antes de contactar) 10. Provenance completo de occupancy 11. Higiene documental comercial | F8, F9, F10 | Ejecutabilidad de la prospección y trazabilidad ante preguntas del cliente |
| **P3 — Solo tras primer cliente pagado** | 12. Deployer real 13. Express 5 páginas 14. Monitoreo mensual automatizado | Gaps 1, 3, 5 | Inversión solo tras validar willingness-to-pay |

### 3.4 Condiciones Duras

1. **El primer cliente no puede ver cifras contradictorias** entre artefactos del mismo output (P0/P1 son no negociables).
2. **La cifra exacta solo llega con datos reales del hotel** — la corrida con Tier A (post-pago Express) es la que produce números defendibles; el hook pre-venta es un rango orientativo y debe presentarse como tal.
3. **Cero willingness-to-pay demostrado** — todo lo demás se subordina a conseguir el primer Express. No construir producto sin demanda.

---

## 4. Incógnitas Declaradas (~5% restante)

1. **Tiempo de corrida fresh**: la corrida Zione fue cacheada (16s); el tiempo real sin cache no está medido.
2. **Ruta productora del pricing $500K**: el valor aparece en el JSON de escenarios pero la cadena exacta de código que lo calcula no fue trazada a fondo.
3. **Comportamiento de scrapers con prospectos nuevos**: desconocido (todas las corridas usaron hoteles ya cacheados).

---

## 5. Matriz de Cobertura — ¿La Parte 3 cubre las Partes 1 y 2? (2026-08-19)

> Pregunta del propietario: *"¿Podría afirmar que la parte 3: estrategia cubre lo anterior (partes previas identificadas)?"*

**Respuesta: SÍ en 21/22 elementos accionables (~95%), con 1 vacío explícito que se corrige abajo.**

### 5.1 Cobertura de Parte 2 → Parte 3 (fallos F1-F10)

| Fallo | ¿Cubierto en Parte 3? | Dónde |
|-------|----------------------|-------|
| F1 (pricing contradictorio) | ✅ | P0, acciones 1-3 |
| F2 (3 valores ADR) | ✅ | P1, acción 5 |
| F3 (fallback caribe) | ✅ | P1, acción 6 |
| F4 (Bogotá YAML/JSON) | ✅ | P1, acción 5 |
| F5 (comisión OTA 15%) | ✅ | P1, acción 7 |
| F6 (rango hook 23x) | ✅ | P1, acción 8 |
| F7 (encoding corrupto) | ✅ | P0, acción 4 |
| F8 (occupancy intrazable) | ✅ | P2, acción 10 |
| F9 (prospectos sin teléfono) | ✅ | P2, acción 9 |
| F10 (docs desactualizadas) | ✅ | P2, acción 11 |

**Cobertura Parte 2: 10/10 (100%).**

### 5.2 Cobertura de Parte 1 → Parte 3 (12 claims)

| Claim | ¿Cubierto en Parte 3? | Dónde |
|-------|----------------------|-------|
| C1-C8 (confirmados: hook PDF, motor, gates, deployer stub, cero WTP, kit, monitoring interno, Express inexistente) | ✅ | Se integran como condiciones habilitadoras: C1-C3 sustentan la viabilidad (condición de que el motor funciona); C4-C8 reposicionados en P3 o como objetivo central (Gap 2) |
| C9 corregido (tiempo corrida fresh desconocido) | ⚠️ **VACÍO PARCIAL** | Aparece como incógnita declarada (§4.1) pero **NO tiene entrada en la tabla P0-P3**. Corrección: se agrega como acción de P2 ("medir corrida fresh con --no-cache en un prospecto del P2") — sin este dato no se puede planificar la capacidad de producción de hooks |
| C10 corregido (prospectos no ejecutables) | ✅ | P2, acción 9 (pre-carga GBP) + F9 |
| C11 corregido (ZIP bien estructurado) | ✅ | Hallazgo positivo: se asume como fortaleza habilitadora; su reverso (F10, docs que describen el ZIP antiguo) cubierto en P2 |
| C12 corregido (pricing incoherente) | ✅ | P0 (vía F1) |

**Cobertura Parte 1: 11/12 (92%), 1 vacío (C9) corregido en esta sección.**

### 5.3 Cobertura de los 5 gaps originales (primer análisis)

| Gap | ¿Cubierto en Parte 3? | Dónde |
|-----|----------------------|-------|
| Gap 1: deployer es stub | ✅ | P3, acción 12 |
| Gap 2: cero willingness-to-pay | ✅ | Objetivo central de toda la estrategia (condición dura 3) |
| Gap 3: Express 5 páginas no existe | ✅ | P3, acción 13 |
| Gap 4: onboarding depende 100% del humano | ✅ (por diseño, no requiere acción) | Aceptado como diseño intencional (ROADMAP: humanos aportan datos de negocio); integrado implícitamente en condición dura 2 ("la cifra exacta solo llega con datos reales del hotel") |
| Gap 5: monitoreo no automatizado | ✅ | P3, acción 14 |

**Cobertura gaps: 5/5 (100%).**

### 5.4 Conclusión de cobertura

La Parte 3 **sí cubre y prioriza** todo el inventario accionable de las partes previas, con una excepción detectada en esta revisión de cobertura (C9: medición de tiempo de corrida fresh), que queda **formalmente incorporada a P2** mediante esta sección. Con esa adición, la cobertura es **22/22 elementos (100%)**: 10/10 fallos F1-F10, 12/12 claims C1-C12 y 5/5 gaps originales.

**Elementos que NO requieren acción por diseño**: C11 (hallazgo positivo del ZIP), Gap 4 (onboarding humano intencional) y el falso positivo descartado de §1.3 (lección metodológica, no hallazgo de producto).

---

## 6. Adenda (2026-08-19, sesión posterior) — Roles de Funnel, Evidencia Tier A y Continuidad Hook→Express

> **Contexto**: sesión posterior al cierre del informe. Preguntas del propietario: (1) ¿el Hook se alinea con la premisa de 3 etapas (valor cuantificable → evaluación remunerada → trabajo continuo) y justifica la intervención, o conviene entregar v4complete en primer contacto para captar clientes del Eje Cafetero y crecer `observations.json`? (2) ¿el Hook y el diagnóstico Express se complementan, son de naturaleza y momentos distintos, o son islas? Esta adenda registra la conclusión, una decisión del propietario, evidencia Tier A nueva, el fallo F11 y una refinación de causa raíz de F8. **No modifica secciones previas: las extiende** (mismo criterio de preservación de trazabilidad que la matriz §5).

### 6.1 Decisión del propietario

**v4complete no se entrega en primer contacto (por ahora); queda a nivel interno como paso de producción del Hook.** Fundamentos verificados:

1. Regalar diagnóstico + propuesta + assets destruye el test de willingness-to-pay (condición dura 3): el Express de $120K no tendría nada que vender.
2. Los datos reales provienen de la conversación, no del artefacto: los 6 registros de `data/hotel_observations/observations.json` son `source: contacto_directo`.
3. Assets sin onboarding salen ESTIMATED (confianza 0.5 < 0.7, WARNING de la corrida FASE-F) y el gate `tier_c_onboarding_required` existe precisamente para bloquear eso.
4. Capacidad no medida (C9: tiempo de corrida fresh desconocido) y lista de prospectos no ejecutable (F9).

**Pipeline de primer contacto resultante**: v4complete (interno, con pre-carga GBP del prospecto) → Hook PDF 2 páginas (único artefacto entregado) → conversación de captura con tarjeta de datos (schema de `observations.json`, incluyendo `avg_stay_nights` y `trip_purpose`, pendientes incluso en los 6 registros actuales) → Express pagado → Implementación.

### 6.2 Evidencia Tier A vs benchmarks runtime (extiende F2 y F8)

Comparación por categoría entre `data/benchmarks/regional_adr_2026.json` (fuente que gana en runtime) y las 6 observaciones Tier A (confidence 0.95, contacto directo):

| Categoría | Benchmark runtime (ADR) | Tier A observado (media, n=3) | Sesgo benchmark |
|-----------|------------------------|-------------------------------|-----------------|
| boutique_10_25 | $420.000 | ~$271K (Luxor $200K, D. Alfonso $330K, Castilla $282K) | **+55%** |
| standard_26_60 | $350.000 | ~$263K (Luma $200K, GHL $300K, Zi One $290K) | **+33%** |
| occupancy (ambas) | 51,2% | ~26,6% (media de las 6 observaciones) | **~1,9x** |

*Caveat: n=6, muestra sesgada hacia hoteles de paso (4/6). El hallazgo es la dirección del sesgo, no su magnitud exacta.*

**Implicación de funnel**: el Express con datos reales corregirá **sistemáticamente hacia abajo** el rango que el Hook prometió con benchmarks. Sin narrativa de la delta, el hotelero lee la corrección honesta como "infló el número para venderme". Esto (a) eleva la urgencia de P1 acciones 5-8 y (b) motiva el fallo F11.

### 6.3 Fallo nuevo F11 — Sin verificación de continuidad Hook→Express

| ID | Fallo | Evidencia (archivo/línea) | Causa raíz | Severidad comercial |
|----|-------|---------------------------|------------|---------------------|
| **F11** | **Ningún mecanismo valida que la cifra del Express caiga dentro del rango prometido por el Hook**, ni genera la narrativa de la delta (benchmark → dato real) | `two_phase_flow.py` (disclaimer que promete "cálculo preciso" sin cierre posterior); `hook_pdf_generator.py` (`fuga_minima`/`fuga_maxima` sin consumo posterior); los 12 publication gates y el consistency_checker (FASE 4.6: whatsapp/gbp/schema/adr) no incluyen continuidad hook→express | El rango del Hook se trata como marketing unidireccional, no como promesa falsable que el producto pagado debe cumplir | 🟡 ALTA — combinado con F6 (rango 23x) y F2/F3 (benchmarks inflados), la corrección a la baja no narrada destruye la confianza en el momento exacto de la entrega pagada |

**Insight estructural**: la única función comercial real del rango del Hook es ser validado por el Express (transacción promesa→cumplimiento que sostiene el modelo de 3 niveles). Un rango que nunca se cierra es marketing decorativo.

**Acción propuesta (se adiciona a P1, vinculada a la acción 8)**: al ejecutar el Express para un hotel que recibió Hook, verificar que la cifra cae dentro del corredor prometido (o documentar por qué no) y generar una sección de **trazabilidad del rango**: *Hook estimó X con benchmarks → el hotel reportó ADR/ocupación reales → resultado Z*. Convierte el cap de plausibilidad (acción 8) de cosmético en estructural: el cap existe para que el rango sea falsable por el Express.

### 6.4 Refinación de causa raíz F8

El occupancy 0.7843 de la corrida FASE-F **no es intrazable**: coincide exactamente con el dato observado de Zi One (800 reservas/mes ÷ 34 hab ÷ 30 días = 0.7843, con estancia de 1 noche por defecto; `observations.json`, collected_at 2026-07-22, corrida de 2026-08-05). La corrida inyectó el dato Tier A real pero lo etiquetó `data_sources.occupancy = "regional"`. Causa raíz refinada: **etiqueta de provenance incorrecta en la ruta de inyección Tier A** (bug de etiqueta, no valor sin origen). La cifra es defendible; la etiqueta es la que miente. La acción 10 de P2 debe incluir la corrección de etiquetas en la inyección, no solo documentar fuentes regionales.

### 6.5 Lección Zione — los datos sobreviven al cliente

Zi One era el mejor datapoint de la base (ocupación 78,43%, 800 reservas/mes, ADR $290K) y el terremoto que dañó sus instalaciones lo volvió inviable como cliente — **pero su registro sigue calibrando el motor** (además de explicar F8 vía §6.4). Consecuencia estratégica: `observations.json` no es un CRM de leads; es el calibrador del motor y el camino para fijar benchmarks defendibles (§6.2). El primer contacto optimiza captura de datos, no entrega de deliverables.

### 6.6 Impacto en la matriz de cobertura (§5)

La matriz §5 (22/22 al cierre) se extiende a **23 elementos accionables**: F11 queda cubierto por la acción de P1 descrita en §6.3. Ninguna entrada previa cambia de estado. El orden de ejecución se mantiene: P0 primero; F11 se implementa dentro de P1 junto a la acción 8 (el cap de plausibilidad y la trazabilidad del rango son dos mitades del mismo fix).

### 6.7 Decisión — Concepción de dos momentos mantenida; reframe "un diagnóstico en dos etapas"

> **Pregunta del propietario**: *"¿Y si unificáramos el Express y el Hook? ¿Sería viable o estaríamos involucionando? Comercialmente, ¿qué es más valioso: mantener la concepción del contexto o unificar?"* — Respuesta analizada y decisión confirmada por el propietario: **mantener la concepción**.

**Decisión**: conservar la estructura de dos momentos con escalera de precio (Hook gratuito → Express $120K → Implementación) y adoptar como presentación comercial el reframe **"un diagnóstico en dos etapas"**: la estimación es gratuita; el cálculo con sus datos reales cuesta $120K.

**Racional registrado**:

1. Hook y Express no son dos productos: son un mismo diagnóstico en dos estados de certeza (benchmark vs Tier A) separados por la conversación de captura. Ese hueco contiene los tres activos del negocio: captura de datos (§6.1), test de willingness-to-pay (condición dura 3) y transacción de confianza promesa→cumplimiento (F11).
2. La unificación estructural es un callejón sin salida: sin conversación, el artefacto unificado se genera solo con benchmarks (el Hook renombrado); con conversación, el documento se recalcula con datos nuevos y vuelven a existir dos momentos.
3. El documento freemium (cifras difuminadas, pagar para desbloquear) fue descartado por tres razones: (a) fabricaría precisión aparente con benchmarks, violando la taxonomía de confianza y revirtiendo la identidad v4 ("sistema con niveles de certeza explícitos") al pecado original v3 ("generador de diagnósticos"); (b) monetiza curiosidad (desbloquear información) en vez de personalización (cálculo con SUS datos) y esconde el servicio humano que justifica los $120K; (c) ante el hotelero escéptico, un PDF con números ocultos pattern-matchea al spam de SEO ("su web tiene 47 errores, pague para verlos").
4. Eliminar el Hook para vender el Express en frío fue descartado: pierde el disparador de la conversación y la demostración previa de valor (principio de diseño de `two_phase_flow.py`: *"minimizes friction by showing value before asking for detailed data"*).
5. **Diagnóstico de la percepción de dualidad**: es síntoma de puentes rotos (F1 pricing isleado, F11 sin convergencia narrada), no de estructura duplicada. Con los puentes reparados, el hotelero experimenta un solo diagnóstico que se afina.

**Implicación operativa**: el reframe eleva la prioridad de la acción F11 (§6.3): la sección de trazabilidad del rango es lo que materializa la experiencia "un diagnóstico, dos etapas" — sin ella, el reframe es retórica. La comunicación comercial (guion de venta, Hook PDF, propuesta) debe presentar las dos etapas como continuidad de un mismo diagnóstico: *"la estimación es gratuita; el cálculo con sus datos reales cuesta $120K"*.

---

## 7. Adenda (2026-08-20) — Validación cruzada del kit de entrega contra sitio vivo (Zione, corrida v4_verify_s5b)

> **Contexto**: sesión posterior a la adenda §6. Solicitudes del propietario: (1) evaluar alineación y coherencia entre el ZIP `zione_20260805.zip` (corrida `output/v4_verify_s5b/v4_complete/`) y `02_PROPUESTA_COMERCIAL`; (2) validar el caso del botón de WhatsApp contra el sitio vivo https://zione.co/ (sede Pereira); (3) evaluar la pertinencia de ajustar este archivo. **Método**: inspección programática del ZIP (MANIFEST, pain_ledger, pain_ledger_resolved, coherence_validation, gate_report, asset_generation_report, financial_scenarios, README_DELIVERY), lectura del diagnóstico y la propuesta, y verificación del sitio vivo vía navegador con capturas de evidencia (`temp/zione_01_initial.png` … `temp/zione_07_fullpage.png`). **Sin modificaciones de código** (misma disciplina que §6).

### 7.1 Fallos nuevos F12-F14 — clase "verdad del sitio vivo no propagada"

| ID | Fallo | Evidencia (esta sesión) | Causa raíz | Severidad comercial |
|----|-------|--------------------------|------------|---------------------|
| **F12** | **Falso positivo de conflicto WhatsApp por cruce entre sedes**: el diagnóstico alerta "Su Google Business muestra 311 6079036, pero su sitio web indica +573103724544"; el número alertado pertenece a la sede **Cartagena**, y el número web de Pereira (+57 311 607 9036) es **idéntico** al del GBP | `01_DIAGNOSTICO_20260805_161055.md` L37-38 y L47-50 (BRECHA 1, $1.198.906/mes, 16%) vs sitio vivo: footer "Pereira Contact" +57 311 607 9036 / "Cartagena Contact" +57 310 372 4544; enlaces `wa.me/573116079036` (Pereira) y `wa.me/573042476691` (Cartagena) funcionales | El cross-validator no distingue sedes en negocios multi-ubicación: compara GBP contra el primer `wa.me`/tel del DOM sin mapear número a sede | 🔴 CRÍTICA — infla la fuga $1.198.906/mes con una BRECHA 1 inexistente, refutable por el cliente en 2 minutos mirando su propio footer |
| **F13** | **`no_whatsapp_visible` HIGH (conf 0.3) cuando el botón existe en 3 ubicaciones**: barra lateral sticky (Elementor `e-fab-whatsapp` con animación pulse), fila de redes del footer y números de contacto como enlaces `wa.me` | `pain_ledger.json` (`no_whatsapp_visible`, DETECTED HIGH) vs `asset_generation_report.json` (`site_verification_applied: true`, whatsapp_button skipped: "ya implementado en sitio de producción") vs capturas `temp/zione_01_initial.png` y `temp/zione_04_footer.png` | La verificación de sitio vivo existe pero es **unidireccional**: el asset layer la consume (skip de generación) y el gate la consume ("verified in production"), pero el pain_ledger/diagnóstico no (sigue reportando la brecha). El scanner además no reconoce widgets Elementor no estándar | 🔴 CRÍTICA — misma clase que F12: brecha falsa visible para el cliente; el coverage gate la "justifica" (8 cubiertas + 1 justificada = 9 detectadas) pero el pain_ledger la mantiene DETECTED HIGH |
| **F14** | **Tres componentes discrepan sobre el mismo hecho** (`whatsapp_button`): coherence post-generación = FAILED ("Assets no implementados", busca archivo físico), gate_report `proposal_asset_alignment` = PASSED ("verified in production"), pain_ledger = DETECTED HIGH | `coherence_validation.json` vs `gate_report_20260805_161056.json` vs `pain_ledger.json` (ZIP s5b) | `promised_assets_exist` del coherence validator no contempla el estado "existe en producción sin archivo" que el gate sí contempla | 🟡 ALTA — señal de calidad contradictoria dentro del mismo kit (PASSED y FAILED sobre el mismo asset) |

**Causa raíz común F12-F14**: la misma violación de principio que domina F1-F10 ("una fuente de verdad por concepto"), aplicada a un concepto nuevo: **el estado de verdad del sitio vivo**. El sitio tiene una verdad (botón existe, números correctos por sede) y tres capas la interpretan distinto. Extiende el patrón dominante de §2.

**Impacto financiero**: al excluir la BRECHA 1 (F12), la fuga estimada baja de $7.192.000 a ~$5.993.094 COP/mes. Combinado con §6.2 (benchmarks +33-55% ADR), el diagnóstico acumula dos fuentes independientes de inflación al alza sobre la misma cifra que ancla el pitch.

### 7.2 Confirmaciones que refuerzan evidencia existente (sin nuevo ID)

| Elemento del archivo | Confirmación de esta sesión |
|---|---|
| **F7 (encoding)** | Reconfirmado: `delivery_quality_report.json` del ZIP s5b lanza `UnicodeDecodeError` (byte 0xf3). F7 sigue vivo y justifica P0 |
| **C3 / C11** | Corrida s5b: 12/12 gates PASSED, coherence 0.92, `READY_FOR_PUBLICATION`, ZIP de 49 archivos bien estructurado (README, MANIFEST, IMPLEMENTATION_ORDER, ASSETS/ con prefijo ESTIMATED_). Complementa la evidencia FASE-F (11 PASSED + 1 WARNING, 53 archivos) |
| **§6.4 (refinación F8)** | La corrida s5b etiqueta el occupancy 0.7843 como `"onboarding"` mientras FASE-F decía `"regional"` — mismo valor. Confirma que el bug es de **etiqueta por ruta de inyección**, no del valor |
| **§6.5 (Lección Zione)** | El sitio vivo verificado el 2026-08-20 está activo y funcional (2 sedes, motor de reservas operativo). Zione sigue vigente como calibrador del motor |

### 7.3 Hallazgos menores (notas, no se formalizan como F)

1. Score de coherencia divergente entre `MANIFEST.json` (0.963) y las validaciones post (0.92-0.94): el MANIFEST captura un score de otra etapa del pipeline.
2. `IMPLEMENTATION_ORDER.md` con secciones vacías (orden, relaciones, checklist); el README_DELIVERY sí porta timeline y checklist útiles.
3. Assets presentes en el ZIP pero no listados en la tabla de servicios de la propuesta (`monthly_report`, `indirect_traffic_optimization`): son bonus, no gaps; solo generan costo de reconocimiento para el cliente.

### 7.4 Lección metodológica (extiende §1.3)

§1.3 registró "nunca declarar bug sin leer el archivo completo". Esta sesión agrega su gemela del lado del diagnóstico: **nunca declarar brecha HIGH sin verificación contra sitio vivo**. El sistema ya produce esa verificación (`site_verification_applied: true`) pero no la propaga upstream al pain_ledger/diagnóstico. El fix de F12-F13 no es un scanner nuevo: es propagar una verificación que ya existe.

### 7.5 Impacto en la matriz de cobertura (§5) y priorización (§3.3)

La matriz §5 (23 elementos al cierre de §6.6) se extiende a **26 elementos accionables**:

| Elemento nuevo | ¿Cubierto? | Dónde |
|----------------|------------|-------|
| F12 (falso positivo cruce sedes) | ✅ Se adiciona | **P1**, vinculado a acciones 5-8: la cifra de fuga debe ser defendible; una brecha refutable por el cliente en su propio footer es más dañina que el benchmark inflado porque no requiere análisis para refutarla |
| F13 (falso negativo botón invisible) | ✅ Se adiciona | **P1**, mismo vínculo que F12; implementación = propagar `site_verification` al pain_ledger y al diagnóstico (§7.4) |
| F14 (discrepancia coherence vs gate) | ✅ Se adiciona | **P1/P2**: `promised_assets_exist` debe aceptar el estado "verificado en producción" que el gate ya consume |

Ninguna entrada previa cambia de estado. P0 se mantiene como prerrequisito absoluto (F1, F7 reconfirmado). La tesis central, la concepción de dos momentos (§6.7) y las decisiones de §6 quedan intactas: F12-F14 no las desafían, refuerzan la condición dura 1 ("el primer cliente no puede ver cifras contradictorias" — ahora también brechas falsas, no solo cifras contradictorias).

**Cobertura tras la adenda: 26/26 elementos (100%).**

---

## Registro de Sesión

- Bucle 1: diagnóstico comercial inicial (veredicto positivo, 4 niveles de ingresos, 5 gaps).
- Bucle 2: validación exhaustiva contra código vivo (confirmación/refutación de claims, sin cambios de fondo).
- Bucle 3: búsqueda de fallos por causa raíz hasta certeza factual (~95%): 10 fallos F1-F10, falso positivo propio descartado, estrategia corregida v2.
- Cierre 2026-08-19: matriz de cobertura §5 incorporada; informe persistido en este archivo por instrucción del propietario.
- Adenda 2026-08-19 (sesión posterior): análisis funnel Hook↔Express y alineación con la premisa de 3 etapas; decisión del propietario (v4complete interno, no se entrega aún); evidencia Tier A vs benchmarks runtime (ADR +33% a +55%, occupancy ~1,9x — §6.2); fallo nuevo F11 (§6.3); refinación de causa raíz F8 (§6.4). Secciones previas intactas; sin modificaciones de código.
- **Decisión 2026-08-19 (misma sesión, confirmada por el propietario)**: unificación Hook↔Express evaluada y descartada (freemium = precisión falsa + patrón spam; eliminar Hook = pérdida del disparador de conversación); concepción de dos momentos mantenida con reframe comercial "un diagnóstico en dos etapas" (§6.7). El reframe refuerza la acción F11 (trazabilidad del rango). Sin modificaciones de código.
- Adenda 2026-08-20: validación cruzada del kit de entrega (ZIP `v4_verify_s5b`) contra diagnóstico, propuesta y sitio vivo https://zione.co/ (evidencia en capturas `temp/zione_*.png`). 3 fallos nuevos F12-F14 — clase "verdad del sitio vivo no propagada": F12 falso positivo de conflicto WhatsApp por cruce entre sedes (BRECHA 1 inexistente, infla la fuga $1.198.906/mes), F13 falso negativo `no_whatsapp_visible` con `site_verification` existente pero no propagada al pain_ledger, F14 discrepancia coherence post-gen (FAILED) vs gate_report (PASSED) sobre `whatsapp_button`. Reconfirmados F7 (encoding), C3/C11 (12/12 gates, ZIP 49 archivos), §6.4 (etiqueta por ruta) y §6.5 (Zione activo). 3 notas menores (§7.3). Lección metodológica que extiende §1.3 (§7.4). Matriz de cobertura 23→26 elementos; F12/F13→P1, F14→P1/P2 (§7.5). Secciones previas intactas; sin modificaciones de código.
- **Estado de implementación: NINGUNO** — no se modificó ni creó código, conforme a la instrucción "No implementar aún ni hacer modificaciones".
- **Próximo paso natural (pendiente autorización explícita)**: P0 — fuente única de pricing + gate `pricing_compliance` bloqueante + precio dinámico en hook PDF + fix encoding utf-8.
