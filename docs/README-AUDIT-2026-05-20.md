# Auditoría README.md — iah-cli (AMPLIADA v2)

**Fecha:** 20 Mayo 2026  
**Perspectiva:** Hotelero colombiano / Directivo COTELCO  
**Archivo auditado:** `README.md` (301 líneas, 14.5 KB)  
**Auditoría extendida:** Código vivo vs README — errores factuales verificados en código  
**Versión del informe:** v2 — incluye validación contra código fuente

---

## DIAGNÓSTICO DEL README: JUEGO DE ROLES HOTELERO / COTELCO

**Escenario**: Soy Juan Pablo, gerente de un hotel de 40 habitaciones en Pereira. Me hablaron de "iah-cli" en un evento de COTELCO. Abro el README en GitHub. Quiero entender si esto me sirve o no.

---

### LÍNEAS 1-5: Título y Subtítulo

```
# IA Hoteles Agent CLI
**Plataforma agéntica de diagnóstico de visibilidad digital hotelera: audita presencia en Google, IAs y búsquedas locales; cuantifica la fuga de reservas directas; y genera assets técnicos (schema, FAQ, llms.txt) para recuperar ingresos que hoy van a OTAs y competidores.**
```

**Veredicto hotelero**: El título dice "CLI" y yo no sé qué es CLI. Ya me perdí. El subtítulo es denso y largo: 3 cláusulas en una sola oración. Las palabras "agéntica", "assets técnicos", "schema", "FAQ", "llms.txt" son jerga que no entiendo. Lo único que me conecta es "fuga de reservas directas" y "recuperar ingresos que hoy van a OTAs" — eso SÍ me interesa muchísimo, pero está ahogado entre términos técnicos.

**Sugerencia**:
- Título: `# IA Hoteles — Recupera las Reservas que Pierdes ante Booking y ChatGPT`
- Subtítulo en 2-3 líneas cortas, lenguaje de negocio primero, tecnología después:
  ```
  Descubre cuánto dinero pierde tu hotel porque no te encuentran en Google, 
  Siri ni ChatGPT — y obtén un plan accionable para recuperarlo.
  
  Plataforma automatizada de diagnóstico y optimización digital para hoteles colombianos.
  ```

---

### LÍNEA 5: Versión y Codename

```
**Version:** 4.47.0 | **Codename:** ADVISORY-WARNINGS | **Ultima actualizacion:** 17 Mayo 2026
```

**Veredicto hotelero**: "Codename: ADVISORY-WARNINGS" me asusta. Suena a que el sistema tiene problemas de advertencias. Un codename interno no le dice nada a un externo; peor, puede generar desconfianza. La versión 4.47.0 tampoco me dice nada — necesita un contexto como "4 años de desarrollo, 47 actualizaciones".

**⚠️ HALLAZGO AMPLIADO (código vivo):** El codename ADVISORY-WARNINGS está justificado en VERSION.yaml l.8-11: corresponde a la FASE-A de v4.47.0 donde se implementaron advisory warnings en el diagnóstico y delivery_quality_report. El nombre tiene sentido técnico válido, pero en el README sobra — es información interna que no aporta al hotelero.

**Sugerencia**: Simplificar o quitar el codename de cara al público:
```
**v4.47.0** — Actualizado 17 Mayo 2026 | +2,700 pruebas automatizadas | 0 errores conocidos
```

---

### LÍNEAS 9-21: Índice de Navegación Rápida

**Veredicto hotelero**: La tabla tiene 8 filas, la mayoría apuntan a archivos internos (`.agents/workflows/`, `AGENTS.md`, `.cursorrules`). Solo un hotelero necesitaría quizá 2-3 de estos. El índice está diseñado para el desarrollador, no para el prospecto comercial.

**Sugerencia**: Agregar una sección distinta para "Si eres hotelero o directivo" vs "Si eres desarrollador":

```
| Si eres... | Empieza por... |
|-------------|-----------------|
| **Hotelero / Gerente** | Sección "¿Qué problema resuelve?" abajo |
| **Directivo COTELCO / Gremio** | Sección "Ventajas para negocios locales" |
| **Desarrollador / Técnico** | Índice completo → [INDICE_DOCUMENTACION.md] |
```

---

### LÍNEAS 24-33: Estado del Proyecto

