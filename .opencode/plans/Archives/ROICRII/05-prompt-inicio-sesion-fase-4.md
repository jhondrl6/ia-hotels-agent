# FASE-4: CAPEX Desglose + Renombrar Variables Sobrecargadas

**Plan**: ROICRII
**Tipo**: Código+Tests
**Hallazgos**: IMP-03, NEW-04
**Prerrequisito**: FASE-3 completada
**Iteración estimada**: 30-40

---

## Objetivo

Dos fixes de capa complementaria: (1) desglosar SETUP_FEE en componentes para transparencia, (2) renombrar la variable sobrecargada `pain_ratio` a nombres semánticos distintos.

---

## Hallazgos a Resolver

### IMP-03: SETUP_FEE sin desglose de componentes
**Evidencia verificada**:
- `SETUP_FEE = 2_500_000` hardcodeado (L126)
- Template: `| Cuota de Activación | ${setup_fee} | Única vez |` (L522)
- No hay desglose de qué incluye la cuota (auditoría, implementación, configuración)

### NEW-04: pain_ratio concepto sobrecargado
**Evidencia verificada**:
1. `addressable_pain_ratio`: porción del dolor que IAO puede abordar (L707, default 0.20)
2. `fee_to_loss_ratio`: se describe como tal en el copy (L795) pero no se calcula
3. `pain_ratio_gate_max`: umbral de gate en pricing.yaml (0.32) — cargado en L246 pero NUNCA comparado; el pipeline usa `gate_max_ratio * 2.0` (L256)

---

## Tareas

### Tarea 4A: Crear CAPEX breakdown — dataclass + config + template
**Paso 1**: Verificar si existe `config/commercial.yaml` con sección de CAPEX:
```bash
grep "capex\|setup_fee\|CAPEX" config/commercial.yaml
```

**Paso 2**: Si no existe sección CAPEX, añadir:
```yaml
capex_breakdown:
  - component: "Auditoría Inicial"
    amount: 800000
    description: "Diagnóstico completo de presencia digital"
  - component: "Implementación Técnica"
    amount: 1200000
    description: "Configuración de activos digitales"
  - component: "Onboarding y Capacitación"
    amount: 500000
    description: "Transferencia de conocimiento al equipo"
  total: 2500000
```

**Paso 3**: En `v4_proposal_generator.py`, crear método `_build_capex_breakdown_table()`:
```python
def _build_capex_breakdown_table(self) -> str:
    config = self._load_commercial_config()
    breakdown = config.get('capex_breakdown', [])
    if not breakdown:
        return f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
    
    rows = []
    for item in breakdown:
        if isinstance(item, dict) and 'component' in item:
            rows.append(f"| {item['component']} | {format_cop(item['amount'])} | {item.get('description', '')} |")
    rows.append(f"| **Total CAPEX** | **{format_cop(config.get('capex_breakdown', {}))} | Única vez |")
    header = "| Componente | Monto | Descripción |\n|---|---|---|\n"
    return header + "\n".join(rows)
```

**Nota**: Antes de implementar, verificar la estructura real de `_load_commercial_config()` — puede retornar un dict anidado. Ajustar el acceso según la estructura real. NO asumas — lee el código.

**Paso 4**: Reemplazar la línea del template L522 (`| Cuota de Activación | ${setup_fee} | Única vez |`) con el output de `_build_capex_breakdown_table()`.

### Tarea 4B: Renombrar variables sobrecargadas de pain_ratio
**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambios**:
- L707: `pain_ratio = ...` → `addressable_pain_ratio = ...` (mantener `pain_ratio` como alias local para compatibilidad con template placeholders)
- L795 (ya corregido en FASE-3): Verificar que el copy usa `addressable_pain_ratio` semánticamente
- L737-738: Variables que usan `pain_ratio` — verificar cuáles son `addressable` vs `fee_to_loss` vs `gate_threshold`

**Estrategia**: NO renombrar en TODA la función de una vez (too risky). En cambio:
1. Añadir comentario al lado de cada uso clarificando qué semántica tiene
2. Crear alias `addressable_pain_ratio = pain_ratio` cerca de L707
3. Dejar `pain_ratio` como variable local para no romper template placeholders que esperan `${pain_ratio}`

**Verificación**: `grep "addressable_pain_ratio" modules/commercial_documents/v4_proposal_generator.py` retorna ≥2 matches.

### Tarea 4C: Tests de CAPEX desglose + renombrar
**Archivo**: `tests/test_capex_rename.py` (nuevo)

Crear tests que verifiquen:
1. `_build_capex_breakdown_table()` retorna tabla markdown con ≥3 filas (componentes + total)
2. El total de componentes == SETUP_FEE (2.5M)
3. `addressable_pain_ratio` existe como alias
4. El copy NO dice "representa el X% de su pérdida" sin aclarar "addressable" (herencia de FASE-3)

**Ejecución**: `pytest tests/test_capex_rename.py -v`

---

## Verificación Final FASE-4

```bash
# 1. CAPEX breakdown existe
grep "capex_breakdown\|_build_capex_breakdown" modules/commercial_documents/v4_proposal_generator.py
# Expected: ≥2 matches

# 2. addressable_pain_ratio existe
grep "addressable_pain_ratio" modules/commercial_documents/v4_proposal_generator.py
# Expected: ≥2 matches

# 3. Tests
pytest tests/test_capex_rename.py -v
# Expected: all passed
```

---

## Log Phase

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase.py --phase "FASE-4" --plan "ROICRII" --status "completed" --desc "CAPEX_desglose_pain_ratio_renombrado"
```

---

## Documentación Post-Fase

Actualizar `09-documentacion-post-proyecto.md` con:
- CAPEX breakdown implementado
- pain_ratio renombrado
- Estado de hallazgos IMP-03 y NEW-04
