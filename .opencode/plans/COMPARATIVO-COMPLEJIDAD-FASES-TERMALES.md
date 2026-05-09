# Comparativo de Complejidad Tecnica por Fase

> **Plan**: PLAN-REFACTOR-TERMALES-20260508.md  
> **Fecha**: 2026-05-08  
> **Metodologia**: Puntuacion por 6 dimensiones (0-10 cada una). Total maximo: 60.  
> **Criterio**: Complejidad tecnica = esfuerzo cognitivo + incertidumbre + riesgo de implementacion, NO impacto de negocio.

---

## Resumen Ejecutivo

**Fase de mayor complejidad tecnica: FASE-2-A** (42/60 puntos)

FASE-2-A supera a FASE-1-A (35/60) principalmente por:
1. **Mayor incertidumbre diagnostica**: el fallo del SitePresenceChecker en Termales es desconocido a priori
2. **Dependencias externas activas**: scraping del sitio real (puede cambiar, bloquear, o fallar por red)
3. **Mayor superficie de cambio**: 4 archivos en 2 modulos distintos (quality_gates + asset_generation)

FASE-1-A es la mas critica para el cliente (marcadores crudos visibles), pero su implementacion es mas predecible.

---

## Matriz de Complejidad

### Dimensiones

| # | Dimension | Descripcion |
|---|-----------|-------------|
| 1 | Complejidad Algoritmica | Profundidad del cambio de codigo (regex, parsing, scoring) |
| 2 | Incertidumbre / Investigacion | Cuanto se desconoce antes de empezar (rabbit holes) |
| 3 | Riesgo de Regresion | Probabilidad de romper funcionalidad existente |
| 4 | Modulos Afectados | Cantidad y dispersion de archivos a tocar |
| 5 | Dependencias Externas | APIs, sitios web, servicios de terceros |
| 6 | Impacto Cliente Final | Consecuencia directa de un error en esta fase |

### Puntuacion por Fase

| Fase | Alg | Inc | Ries | Mod | Dep | Imp | **Total** | Rank |
|------|-----|-----|------|-----|-----|-----|-----------|------|
| FASE-PRE | 1 | 1 | 1 | 2 | 1 | 1 | **7** | 7 |
| FASE-1-A | 7 | 5 | 8 | 4 | 2 | 9 | **35** | 2 |
| FASE-1-B | 4 | 3 | 5 | 3 | 2 | 6 | **23** | 4 |
| **FASE-2-A** | **6** | **8** | **6** | **7** | **8** | **7** | **42** | **1** |
| FASE-2-B | 2 | 4 | 5 | 1 | 6 | 8 | **26** | 3 |
| FASE-3 | 3 | 4 | 5 | 2 | 1 | 6 | **21** | 5 |
| FASE-RELEASE | 1 | 1 | 2 | 1 | 1 | 3 | **9** | 6 |

---

## Analisis Detallado por Fase

### FASE-PRE: Saneamiento (7/60)

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 1 | Validaciones base, mkdir, grep |
| Inc | 1 | Todo es conocido de antemano |
| Ries | 1 | Sin riesgo de regresion (solo verificacion) |
| Mod | 2 | No se modifica codigo productivo |
| Dep | 1 | Solo scripts internos |
| Imp | 1 | No afecta entregables al cliente |

**Veredicto**: Fase operativa. Cero complejidad tecnica.

---

### FASE-1-A: Bugs Criticos — Template + Coherence (35/60)

**FIX-1**: Reemplazar `string.Template` por pre-procesador de condicionales `{{if}}...{{endif}}`  
**FIX-2**: Coherence validator debe usar `generated_assets`, no catalogo estatico

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 7 | Regex con DOTALL para pre-procesar bloques condicionales; cambio de fuente de verdad en scoring |
| Inc | 5 | El problema esta identificado (incompatibilidad motor/template); la solucion es clara pero requiere precision |
| Ries | 8 | Propuesta comercial es el documento mas visible al cliente; un error aqui es catastrofico para la percepcion de calidad |
| Mod | 4 | 2 archivos core en 1 modulo (commercial_documents) |
| Dep | 2 | Solo codigo interno; el template V6 ya existe |
| Imp | 9 | Marcadores `{{if}}` crudos en propuesta = documento no publicable; el cliente ve el bug directamente |

**Fortalezas de esta fase**: El scope es muy acotado (2 archivos, 1 modulo). El problema esta perfectamente caracterizado.

**Debilidades**: FIX-1 requiere compatibilidad exacta con la sintaxis Jinja2-lite del template V6. Un error en el regex puede dejar bloques residuales o eliminar contenido valido.