**Veredicto hotelero**: Veo "2,721 test functions", "192 módulos Python", "69K líneas", "225 archivos de test", "9 publication gates", "Coherence Score >= 0.8", "Financial Evidence Engine". Cero de esto me importa como hotelero. Es información de ingeniería que pertenece a la guía técnica, no al README de presentación.

**⚠️ ERROR-1 DETECTADO (verificado en código):** README línea 27 dice "225 archivos de test". El código vivo tiene 209 archivos (209 test files Python reales). Diferencia: 16 archivos. El ROADMAP.md (2026-05-14) ya decía 210, indicando que la cifra migró o se redujo. La cifra de "225" está desactualizada.

**⚠️ ERROR-2 DETECTADO (verificado en código):** README líneas 30-31 dice "9 publication gates (6 blocking + 3 advisory)". El código vivo (`modules/quality_gates/publication_gates.py` l.157-169) tiene **11 gates** en el diccionario `self.gates`: los 6 blocking esperados + 3 advisory esperados + 2 adicionales NO documentados:
- `tier_c_onboarding_required` (l.167) — Gate de Tier C (propuestas preliminares requieren onboarding para publicarse)
- `coverage` (l.168) — "Coverage — No Silent Drop" (FASE-0C: ninguna brecha puede desaparecer sin explicación)

**Causa raíz de ERROR-1 y ERROR-2:** Desincronización post-fase. Cada fase agrega gates, assets o métricas pero no actualiza списки numéricos del README. No existe hook de pre-commit que valide conteos reales vs README.

**Sugerencia**: Mover toda esta sección a `GUIA_TECNICA.md`. En el README, reemplazar con algo que un hotelero valore:

```
## Confianza y Rigor
- +2,700 pruebas automatizadas — sin errores conocidos
- Cada dato financiero tiene origen rastreable y etiqueta honesta
- Sistema de 9 controles de calidad antes de entregar resultados (verdadd)
- Usado en hoteles reales de Colombia con datos verificados
```

---

### LÍNEAS 37-47: Cómo Funciona el Sistema

**Veredicto hotelero**: "cerebro orquestador (Agent Harness)" — más jerga. Los 5 pasos (Recolecta, Valida, Calcula, Genera, Certifica) son buena estructura, pero el lenguaje sigue siendo técnico. "recovery_factor", "YAML", "backwards compatible" se me escapan.

**⚠️ HALLAZGO NUEVO-4 (código vivo):** El flujo 5-fase del README NO menciona que existe un paso crítico implícito: **Onboarding**. Sin `onboard` (captura de datos operativos reales del hotel), el coherence score多半 no alcanza 0.8 y la propuesta comercial多半 no se desbloquea. El README presenta v4complete como flujo automático, omitiendo este requerimiento que determina si el cliente recibe propuesta o solo diagnóstico.

**Sugerencia**: Mantener los 5 pasos pero en lenguaje de negocio:

```
1. **Investiga** → Revisa tu web, Google Maps y datos online del hotel
2. **Verifica** → Cruza fuentes para detectar contradicciones (¿tu web dice una tarifa y Google otra?)
3. **Calcula** → Proyecta cuánto podrías recuperar en 3 escenarios
4. **Entrega** → Diagnóstico + Propuesta comercial + Archivos listos para subir
5. **Certifica** → Control de calidad antes de entregar — no vendemos humo

NOTA: Para recibir la propuesta comercial (no solo el diagnóstico), necesitas 
proporcionar datos reales de tu hotel via `onboard`.
```

---

### LÍNEAS 51-62: Qué es IA Hoteles Agent? + 4 Pilares

**Veredicto hotelero**: Esta es la sección MÁS IMPORTANTE del README y está bien escondida en la línea 51, después de secciones técnicas. La pregunta "Por qué este hotel pierde reservas" es EXCELENTE y debería estar arriba, en la línea 3. La tabla de 4 pilares es CLARA y BUENA — es lo primero que un hotelero debería ver. Los ejemplos son comprensibles ("Siri lee tu ficha: Cierra a las 8:00 PM").

**Sugerencia**: Esta sección debería ser la #1 o #2 del README, no la #5. Mover arriba. Reforzar con una pregunta gancho antes de la tabla:

