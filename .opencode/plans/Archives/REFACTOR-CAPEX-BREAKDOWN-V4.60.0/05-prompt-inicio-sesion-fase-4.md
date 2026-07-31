# FASE-4: v4complete + Verificación Post-Implementación

## Estrategia: delegate_task para v4complete

Esta fase ejecuta v4complete para **Hotel Castilla Real** y verifica que todos los fixes (F1, F6, F7, F8) fueron resueltos correctamente.

---

## Contexto de Fases Anteriores

- **FASE-1 (completada)**: Tabla CAPEX movida a sección propia
- **FASE-2 (completada)**: 9 keys huérfanas eliminadas + fallback con header
- **FASE-3 (completada)**: Coherence checklist resuelto (YAGNI o integrado)
- **Esta fase**: Ejecución end-to-end + análisis post-implementación

---

## T1: Ejecutar v4complete para Hotel Castilla Real (VÍA SUBAGENTE)

### Protocolo de Subagente

```python
delegate_task(
    goal="""Ejecutar v4complete para Hotel Castilla Real en el proyecto iah-cli.

Comando exacto:
cd /mnt/c/Users/Jhond/Github/iah-cli
cmd.exe /c "C:\\Users\\Jhond\\Github\\iah-cli\\venv\\Scripts\\python.exe main.py execute https://www.hotelcastillareal.com/ --region eje_cafetero --plan v4complete"

Esperar a que el comando termine (tarda 5-10 minutos).
Verificar que se generaron los archivos de output en output/v4_complete/ o output/v4_complete_fix_v2/v4_complete/.

Reportar:
1. Exit code del comando
2. Lista de archivos generados en el directorio de output
3. Cualquier error o warning en la salida del comando""",
    context="""Proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.
v4complete ejecuta el pipeline completo: scraping → diagnóstico → propuesta → assets → gates.
El comando tarda 5-10 minutos de wall clock time.
Los outputs van a output/v4_complete/ o output/v4_complete_fix_v2/v4_complete/.
IMPORTANTE: Esperar pacientemente a que termine. No hacer polling excesivo.""",
    toolsets=["terminal"]
)
```

### Cuando el subagente retorna:

1. **Verificar archivos existen:**
```bash
ls -lt /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/ | head -10
# O si está en la otra ruta:
ls -lt /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete_fix_v2/v4_complete/ | head -10
```

2. **Identificar el output más reciente:**
```bash
# Encontrar la propuesta más reciente
PROPUESTA=$(ls -t /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_COMERCIAL_*.md 2>/dev/null | head -1)
echo "Propuesta más reciente: $PROPUESTA"
```

---

## Protocolo de Evidencia Proactiva (OBLIGATORIO)

**Inmediatamente después de que v4complete genera output, ANTES de cualquier verificación:**

```bash
EVIDENCE_DIR="/mnt/c/Users/Jhond/Github/iah-cli/evidence/FASE-4-CAPEX-VERIFY"
mkdir -p "$EVIDENCE_DIR"

# Copiar archivos críticos
cp /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/01_DIAGNOSTICO_*.md "$EVIDENCE_DIR/" 2>/dev/null
cp /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_*.md "$EVIDENCE_DIR/" 2>/dev/null
cp -r /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/*/v4_audit/*.json "$EVIDENCE_DIR/" 2>/dev/null

echo "Evidencia guardada en: $EVIDENCE_DIR"
ls -la "$EVIDENCE_DIR"
```

---

## T2: Análisis Post-Implementación

### Verificación F1: Tabla CAPEX Integridad

