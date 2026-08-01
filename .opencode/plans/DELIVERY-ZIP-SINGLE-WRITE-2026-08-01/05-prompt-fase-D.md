# FASE-D: E2E Verification — v4complete Zi One Luxury

**ID**: FASE-D-E2E-VERIFICATION
**Objetivo**: Ejecutar `v4complete` real para Zi One Luxury (https://zione.co/) y verificar que el ZIP de entrega se materializa correctamente, validando todos los criterios de aceptacion del fix.
**Dependencias**: FASE-A ✅ + FASE-B ✅ + FASE-C ✅
**Duracion estimada**: 1-1.5 horas (v4complete tarda 5-10 min)
**Skill**: `phased_project_executor.md`
**Modo de ejecucion**: Agente principal + `delegate_task` para v4complete (timeout=900)

---

## Contexto

Las fases A-C corrigieron los bugs y endurecieron el error handling. Esta fase verifica que el fix funciona en **produccion real** (no solo tests unitarios). Es la validacion end-to-end obligatoria segun la leccion "Verificar integracion completa" del plan EVIDENCE-TIER.

**Hotel**: Zi One Luxury
**URL**: https://zione.co/
**Onboarding**: `output/clientes/zi-one-luxury_onboarding.yaml`
**Datos**: 34 habitaciones, 800 reservas/mes, $290,000 COP/reserva, 40% canal directo

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ✅ Completada |
| FASE-D | ⏳ En progreso (esta fase) |

---

## Tareas

### T1: Pre-flight checks (3-5 iteraciones)

**Objetivo**: Verificar que todo esta listo antes de ejecutar v4complete.

**Acciones**:
1. Limpiar artefactos huerfanos de ejecuciones anteriores:
```bash
Remove-Item output/v4_complete/deliveries/zione_*_MANIFEST.json -ErrorAction SilentlyContinue
Remove-Item output/v4_complete/deliveries/README_DELIVERY.md -ErrorAction SilentlyContinue
```

2. Verificar que el onboarding existe:
```bash
cat output/clientes/zi-one-luxury_onboarding.yaml
```

3. Verificar que los tests de delivery pasan:
```bash
./venv/Scripts/python.exe -m pytest tests/delivery/ -q
```

**Criterios de aceptacion**:
- [ ] `deliveries/` limpio de artefactos huerfanos
- [ ] Onboarding confirmado
- [ ] Tests de delivery pasando

### T2: Ejecutar v4complete (1 tool call via delegate_task)

**Objetivo**: Ejecutar el pipeline completo para Zi One Luxury.

**Protocolo de subagente** (segun §Protocolo-Subagente-v4complete):
```
delegate_task(
    goal="Ejecutar v4complete para Zi One Luxury (https://zione.co/)",
    context="""
    Comando: ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
    Onboarding: output/clientes/zi-one-luxury_onboarding.yaml
    Expected output:
    - output/v4_complete/01_DIAGNOSTICO_*.md
    - output/v4_complete/02_PROPUESTA_*.md
    - output/v4_complete/zione/ (165+ archivos)
    - output/v4_complete/deliveries/zione_YYYYMMDD.zip (EL ZIP DEBE EXISTIR)
    - Coherence >= 0.80
    Timeout: 900 segundos
    """,
    timeout=900,
    notify_on_complete=True,
    toolsets=["terminal"]
)
```

**Criterios de aceptacion**:
- [ ] Comando completa sin error fatal
- [ ] Output genera diagnostico y propuesta

### T3: Protocolo de Evidencia Proactiva (OBLIGATORIO, 2-3 iteraciones)

> [!CAUTION]
> **INMEDIATAMENTE** despues de que v4complete genera output, ANTES de cualquier verificacion:

```bash
mkdir -p evidence/FASE-D-E2E
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-D-E2E/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-D-E2E/
cp output/v4_complete/deliveries/zione_*.zip evidence/FASE-D-E2E/ 2>/dev/null || echo "ZIP NO EXISTE"
cp output/v4_complete/v4_complete_report.json evidence/FASE-D-E2E/
```

### T4: Verificacion de criterios de aceptacion (10-15 iteraciones)

**Objetivo**: Validar los 13 criterios del Contexto §10 contra output real.

**Checklist de verificacion**:

| # | Criterio | Comando de verificacion | Esperado |
|---|----------|------------------------|----------|
| 1 | ZIP existe | `Get-ChildItem output/v4_complete/deliveries/*.zip` | 1 archivo ZIP |
| 2 | Validacion exacta | Revisar logs: `_validate_zip()` sin errores | 0 errors |
| 3 | Sin MANIFESTs huerfanos | `Get-ChildItem output/v4_complete/deliveries/*MANIFEST*` | 0 archivos |
| 4 | README coherente | Abrir ZIP, verificar README referencia ZIP correcto | Filename match |
| 5 | quality_metadata | Extraer MANIFEST del ZIP, verificar `evidence_tier` | "B+" |
| 6 | Tests actualizados | Ya verificado en FASE-A | N/A |
| 7 | No regresion | Ya verificado en FASE-B/C | N/A |
| 8 | Control de caso | Verificar modo (FASE-C activo por asset_generation_report) | DeliveryContext loaded |
| 9 | Test FASE-C | Ya verificado en FASE-B | N/A |
| 10 | Test legacy | Ya verificado en FASE-A | N/A |
| 11 | Logging fallback | Revisar logs: sin `except Exception: pass` | Warning visible si aplica |
| 12 | Cleanup | `deliveries/` solo tiene ZIP (sin basura) | Limpio |
| 13 | E2E real | Esta fase | ZIP materializado |

**Comandos de verificacion**:
```bash
# 1. ZIP existe
Get-ChildItem output/v4_complete/deliveries/*.zip | Select-Object Name, Length

# 2. Contenido del ZIP
./venv/Scripts/python.exe -c "import zipfile; z=zipfile.ZipFile('output/v4_complete/deliveries/zione_20260801.zip'); print(f'Files: {len(z.namelist())}'); print('\n'.join(z.namelist()[:20]))"

# 3. Sin huerfanos
Get-ChildItem output/v4_complete/deliveries/ | Where-Object { $_.Name -like '*MANIFEST*' }

# 4. MANIFEST dentro del ZIP
./venv/Scripts/python.exe -c "import zipfile,json; z=zipfile.ZipFile('output/v4_complete/deliveries/zione_20260801.zip'); m=json.loads(z.read('MANIFEST.json')); print(f'Total files: {m[\"total_files\"]}'); print(f'Quality: {m.get(\"quality_metadata\",{})}')"
```

### T5: Analisis post-implementacion (5 iteraciones)

**Objetivo**: Documentar que los fixes fueron superados y lecciones aprendidas.

**Output**: Actualizar `09-documentacion-post-proyecto.md` con:
- Seccion F: Analisis post-implementacion
  - Estado de cada bug (Bug 1, 2, 3) → RESUELTO
  - Estado de cada NF (1-6) → RESUELTO
  - Evidencia: ZIP materializado, tamanos exactos, 0 huerfanos
  - Lecciones aprendidas del plan completo

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| v4complete E2E | Output real | ZIP existe en deliveries/ |
| Suite final | `tests/` | 3,160+ pasan |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/ -x -q --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-D como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Seccion F (analisis post-implementacion)
3. **`evidence/FASE-D-E2E/`**: Evidencia preservada
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D --desc "E2E Verification: v4complete Zi One Luxury produce ZIP valido. 13 criterios de aceptacion verificados." \
    --archivos-mod "evidence/FASE-D-E2E/" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado exitosamente para https://zione.co/
- [ ] ZIP materializado en `output/v4_complete/deliveries/`
- [ ] 0 MANIFESTs huerfanos en `deliveries/`
- [ ] MANIFEST dentro del ZIP tiene `quality_metadata.evidence_tier`
- [ ] README dentro del ZIP referencia filename correcto
- [ ] Evidencia copiada a `evidence/FASE-D-E2E/`
- [ ] Analisis post-implementacion documentado
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- Maximo 60 iteraciones del agente
- NO modificar codigo fuente (esta fase es solo verificacion)
- Si v4complete falla por razones de red/API: reintentar 1 vez, luego documentar como bloqueo
- v4complete SIEMPRE con `notify_on_complete=True` o via subagente
- Evidencia ANTES de cualquier otra verificacion