```
## ¿Por qué tu hotel pierde reservas?

Cada mes, hoteles colombianos pierden reservas que van a Booking.com, competidores
o respuestas de ChatGPT — porque no aparecen donde los viajeros buscan.

IA Hoteles responde: **¿Cuánto pierde SU hotel y qué puede hacer al respecto?**
```

---

### LÍNEAS 66-81: Inicio Rápido (5 minutos)

**Veredicto hotelero**: `git clone`, `python -m venv venv`, `.\venv\Scripts\Activate.ps1` — esto no es "5 minutos" para un hotelero. Es intimidante. Un hotelero no va a clonar un repo. Esta sección es 100% para desarrolladores.

**Sugerencia**: Separar en dos rutas:

```
## ¿Cómo empezar?

**Para hoteleros y gerentes** (sin instalar nada):
1. Pide un diagnóstico a tu asesor digital o contáctanos
2. Recibirás un informe con: brechas detectadas, costo en pesos, plan de acción

**Para desarrolladores y consultores:**
```bash
git clone https://github.com/jhondrl6/ia-hotels-agent.git
cd iah-cli
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py setup
python main.py v4complete --url https://hotel.com
```
```

---

### LÍNEAS 85-108: Flujo v4complete (5 Fases)

**Veredicto hotelero**: El diagrama ASCII es claro para un técnico. Para un hotelero, "HOOK -> VALIDACION -> MAPEO P->S -> GATE COHERENCIA -> ASSETS" es incomprensible. "coherence >= 0.8", "PainSolutionMapper" no significan nada.

**Sugerencia**: Agregar una versión narrada del flujo:

```
**Lo que tu hotel recibe:**

FASE 1: Diagnóstico automático de tu presencia online
FASE 2: Verificación cruzada (¿tu web contradice a Google Maps?)
FASE 3: Mapeo de problemas → soluciones priorizadas
FASE 4: Control de calidad (solo entregamos si los datos son confiables)
FASE 5: Archivos listos para deploy (schema, FAQ, llms.txt)

**Siempre recibes:** Diagnóstico con costo de brechas en COP
**Si los datos son confiables:** Propuesta comercial + Kit de implementación
```

---

### LÍNEAS 111-134: Comandos Disponibles

**Veredicto hotelero**: Tabla de 10 comandos con estado. A un hotelero solo le importan 2-3: "v4complete" (que es el análisis) y "onboard" (que mejora el análisis). El resto es ruido. Además, la tabla mezcla activos y deprecados sin jerarquía visual.

**Sugerencia**: Reducir a los 3 que importan al prospecto, mover el resto a guía técnica:

```
| Comando | Para qué | Qué recibes |
|---------|----------|-------------|
| `v4complete` | Análisis completo | Diagnóstico + Propuesta + Assets |
| `onboard` | Mejorar con tus datos reales | Mayor precisión financiera |
| `--doctor` | Verificar que todo funciona | Reporte de salud del sistema |
```

---

### LÍNEAS 137-151: Comando onboard

**Veredicto hotelero**: "confidence ESTIMATED -> VERIFIED", "WARNING -> PASSED" — jerga de gates internos. Un hotelero entiende "mejora la precisión del análisis con datos reales de tu hotel". La lista de datos que captura (habitaciones, ADR, ocupación) es BUENA — es lo que un hotelero conoce.

**Sugerencia**: Simplificar lenguaje:

```
**¿Qué datos te pedimos?** Los que ya tienes a la mano:
- Número de habitaciones
- Reservas mensuales
- Tarifa promedio (ADR)
- % de reservas por canal directo
- % de ocupación

**Resultado:** De estimaciones pasamos a datos verificados → tu diagnóstico es más preciso.
```

---

### LÍNEAS 154-175: Doctor — Diagnóstico del Ecosistema

**Veredicto hotelero**: "Symlink integrity", "Shadow logs health", "Gitignore patterns" — cero relevante para un hotelero. Esta sección es 100% operacional interna.

**Sugerencia**: Mover íntegramente a `GUIA_TECNICA.md`. En README: una línea que diga "El sistema incluye autodiagnóstico integrado (`--doctor`) para verificar su correcto funcionamiento."

---

### LÍNEAS 179-192: Escenarios Financieros

**Veredicto hotelero**: Esta sección es VALIOSA pero mal presentada. "recovery_factor 0.15" es opaco. La fórmula matemática asusta. Pero el concepto de 3 escenarios con probabilidades es excelente y un hotelero lo entiende si se le explica en su idioma.

