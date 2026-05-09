# Comparativo de Complejidad Técnica — FASE-2-PATCH-TERMALES

> **Plan**: `PLAN-FASE-2-PATCH-TERMALES-20260508.md`
> **Origen**: `AUDITORIA_FASE-2-B_TERMALES_20260508.md`
> **Generado**: 2026-05-08 | **Versión**: v1.0.0

---

## Veredicto Ejecutivo

**FASE-2-PATCH-B es la de mayor complejidad técnica.** PATCH-5 (SitePresenceChecker contra DOM real) concentra el 60% de la dificultad del plan completo por 3 razones: requiere investigación externa con browser antes de tocar código, implica reescribir lógica de detección multi-capa, y sus cambios tienen efecto cascada en el gate system.

---

## Matriz Comparativa

| Dimensión | FASE-A (3 fixes code) | FASE-B (3 fixes orch) | FASE-C (v4complete) |
|-----------|----------------------|----------------------|---------------------|
| **Tipo de trabajo** | Regex + wiring local | Investigación browser + orquestador | Ejecución + verificación |
| **Archivos a tocar** | 4 (3 .py + main.py) | 6 (3 .py + template + main.py ×2) | 0 código |
| **Líneas de cambio** | ~15-30 líneas | ~70-100 líneas | 0 |
| **Requisito previo** | Ninguno | Browser investigation OBLIGATORIO | FASE-A y B completadas |
| **Conocimiento requerido** | Regex, firmas de método | DOM/CSS, BeautifulSoup, Schema.org, orquestador | CLI, grep, jq |
| **Riesgo de regresión** | Bajo (cambios aditivos) | Medio (cambia detección + orquestador) | Nulo (solo lectura) |
| **Testabilidad aislada** | Alta (funciones puras) | Media-Baja (necesita HTML real o mocks) | N/A |
| **Dependencia entre tareas** | Baja (3 fixes independientes) | Alta (PATCH-3 y PATCH-6 tocan mismo main.py) | N/A |
| **Presupuesto estimado** | ~48 iteraciones | ~53 iteraciones | ~43 iteraciones |
| **Margen de seguridad** | 12 iter (20%) | 7 iter (12%) | 17 iter (28%) |

---

## Ranking

```
1. FASE-2-PATCH-B   ████████████████████  ALTA    (53/60 iter, browser investigation, multi-capa)
2. FASE-2-PATCH-A   ████████████          MEDIA   (48/60 iter, cambios locales, pseudo-code listo)
3. FASE-2-PATCH-C   ██████                BAJA    (43/60 iter, solo verificación + docs mecánicos)
```

---

## Análisis por Fase

### FASE-2-PATCH-A — MEDIA

Tres fixes locales de código, todos con pseudo-code proporcionado por la auditoría:

| Patch | Tipo de cambio | Dificultad | Riesgo |
|-------|---------------|------------|--------|
| PATCH-1 | Regex engineering (OR expansion + simple eval) | Media | Bajo — aditivo |
| PATCH-2 | Firma de método + caller wiring | Media | Medio — tracing de call sites |
| PATCH-4 | Regex: 1 carácter añadido (`[^\]]*`) | Trivial | Muy bajo |

**Fortalezas**: Todo auto-contenido. Pseudo-code listo. Tests aislables. Cambios aditivos.

**Debilidades**: PATCH-2 requiere buscar TODOS los call sites de `CoherenceValidator().validate()` en main.py — si hay más de uno, hay que actualizarlos todos.

---

### FASE-2-PATCH-B — ALTA (la de mayor complejidad)

Tres fixes que tocan el orquestador y requieren investigación externa:

| Patch | Tipo de cambio | Dificultad | Riesgo |
|-------|---------------|------------|--------|
| PATCH-3 | Orchestrator wiring (monthly report) | Media | Medio — toca main.py |
| PATCH-5 | Reescritura de detección HTML + browser investigation | **Alta** | **Alto** — cascada en gates |
| PATCH-6 | Orchestrator wiring + template (GBP phone) | Media | Medio — toca main.py ×2 |

#### Por qué PATCH-5 domina la complejidad

**1. Investigación externa obligatoria antes de tocar código**

A diferencia de todos los demás patches — donde el contexto ya entrega pseudo-código listo para implementar — PATCH-5 exige:

```
browser_navigate("http://www.termales.com.co/")
browser_console: document.querySelectorAll('[href*="wa.me"], [class*="whatsapp"], [class*="joinchat"]')
browser_console: document.querySelectorAll('script[type="application/ld+json"]')
```

Esto consume iteraciones del presupuesto (R2: 60 máx) antes de empezar a codificar. Sin este paso, el agente no sabe:
- Si el botón WhatsApp está en HTML estático o cargado vía JS
- Qué clases CSS existen realmente
- Qué schemas JSON-LD tiene el sitio

**2. Cambio multi-capa en lógica de detección**

```
_check_html_element() ACTUAL:
  └── soup.text.lower() → busca "whatsapp", "wa.me", "chat"

_check_html_element() REQUERIDO:
  ├── soup.text.lower()              (existente, se conserva)
  ├── soup.find_all('a', href=True)  → busca wa.me/api.whatsapp en atributos
  └── soup.find_all(class_=True)     → busca 'whatsapp'/'joinchat' en clases CSS
```

No es un cambio de 3 caracteres como PATCH-4. Es reescribir la función completa con 3 métodos de búsqueda distintos, cada uno con sus propias estructuras de BeautifulSoup. ~50 líneas nuevas.

