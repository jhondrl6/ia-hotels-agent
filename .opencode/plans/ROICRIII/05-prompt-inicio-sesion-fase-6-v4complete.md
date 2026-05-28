# FASE-6 — v4complete Hotel Castilla Real + Verificación 5 Niveles

**ID**: ROICRIII-FASE-6
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real y verificar que los 5 niveles de coherencia fueron superados post-implementación.
**Dependencias**: FASE-5 ✅ (todas las correcciones y features aplicadas)
**Complejidad**: 🟡 MEDIA — 1 comando largo + verificación de output
**Skill**: `iah-cli-phased-execution`
**Modo de ejecución**: ✅ `delegate_task` para v4complete

---

## Contexto

Esta es la ÚNICA ejecución de v4complete en todo el plan. Sirve como validación end-to-end de que las fases 1-5 resolvieron los problemas. El sitio de prueba es Hotel Castilla Real (https://www.hotelcastillareal.com/), la misma referencia usada en el baseline de coherencia (0.83, 9/11 gates, coherence ≥0.80).

**Baseline pre-fix** (v4.56.0):
- Coherence: 0.83
- ROIs en documento: 2 (0.45X + 2.10X)
- Assets deprecados: 4
- Score cumplimiento: 44%

**Target post-fix**:
- Coherence: ≥0.80 (mantener baseline)
- ROI único: 2.10X en todo el documento
- Assets deprecados: 0
- Score cumplimiento: ~96%

---

## Protocolo de Ejecución

### T1: Ejecutar v4complete vía delegate_task

**IMPORTANTE**: Usar `delegate_task` con timeout=900 para el comando largo. No ejecutar directamente.

```python
delegate_task(
    goal="Ejecutar v4complete para Hotel Castilla Real y reportar resultados",
    context=(
        "Directorio del proyecto: /mnt/c/Users/Jhond/Github/iah-cli\n"
        "Comando exacto:\n"
        "cd /mnt/c/Users/Jhond/Github/iah-cli && "
        "./venv/Scripts/python.exe main.py v4complete "
        "--url https://www.hotelcastillareal.com/ "
        "--nombre 'Hotel Castilla Real'\n"
        "Este comando tarda 5-10 minutos. Usar terminal con timeout=600.\n"
        "Reportar: (1) si el comando terminó exitosamente, (2) lista de archivos generados en output/v4_complete/, "
        "(3) cualquier error o warning."
    ),
    toolsets=["terminal"]
)
```

**Después de que el subagente complete**:

### T2: Copiar Evidence (OBLIGATORIO — Protocolo de Evidencia Proactiva)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
mkdir -p evidence/roicriii-fase-6
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/roicriii-fase-6/
cp output/v4_complete/02_PROPUESTA_*.md evidence/roicriii-fase-6/
# Copiar audit JSONs si existen:
cp output/v4_complete/*/v4_audit/*.json evidence/roicriii-fase-6/ 2>/dev/null || true
```

### T3: Verificación Post-Implementación — 5 Niveles

Ejecutar las siguientes verificaciones sobre el output generado:

**Nivel 1: Coherencia Financiera (FASE-1 + FASE-2)**
```bash
# ROI único en todo el documento
grep -n "ROI" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar UN solo valor de ROI (~2.10X), NO "0.45X"

# Beneficio neto positivo
grep -n "Beneficio neto" output/v4_complete/02_PROPUESTA_*.md
# Debe ser positivo (~$2.64M), NO negativo

# Total recuperación consistente
grep -n "recuperación\|Recupera\|total_recovered" output/v4_complete/02_PROPUESTA_*.md
```

**Criterio N1**: ✅ Un solo ROI (~2.10X), beneficio neto positivo, sin dualidad de totales.

**Nivel 2: Trazabilidad y Porcentajes (FASE-2)**
```bash
# Porcentaje inversión/fuga
grep -n "10.7%\|10\.7" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar 10.7%, NO "14%" ni "41%"

# Trazabilidad origen
grep -n "Origen\|trazabilidad_origen" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar origen trazable (Fuga × Curva × Recovery Factor)

# Sin "13% número mágico"
grep -n "13% del dolor" output/v4_complete/02_PROPUESTA_*.md
# Debe estar VACÍO
```

**Criterio N2**: ✅ Porcentaje correcto (10.7%), trazabilidad presente, sin número mágico.

**Nivel 3: Semántica de Assets (FASE-3)**
```bash
# Mapeo correcto — NO "Informe Mensual → FAQ"
grep -n "Informe Mensual" output/v4_complete/02_PROPUESTA_*.md
# Debe decir "Informe de rendimiento" o similar, NO "Sin FAQ"

# WhatsApp narrativa
grep -n "Auditoría\|Optimización de Conversión" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar nueva narrativa, NO "Guía de corrección"
```

**Criterio N3**: ✅ Mapeos semánticos correctos, narrativa WhatsApp coherente.

**Nivel 4: Assets Deprecados (FASE-4)**
```bash
# Sin assets deprecados
grep -n "og_tags_guide\|indirect_traffic\|local_content_page\|optimization_guide" output/v4_complete/02_PROPUESTA_*.md
# Debe estar VACÍO (0 resultados)
```

**Criterio N4**: ✅ Cero assets deprecados en el output.

**Nivel 5: Nuevas Features (FASE-5)**
```bash
# Piloto 30 días
grep -n "Piloto\|30 Días\|validar antes" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar sección de piloto

# CAPEX breakdown
grep -n "Componente\|Monto\|Descripción" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar tabla de desglose CAPEX

# Garantía con KPI
grep -n "15%\|GSC\|Google Search Console" output/v4_complete/02_PROPUESTA_*.md
# Debe mostrar métrica verificable
```

**Criterio N5**: ✅ Las 3 features presentes en el output.

---

## Coherence Score Gate

```bash
# Verificar coherence score del output
grep -n "coherence\|Coherencia" output/v4_complete/*_generation_report*.json 2>/dev/null || \
grep -n "coherence\|Coherencia" output/v4_complete/*_audit*.json 2>/dev/null
```

**Criterio**: Coherence score ≥ 0.80 (baseline). Si baja debajo de 0.80, la fase NO se completa y requiere análisis.

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-6 como ✅ con resultados de los 5 niveles
2. **`06-checklist-implementacion.md`** — Actualizar estado + métricas finales
3. **`evidence/roicriii-fase-6/`** — Ya copiado en T2
4. **`09-documentacion-post-proyecto.md`** — Sección D: métricas finales
5. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-6 --desc "v4complete_Hotel_Castilla_Real_5_niveles" --coherence TUDIDO --check-manual-docs
```
(Reemplazar TUDIDO con el coherence score real obtenido)

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado exitosamente
- [ ] Evidence copiada a `evidence/roicriii-fase-6/`
- [ ] **Nivel 1** ✅: ROI único ~2.10X, beneficio positivo
- [ ] **Nivel 2** ✅: Porcentaje 10.7%, trazabilidad presente
- [ ] **Nivel 3** ✅: Mapeos correctos, narrativa coherente
- [ ] **Nivel 4** ✅: 0 assets deprecados
- [ ] **Nivel 5** ✅: Piloto + CAPEX + Garantía presentes
- [ ] Coherence ≥ 0.80
- [ ] Post-ejecución completada

---

## Restricciones

- NO ejecutar v4complete SIN notify_on_complete o subagente
- NO modificar código fuente en esta fase (solo verificar output)
- Protocolo de Evidencia Proactiva es OBLIGATORIO (copiar ANTES de verificar)
- Si los 5 niveles no se superan, DOCUMENTAR qué falló y marcar fase como ⏳ INCOMPLETA
- Límite: 60 iteraciones
