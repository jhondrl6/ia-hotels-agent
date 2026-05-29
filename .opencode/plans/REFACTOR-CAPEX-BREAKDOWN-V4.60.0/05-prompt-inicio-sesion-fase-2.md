# FASE-2: F7+F8 — Generator Cleanup (Keys Huérfanas + Fallback Header)

## Estrategia: delegate_task para Trabajo Paralelo

Esta fase tiene 2 tracks independientes que pueden ejecutarse en paralelo vía `delegate_task`:
- **Track A (Subagente)**: F7 — Eliminar 9 keys huérfanas (L791-940)
- **Track B (Agente principal)**: F8 — Fix fallback header (L201-203)

**Por qué delegate_task:** Ambos tracks editan el mismo archivo pero en secciones completamente separadas (L201 vs L791+). El trabajo paralelo ahorra ~10 iteraciones del budget de la sesión.

---

## Contexto de Fases Anteriores

- **FASE-1 (completada)**: Fix template CAPEX — `${capex_breakdown_table}` movido a sección propia
- **Esta fase**: Limpieza de código muerto en `v4_proposal_generator.py`

---

## F7 — Keys Huérfanas en Template Data

### Problema (verificado contra código vivo)
9 keys se generan en `_prepare_template_data()` pero NUNCA son consumidas por ningún template:

| Key | Línea actual | Reemplazada por / Razón |
|-----|-------------|------------------------|
| `setup_fee` | L791 | `capex_total` (L872) |
| `projected_real_gain` | L805 | No renderizada en ningún template |
| `plan_7d` | L905 | `plan_7_days` (L947) |
| `plan_30d` | L906 | `plan_30_days` (L948) |
| `plan_60d` | ~L907 | `plan_60_days` (L949) |
| `plan_90d` | ~L908 | `plan_90_days` (L950) |
| `total_investment` | L938 | `total_investment_6m` (L902) |
| `total_recovered` | L939 | `total_recuperacion_6m` vía maturity |
| `net_benefit` | L940 | `net_benefit_6m` (L904) |

### Acción
Eliminar cada entrada del dict `{key: value}` en `_prepare_template_data()`.

**⚠️ IMPORTANTE:**
- **NO eliminar variables locales** que calculan estos valores (algunas se usan internamente)
- **Solo eliminar la entrada del dict** (la línea `'key': value,`)
- El método `_build_capex_breakdown_table()` (L191) NO se toca en esta fase

### Comando de verificación post-fix
```bash
# Confirmar que las keys huérfanas ya no están en el dict
grep -n "'setup_fee':\|'projected_real_gain':\|'plan_7d':\|'plan_30d':\|'plan_60d':\|'plan_90d':\|'total_investment':\|'total_recovered':\|'net_benefit':" \
  modules/commercial_documents/v4_proposal_generator.py
# Debe retornar VACÍO (no matches en el dict de _prepare_template_data)

# Confirmar que las keys válidas SÍ permanecen
grep -n "'capex_total':\|'plan_7_days':\|'total_investment_6m':\|'net_benefit_6m':" \
  modules/commercial_documents/v4_proposal_generator.py
# Debe mostrar matches (keys reales en uso)
```

---

## F8 — Fallback sin Header

### Problema (verificado contra código vivo)
`_build_capex_breakdown_table()` L201-203:
```python
if not components:
    # Fallback: single-row table with total
    return f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
```
Retorna fila de datos SIN header. Si se renderiza como sección independiente (como lo hace FASE-1), produce tabla markdown sin header.

### Acción
Agregar header al fallback:
```python
if not components:
    # Fallback: single-row table with header
    header = "| Componente | Monto | Descripción |\n|---|---|---|\n"
    return header + f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
```

### Verificación
```bash
grep -A2 'if not components' modules/commercial_documents/v4_proposal_generator.py
# Debe mostrar: header string + return con header concatenado
```

---

## Ejecución

### Paso 1: Spawn subagente para F7 (keys huérfanas)

```python
delegate_task(
    goal="""Eliminar 9 keys huérfanas del dict de retorno en _prepare_template_data() de modules/commercial_documents/v4_proposal_generator.py.

Keys a eliminar SOLO del dict data (NO eliminar variables locales que las calculan):
- 'setup_fee' (L791)
- 'projected_real_gain' (L805)
- 'plan_7d' (L905)
- 'plan_30d' (L906)
- 'plan_60d' (~L907)
- 'plan_90d' (~L908)
- 'total_investment' (L938)
- 'total_recovered' (L939)
- 'net_benefit' (L940)

IMPORTANTE: Line numbers pueden estar stale. Grep para encontrar posición actual antes de editar.
Solo eliminar las líneas del dict, NO las variables locales.
Verificar con grep que las keys ya no aparecen en el dict pero sí en las variables locales.""",
    context="""Proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.
Python venv: ./venv/Scripts/python.exe
Archivo: modules/commercial_documents/v4_proposal_generator.py
Método: _prepare_template_data() que construye un dict grande con string.Template keys.
Las keys huérfanas son residuos del refactor CAPEX/OPEX y migración V4→V6 templates.
NO modificar _build_capex_breakdown_table() (eso es otro track de la misma fase).""",
    toolsets=["terminal", "file"]
)
```

### Paso 2: Agente principal ejecuta F8 (fallback header)

Mientras el subagente trabaja en F7, el agente principal:
1. Edita L201-203 para agregar header al fallback
2. Ejecuta tests de CAPEX para verificar F8
3. Espera resultado del subagente

### Paso 3: Merge y verificación

Cuando el subagente retorna:
1. Verificar que ambos cambios están en el archivo
2. Ejecutar tests completos:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_capex_rename.py tests/commercial_documents/test_financial_coherence.py -v
```

---

## Post-Ejecución

### log_phase_completion.py
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-2 --desc F7+F8_generator_cleanup_keys_and_fallback --archivos-mod modules/commercial_documents/v4_proposal_generator.py --tests 0 --check-manual-docs"
```

### Documentación
1. **CHANGELOG.md**: Agregar FASE-2 bajo entrada [4.60.0]
2. **GUIA_TECNICA.md**: Nota técnica FASE-2
3. **09-documentacion-post-proyecto.md**: Acumular datos

---

## Criterios de Completitud

- [ ] **F7**: 9 keys eliminadas del dict (grep confirma cero matches en dict)
- [ ] **F7**: Variables locales preservadas (grep confirma que siguen existiendo)
- [ ] **F8**: Fallback con header row (grep -A2 confirma)
- [ ] **Tests**: `test_capex_rename.py` y `test_financial_coherence.py` pasan
- [ ] **log_phase_completion.py**: Ejecutado
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete**
- **NO modificar templates** (eso fue FASE-1)
- **NO tocar _build_coherence_checklist()** (eso es FASE-3)
- **Máximo 60 iteraciones**

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - delegate_task spawn + wait: ~5 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18 iters

Específico:
  - F8 (fallback fix): ~5 iters
  - Verificación de subagente: ~5 iters
  - Tests: ~3 iters
  Total específico: ~13 iters

Subagente (F7):
  - Investigación keys: ~5 iters
  - Edición 9 keys: ~9 iters
  - Verificación: ~3 iters
  Total subagente: ~17 iters (no consume budget del parent)

Total estimado parent: 31 iters (cómodamente dentro de 60)
```
