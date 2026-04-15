# FASE-RELEASE — v4.30.1 Release + ÚNICA Prueba v4complete

**ID**: FASE-RELEASE  
**Objetivo**: Release v4.30.1 con validación final mediante única ejecución de v4complete  
**Dependencias**: FASE-VALIDATION-GATE (todas las fases 1-5 completadas)  
**Duración estimada**: 1-2 horas  
**Skill**: iah-cli-phased-execution  

---

## Contexto

**FASE-VALIDATION-GATE debe estar ✅ completada ANTES de ejecutar esta fase.**

**⚠️ IMPORTANTE**: Esta es la **ÚNICA** ejecución de v4complete en todo el proyecto. No se ejecuta v4complete durante el desarrollo de fases para minimizar costos API.

### Flujo
```
FASE-DATASOURCE → FASE-PERSONALIZATION → FASE-BUGFIXES → FASE-CONTENT-FIXES
       ↓                    ↓                    ↓                    ↓
FASE-VALIDATION-GATE ──────────────────────────────────────────────────→
       ↓
FASE-RELEASE ← ÚNICA prueba v4complete aquí
```

---

## Tarea 1: Documentación Pre-Release

### 1.1 Actualizar CHANGELOG.md
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
cat >> CHANGELOG.md << 'EOF'

## [4.30.1] - 2026-04-14

### Objetivo
Corrección de bugs críticos en v4complete: coordenadas GPS falsas, región incorrecta, WhatsApp roto, review falso, org_schema placeholder, y personalización de assets con datos reales.

### Cambios Implementados
- FASE-DATASOURCE: Corrección coords GPS, región, teléfono, GBP
- FASE-PERSONALIZATION: Generators usan audit_report como contexto
- FASE-BUGFIXES: Fix WhatsApp, Review, Org_schema, Propuesta
- FASE-CONTENT-FIXES: Fix optimization_guide, monthly_report, llms_txt
- FASE-VALIDATION-GATE: Validación pre-release

### Archivos Modificados
- modules/asset_generation/hotel_schema_generator.py
- modules/asset_generation/whatsapp_button_generator.py
- modules/asset_generation/review_widget_generator.py
- modules/asset_generation/org_schema_generator.py
- modules/asset_generation/llmstxt_generator.py
- modules/asset_generation/optimization_guide_generator.py
- modules/asset_generation/monthly_report_generator.py
- modules/asset_generation/v4_asset_orchestrator.py
- modules/asset_generation/conditional_generator.py
- modules/auditors/web_auditor.py
- modules/auditors/gbp_auditor.py
- main.py

### Tests
- Tests existentes pasando
- Nuevos tests para fixes aplicados
EOF
```

### 1.2 Sync Versions
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/sync_versions.py
```

