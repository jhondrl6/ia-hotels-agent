# 05-prompt-inicio-sesion-fase-COPY-C

**Fase**: COPY-C — E2E v4complete Validation (Hotel Castilla Real)
**Plan**: COPYWRITING-REFACTOR (Copywriting.jsonl → Refactorización Comercial)
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: COPY-B ✅ (commercial gates integrados)
**Bloquea a**: COPY-RELEASE
**⚠️ CONTIENE COMANDO LARGO** (v4complete)

## Objetivo

Ejecutar v4complete para Hotel Castilla Real con los templates y gates modificados, y validar que el output cumple con TODOS los criterios comerciales del Copywriting.jsonl.

## Contexto de Fases Anteriores

- COPY-A: Templates reestructurados (vista gerencia, OTA narrative, scenario clamp)
- COPY-B: Commercial gates integrados (bloquean IA Bloqueada falsa, escenarios negativos, ROI negativo)
- Ambos completados ✅

## Tareas

### T1: Verificar estado pre-ejecución

Antes de ejecutar v4complete, verificar que los cambios de fases anteriores están presentes:

```bash
# Verificar que los templates tienen la nueva estructura
grep -c "Vista Gerencia\|Anexo Técnico\|OTA\|Booking\|Expedia" modules/commercial_documents/templates/diagnostico_v6_template.md
grep -c "OTA\|Booking\|Expedia\|dependencia" modules/commercial_documents/templates/propuesta_v6_template.md

# Verificar que commercial_gate.py existe
test -f modules/quality_gates/commercial_gate.py && echo "EXISTS" || echo "MISSING"

# Verificar que los generators importan CommercialGateValidator
grep -c "CommercialGateValidator\|commercial_gate" modules/commercial_documents/v4_diagnostic_generator.py
grep -c "CommercialGateValidator\|commercial_gate" modules/commercial_documents/v4_proposal_generator.py
```

Si algo falta, reportar como bloqueante — no ejecutar v4complete hasta resolver.

### T2: Ejecutar v4complete para Hotel Castilla Real

**⚠️ COMANDO LARGO — ejecutar vía delegate_task con timeout=900**

```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Modo de ejecución**: `delegate_task` con timeout=900, notify_on_complete=True

**Contexto para el subagente**:
```
goal: "Ejecutar v4complete para Hotel Castilla Real (https://www.hotelcastillareal.com/) y reportar los paths de los archivos generados"

context: "
Comando exacto: ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
Workdir: /mnt/c/Users/Jhond/Github/iah-cli
Output esperado: 01_DIAGNOSTICO, 02_PROPUESTA, assets, coherence >= 0.80, gate_report
No necesitas verificar el contenido — solo ejecutar y reportar paths.
"

toolsets: ["terminal"]
```

### T3: Validar output contra Copywriting.jsonl

Después de que v4complete complete, verificar cada gate del Copywriting.jsonl:

**Paso 3a: Guardar evidencia inmediatamente**
```bash
mkdir -p evidence/COPY-C
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/COPY-C/
cp output/v4_complete/02_PROPUESTA_*.md evidence/COPY-C/
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/COPY-C/
cp output/v4_complete/v4_complete_report.json evidence/COPY-C/
```

**Paso 3b: Validar gates bloqueantes del Copywriting.jsonl**

| # | Gate | Verificación | Herramienta |
|---|------|-------------|-------------|
| 1 | Escenario optimista NO negativo | `grep -c '\-.*COP/mes' 01_DIAGNOSTICO_*.md` — el campo "Optimista" no debe mostrar valor negativo | grep |
| 2 | Escenario optimista ≥ realista | Verificar que optimista ≥ realista en la tabla de escenarios | grep |
| 3 | Sin "IA Bloqueada" si blocked_crawlers vacío | `grep -i 'bloqueada' 01_DIAGNOSTICO_*.md` debe retornar 0 matches | grep |
| 4 | Propuesta sin ROI negativo como argumento principal | Si ROI < 1.0X, verificar que NO se muestra tabla de pérdidas como cierre y SÍ hay plan de onboarding | grep |
| 5 | Coherence ≥ 0.80 | Leer `coherence_validation_post_gen.json` → `overall_score` | read_file |
| 6 | Disclaimers consistentes (un solo tier) | `grep -c 'Tier [ABC]' 01_DIAGNOSTICO_*.md` — contar tiers distintos | grep |
| 7 | Sin claims absolutos falsos ("No aparece" cuando place_found=true) | `grep -c 'No aparece\|Aparece último' 02_PROPUESTA_*.md` | grep |

**Paso 3c: Validar gates advisory**

| # | Gate | Verificación |
|---|------|-------------|
| 8 | OTA narrative presente | `grep -ci 'booking\|expedia\|comisión\|ota' 02_PROPUESTA_*.md` ≥ 1 |
| 9 | WhatsApp como gancho #1 | Verificar que WhatsApp aparece en las primeras 30 líneas del diagnóstico |
| 10 | Quick wins son acciones del dueño (no técnicas) | Leer sección de quick wins — verificar que son verificables por un no-técnico |

**Paso 3d: Generar informe de validación**

Crear `evidence/COPY-C/validation_report.md` con:

```markdown
# Validación de Cumplimiento — COPY-C

**Hotel**: Hotel Castilla Real
**URL**: https://www.hotelcastillareal.com/
**Fecha**: [fecha]
**v4complete ejecutado**: ✅

## Gates Bloqueantes

| Gate | Estado | Evidencia |
|------|--------|-----------|
| Escenario optimista no negativo | ✅/❌ | [valor] |
| Escenario optimista ≥ realista | ✅/❌ | [valores] |
| Sin "IA Bloqueada" falsa | ✅/❌ | [grep result] |
| ROI no negativo como cierre | ✅/❌ | [ROI, net_benefit] |
| Coherence ≥ 0.80 | ✅/❌ | [score] |
| Disclaimers consistentes | ✅/❌ | [tiers encontrados] |
| Sin claims absolutos falsos | ✅/❌ | [grep result] |

## Gates Advisory

| Gate | Estado | Detalle |
|------|--------|---------|
| OTA narrative presente | ✅/❌ | [menciones] |
| WhatsApp como gancho #1 | ✅/❌ | [posición] |
| Quick wins accionables | ✅/❌ | [descripción] |

## Conclusión

- Gates bloqueantes: X/7 pasados
- Gates advisory: Y/3 pasados
- ¿Listo para publicación?: SÍ/NO
```

## Criterios de Completitud

- [ ] v4complete ejecutado exitosamente (sin errores de pipeline)
- [ ] Evidencia guardada en `evidence/COPY-C/`
- [ ] 7/7 gates bloqueantes validados (cada uno con ✅ o ❌ documentado)
- [ ] 3/3 gates advisory validados
- [ ] `validation_report.md` generado con conclusiones
- [ ] Si algún gate bloqueante falla: documentar el fallo y su causa raíz
- [ ] `log_phase_completion.py` ejecutado al finalizar

## Restricciones

- **NO modificar código** en esta fase (solo verificar)
- **NO modificar** templates ni generators
- Máximo 60 iteraciones — si v4complete se va a delegate_task, el parent tiene ~40 iters para verificación
- Usar `delegate_task` para v4complete, NO `terminal` directo (evitar bloqueo del parent)

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-C --desc "E2E v4complete Hotel Castilla Real: validation against Copywriting.jsonl commercial gates" --check-manual-docs
```

Luego actualizar `09-documentacion-post-proyecto.md` marcando FASE-COPY-C como [x].
