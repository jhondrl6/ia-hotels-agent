# FASE-3: F6 — Coherence Checklist (Decisión + Fix)

## Contexto de Fases Anteriores

- **FASE-1 (completada)**: Fix template CAPEX — `${capex_breakdown_table}` movido a sección propia
- **FASE-2 (completada)**: Eliminadas 9 keys huérfanas + fallback con header
- **Esta fase**: Decidir sobre `_build_coherence_checklist()` y fix hardcoded region

---

## F6 — Coherence Checklist Invisible

### Problema (verificado contra código vivo)

**6A — Placeholder inexistente:**
- `_build_coherence_checklist()` funciona correctamente (L1878-1927)
- Generado como `'coherence_checklist'` en data dict (L943)
- **PERO** ningún template tiene `${coherence_checklist}`:
  - `propuesta_v6_template.md` → 0 matches
  - `propuesta_v4_template.md` → 0 matches
  - `diagnostico_v6_template.md` → 0 matches
  - `diagnostico_v4_template.md` → 0 matches
- Código que se ejecuta sin propósito

**6B — Hardcoded region:**
```python
# L1895 en _build_coherence_checklist():
adr_value = (
    validated_data.get('adr')
    or self._get_adr_from_benchmarks('eje_cafetero')  # ← hardcoded!
    or None
)
```
Ignora el parámetro `region` del generator.

---

## Decisión Requerida

### Opciones

| Opción | Descripción | Pros | Contras |
|--------|-------------|------|---------|
| **A — Eliminar (YAGNI)** | Borrar `_build_coherence_checklist()` + `'coherence_checklist'` del data dict | Reduce código muerto, sin impacto funcional | Pierde funcionalidad futura |
| **B — Integrar al template** | Agregar `${coherence_checklist}` a `propuesta_v6_template.md` + fix hardcoded region | Completa la feature | Agrega complejidad al template |
| **C — Solo fix hardcoded** | Mantener código pero fix el `eje_cafetero` por `self.region` | Bug latente corregido | Código sigue sin uso |

### Recomendación: **Opción A (YAGNI)**

**Razón:** La funcionalidad NUNCA se ha renderizado. No afecta coherence score ni gates. Es código muerto que consume CPU sin propósito. Si en el futuro se necesita, se implementa con datos reales y la región correcta.

---

## Tareas

### T1: Eliminar _build_coherence_checklist() [Opción A]

**Acción 1:** Eliminar llamada en data dict (L943):
```python
# Eliminar esta línea:
'coherence_checklist': self._build_coherence_checklist(diagnostic_summary),
```

**Acción 2:** Eliminar método `_build_coherence_checklist()` (L1878-1927):
```python
# Eliminar todo el método def _build_coherence_checklist(...) -> str:
#   ... (50 líneas aprox)
```

**⚠️ IMPORTANTE:** Antes de eliminar, verificar consumidores:
```bash
grep -rn 'coherence_checklist' modules/ tests/ --include="*.py"
# Debe retornar SOLO las 2 ubicaciones a eliminar (L943 y L1878)
# Si hay más consumidores, NO eliminar
```

**Comando de verificación:**
```bash
grep -n 'coherence_checklist' modules/commercial_documents/v4_proposal_generator.py
# Debe retornar VACÍO (método eliminado)
```

---

### T2: Ejecutar tests

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_capex_rename.py tests/commercial_documents/ -v --timeout=120
```

**⚠️ Nota:** Si hay tests que importan `_build_coherence_checklist` directamente, esos tests también deben eliminarse o actualizarse.

---

### T3: Si se elige Opción B (integrar al template)

**SOLO si el usuario rechaza Opción A:**

1. Fix hardcoded region en `_build_coherence_checklist()` L1895:
   ```python
   # ANTES:
   or self._get_adr_from_benchmarks('eje_cafetero')
   # DESPUÉS:
   or self._get_adr_from_benchmarks(self.region or 'eje_cafetero')
   ```
   Verificar que `self.region` existe en el generator (grep para `self.region`).

2. Agregar al template `propuesta_v6_template.md` antes de la sección de garantías:
   ```markdown
   ### ✅ Coherence Checklist
   ${coherence_checklist}
   ```

---

## Post-Ejecución

### log_phase_completion.py
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-3 --desc F6_coherence_checklist_cleanup --archivos-mod modules/commercial_documents/v4_proposal_generator.py --tests 0 --check-manual-docs"
```

### Documentación
1. **CHANGELOG.md**: Agregar FASE-3 bajo [4.60.0]
2. **GUIA_TECNICA.md**: Nota técnica FASE-3
3. **09-documentacion-post-proyecto.md**: Acumular datos

---

## Criterios de Completitud

- [ ] **T1**: Decisión tomada (A o B) y ejecutada
- [ ] **T1**: grep confirma eliminación (Opción A) o integración (Opción B)
- [ ] **T2**: Tests relevantes pasan sin errores
- [ ] **log_phase_completion.py**: Ejecutado
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-4)
- **NO modificar _build_capex_breakdown_table()** (eso fue FASE-2)
- **NO modificar template CAPEX** (eso fue FASE-1)
- **Máximo 60 iteraciones**

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigación consumidores: ~5 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18 iters

Específico:
  - T1 (eliminar/integrar): ~5-8 iters
  - T2 (tests): ~3-5 iters
  Total específico: ~8-13 iters

Total estimado: 26-31 iters (muy cómodo dentro de 60)
```