**Comparativa vs FASE-2-A**: FASE-1-A es mas critica para el cliente pero tecnicamente mas predecible. No hay variables externas incontrolables.

---

### FASE-1-B: Bugs de Contenido — Scrubber + Monthly Report (23/60)

**FIX-4**: Agregar Rule 6 al ContentScrubber para detectar `[PENDING_*]`  
**FIX-3**: monthly_report data-driven desde `asset_generation_report.json`

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 4 | Regex simple (`\[PENDING_[A-Z_]+\]`); lectura de JSON y generacion de tabla Markdown |
| Inc | 3 | Problema identificado; solucion directa |
| Ries | 5 | monthly_report cambia output visible; scrubber ahora bloquea publicacion (nuevo comportamiento) |
| Mod | 3 | 2 archivos en 2 modulos distintos (postprocessors + asset_generation) |
| Dep | 2 | Solo codigo interno y JSON existente |
| Imp | 6 | Monthly report con datos falsos es enganoso; scrubber que no detecta PENDING deja pasar documentos defectuosos |

**Veredicto**: Cambios localizados de complejidad media-baja. El riesgo principal es introducir `block_publication=True` como comportamiento nuevo.

---

### FASE-2-A: Deteccion y Enriquecimiento (42/60) ⭐ GANADORA

**FIX-5**: SitePresenceChecker hardening + investigacion de fallo en Termales  
**FIX-6**: indirect_traffic lee `audit_context`  
**FIX-7**: FAQ extrae datos del sitio via scraping

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 6 | Scraping con BeautifulSoup + requests; hardening de excepciones con traceback; parsing de servicios |
| Inc | 8 | **Razon principal de la victoria**: Se desconoce POR QUE falla SitePresenceChecker en Termales. Puede ser: bloqueo de WordPress, timeout, SSL, selectors desactualizados, CF7 Conditional Fields, o interaccion con WPML. Requiere debug iterativo |
| Ries | 6 | Cambios en 4 archivos; scraping puede romper si el sitio cambia de estructura |
| Mod | 7 | 4 archivos en 2 modulos (quality_gates + asset_generation) con interacciones cruzadas |
| Dep | 8 | **Dependencia externa critica**: sitio web real `http://www.termales.com.co/`. Fuera de control del desarrollador. Puede: cambiar, bloquear bots, estar caido, o tener estructura dinamica |
| Imp | 7 | Falsos negativos en WhatsApp/Schema afectan la propuesta (dice "no tiene" cuando si tiene); FAQ generica reduce valor percibido |

**Por que gana FASE-2-A**:

1. **Incertidumbre diagnostica**: Mientras que FASE-1-A tiene el problema totalmente caracterizado (string.Template no soporta `{{if}}`), FASE-2-A requiere investigar un fallo silencioso. El `except Exception` ha estado ocultando el error real. El agente de FASE-2-A debera:
   - Quitar el catch-all temporalmente
   - Ejecutar SitePresenceChecker contra Termales
   - Ver el error real
   - Corregir la causa raiz (que puede ser cualquiera de 5+ razones)
   - Volver a poner el hardening

2. **Dependencia del sitio real**: FIX-7 requiere scraping de `termales.com.co`. Si el sitio:
   - Usa JavaScript para renderizar servicios → BeautifulSoup no vera nada
   - Bloquea bots por User-Agent → requests falla
   - Cambia estructura HTML entre sesiones → tests se rompen
   - Esta caido durante la fase → no hay datos para extraer

3. **Superficie amplia**: Afecta tanto quality_gates (FIX-5 hardening) como 3 generadores de asset_generation (FIX-6, FIX-7, y la correccion del checker mismo).

**Debilidad comparativa**: El impacto directo al cliente es menor que FASE-1-A. Un bug aqui no deja marcadores de codigo visibles; solo genera contenido sub-optimo o falsos negativos.

---

### FASE-2-B: Verificacion E2E con v4complete (26/60)

**Tareas**: Ejecutar v4complete para Termales + verificar 7 metricas + evidencia

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 2 | No hay implementacion de codigo; solo ejecucion y verificacion |
| Inc | 4 | v4complete puede fallar por razones externas (APIs, rate limits) |
| Ries | 5 | Si v4complete falla, la fase se bloquea; requiere rerun |
| Mod | 1 | No se modifica codigo |
| Dep | 6 | v4complete consume APIs externas (PageSpeed, Places, Rich Results); puede tardar 5-10 min |
| Imp | 8 | El veredicto E2E determina si todo el plan fue efectivo |

