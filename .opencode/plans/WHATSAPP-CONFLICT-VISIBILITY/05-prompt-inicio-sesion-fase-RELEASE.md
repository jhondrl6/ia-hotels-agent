# FASE-RELEASE: v4complete Hotel Castilla Real + Cierre Documental

**ID**: FASE-RELEASE-2.??  
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real (https://www.hotelcastillareal.com/) y validar que el warning de WhatsApp conflict ahora aparece con visibilidad de impacto de negocio en la sección de contexto.  
**Dependencias**: FASE-A-02a, FASE-A-02b, FASE-A-02c (todas completadas)  
**Duración estimada**: 15-20 min (v4complete 5-10 min + verificación)  
**Skill**: iah-cli-phased-execution

---

## Contexto

**Todas las fases de implementación completadas**:

| Fase | Estado | Cambio principal |
|------|--------|------------------|
| FASE-A-02a | ✅ Completada | Investigación de visibilidad documentada |
| FASE-A-02b | ✅ Completada | Nota de contexto implementada |
| FASE-A-02c | ✅ Completada | Impacto ajustado 0.10→0.20, phrasing mejorado |

**Cambios esperados en el output**:
1. `whatsapp_conflict` aparece como 🔴 ALERTA en sección contexto (no solo en "Validación de Calidad")
2. La nota de contexto usa phrasing de impacto de negocio (reservas perdidas sin conocimiento del hotelero)
3. No hay costo mensual asociado (operativo, no tenemos activo para cuantificar)

**Hotel objetivo**: Hotel Castilla Real  
**URL**: https://www.hotelcastillareal.com/  
**Región**: Armenia, Quindío (Eje Cafetero)

---

## Tareas

### Tarea 1: Ejecutar v4complete para Hotel Castilla Real
**Objetivo**: Generar diagnóstico con los cambios de FASE-A-02a/b/c aplicados

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Criterios de aceptación**:
- [ ] v4complete completa sin errores blocking
- [ ] Coherence score >= 0.80
- [ ] G8 (asset_confidence) genera WARNING pero blocking=false (comportamiento esperado)

### Tarea 2: Verificar visibilidad del WhatsApp conflict en el diagnóstico generado
**Objetivo**: Confirmar que la nota de contexto aparece en 01_DIAGNOSTICO_* con el phrasing correcto

**Criterios de aceptación**:
- [ ] Buscar `whatsapp_conflict_business_note` o texto de alerta en sección contexto del diagnóstico
- [ ] Confirmar que la nota menciona: "Su Google Business muestra un número diferente al de su sitio"
- [ ] Confirmar que NO hay costo mensual en la nota
- [ ] Confirmar que la tabla "Validación de Calidad" también muestra el conflicto (doble visibilidad)

### Tarea 3: Guardar evidencia en evidence/FASE-RELEASE/
**Objetivo**: Preservar los archivos generados para análisis

**Archivos a copiar** (NOTA: `{hotel_id}` no es variable de shell — ruta real corregida):
```bash
mkdir -p evidence/FASE-RELEASE/
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-RELEASE/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-RELEASE/
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/FASE-RELEASE/
```

**Criterios de aceptación**:
- [ ] Todos los archivos del delivery copiados a evidence/FASE-RELEASE/

### Tarea 4: Documentación post-proyecto
**Objetivo**: Completar el ciclo documental para todas las fases

**Criterios de aceptación**:
- [ ] REGISTRY.md actualizado con las 4 fases
- [ ] CHANGELOG.md tiene entrada para los cambios
- [ ] GUIA_TECNICA.md tiene nota técnica de la refactorización

---

## Análisis de Ejecución (OBLIGATORIO)

Después de ejecutar v4complete, documentar:

```markdown
## Análisis de Ejecución — FASE-RELEASE (Hotel Castilla Real)

### v4complete Output
- Coherence score: X.XX
- Gate status: PASS / WARNING
- Assets generados: N
- WhatsApp conflict warning: SÍ/NO visible en sección contexto

### Verificación de Cambios
- [ ] Nota de contexto con phrasing de impacto de negocio: ✅/❌
- [ ] Sin costo mensual en la nota: ✅/❌
- [ ] Tabla "Validación de Calidad" muestra conflicto: ✅/❌

### Hallazgos
- Texto libre para observaciones
```

---

## Tests Obligatorios

No hay tests nuevos para esta fase.

**Comando de validación**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe main.py --doctor
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-RELEASE como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Completar todas las secciones acumulativas
3. **`REGISTRY.md`**: Registrar las 4 fases (A-02a, A-02b, A-02c, RELEASE)
4. **`scripts/doctor.py --regenerate-domain-primer`**: Regenerar DOMAIN_PRIMER.md con version y codename actuales (NO `main.py --doctor` — esa opcion no existe ahi; el flag correcto vive en `scripts/doctor.py`)
5. **`git add -A && git commit`**: Commit de todos los cambios con mensaje descriptivo

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete Hotel Castilla Real ejecutó sin errores blocking
- [ ] Coherence score >= 0.80
- [ ] Nota de contexto visible en sección contexto del diagnóstico
- [ ] Phrasing de impacto de negocio presente
- [ ] Sin costo mensual en la nota
- [ ] Evidencia copiada a evidence/FASE-RELEASE/
- [ ] REGISTRY.md actualizado (4 fases)
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizada
- [ ] DOMAIN_PRIMER regenerado (manual: header + footer con version+codename)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `git commit` realizado

---

## Restricciones

- v4complete es el comando largo de esta fase — planificar presupuesto de iteraciones
- NO modificar código después de v4complete — solo verificar y documentar
- El WhatsApp conflict warning en G8 es esperado (WARNING non-blocking) — no es un failure

---

*Fase: WHATSAPP-CONFLICT-VISIBILITY / FASE-RELEASE*  
*Depende de: FASE-A-02a, FASE-A-02b, FASE-A-02c*  
*Creado: 2026-05-24*