**⚠️ HALLAZGO NUEVO-1 (código vivo):** La fórmula `projected_gain = monthly_loss_cop x pain_ratio x recovery_factor` está simplificada. En realidad:
- `recovery_factor` es correcto: 0.15/0.20/0.25 según escenario (config/scenarios.yaml l.11-13) ✅
- `pain_ratio` NO es un valor único. Es un vector de 15 pesos diferenciados por tipo de dolor (`config/regional_benchmarks.yaml` l.19-33). Cada brecha (no_whatsapp_visible=0.20, low_gbp_score=0.30, etc.) tiene su propio factor. El README presenta pain_ratio como escalar único cuando es un vector de 15 valores.

**⚠️ HALLAZGO NUEVO-5 (código vivo):** El recovery_factor de 0.15 (conservador) puede malinterpretarse. La comisión OTA mínima es 18% (financial_defaults.yaml l.15). Recuperar solo 15% de la fuga dejaría al hotel en peor posición que OTA si no se contextualiza. El factor de recuperación de 0.15 representa "de cada 100 viajeros que te buscan pero no te reservan porque no te encuentran, recuperas 15 al año" — no "recuperas 15% de comisiones OTA". Esta distinción no está explicada en el README.

**Sugerencia**: Reformular:

```
## Proyecciones Financieras: 3 Escenarios

| Escenario | Probabilidad | Qué significa |
|-----------|---------------|---------------|
| **Conservador** | 70% | En el peor de los casos, recuperas ~15% de lo que pierdes |
| **Realista** | 20% | Con mejoras moderadas, recuperas ~20% |
| **Optimista** | 10% | Si implementas todo, recuperas hasta ~25% |

**Ejemplo real:** Un hotel que pierde $10M COP/mes en comisiones OTA
podría recuperar entre $1.5M (conservador) y $2.5M (optimista) mensuales.

**Principio:** Cada peso tiene origen rastreable. No inventamos cifras.
Si un dato es estimado, lo marcamos. Si es verificado, lo certificamos.

**Cómo funciona:** El modelo aplica un factor de recuperación (15-25%) sobre la pérdida 
mensual estimada. La pérdida se calcula a partir de tus reservas perdidas por canal directo,
no de las comisiones OTA.
```

---

### LÍNEAS 196-209: Configuración YAML

**Veredicto hotelero**: 100% técnico. "31 hardcoded values migrados a 6 archivos YAML" — un hotelero no sabe ni qué es YAML ni le importa.

**Sugerencia**: Mover a GUIA_TECNICA.md. En README: "Todos los parámetros son configurables sin tocar código — desde precios hasta umbrales financieros."

---

### LÍNEAS 213-229: Voice Readiness Proxy

**Veredicto hotelero**: Este concepto es MUY BUENO y MUY RELEVANTE para un hotelero ("¿Siri menciona tu hotel?"). Pero el título "Voice Readiness Proxy" y la tabla de pesos porcentuales lo oscurecen. Los niveles Critical/Basic/Good/Excellent son útiles.

**Sugerencia**: Renombrar y simplificar:

```
## ¿Puede Siri Recomendar Tu Hotel?

Cuando un viajero pregunta "Siri, ¿dónde me quedo en Pereira?" — 
¿tu hotel aparece en la respuesta?

| Nivel | Rango | Significado |
|-------|-------|-------------|
| 🔴 Crítico (0-25) | Siri ni te menciona — no existes para voz |
| 🟡 Básico (26-50) | Datos parciales — apareces pero mal |
| 🟢 Bueno (51-75) | Optimización sólida — voz te captura |
| 🟢✅ Excelente (76-100) | Presencia completa y consistente |

IA Hoteles evalúa 4 factores: tu ficha de Google, schema de datos, 
posicionamiento en Google y cobertura de datos factuales.
```

---

### LÍNEAS 233-244: Calidad Garantizada

**Veredicto hotelero**: Repite la sección de "Estado del Proyecto" (línea 24). Misma información técnica. "Pre-commit hooks", "Suite de regresión Amaziliahotel + Hotel Visperas" — nombres de casos de prueba internos que no explican nada.

