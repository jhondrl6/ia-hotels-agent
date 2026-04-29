# FASE-1B-PATCH: Fix ContentScrubber Post-T4FIX

**ID**: FASE-1B-PATCH
**Objetivo**: Resolver bug estructural — ContentScrubber valida diagnostico STALE en lugar del regenerado post-T4FIX
**Dependencias**: FASE-1B ✅ Completada
**Duracion estimada**: ~25-30 min (fase debug + continuacion)
**Skill**: iah-cli-phased-execution
**Estado**: 🔴 Parcial — contenido insertado, gate aun falla

---

## Estado Actual (sesion previa)

### Lo que YA se ejecuto

**Codigo insertado en main.py L2417-2459**:
- Bloque ContentScrubber post-T4FIX insertado exitosamente
- `v4complete` re-ejecutado — 2 fixes aplicados ("passo"->"paso", "booking"->"reserva")
- Gate results: 7/8 PASSED, solo `content_quality` falla

### Issue Residual

```
❌ content_quality: "Línea 186: Confianza del 0% destruye credibilidad comercial."
```

**Hipotesis**: El gate Lee un archivo de diagnostico STALE (timestamp 20:47:02) en lugar del recién regenerado+scrubbed (20:59:59). La línea 186 del archivo reciente dice "70% de confianza", no "0%".

**Call chain problema**:
```
L2405: diagnostic_path = diagnostic_gen.generate(...)  → NUEVO archivo 20:59:59
L2444: postscrubber.scrub(diagnostic_path)            → sobreescribe 20:59:59
L2621: assessment["diagnostico_text"] = f.read(diagnostic_path) → deberia ser 20:59:59
```

Necesita confirmarse cuál archivo lee el gate exactamente.

---

## FASE-1B-PATCH-DEBUG: Causa Raiz del content_quality gate

**Objetivo**: Confirmar o descartar la hipotesis del archivo STALE
**Dependencias**: Ninguna (sobre outputs existentes)
**Duracion**: ~5 min
**Estado**: ✅ COMPLETADO (2026-04-28)

### Resultados del Debug

**DR-1 — Archivo STALE → DESCARTADO**:
- Ambos diagnosticos (20:47 y 20:59) dicen "70% de confianza" en L186
- NINGUNO tiene "0% de confianza"
- gate_report.json (21:00) es POSTERIOR al diagnostico nuevo (20:59)

**DR-2 — "0% de confianza" en output → 0 MATCHES**:
- `grep -rn "0%.*confianza"` en `output/v4_complete/` → 0 resultados
- El string NO EXISTE en ningun archivo de output

**DR-3 — Regex falso positivo → CONFIRMADO (ROOT CAUSE)**:
- Regex original L245: `r'0\s*%\s*(?:de\s+)?confianza'`
- "70% de confianza" matchea porque "70" contiene "0" al inicio
- Fix aplicado: `r'(?<!\d)0\s*%\s*(?:de\s+)?confianza'` (lookbehind negativo)
- Verificado: 151 tests pasan, validate_document → PASSED, 0 blockers

**Archivo modificado**: `modules/postprocessors/document_quality_gate.py` L245

### Tarea DR-1: Identificar archivo exacto que lee el gate

En main.py L2621, el gate lee `diagnostic_path`. Agregar print DEBUG temporal:

```python
# DR-1: DEBUG — identificar archivo real que lee el gate
print(f"   [DEBUG] Gate leyendo diagnostico desde: {diagnostic_path}")
```

Ejecutar solo esta linea en main.py (patch rapido), luego:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | grep "DEBUG.*Gate leyendo"
```

Alternativa sin patch: verificar timestamps de archivos generados:

```bash
ls -la output/v4_complete/01_DIAGNOSTICO_*.md
ls -la output/v4_complete/gate_report.json
```

### Tarea DR-2: Buscar "0% de confianza" en archivos con grep recursivo

```bash
grep -rn "0%.*confianza\|0 por.*ciento.*confianza\|Confianza del 0" output/v4_complete/
```

Si no encuentra nada en ninguno de los dos diagnosticos, el problema es otra cosa.

### Tarea DR-3: Verificar regex del content_quality_gate

En `modules/postprocessors/document_quality_gate.py` L245:

```python
pattern = re.compile(r'0\s*%\s*(?:de\s+)?confianza', re.IGNORECASE)
```

Testear manualmente en Python:

```python
import re
pattern = re.compile(r'0\s*%\s*(?:de\s+)?confianza', re.IGNORECASE)
# Probar con contenido de L186 del diagnostico actual
test = "Esta estimacion esta con 70% de confianza, cada mes"
print(pattern.search(test))  # Debe ser None
```

### Criterios de aceptacion DR

- [x] Saber exactamente que archivo lee el gate (ambos, NO es stale)
- [x] Saber si "0% de confianza" existe en algun output (NO existe, 0 matches)
- [x] Saber si el patron regex es la causa o si hay otro source (REGEX FALSO POSITIVO)

---

## FASE-1B-PATCH-CONT: Validacion E2E Post-Fix

**Objetivo**: Re-ejecutar v4complete para confirmar content_quality: PASSED en gate_report.json
**Dependencias**: FASE-1B-PATCH-DEBUG ✅ completada, regex fix ya aplicado
**Duracion**: ~15 min (incluye v4complete)
**Estado**: ⏳ Pendiente

### Fix ya aplicado (no requiere codigo)

El regex fix en `document_quality_gate.py` L245 ya fue aplicado y verificado:
- `r'(?<!\d)0\s*%\s*(?:de\s+)?confianza'` (lookbehind negativo)
- 151 tests pasan
- validate_document(diagnostico) → PASSED, 0 blockers

### Tarea CONT-1: Re-ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | tee evidence/fase-1b-patch-debug/ejecucion_post_fix.log
```

### Tarea CONT-2: Verificar gate_report.json

```bash
grep -A5 "content_quality" output/v4_complete/gate_report.json
```

Esperado: `"passed": true, "status": "PASSED"`

### Tarea CONT-3: Verificar publication_ready

```bash
grep "ready" output/v4_complete/gate_report.json
```

Esperado: `"ready": true`

### Criterios de aceptacion CONT

- [ ] `content_quality: PASSED` en gate_report.json
- [ ] `publication_ready: true`
- [ ] 0 "0% de confianza" en output
- [ ] Evidencia guardada en evidence/fase-1b-patch-debug/

### Post-ejecucion (solo si CONT completa exitosamente)

1. `log_phase_completion.py` para FASE-1B-PATCH
2. Actualizar dependencias-fases.md

---

## Criterios de Completitud Final

- [x] DR-1 a DR-3 ejecutados y causa raiz confirmada (REGEX FALSO POSITIVO)
- [ ] `content_quality: PASSED` en gate_report.json (pendiente v4complete)
- [ ] `publication_ready: true` (pendiente v4complete)
- [x] 0 "0% de confianza" en output (confirmado: 0 matches)
- [x] evidencia guardada en evidence/fase-1b-patch-debug/
- [ ] 0 "COP COP" en output
- [ ] 0 "0% de confianza" en diagnostico
- [ ] evidencia guardada
- [ ] REGISTRY.md actualizado