**3. Efecto cascada en el gate system**

```
_check_html_element
  → _check_asset_presence
    → check_site
      → SitePresenceReport
        → proposal_asset_alignment_gate (publication_gates.py:828)
          → gate_report.json
            → present_in_production[]
```

Un falso positivo (reportar WhatsApp donde no existe) es PEOR que el bug actual (no detectar WhatsApp que sí existe), porque la propuesta afirmaría "usted ya tiene WhatsApp" cuando no es cierto.

**4. Schema detection también cambia**

`_check_schema_exists()` debe considerar `Organization` o `LocalBusiness` como válido para hoteles sin `Hotel` schema explícito. Esto cambia el criterio de `NOT_EXISTS` → `EXISTS_WITH_ISSUES` para sitios como Termales que tienen Organization schema pero no Hotel schema.

#### Comparación directa PATCH-4 vs PATCH-5

```
PATCH-4 (FASE-A):  pattern = r'\[PENDING_[A-Z_]+\]'
                    → pattern = r'\[PENDING_[A-Z_]+[^\]]*\]'
                    Complejidad: 1 carácter añadido. Test: 1 caso.

PATCH-5 (FASE-B):  soup.text.lower()
                    → soup.text + soup.find_all('a', href) + soup.find_all(class_=True)
                    + _check_schema_exists() con Organization/LocalBusiness fallback
                    Complejidad: ~50 líneas nuevas. Test: necesita mock de HTML real.
```

#### Conflictos internos en FASE-B

PATCH-3 y PATCH-6 **tocan la misma zona de main.py** (orquestador v4complete). Si el agente no planifica el orden:
- PATCH-3 agrega `asset_report_path` al llamado de `MonthlyReportGenerator.generate()`
- PATCH-6 agrega enriquecimiento `hotel_data["phone"]` desde `audit_report["gbp"]["phone"]`

Ambos cambios son en la sección del orquestador que prepara datos antes de invocar generadores. Sin coordinación, el segundo patch puede sobrescribir el primero si se usa `write_file` en vez de `patch`.

---

### FASE-2-PATCH-C — BAJA

Verificación mecánica. Sin cambios de código:

| Paso | Tipo | Dificultad |
|------|------|------------|
| Ejecutar v4complete | Comando largo (5-10 min) | Baja |
| Copiar evidencia | cp | Trivial |
| Verificar 7 métricas | grep + jq + lectura de JSONs | Baja |
| Docs cascade | 5 scripts secuenciales | Media (por volumen) |

**Riesgo oculto**: Si FASE-A o FASE-B dejaron bugs, v4complete falla y FASE-C se convierte en sesión de debugging. No es complejidad de FASE-C en sí, sino riesgo heredado.

---

## Riesgo de Cuello de Botella en FASE-B

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Browser investigation consume >15 iteraciones | Media | Agota presupuesto antes de implementar | Pivotar: usar selectores documentados en auditoría, posponer verificación browser a FASE-C |
| PATCH-3 y PATCH-6 tocan misma zona de main.py | Alta | Conflicto de merge | Usar `patch` (no `write_file`) para cambios quirúrgicos. Hacer PATCH-3 primero, luego PATCH-6 |
| `_check_html_element` ampliado rompe detección existente | Media | Regresión en otros hoteles | Test con HTML de Termales + HTML de hotel sin WhatsApp |
| Budget 60 iteraciones insuficiente (~53 estimado) | Media | Fase incompleta | Priorizar: PATCH-5 → PATCH-3 → PATCH-6. Si se agota, PATCH-6 es el más sacrificable |
| Schema detection cambia criterio de gates | Baja | Falsos positivos en Organization schema | Solo aplicar fallback para `hotel_schema`, no para `org_schema` |

---

## Recomendaciones de Ejecución

1. **FASE-2-PATCH-A primero**: Es la más predecible. Si el agente completa en <50 iteraciones, confirma que el presupuesto es realista para las demás.

2. **FASE-2-PATCH-B con margen estrecho**: El agente debe monitorear su contador de iteraciones. Si llega a 40 sin haber empezado PATCH-5, debe priorizar: implementar `_check_html_element` con los selectores documentados en la auditoría SIN browser investigation (posponer verificación browser para FASE-C).

3. **FASE-2-PATCH-C es el cierre**: Si v4complete falla, NO debuguear en esta fase. Reportar métricas fallidas, cerrar con veredicto PARCIAL/NO EFECTIVA, y abrir nuevo plan.

---

## Resumen Visual

```
COMPLEJIDAD POR FASE
═══════════════════════════════════════════════════════

FASE-A  ████████████░░░░░░░░  48/60 iter  MEDIA
        PATCH-1 ████           Regex engineering
        PATCH-2 ████           Signature + wiring
        PATCH-4 █              Trivial (1 char)

FASE-B  ████████████████░░░░  53/60 iter  ALTA ← MAYOR COMPLEJIDAD
        PATCH-3 ████           Orchestrator wiring
        PATCH-5 ██████████     Browser + multi-capa + cascada gates
        PATCH-6 ████           Orchestrator + template

FASE-C  ████████░░░░░░░░░░░░  43/60 iter  BAJA
        v4complete   ████      Comando largo (wait)
        Verificación ██        7 métricas (grep/jq)
        Docs cascade ████      5 scripts secuenciales
```
