# Contexto: Fix Pendiente — IMP-03 CAPEX Breakdown

## Origen
Plan: `REFACTOR-PENDIENTE-V4.58.0`
FASE-RELEASE ejecutada: 2026-05-29
v4.59.0 taggeada y pusheada
Auditado y validado contra código vivo: 2026-05-29 (misma fecha)
Re-auditoría forense con verificación de causa raíz: 2026-05-29

---

## Confianza: 100% — Todos los claims verificados contra código vivo

Cada claim del documento original fue re-verificado contra:
- Template real: `propuesta_v6_template.md` L147-158
- Generator real: `v4_proposal_generator.py` L191-217, L772-1034, L1560-1567
- Config real: `config/commercial.yaml` L36-47
- Output corrupto real: `02_PROPUESTA_COMERCIAL_20260529_151050.md` L175-186
- Output pre-fix real: `02_PROPUESTA_COMERCIAL_20260528_202916.md` L153-158
- Tests reales: `test_capex_rename.py`, `test_financial_coherence.py`
- Git real: commit `e9da3bc`

**CERO claims sin evidencia directa. CERO suposiciones.**

---

## Matriz de Verificación (Claim vs Código Vivo)

| # | Claim | Verificación | Evidencia |
|---|-------|-------------|-----------|
| F1 | Tabla CAPEX corrupta por `${capex_breakdown_table}` embebido en celda | CONFIRMADO | Output L180: `| Desglose CAPEX | | | Componente | Monto | Descripción |` — 7 pipes en vez de 4 |
| F2 | Template en `propuesta_v6_template.md` L147-155 | CONFIRMADO | L152: `| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |` |
| F3 | `_build_capex_breakdown_table()` ya funciona | CONFIRMADO | L191-217: retorna tabla markdown completa con header `| Componente | Monto | Descripción |` |
| F4 | `config/commercial.yaml` con datos correctos | CONFIRMADO | 3 componentes: Auditoría ($800K), Implementación ($1.2M), Onboarding ($500K) |
| F5 | `_build_coherence_checklist()` implementa cascada ADR pero placeholder ausente | CONFIRMADO | L1878-1927: código funcional. 0/4 templates contienen `${coherence_checklist}` |
| F6 | Archivos involucrados: template + generator sin cambios necesarios | PARCIAL | Generator no necesita cambios de lógica, pero tiene 5 keys huérfanas (ver F8) |

---

## Problema Principal (F1)

El fix IMP-03 (CAPEX breakdown) produce output pero con estructura markdown corrupta.

### Evidencia Visual

**Archivo:** `output/v4_complete/02_PROPUESTA_COMERCIAL_20260529_151050.md` L175-186

```
| Concepto | Tipo | Monto | ¿De quién es? |
|----------|------|-------|---------------|
| Setup fee (único) | **CAPEX** | $2.500.000 COP | **100% suyo** — Real Estate Digital |
| Desglose CAPEX | | | Componente | Monto | Descripción |  ← celda = header de tabla interna (7 pipes!)
|---|---|---|                                           ← fila separadora huérfana (3 pipes en tabla de 4 col)
| Auditoría Inicial | $800.000 COP | Diagnóstico completo... |  ← filas de tabla interna
| Implementación Técnica | $1.200.000 COP | ... |
| Onboarding y Capacitación | $500.000 COP | ... |
| **Total CAPEX** | **$2.500.000 COP** | Única vez | | Detalle del activo |  ← 5 columnas!
| Fee mensual (×6) | **OPEX** | $2.400.000 COP | Servicio de implementación |
```

**Lo que se produce vs lo que se espera:**
- ✅ Datos: Los 3 componentes + total ($2.5M) SÍ aparecen
- ❌ Estructura: La tabla está mal formada — filas desincronizadas, columnas rotas
- ❌ Legibilidad: Un lector humano ve una tabla rota; en PDF/HTML se renderiza corrupta

### Confirmación: el bug fue INTRODUCIDO, no pre-existente

El output `v4_complete_fix_v2/02_PROPUESTA_COMERCIAL_20260528_202916.md` (día anterior) NO tiene el bug — la fila `Desglose CAPEX` simplemente no existe:

```
| Setup fee (único) | **CAPEX** | $2.500.000 COP | **100% suyo** — Real Estate Digital |
| Fee mensual (×6) | **OPEX** | $2.400.000 COP | Servicio de implementación |
```

El commit `e9da3bc` (FASE-1A, 2026-05-29 11:58) introdujo la regresión al añadir UNA sola línea al template.

---

## Causa Raíz (Profundizada)

### Commit culpable

```
e9da3bc FASE-1A: IMP-03 CAPEX breakdown en template + F7 unificar gate evidence_tier
Date:   Fri May 29 11:58:13 2026 -0500
```

