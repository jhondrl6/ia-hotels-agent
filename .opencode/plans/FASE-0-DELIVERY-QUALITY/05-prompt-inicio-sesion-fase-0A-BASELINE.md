# FASE-0A: Baseline Real — Auditoría de Output Existente

> **Fase:** 0A  
> **Tipo:** Investigación (sin código)  
> **Comando largo:** No  
> **Dependencias:** Ninguna  
> **Máximo iteraciones:** 60  
> **Restricción:** NO ejecutar `v4complete`. NO modificar código productivo.

---

## Contexto

Este plan implementa ROADMAP FASE 0. Lee primero:
1. `.opencode/context/FASE-0-CONTEXTO-IMPLEMENTACION-ROADMAP.md`
2. `ROADMAP.md` §7 FASE 0
3. Este prompt

---

## Tareas

### Tarea 1: Auditar artifacts existentes

Listar TODO el contenido de:
```
output/v4_complete/hotelcastillareal/v4_audit/
output/v4_complete/hotelcastillareal/ (assets generados)
output/v4_complete/deliveries/
```

Para cada archivo JSON en `v4_audit/`, extraer top-keys y summary.

### Tarea 2: Construir matriz de trazabilidad

Crear tabla:
```
brecha_detectada (pain_id) → diagnóstico → oportunidad → propuesta → asset → estado → evidencia
```

Usar como fuente:
- `asset_generation_report.json` (pain_ids_resolved por asset)
- `coherence_validation.json`
- `gate_report_*.json`
- Archivos markdown de diagnóstico/propuesta si existen en `output/v4_complete/`

Meta: 1 fila por asset generado (12-13 filas).

### Tarea 3: Verificar GAPs del contexto

Ejecutar y documentar:
```bash
find output/v4_complete -iname 'delivery_quality_report.json' -o -iname '*delivery*quality*'
grep -RIn "pain_ledger\|PainLedger\|delivery_quality_report\|DeliveryQuality" modules tests main.py --include='*.py'
grep -RIn "pain_id\|pain_ids_resolved\|PROPOSAL_SERVICE_TO_ASSET\|proposal_asset_alignment" modules tests main.py --include='*.py' | head -50
```

Confirmar GAP-H1, GAP-H2, GAP-H4, GAP-H5 con evidencia.

### Tarea 4: Documentar baseline

Crear `.opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md` con:
- Resumen de artifacts encontrados
- Matriz de trazabilidad
- Gaps confirmados vs hipótesis del contexto
- Veredicto: ¿FASE 0 requiere implementación / endurecimiento / solo documentación?

---

## Criterios de Completitud

- [ ] Lista completa de artifacts con timestamps
- [ ] Matriz con >= 10 filas
- [ ] GAP-H1 confirmado (delivery_quality_report inexistente)
- [ ] GAP-H2 confirmado (pain_ledger inexistente nominalmente)
- [ ] Archivo FASE-0-BASELINE-DELIVERY-QUALITY.md creado y legible

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0A-BASELINE \
    --desc "Auditoria baseline de output hotelcastillareal sin codigo" \
    --archivos-nuevos ".opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md" \
    --tests "0" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0A-1..0A-4 como ✅.