**⚠️ ERROR-3 DETECTADO (verificado en código):** README línea 242 lista `ia_readiness_critical` como "advisory gate". El código vivo NO tiene ningún gate con ese nombre. En `delivery_quality_report.py` l.194-200, `ia_readiness_critical` aparece como **advisory warning** (no gate) — se emite cuando el score IA es critical o < 50 en el delivery_quality_report. Es una alerta, no un gate bloqueante ni advisory. El README confundió "advisory warning" con "advisory gate".

**Sugerencia**: Consolidar con Estado del Proyecto. Una única sección corta:

```
## Rigor y Transparencia

- +2,700 pruebas automatizadas — 0 errores conocidos
- 9 controles de calidad antes de entregar resultados (9 gates activos)
- Cada dato financiero: rastreable, etiquetado (verificado vs estimado)
- Backwards compatible: funciona sin configuración adicional
- Advisory warnings: el sistema también alerta sobre riesgos no-bloqueantes (ej: IA-Readiness Critical)
```

---

### LÍNEAS 248-255: Troubleshooting

**Veredicto hotelero**: 3 problemas técnicos ("sync_versions.py desincronizado") que no le importan a un hotelero.

**⚠️ HALLAZGO AMPLIADO:** `sync_versions.py` sí existe en `scripts/sync_versions.py` y el troubleshooting es técnicamente correcto. PERO para un hotelero es irrelevante. El problema de desincronización de versiones es un problema de desarrollo, no de uso.

**Sugerencia**: Mover a GUIA_TECNICA.md. O reformular para usuario final:

```
## Preguntas Frecuentes

| Pregunta | Respuesta |
|----------|-----------|
| ¿El diagnóstico falló? | Verifica que tu URL sea correcta y esté online |
| ¿No tengo API keys? | Ejecuta `python main.py setup` — te guía paso a paso |
| ¿Los resultados no son precisos? | Usa `onboard` para ingresar datos reales de tu hotel |
```

---

### LÍNEAS 258-296: Arquitectura del Repositorio

**Veredicto hotelero**: Árbol de directorios completo. Solo relevante para desarrolladores.

**Sugerencia**: Mover a GUIA_TECNICA.md. En README: link a la guía técnica para quien quiera ver la arquitectura.

---

### LÍNEAS 300-301: Cierre

```
**IA HOTELES AGENT (c) 2026**
*Diagnosticando la invisibilidad digital hotelera y recuperando reservas que hoy van a OTAs.*
```

**Veredicto hotelero**: El tagline es EXCELENTE. "Diagnosticando la invisibilidad digital hotelera" es potente y claro. Debería estar arriba, no solo al final.

---

## RESUMEN DE DIAGNÓSTICO ESTRUCTURAL

### Problemas sistémicos detectados:

1. **Inversión de audiencia**: El README está escrito para el desarrollador que ya conoce el proyecto, no para el prospecto que necesita entenderlo. La información comercial (valor para el hotel) está enterrada bajo capas de jerga técnica.

2. **Orden incorrecto**: Lo que más le importa a un hotelero (el problema, el valor, los escenarios financieros, la preparación para voz) aparece en las líneas 51-192. Las primeras 50 líneas son metadata técnica que debería ir al final.

3. **Jerga no traducida**: "CLI", "agéntica", "schema", "llms.txt", "YAML", "recovery_factor", "Coherence Score", "PainSolutionMapper", "Agent Harness", "preflight checks", "backwards compatible" — ningún término se explica para un no-técnico.

4. **Duplicación**: "Estado del Proyecto" y "Calidad Garantizada" repiten la misma información técnica (2,721 tests, 9 gates, coherence score).

5. **Falta contexto de negocio**: No hay sección que conteste "por qué debería adoptar esto?", "¿a quién le ha funcionado?", "¿qué ventaja competitiva representa para hoteles colombianos vs OTAs?". No hay un caso de uso narrado, ni un ejemplo con cifras reales.

6. **Falta audiencia COTELCO**: No menciona gremios, cadenas, asociaciones. No hay argumento para un directivo que decide si recomendar la herramienta a sus afiliados.

7. **Falta paso de Onboarding**: El flujo v4complete no menciona que sin `onboard` la propuesta多半 no se desbloquea. Información crítica oculta.

---

### Errores factuales verificados en código (NUEVOS en v2):