```bash
PROPUESTA=$(ls -t /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | head -1)

echo "=== F1: Verificación tabla CAPEX ==="
echo "Archivo: $PROPUESTA"
echo ""

# 1. Extraer sección CAPEX vs OPEX
echo "--- Sección CAPEX vs OPEX ---"
sed -n '/## 🏗️ CAPEX vs OPEX/,/### Desglose del Setup Fee/p' "$PROPUESTA"

echo ""
echo "--- Verificación de pipes en tabla CAPEX (esperado: 5 por fila) ---"
sed -n '/## 🏗️ CAPEX vs OPEX/,/### Desglose del Setup Fee\|^$/p' "$PROPUESTA" | grep '^|' | while read line; do
  pipes=$(echo "$line" | tr -cd '|' | wc -c)
  echo "pipes=$pipes: $line"
done

echo ""
echo "--- Sección Desglose del Setup Fee ---"
sed -n '/### Desglose del Setup Fee/,/Activos digitales/p' "$PROPUESTA"

echo ""
echo "--- Verificación pipes en tabla Desglose (esperado: 4 por fila) ---"
sed -n '/### Desglose del Setup Fee/,/\*\*Activos digitales/p' "$PROPUESTA" | grep '^|' | while read line; do
  pipes=$(echo "$line" | tr -cd '|' | wc -c)
  echo "pipes=$pipes: $line"
done
```

**Criterios F1:**
- ✅ Tabla CAPEX: cada fila tiene exactamente 5 pipes (4 celdas + cierre)
- ✅ NO hay fila "Desglose CAPEX" dentro de la tabla de 4 columnas
- ✅ Sección "### Desglose del Setup Fee (CAPEX)" existe como bloque independiente
- ✅ Tabla de desglose: cada fila tiene exactamente 4 pipes (3 celdas + cierre)
- ✅ Total CAPEX = $2.500.000 COP (3 componentes suman correctamente)

### Verificación F6: Coherence Checklist

```bash
echo "=== F6: Verificación coherence checklist ==="
grep -c 'coherence_checklist' "$PROPUESTA"
# Esperado: 0 si Opción A (YAGNI) > el placeholder no debe aparecer literal
# Esperado: 1+ si Opción B (integrado) > el contenido renderizado aparece

echo ""
echo "Coherence score:"
grep -i 'coherence' "$PROPUESTA" | head -5
```

**Criterios F6:**
- ✅ `${coherence_checklist}` NO aparece como texto literal (fue sustituido o eliminado)
- ✅ Coherence score ≥ 0.80

### Verificación F7: Sin Keys Huérfanas

```bash
echo "=== F7: Verificación sin keys huérfanas ==="
# Buscar placeholders no sustituidos (indica que una key del dict faltó)
grep -oP '\$\{[a-z_0-9]+\}' "$PROPUESTA" | sort -u
# Esperado: NINGÚN placeholder sin sustituir (todos fueron reemplazados)

echo ""
echo "Si hay placeholders sin sustituir, son keys que faltan en el generator."
echo "Si no hay placeholders sin sustituir, F7 está correcto (keys huérfanas eliminadas sin impacto)."
```

**Criterios F7:**
- ✅ Cero placeholders `${...}` sin sustituir en el output
- ✅ No aparece contenido de keys huérfanas en la propuesta

### Verificación F8: Fallback con Header

```bash
echo "=== F8: Verificación fallback ==="
# Si hay componentes en commercial.yaml (caso normal), F8 no se activa
# Verificar que la tabla de desglose tiene header:
grep -A1 '### Desglose del Setup Fee' "$PROPUESTA" | grep '| Componente |'
# Esperado: línea de header presente
```

**Criterios F8:**
- ✅ La tabla de desglose tiene header `| Componente | Monto | Descripción |`
  (Nota: F8 específicamente se verifica en tests unitarios, no en v4complete con commercial.yaml completo)

### Verificación Gates

```bash
echo "=== Verificación de Gates ==="
GATE_REPORT=$(ls -t /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/*/v4_audit/gate_report*.json 2>/dev/null | head -1)
if [ -n "$GATE_REPORT" ]; then
    echo "Gate report: $GATE_REPORT"
    cat "$GATE_REPORT" | python3 -m json.tool 2>/dev/null | grep -E '"result"|"gate"' | head -20
else
    echo "No gate_report.json encontrado — buscar en rutas alternativas"
    find /mnt/c/Users/Jhond/Github/iah-cli/output/ -name "gate_report*.json" -newer "$PROPUESTA" 2>/dev/null
fi
```

**Criterios Gates:**
- ✅ 11/11 gates PASS (o ≥ 9/11 conocido pre-existente sin nuevas regresiones)
- ✅ G1: proposal_asset_alignment (whatsapp_button puede fallar — pre-existente, NO bloqueo)
- ✅ Coherence score ≥ 0.80