Diff relevante:
```diff
 | Setup fee (único) | **CAPEX** | ${capex_total} | **100% suyo** — Real Estate Digital |
+| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |
 | Fee mensual (×6) | **OPEX** | ${opex_total_6m} | Servicio de implementación |
```

### Por qué falla: Tabla markdown dentro de celda de tabla markdown

`_build_capex_breakdown_table()` (L191-217) retorna una tabla markdown COMPLETA:

```
| Componente | Monto | Descripción |
|---|---|---|
| Auditoría Inicial | $800.000 COP | Diagnóstico completo de presencia digital |
| Implementación Técnica | $1.200.000 COP | Configuración de activos digitales |
| Onboarding y Capacitación | $500.000 COP | Transferencia de conocimiento al equipo |
| **Total CAPEX** | **$2.500.000 COP** | Única vez |
```

Al sustituir esto dentro de la celda de una tabla exterior de 4 columnas, el parser markdown interpreta TODOS los pipes (`|`) como bordes de columna de la tabla exterior. Markdown NO soporta tablas anidadas. El resultado son filas desincronizadas con número variable de columnas (3, 4, 5, 7 pipes).

### Mecanismo de renderizado verificado

**Archivo:** `v4_proposal_generator.py` L1560-1567

```python
def _render_template(self, template_content: str, data: Dict[str, str]) -> str:
    preprocessed = self._preprocess_conditionals(template_content, data)
    template = Template(preprocessed)  # string.Template
    return template.safe_substitute(data)
```

- Usa `string.Template.safe_substitute()` — sustituye `${key}` con el valor del dict
- `_preprocess_conditionals()` (L1520-1558) solo procesa bloques `{{if}}...{{endif}}` — NO interactúa con `${capex_breakdown_table}`
- La sustitución ocurre ANTES del parsing markdown del renderizador final
- `safe_substitute` NO falla en keys faltantes — solo deja `${key}` literal

**Conclusión:** El único punto de falla es la línea L152 del template. El generator, la config, y el mecanismo de renderizado son correctos.

### Template original

**Archivo:** `modules/commercial_documents/templates/propuesta_v6_template.md` L147-155

```markdown
## 🏗️ CAPEX vs OPEX: Lo que es suyo vs. lo que es servicio

| Concepto | Tipo | Monto | ¿De quién es? |
|----------|------|-------|---------------|
| Setup fee (único) | **CAPEX** | ${capex_total} | **100% suyo** — Real Estate Digital |
| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |  ← CELDA CONTIENE TABLA MARKDOWN → CORRUPCIÓN
| Fee mensual (×6) | **OPEX** | ${opex_total_6m} | Servicio de implementación |

${nota_capex_opex}

**Activos digitales que quedan en su propiedad:**
${activos_digitales_lista}
```

---

## Amplificación: Hallazgos Adicionales (no en el doc original)

### F6 — Coherence Checklist Invisible (Severidad: BAJA)

**Hallazgo:** `_build_coherence_checklist()` (v4_proposal_generator.py L1878-1927) SÍ implementa la cascada ADR correctamente:
- `adr_value = validated_data.get('adr') or self._get_adr_from_benchmarks(...)`
- Muestra `[OK]` cuando el benchmark tiene ADR
- ADR $420,000 COP de `eje_cafetero` aparece en la propuesta (L36)

**Problema:** Ningún template tiene `${coherence_checklist}`. El placeholder no existe en:
- `propuesta_v6_template.md` — 0 matches
- `propuesta_v4_template.md` — 0 matches
- `diagnostico_v6_template.md` — 0 matches (solo `${coherence_score}` que es otra cosa)
- `diagnostico_v4_template.md` — 0 matches

Se genera en L943: `'coherence_checklist': self._build_coherence_checklist(diagnostic_summary)` pero el resultado nunca se renderiza en ningún output.

**Severidad:** BAJA — la funcionalidad funciona, solo no se ve. No afecta coherence score ni gates. Pero es código que se ejecuta sin propósito.

**Hallazgo adicional (re-auditoría):** `_build_coherence_checklist()` hardcodea `'eje_cafetero'` en L1895 como fallback de región:
```python
adr_value = (
    validated_data.get('adr')
    or self._get_adr_from_benchmarks('eje_cafetero')  # ← hardcoded!
    or None
)
```
Esto ignora el parámetro `region` que el generator recibe. Si el template se usara con otra región, el ADR sería incorrecto. **No afecta hoy** porque el placeholder no se renderiza, pero es un bug latente.

### F7 — Keys Huérfanas en Template Data (Severidad: BAJA)