| # | Afirmación README | Valor real en código | Diferencia | Causa raíz |
|---|---|---|---|---|
| ERROR-1 | "225 archivos de test" (l.27) | **209 test files** reales | -16 | Desincronización post-reorganización |
| ERROR-2 | "9 publication gates" (l.30) | **11 gates activos** (faltan coverage + tier_c_onboarding) | +2 gates ocultos | Post-fase sin update del README |
| ERROR-3 | "ia_readiness_critical" como advisory gate (l.242) | **No existe como gate** — es advisory warning en delivery_quality_report | Categoría equivocada | Confusión terminológica gate vs warning |
| ERROR-4 | "22 assets IMPLEMENTED" (l.32) | **20 assets IMPLEMENTED** (2 deprecated: geo_playbook, voice_assistant_guide) | -2 | Post-FASE-PROP-D sin actualizar contador |
| ERROR-5 | "Pain narratives (14)" (l.207) | **15 pain_narratives** (falta low_organic_visibility) | +1 | Post-ANALYTICS-01 sin actualizar contador |

---

### Estructura propuesta (reordenada):

```
1.  Título + Tagline (el problema en 1 línea)
2.  ¿Qué problema resuelve? (el dolor del hotelero)
3.  Los 4 Pilares (SEO/GEO/AEO/IAO con ejemplos)
4.  ¿Qué recibes? (outputs en lenguaje de negocio)
5.  Proyecciones financieras (3 escenarios con ejemplo real)
6.  ¿Puede Siri recomendar tu hotel? (Voice Readiness)
7.  ¿Cómo empezar? (2 rutas: hotelero / desarrollador)
8.  Rigor y Transparencia (calidad simplificada, sin duplicación)
9.  Preguntas Frecuentes
10. Para desarrolladores (arquitectura, YAML, comandos, doctor)
11. Enlaces y documentación adicional
```

---

### Lo que ESTÁ BIEN (conservar):

- La tabla de 4 pilares con ejemplos (líneas 57-62) — es oro
- El tagline de cierre (línea 301) — subirlo arriba
- La pregunta "Por qué este hotel pierde reservas" (línea 53) — es el gancho perfecto
- Los escenarios financieros con probabilidades (líneas 183-187) — son correctos en valores
- Los niveles de Voice Readiness (Critical/Basic/Good/Excellent) — buen marco mental
- La lista de datos que captura `onboard` (línea 148) — relevante
- La fórmula ROI `roi = (projected_gain x 6) / (precio_mensual x 6)` — matemáticamente correcta con cap 5.0X

---

### Patrón de causa raíz identificado: Desincronización documental post-fase

Cada fase introduce nuevos gates, assets o métricas:
1. El código se actualiza ✅
2. El VERSION.yaml recibe entrada en el changelog ✅
3. **El README.md NO se actualiza** ❌

**Mecanismo de falla:** No existe un gate que valide списки numéricos (conteos de gates, assets, pain_narratives, test files) contra el código. `sync_versions.py` sincroniza versión/codename/fecha pero no valida coherencia de listas.

**Solución adoptada — Ampliar `validate_document_integration.py`:**

Agregar un check `validate_readme_counts()` al script existente `scripts/validate_document_integration.py` que cuente desde el código real y compare contra los numerales del README (test functions, módulos, scripts, test files, config YAML, skills, gates, assets). Se ejecuta en **FASE-RELEASE** como parte del Paso 4.5.5 del executor (`run_all_validations.py --quick`), NO en pre-commit local.

**Por qué NO en pre-commit (solución original descartada):**
1. El pre-commit ya tiene 11 hooks — agregar un scan de filesystem + AST parsing por commit degrada DX (~10-30s extra).
2. Los conteos cambian en commits intermedios de desarrollo pero el README se actualiza en FASE-RELEASE — el hook fallaría en cada commit de trabajo, generando ruido y forzando `--no-verify`.
3. Contradice `phased_project_executor.md` §4.5 y §6: la documentación se actualiza en FASE-RELEASE, no en cada commit.
4. `validate_document_integration.py` ya tiene 7 checks de coherencia inter-documento — ampliarlo es consistente con la infraestructura existente (0 scripts nuevos, 0 cambios en `.pre-commit-config.yaml`).

---

*Documento generado por Hermes Agent — 20 Mayo 2026 — v2: Auditoría forense contra código vivo*