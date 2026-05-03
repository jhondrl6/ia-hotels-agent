# 05-prompt-inicio-sesion-fase-SCORING-3.md

> **FASE:** FASE-SCORING-3
> **Estado:** ✅ COMPLETADA — 2026-05-02 20:35
> **Objetivo:** Verificar implementación + ejecutar v4complete + docs cascade
> **Contexto previo:** FASE-SCORING-1 ✅ y FASE-SCORING-2 ✅ completadas

---

## TAREAS

### 1. Verificar implementación de FASE-SCORING-1 y FASE-SCORING-2

```bash
# Verificar que las funciones Python existen
grep -n "_build_scoring_breakdown\|_build_excluded_factors_section" \
  /mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py

# Verificar que el template fue actualizado
grep -n "scoring_methodology_url\|geo_score_breakdown\|excluded_factors_section" \
  /mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/templates/diagnostico_v6_template.md

# Verificar que scoring_methodology.md existe
ls -la /mnt/c/Users/Jhond/Github/iah-cli/docs/scoring_methodology.md
```

### 2. Ejecutar v4complete como verificación

**Hotel de prueba:** Hotel Castilla Real — https://www.hotelcastillareal.com/

**Presupuesto:** ~30-40 iteraciones disponibles para verificación + docs.

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete \
  --url https://www.hotelcastillareal.com/ \
  --region eje_cafetero \
  --output output/test-scoring-castilla \
  2>&1
```

**Usar subagente si el agente parent tiene < 30 iteraciones restantes:**

```python
delegate_task(
    goal="Ejecutar v4complete para Hotel Castilla Real como verificación de FASE-SCORING-3",
    context="""URL: https://www.hotelcastillareal.com/
Hotel: Hotel Castilla Real
Region: eje_cafetero
Output dir: output/test-scoring-castilla
Comando: ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/ --region eje_cafetero --output output/test-scoring-castilla
Verificar al finalizar:
1. El diagnóstico en output/test-scoring-castilla/ tiene breakdown visible: 'GEO XX/100 = Fotos(15%) + ...'
2. Tiene sección 'Este score NO mide' visible
3. scoring_methodology.md está linkado en frontmatter""",
    toolsets=["terminal"]
)
```

### 3. Guardar evidencia (OBLIGATORIO — inmediatamente después de output)

```bash
mkdir -p evidence/FASE-SCORING-3
cp output/test-scoring-castilla/01_DIAGNOSTICO_*.md evidence/FASE-SCORING-3/ 2>/dev/null || true
ls -la evidence/FASE-SCORING-3/
```

### 4. Verificar criterios de éxito

Abre el diagnóstico generado en `evidence/FASE-SCORING-3/` y verifica:

- [ ] **Breakdown visible:** "GEO XX/100 = Fotos(15%) + NAP(15%) + ..." aparece debajo de la tabla de scores. El score en el breakdown DEBE coincidir con la suma exacta de pesos de los items True del CHECKLIST_GEO (consistencia matemática).
- [ ] **Nota de divergencia:** Texto "⚠️ Nota sobre el score GEO" visible entre el breakdown y "Este score NO mide", explicando la diferencia entre checklist GEO y GBP raw score.
- [ ] **"Este score NO mide":** La sección aparece con los factores excluidos
- [ ] **"Metodología de Scoring":** La sección aparece al final del documento con nota de divergencia GEO
- [ ] **Frontmatter:** `scoring_methodology_url: ./scoring_methodology.md` está presente

### 5. Ejecutar tests

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v -x --tb=short 2>&1 | tail -20
```

---

## CRITERIOS DE COMPLETITUD

- [ ] Funciones Python verificadas en el archivo
- [ ] Template actualizado con todas las variables
- [ ] `scoring_methodology.md` existe y es válido
- [ ] v4complete genera output con breakdown visible
- [ ] Los 4 criterios de éxito del checklist maestro se cumplen
- [ ] Tests pasan (0 regresiones)

---

## RESTRICCIONES

- No modificar código fuente (solo verificar)
- Máximo 60 iteraciones
- Si algo falla, documentar en el plan qué falla y por qué

---

## EVIDENCIA A GUARDAR

Al terminar:
1. Listado de archivos en `evidence/FASE-SCORING-3/`
2. Resultado de verificación de criterios (✓/✗ por criterio)
3. Output de tests
