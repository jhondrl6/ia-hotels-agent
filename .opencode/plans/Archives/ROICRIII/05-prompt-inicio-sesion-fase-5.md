# FASE-5 — Features: Piloto 30 Días + CAPEX Breakdown + Garantía KPI (C1+C2+C3)

**ID**: ROICRIII-FASE-5
**Objetivo**: Añadir 3 features comerciales al template V6 que aumentan la probabilidad de cierre.
**Dependencias**: FASE-4 ✅ (assets deprecados limpios)
**Complejidad**: 🟡 MEDIA — Nuevos métodos + config + template (3 archivos)
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La propuesta actual carece de tres elementos comerciales clave:
1. **Piloto 30 días**: No existen opciones de bajo riesgo. El cliente sin presupuesto para 6 meses no tiene alternativa.
2. **CAPEX breakdown**: Los $2.500.000 de Setup Fee se presentan como número único. `commercial.yaml` tiene `capex_breakdown` con 3 componentes pero el template no los renderiza.
3. **Garantía Día 55 sin KPI**: Dice "estándares de calidad pactados" sin métrica ni umbral específico.

---

## Tareas

### T1: Sección Piloto 30 Días [C1]

**Archivos**: `config/commercial.yaml` + `v4_proposal_generator.py` + `propuesta_v6_template.md`

**Paso 1**: Añadir config a `config/commercial.yaml`:
```yaml
pilot_options:
  piloto_30_dias:
    nombre: "Piloto de Validación 30 Días"
    duracion: 30
    inversion_unica: true
    precio: 400000
    entregables:
      - "Implementación completa del Kit 4 Pilares"
      - "Reporte de brechas cerradas (evidencia técnica)"
      - "Primera señal en GSC (consultas orgánicas)"
    condicion_continuidad:
      umbral_mejora: 0.10
      metrica: "consultas_directas_gsc"
      sin_mejora: "No hay mes 2. Activos quedan en propiedad del cliente."
      con_mejora: "Continuamos con plan semestral a precio estándar."
```

**NOTA AUDIT**: El precio del piloto es $400.000 (= 1 mes OPEX sin CAPEX). NO usar $665.480 que no tenía trazabilidad.

**Paso 2**: Nuevo método en `v4_proposal_generator.py`:
```python
def _build_pilot_section(self) -> str:
    """Construye sección de piloto 30 días para el template V6."""
    config = self._load_commercial_config()
    pilot = config.get('pilot_options', {}).get('piloto_30_dias', {})
    if not pilot:
        return ""
    
    precio = format_cop(pilot.get('precio', 0))
    entregables = '\n'.join(f"- {e}" for e in pilot.get('entregables', []))
    cond = pilot.get('condicion_continuidad', {})
    
    return f"""---
## 🎯 ¿Prefiere validar antes de comprometerse?

Entendemos que invertir en algo nuevo requiere confianza. Por eso ofrecemos:

### {pilot.get('nombre', 'Piloto de Validación')}

**Inversión única: {precio} COP** — Sin compromiso mensual.

**Lo que incluye:**
{entregables}

**Condiciones transparentes:**
- Si al día {pilot.get('duracion', 30)} no hay +{int(cond.get('umbral_mejora', 0.10)*100)}% en {cond.get('metrica', 'consultas directas').replace('_', ' ')} → {cond.get('sin_mejora', '')}
- Si hay mejora → {cond.get('con_mejora', '')}
"""
```

**Paso 3**: Añadir al data dict en `_prepare_template_data()`:
```python
'pilot_section': self._build_pilot_section(),
```

**Paso 4**: Añadir al template `propuesta_v6_template.md` ANTES de "SIGUIENTE PASO":
```markdown
${pilot_section}
```

**Verificar**: Que `_load_commercial_config()` existe en el generator y lee `commercial.yaml`. Grep para confirmar. Si no existe, cargar el YAML manualmente.

**Criterios**:
- [ ] `pilot_options` existe en `config/commercial.yaml`
- [ ] `_build_pilot_section()` método existe y retorna markdown
- [ ] `${pilot_section}` en el template antes de "SIGUIENTE PASO"
- [ ] Precio = $400.000 (no $665.480)

### T2: CAPEX Breakdown [C2]

**Archivos**: `v4_proposal_generator.py` + `propuesta_v6_template.md`

**Paso 1**: Verificar que `_build_capex_breakdown_table()` existe en el generator. Grep para `capex_breakdown`.

**SI EXISTE**: Añadir al data dict:
```python
'capex_breakdown_detalle': self._build_capex_breakdown_table(),
```

**SI NO EXISTE**: Crear método que lea `capex_breakdown` de `config/commercial.yaml` y genere tabla markdown.

**Paso 2**: En el template, reemplazar la línea del CAPEX total con breakdown detallado:
```markdown
| Componente | Monto | Descripción |
|---|---|---|
${capex_breakdown_detalle}
```

**Criterios**:
- [ ] Template renderiza tabla de componentes CAPEX (no solo total)
- [ ] Los datos vienen de `config/commercial.yaml` capex_breakdown

### T3: Garantía Día 55 con KPI específico [C3]

**Archivos**: `v4_proposal_generator.py` + `propuesta_v6_template.md`

**Paso 1**: Añadir al data dict:
```python
'garantia_metrica': 'Clics directos desde Google Search Console',
'garantia_umbral': '+15% vs. línea base del Día 0',
'garantia_consecuencia': 'Nota crédito automática del 50% del mes 2',
```

**Paso 2**: En el template, reemplazar la sección de garantía (grep "Garantía Día 55" o "estándares de calidad"):
```markdown
### 3. Garantía Día 55: Auditoría automática con KPI verificable

El **Día 55** de nuestro servicio, nuestra IA ejecuta una auditoría completa de todos los entregables.
**Métrica auditada:** ${garantia_metrica}
**Umbral mínimo:** ${garantia_umbral}
**Si no se cumple:** ${garantia_consecuencia}
Sin reclamos, sin papeleo, sin llamadas.
```

**Criterios**:
- [ ] Garantía tiene métrica, umbral y consecuencia específicos
- [ ] No dice "estándares de calidad pactados"

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_pilot_section_renders` | `tests/commercial_documents/test_financial_coherence.py` | contiene "Piloto" |
| `test_capex_breakdown_renders` | `tests/commercial_documents/test_financial_coherence.py` | tiene tabla de componentes |
| `test_garantia_con_kpi` | `tests/commercial_documents/test_financial_coherence.py` | contiene "+15%" |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_financial_coherence.py -v
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-5 como ✅ Completada
2. **`06-checklist-implementacion.md`** — Actualizar estado
3. **`09-documentacion-post-proyecto.md`** — Secciones B + C
4. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-5 --desc "Features_Piloto_CAPEX_Garantia_C1_C2_C3" --archivos-mod "config/commercial.yaml,modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" --tests "3" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Piloto 30 días en template + config ($400K precio correcto)
- [ ] CAPEX desglosado en tabla (no número único)
- [ ] Garantía Día 55 con KPI (+15% clics GSC)
- [ ] 3 tests nuevos pasan + no regresiones
- [ ] run_all_validations.py --quick pasa
- [ ] Post-ejecución completada

---

## Restricciones

- NO modificar la lógica financiera (FASE-1/2 ya hicieron su trabajo)
- Precio del piloto = 1 mes OPEX ($400.000), NO CAPEX incluido
- Límite: 60 iteraciones
- Si `_load_commercial_config()` no existe, implementar carga manual de YAML (no inventar función)