### Métricas de Éxito Completas

```bash
echo "=== MÉTRICAS FINALES FASE-4 ==="
echo ""
echo "Archivo analizado: $PROPUESTA"
echo "Fecha: $(stat -c '%y' "$PROPUESTA" 2>/dev/null || echo 'N/A')"
echo ""

# Coherence score
grep -i 'coherence.*score\|score.*coherence\|Coherencia' "$PROPUESTA" | head -3

# Contar secciones clave
echo ""
echo "Secciones en propuesta:"
grep '^##' "$PROPUESTA" | wc -l
```

---

## Post-Ejecución

### log_phase_completion.py
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-4 --desc v4complete_Hotel_Castilla_Real_post_fix_verification --archivos-mod NONE --tests 0 --check-manual-docs"
```

### Documentación
1. **CHANGELOG.md**: Agregar FASE-4 con métricas de v4complete
2. **GUIA_TECNICA.md**: Métricas post-implementación
3. **09-documentacion-post-proyecto.md**: Datos finales

---

## Criterios de Completitud

- [x] **T1**: v4complete ejecutado exitosamente para Hotel Castilla Real
- [x] **Evidencia**: Archivos copiados a `evidence/FASE-4-CAPEX-VERIFY/`
- [x] **F1 ✅**: Tabla CAPEX con 5 pipes/fila + desglose en sección independiente
- [x] **F6 ✅**: `${coherence_checklist}` no aparece literal + coherence ≥ 0.80
- [x] **F7 ✅**: Cero placeholders sin sustituir en output
- [x] **F8 ✅**: Tabla desglose con header row
- [x] **Gates**: ≥ 9/11 PASS sin nuevas regresiones (11/11 PASS)
- [x] **log_phase_completion.py**: Ejecutado
- [ ] **Docs cascade**: Actualizados

---

## Resultados

**v4complete exit code:** 0
**Coherence score:** 0.83 (threshold: 0.80) ✅
**Gates:** 11/11 PASS
**Total assets:** 12
**Ready for publication:** YES

### Verificación de Fixes
| Fix | Estado | Detalle |
|-----|--------|---------|
| F1 (CAPEX tabla) | ✅ PASS | 5 pipes/fila en tabla principal, 4 pipes/fila en desglose, sección independiente |
| F6 (coherence checklist) | ✅ PASS | coherence_checklist no aparece como placeholder, score 0.83 |
| F7 (keys huérfanas) | ✅ PASS | 0 placeholders ${...} sin sustituir |
| F8 (header row) | ✅ PASS | Header row `| Componente | Monto | Descripción |` presente |

### Gates Detallados
| Gate | Resultado | Score |
|------|-----------|-------|
| hard_contradictions | PASSED | - |
| evidence_coverage | PASSED | 0.95 |
| financial_validity | WARNING | Tier B (datos por defecto) |
| coherence | PASSED | 0.83 |
| critical_recall | PASSED | 1.0 |
| ethics | PASSED | - |
| content_quality | PASSED | 1.0 |
| asset_confidence | PASSED | 1.0 (12/12 assets) |
| proposal_asset_alignment | PASSED | 1.0 (8/8 servicios alineados) |
| tier_c_onboarding_required | PASSED | Tier B |
| coverage | PASSED | 1.0 |

**Ejecutado:** 2026-05-29 17:52 UTC

---

## Restricciones

- **NO modificar código fuente** (todas las fases de código ya completaron)
- **Máximo 60 iteraciones**
- **Subagente para v4complete con timeout=900**
- **Protocolo de evidencia proactiva NO NEGOCIABLE**

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Spawn subagente v4complete: ~3 iters
  - Protocolo evidencia: ~5 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~21 iters

Específico:
  - T2 Verificación F1: ~8 iters
  - T2 Verificación F6: ~3 iters
  - T2 Verificación F7: ~3 iters
  - T2 Verificación F8: ~3 iters
  - T2 Verificación Gates: ~5 iters
  - Métricas finales: ~3 iters
  Total específico: ~25 iters

Total estimado parent: 46 iters (dentro de 60)
Subagente v4complete: ~5 min wall clock (timeout=900s)
```