**Veredicto**: Alta complejidad OPERATIVA (orquestar v4complete, manejar timeout, guardar evidencia), pero baja complejidad TECNICA. No se escribe codigo nuevo.

---

### FASE-3: Policy y Gates (21/60)

**FIX-9**: Evaluar proposal_asset_alignment WARNING → BLOCKED  
**FIX-10**: Onboarding gate para Tier C

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 3 | Comparacion de porcentaje + retorno de GateResult |
| Inc | 4 | Requiere decision de producto: ¿debe bloquear? ¿el umbral 50% es correcto? |
| Ries | 5 | Cambio de policy puede afectar todos los pipelines futuros |
| Mod | 2 | 1 archivo (publication_gates.py) |
| Dep | 1 | Solo codigo interno |
| Imp | 6 | Gate bloqueante afecta el flujo de publicacion; debe documentarse bien |

**Veredicto**: Complejidad media-baja. El reto no es tecnico sino de producto/negocio.

---

### FASE-RELEASE: Documentacion y Version Bump (9/60)

| Dimension | Score | Justificacion |
|-----------|-------|---------------|
| Alg | 1 | Scripts automatizados (sync_versions, log_phase, run_all_validations) |
| Inc | 1 | Proceso repetible y documentado |
| Ries | 2 | Riesgo bajo; si falla, se reintenta |
| Mod | 1 | No se modifica codigo productivo |
| Dep | 1 | Solo scripts internos |
| Imp | 3 | Documentacion incorrecta es molesta pero no rompe el pipeline |

**Veredicto**: Fase de proceso. Complejidad tecnica minima.

---

## Ranking Final

| Rank | Fase | Total | Perfil de Riesgo |
|------|------|-------|------------------|
| 1 | **FASE-2-A** | 42/60 | Alta incertidumbre + dependencias externas + superficie amplia |
| 2 | FASE-1-A | 35/60 | Alta criticidad + riesgo de regresion, pero predecible |
| 3 | FASE-2-B | 26/60 | Complejidad operativa (v4complete), no tecnica |
| 4 | FASE-1-B | 23/60 | Localizada, media complejidad |
| 5 | FASE-3 | 21/60 | Decision de producto, no tecnica |
| 6 | FASE-RELEASE | 9/60 | Proceso puro |
| 7 | FASE-PRE | 7/60 | Operativa |

---

## Recomendaciones por Fase

### FASE-2-A (Ganadora — requiere atencion especial)

- **Reservar margen de iteraciones**: Dada la alta incertidumbre, si el presupuesto de 60 iteraciones se agota durante la investigacion de SitePresenceChecker, guardar checkpoint y continuar en sesion de recuperacion.
- **Estrategia de debug para FIX-5**:
  1. Quitar el `except Exception` temporalmente
  2. Ejecutar solo el checker contra Termales
  3. Capturar el traceback real
  4. Corregir la causa
  5. Reinstalar el hardening mejorado
- **Fallback para FIX-7**: Si el scraping falla (sitio bloquea bots, JS-rendered), implementar fallback a FAQ generica con al menos 1 pregunta sobre termas/spa (basado en keywords del dominio `termales.com.co`).
- **Priorizacion interna**: Si se agota tiempo, priorizar FIX-5 (critico para deteccion) > FIX-7 (mejora) > FIX-6 (mejora).

### FASE-1-A (Segunda — critica para el cliente)

- **Tests exhaustivos para FIX-1**: Probar con: condicion verdadera, condicion falsa, anidamiento de condicionales, bloques vacios, y caracteres especiales dentro de bloques.
- **Backwards compatibility para FIX-2**: Mantener fallback a catalogo estatico si `generated_assets=None` para no romper pipelines legacy.

### FASE-2-B (Orquestacion critica)

- **Usar subagente si el presupuesto de iteraciones es <30** tras la revision de fixes.
- **Evidencia proactiva OBLIGATORIA**: Ejecutar el `cp` de evidencia inmediatamente post-v4complete, antes de cualquier verificacion.

---

## Comparativa Visual: Complejidad por Dimension

```
Alg      Inc      Ries     Mod      Dep      Imp
|        |        |        |        |        |
FASE-1-A [#######] [#####]  [########] [####]   [##]     [#########]
FASE-1-B [####]    [###]    [#####]  [###]    [##]     [######]
FASE-2-A [######]  [########] [######] [#######] [########] [#######]
FASE-2-B [##]      [####]   [#####]  [#]      [######] [########]
FASE-3   [###]     [####]   [#####]  [##]     [#]      [######]

Leyenda: # = 1 punto (max 10 por barra)
```

---

*Documento generado el 2026-05-08 como insumo para la planificacion de sesiones.*
