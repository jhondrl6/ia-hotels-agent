# FASE-VALIDATION-GATE — Gate de Validación Pre-Release

**ID**: FASE-VALIDATION-GATE  
**Objetivo**: Verificar que todas las correcciones están correctamente implementadas antes del release  
**Dependencias**: FASE-DATASOURCE, FASE-BUGFIXES, FASE-PERSONALIZATION, FASE-CONTENT-FIXES  
**Duración estimada**: 1-2 horas  
**Skill**: systematic-debugging  

---

## Contexto

**FASES 1-4 deben estar completadas ANTES de ejecutar esta fase.**

Esta es la fase de validación interna ANTES de ejecutar la única prueba v4complete en FASE-RELEASE.

### Validaciones a Realizar
1. **Tests unitarios**: Todos los tests pasando
2. **Validaciones del sistema**: run_all_validations.py --quick pasa 4/4
3. **Verificación de fixes**: Los fixes específicos fueron aplicados correctamente
4. **No regressions**: Funcionalidad existente no se rompió

---

## Tarea 1: Ejecutar Suite Completa de Tests

### Comando
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/ -v --tb=short 2>&1 | tail -50
```

### Criterio de Éxito
- [ ] 385+ tests pasando
- [ ] 0 tests fallando
- [ ] 0 errores de importación

### Si Falla Algún Test
1. Identificar el test que falló
2. Determinar si es regression de los cambios o test pre-existente roto
3. Fix si es regression, documentar si es pre-existente
4. Re-ejecutar hasta que todos pasen

---

## Tarea 2: Ejecutar Validaciones del Sistema

### Comando
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Criterio de Éxito
- [ ] 4/4 validaciones pasando
- [ ] 0 warnings críticos
- [ ] doctor.py --status sin errores

### Si Falla Validación
1. Verificar qué validación falló
2. Inspect 输出 para entender el problema
3. Fix y re-validar

---

## Tarea 3: Verificar Fixes Aplicados (Inspección de Código)

### D1: Coordenadas GPS
```bash
grep -rn "40.7128\|NYC_DEFAULT" modules/ --include="*.py"
# Esperado: 0 matches (coordenadas NYC eliminadas)
```

### D3: Región
```bash
grep -rn '"nacional"\|"national"' modules/ --include="*.py"
# Esperado: 0 matches o solo en contextos legítimos
```

### D4: WhatsApp
```bash
grep -rn "detected_via_html" modules/ --include="*.py"
# Esperado: 0 matches
```

### D5: Review Falso
```bash
grep -rn "Excelente servicio\|★★★★★" modules/ --include="*.py"
# Esperado: 0 matches
```

### D6: Org Schema
```bash
grep -rn "example.com" modules/ --include="*.py"
# Esperado: 0 matches
```

---

## Tarea 4: Verificar Integración de audit_report en Generators

### Verificación
```bash
grep -rn "audit_report" modules/asset_generation/*_generator.py | grep -v "import\|#" | head -20
# Esperado: múltiples matches mostrando que generators usan audit_report
```

### Verificación de Personalización
```bash
# Los generators deben usar audit_report["name"], audit_report["region"], etc.
grep -n 'audit_report\["' modules/asset_generation/*_generator.py
# Esperado: varios matches
```

---

## Tarea 5: Verificar Publication Gates

### Verificación
```bash
grep -n "gate\|publication" modules/quality_gates/publication_gates.py | head -20
# Esperado: 9 gates (incluyendo asset_confidence y proposal_alignment)
```

### Gate Count
```bash
grep -c "def gate_" modules/quality_gates/publication_gates.py
# Esperado: 9 o más
```

---

## Validación Final

### Resumen de Estados
```bash
echo "=== RESUMEN DE VALIDACIÓN ==="
echo "Tests: $(venv/Scripts/python.exe -m pytest tests/ --cohort -q 2>&1 | tail -1)"
echo "Validaciones: $(venv/Scripts/python.exe scripts/run_all_validations.py --quick 2>&1 | tail -3)"
echo "Coords NYC: $(grep -c '40.7128' modules/ --include='*.py' -r)"
echo "WhatsApp roto: $(grep -c 'detected_via_html' modules/ --include='*.py' -r)"
echo "Review falso: $(grep -c 'Excelente servicio' modules/ --include='*.py' -r)"
echo "Org Schema: $(grep -c 'example.com' modules/ --include='*.py' -r)"
```

### Criterio de Éxito
- [ ] Tests: todos pasando
- [ ] Validaciones: 4/4 pasando
- [ ] D1-D6: 0 matches de problemas en código
- [ ] Publication gates: 9+

---

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `.opencode/plans/context/dependencias-fases.md`**:
   - FASE-VALIDATION-GATE = ✅ Completada
   - Fecha de finalización

2. **Actualizar `.opencode/plans/context/06-checklist-implementacion.md`**:
   - Todas las tareas de FASE-VALIDATION-GATE marcadas [x]

3. **Actualizar `.opencode/plans/context/09-documentacion-post-proyecto.md`**:
   - Sección D: métricas actualizadas (tests passing)
   - Sección E: archivos verificados

4. **Registrar en REGISTRY.md**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-VALIDATION-GATE \
       --desc "Gate validación pre-release - tests y validaciones" \
       --check-manual-docs
   ```

---

## Criterios de Completitud

- [ ] 385+ tests pasando
- [ ] run_all_validations.py --quick pasa 4/4
- [ ] doctor.py --status sin errores
- [ ] D1-D6: fixes verificados en código
- [ ] Publication gates: 9+
- [ ] No regressions detectadas
- [ ] dependencias-fases.md actualizado
- [ ] 06-checklist-implementacion.md actualizado
- [ ] REGISTRY.md actualizado

---

## IMPORTANTE: Listo para FASE-RELEASE

Cuando esta fase esté ✅ completada, proceder a FASE-RELEASE para la **ÚNICA** ejecución de v4complete como validación final.