Descubierto durante la auditoría de placeholders. Estas keys se generan en `_prepare_template_data` (L772-1034) pero NUNCA son consumidas por ningún template (verificado con `grep -oP '\$\{[a-z_0-9]+\}' propuesta_v6_template.md`):

| Key | Línea(s) en generator | ¿En template? | Nota |
|-----|----------------------|---------------|------|
| `setup_fee` | 791 | NO | Reemplazado por `capex_total` (L872). Cálculo redundante. |
| `net_benefit` | 940 | NO | Calculado pero `${net_benefit}` no existe en template. |
| `total_investment` | 938 | NO | Calculado pero no renderizado. Template usa `${monthly_investment}`. |
| `total_recovered` | 939 | NO | Redundante con `${total_recuperacion_6m}` que SÍ está en template. |
| `projected_real_gain` | 805 | NO | Calculado pero no renderizado. |
| `plan_7d` | 905 | NO | Template usa `${plan_7_days}` (L947). Key duplicada con diferente nombre. |
| `plan_30d` | 906 | NO | Template usa `${plan_30_days}` (L948). |
| `plan_60d` | 907 | NO | Template usa `${plan_60_days}` (L949). |
| `plan_90d` | 908 | NO | Template usa `${plan_90_days}` (L950). |

**Nota sobre duplicados:** El dict `data` (L772-1034) contiene keys duplicadas. En Python, la segunda definición prevalece silenciosamente:
- `plan_7d` (L905) vs `plan_7_days` (L947): keys diferentes, no conflicto, pero `plan_7d` es huérfana
- `coherence_score` (L909): única en el dict
- `score_tecnico` (L916): única en el dict

Estas 9 keys son **código muerto** — consumen CPU (especialmente `_build_7_day_plan` que se llama 2 veces: L905 y L947) con cero impacto en el output final. Probablemente son residuos del refactor CAPEX/OPEX y la migración V4→V6 de templates.

### F8 — Fallback de `_build_capex_breakdown_table()` sin Header (Severidad: BAJA)

Cuando `config/commercial.yaml` no tiene `capex_breakdown.components` (L201-203):

```python
if not components:
    return f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
```

Retorna una sola fila de datos SIN header row. Si alguna vez se ejecuta este caso:
- Embebido en celda: misma corrupción que F1
- En sección propia: tabla markdown sin header — válido pero visualmente inconsistente

**Probabilidad:** Muy baja (requiere borrar/dañar `commercial.yaml`).

---

## Soluciones

### F1 — Tabla CAPEX Corrupta (PRIMARIO, ALTA prioridad)

**Opción A (RECOMENDADA): Sección propia después de la tabla CAPEX**

```markdown
| Setup fee (único) | **CAPEX** | ${capex_total} | **100% suyo** — Real Estate Digital |
| Fee mensual (×6) | **OPEX** | ${opex_total_6m} | Servicio de implementación |

${nota_capex_opex}

### Desglose del Setup Fee (CAPEX)
${capex_breakdown_table}

**Activos digitales que quedan en su propiedad:**
${activos_digitales_lista}
```

- Cambio: eliminar 1 línea (`| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |`), añadir 2 líneas (sección + heading)
- La tabla interna se renderiza como markdown independiente
- Sin cambios en `v4_proposal_generator.py`
- Sin cambios en `config/commercial.yaml`

**Por qué funciona (verificado contra mecanismo de renderizado):**
1. `string.Template.safe_substitute()` sustituye `${capex_breakdown_table}` con la tabla completa
2. `_preprocess_conditionals()` NO interactúa con este placeholder
3. La tabla resultante se renderiza como bloque markdown independiente (no dentro de otra tabla)
4. Los pipes internos de la tabla CAPEX NO se confunden con pipes de tabla exterior

**Opción B: Refactorizar `_build_capex_breakdown_table()` para no incluir header**

Modificar el método para que retorne SOLO filas de datos (sin `| Componente | Monto | Descripción |\n|---|---|---|\n`). Así se podría incrustar en la celda sin conflicto de headers. Pero:
- Rompe los tests existentes (`test_capex_rename.py` L42 espera el header)
- Cambia el contrato semántico del método
- Mayor riesgo de regresión

**Opción C: Solo eliminar la fila de Desglose CAPEX**

Quitar L152 del template sin añadir sección nueva. Simple pero se pierde el desglose detallado.

**Recomendación final: Opción A.**

### F6 — Coherence Checklist Invisible (BAJA prioridad)

**Opción A:** Agregar `### ✅ Coherence Checklist` + `${coherence_checklist}` al final de `propuesta_v6_template.md` (ej: antes de la sección de garantías).

**Opción B:** Eliminar `_build_coherence_checklist()` y su llamada en L943 (YAGNI — no se usa, no se necesita).