### 1.3 Verificar Consistency
```bash
venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### 1.4 Verificar GBP Query (D12)
```bash
# GBP query debe usar "Amazilia Hotel" Pereira, Colombia (no "amaziliahotel")
grep -rn "amaziliahotel\|Amazilia Hotel" modules/providers/ --include="*.py"
```

---

## Tarea 2: Ejecutar v4complete — ÚNICA PRUEBA (Validación Final)

### ⚠️ COMANDO FINAL — EJECUTAR SOLO UNA VEZ ⚠️

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

### Criterio de Éxito de la Ejecución
- [ ] Exit code = 0 (sin errores)
- [ ] Coherence Score >= 0.8
- [ ] Publication Ready = true

---

## Tarea 3: Verificación de Datos Reales (POST-v4complete)

**IMPORTANTE**: Ejecutar DESPUÉS de que v4complete termine.

### D1: Coordenadas GPS
```bash
grep "latitude\|longitude" output/v4_complete/amaziliahotel/hotel_schema/*.json
# Esperado: ~4.81°N, -75.69°W (Pereira, Colombia)
# NO ACEPTAR: 40.7128, -74.0060 (NYC)
```

### D3: Región
```bash
grep -i "pereira\|eje cafetero" output/v4_complete/01_DIAGNOSTICO*.md
# Esperado: Menciona Pereira o Eje Cafetero
# NO ACEPTAR: "nacional"
```

### D4: WhatsApp
```bash
grep -E "wa\.me|whatsapp" output/v4_complete/amaziliahotel/whatsapp_button/*.html | head -5
# Esperado: Número real o "PENDIENTE"
# NO ACEPTAR: "detected_via_html"
```

### D5: Review Widget
```bash
grep "★" output/v4_complete/amaziliahotel/review_widget/*.html
# NO ACEPTAR: 5 estrellas si rating real es 0.0
```

### D6: Org Schema
```bash
grep "url" output/v4_complete/amaziliahotel/org_schema/*.json | head -3
# Esperado: https://amaziliahotel.com/
# NO ACEPTAR: https://example.com
```

### GAP-2: Monthly Report
```bash
grep -i "hotel" output/v4_complete/amaziliahotel/monthly_report/*.md | head -3
# NO ACEPTAR: "**Hotel**: Hotel" (debe ser "Amazilia" o nombre real)
```

### GAP-3: llms_txt
```bash
grep -i "pereira\|spa\|eje cafetero" output/v4_complete/amaziliahotel/llms_txt/*.txt
# Esperado: Al menos 2-3 términos del contenido real del sitio
```

### D7: Propuesta vs Assets
```bash
# Verificar que propuesta refleja estado real
ls output/v4_complete/amaziliahotel/voice_assistant_guide/
ls output/v4_complete/amaziliahotel/whatsapp_button/
ls output/v4_complete/amaziliahotel/monthly_report/
# Todos deben existir (no "No generado" si el archivo existe)
```

---

## Tarea 4: Verificación de Integridad

### Cadena Financiera
```bash
grep "2.610.000\|2610000" output/v4_complete/amaziliahotel/financial_scenarios.json
grep "2.610.000\|2610000" output/v4_complete/01_DIAGNOSTICO*.md
grep "2.610.000\|2610000" output/v4_complete/02_PROPUESTA*.md
# Esperado: Mismo valor en los 3 archivos
```

### Tests
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/ -v --tb=short 2>&1 | tail -10
# Esperado: todos pasando
```

### Publication Gates
```bash
grep "gate_\|GateStatus" output/v4_complete/amaziliahotel/v4_complete_report.json | head -20
# Esperado: 9 gates
```

---

## Tarea 5: Monitoreo API

### Verificar OpenRouter NO se Activó
```bash
grep -i "openrouter\|fallback\|provider.*switch" ~/.hermes/logs/*.log 2>/dev/null | tail -20
# Esperado: 0 matches (MiniMax funcionó sin fallback)
```

### Verificar Costo
- Verificar que el costo de la ejecución única está dentro del presupuesto

---

## Tarea 6: Registro Final

### Registrar Release en REGISTRY.md
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.30.1 \
    --desc "Release v4.30.1 - Corrección bugs Amazilia Hotel + ÚNICA prueba v4complete" \
    --archivos-mod "modules/asset_generation/*.py,modules/auditors/*.py,main.py" \
    --tests "385+" \
    --check-manual-docs
```

### Commit
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
git add -A
git commit -m "fix: v4.30.1 - Corrección bugs críticos (coords, WhatsApp, review, org_schema, personalization)"
```

---

## Criterios de Completitud FINAL

### Validación de Datos Reales
- [ ] D1: hotel_schema coordenadas Pereira, Colombia (NO NYC)
- [ ] D3: Región Pereira/Eje Cafetero (NO "nacional")
- [ ] D4: WhatsApp funcional (NO "detected_via_html")
- [ ] D5: Review honesto (NO 5 estrellas falsas)
- [ ] D6: org_schema URL real (NO example.com)
- [ ] D7: Propuesta refleja estado real de assets
- [ ] D12: GBP query usa "Amazilia Hotel" (NO "amaziliahotel")
- [ ] GAP-2: monthly_report nombre real
- [ ] GAP-3: llms_txt con contenido real

### Validación de Integridad
- [ ] Cadena financiera intacta
- [ ] Tests pasando
- [ ] Publication gates = 9+

### Validación de Monitoreo
- [ ] OpenRouter fallback NO se activó
- [ ] Costo dentro de presupuesto

### Documentación
- [ ] CHANGELOG.md actualizado
- [ ] REGISTRY.md actualizado
- [ ] sync_versions.py ejecutado
- [ ] git commit realizado

---

## Checklist Final Completo

| Verificación | Estado |
|------------|--------|
| v4complete ejecutó exitosamente | [ ] |
| Coherence Score >= 0.8 | [ ] |
| D1: coords Pereira (no NYC) | [ ] |
| D3: región correcta (no nacional) | [ ] |
| D4: WhatsApp funcional | [ ] |
| D5: Review honesto | [ ] |
| D6: org_schema real | [ ] |
| D7: propuesta correcta | [ ] |
| GAP-2: monthly_report nombre real | [ ] |
| GAP-3: llms_txt con contenido real | [ ] |
| Cadena financiera intacta | [ ] |
| Tests pasando | [ ] |
| Publication gates = 9+ | [ ] |
| OpenRouter fallback = 0 | [ ] |
| CHANGELOG.md actualizado | [ ] |
| REGISTRY.md actualizado | [ ] |
| git commit realizado | [ ] |

**Si todos los items están marcados ✅ → Release exitoso**