**Opción C:** No hacer nada. No afecta gates.

### F7 — Keys Huérfanas (BAJA prioridad)

Eliminar las 9 keys del diccionario de retorno en `_prepare_template_data` (L772-1034). Solo eliminar la entrada del dict, NO la variable/propiedad (algunas como `setup_fee` se usan internamente para otros cálculos vía `_current_setup_fee`).

**Keys a eliminar:**
- L791: `'setup_fee': format_cop(...)` — reemplazado por `capex_total` (L872)
- L805: `'projected_real_gain': format_cop(...)` — no renderizado
- L905-908: `'plan_7d'`, `'plan_30d'`, `'plan_60d'`, `'plan_90d'` — reemplazados por `plan_*_days` (L947-950)
- L938: `'total_investment': format_cop(...)` — no renderizado
- L939: `'total_recovered': format_cop(...)` — no renderizado
- L940: `'net_benefit': format_cop(...)` — no renderizado

**Impacto:** Eliminar L905-908 evita la llamada duplicada a `_build_*_day_plan()` (ahorra ~4 llamadas a métodos por generación).

### F8 — Fallback sin Header (BAJA prioridad)

Agregar header al fallback:
```python
if not components:
    header = "| Componente | Monto | Descripción |\n|---|---|---|\n"
    return header + f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
```

---

## Archivos a Modificar (Fix Primario F1)

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `propuesta_v6_template.md` L147-155 | Mover placeholder `capex_breakdown_table` a sección propia | ALTA |
| `v4_proposal_generator.py` | Ninguno — `_build_capex_breakdown_table()` ya funciona | — |
| `config/commercial.yaml` | Ninguno — datos correctos | — |

## Archivos a Modificar (Opcional — F6, F7, F8)

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `propuesta_v6_template.md` | Agregar `${coherence_checklist}` (F6) | BAJA |
| `v4_proposal_generator.py` L791,805,905-908,938-940 | Eliminar 9 keys huérfanas del dict (F7) | BAJA |
| `v4_proposal_generator.py` L201-203 | Agregar header al fallback (F8) | BAJA |

---

## Tests Impactados

| Test | ¿Requiere cambio? | Razon |
|------|-------------------|-------|
| `test_capex_rename.py` L25-45 | NO | Verifica `_build_capex_breakdown_table()` directamente (header + componentes) — no depende de la posición del placeholder en el template |
| `test_capex_rename.py` L47-62 | NO | Verifica total row — independiente de la posición |
| `test_capex_rename.py` L74-82 | NO | Verifica fallback — independiente |
| `test_capex_rename.py` L108-133 | NO | Verifica que `capex_breakdown_table` existe en `template_data` — no verifica renderizado |
| `test_financial_coherence.py` L172-217 | NO | Verifica que componentes aparecen en `capex_breakdown_table` — no verifica posición en tabla CAPEX |

**Ningún test verifica la estructura de la tabla CAPEX principal (la de 4 columnas).** Esto es una debilidad del test suite — se podría añadir un test que verifique que cada fila de la tabla CAPEX tiene exactamente 4 pipes.

---

## Métricas de Éxito (Post-Fix)

1. La tabla CAPEX principal tiene estructura markdown válida (cada fila con exactamente 4 pipes → 4 celdas)
2. El desglose aparece como sección independiente (`### Desglose del Setup Fee (CAPEX)`) con su propia tabla
3. Coherence score se mantiene ≥ 0.80
4. 11/11 gates se mantienen PASS
5. Tests existentes de CAPEX pasan sin cambios (`test_capex_rename.py`, `test_financial_coherence.py`)

---

## Comando de Verificación Post-Fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Tests de regresión
./venv/Scripts/python.exe -m pytest tests/test_capex_rename.py tests/commercial_documents/test_financial_coherence.py -v

# 2. Regenerar propuesta para verificar fix visual
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe main.py execute https://www.hotelcastillareal.com/ --region eje_cafetero --plan v4complete"

# 3. Validar estructura post-fix
grep -n 'Desglose del Setup Fee' output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
grep -c '^|' output/v4_complete/02_PROPUESTA_COMERCIAL_*.md

# 4. Verificar que NO hay pipes extra en tabla CAPEX
sed -n '/CAPEX vs OPEX/,/Activos digitales/p' output/v4_complete/02_PROPUESTA_COMERCIAL_*.md

# 5. Verificar que la tabla CAPEX tiene exactamente 4 pipes por fila
sed -n '/CAPEX vs OPEX/,/Fee mensual/p' output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | grep '^|' | while read line; do
  pipes=$(echo "$line" | tr -cd '|' | wc -c)
  echo "pipes=$pipes: $line"
done
```
