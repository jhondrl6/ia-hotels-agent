# Dependencias y Conflictos entre Fases

**Proyecto**: FASE-1-AMAZILIA-CORRECCION-ESTADO-ENTREGABLES
**Version**: 4.36.1
**Fecha**: 2026-04-28

---

## Diagrama de Dependencias

```
FASE-1A (Implementar codigo)
    │
    ├── v4_proposal_generator.py: cerrar call chain
    ├── main.py: invocar SitePresenceChecker antes de generate()
    └── test_proposal_alignment.py: fix tilde + nuevos tests
    │
    ▼
| FASE-1B (Ejecutar v4complete + Verificar)
    │
    ├── Ejecutar v4complete --url https://amaziliahotel.com/
    ├── Verificar propuesta: WhatsApp = "Verificado en sitio"
    ├── Verificar propuesta: Schema/FAQ = "Listo para implementar"
    └── Guardar evidencia en evidence/fase-1-amazilia-correccion/
    │
    ▼
FASE-1B-PATCH (Fix regex content_quality gate)
    │
    ├── DR-1/2/3: causa raiz = regex falso positivo en L245
    ├── Fix: `(?<!\d)0\s*%\s*(?:de\s+)?confianza` (lookbehind negativo)
    ├── Verificacion: 151 tests pasan, validate_document → PASSED
    └── CONT: v4complete re-ejecutado → content_quality PASSED, ready=true
    │
    ▼
[FASE-1C] (Documentacion cascade) ✅ COMPLETADA 2026-04-28
    │
    ├── log_phase_completion.py --fase FASE-1A
    ├── log_phase_completion.py --fase FASE-1B
    ├── sync_versions.py
    ├── CHANGELOG.md: entrada [4.36.1]
    ├── GUIA_TECNICA.md: nota tecnica
    └── run_all_validations.py --quick
```

---

## Tabla de Conflictos de Archivos

| Archivo | FASE-1A | FASE-1B | FASE-1C | Conflicto |
|---------|---------|---------|---------|-----------|
| `v4_proposal_generator.py` | ESCRIBE | LEE | - | Ninguno (secuencial) |
| `main.py` | ESCRIBE | LEE | - | Ninguno (secuencial) |
| `test_proposal_alignment.py` | ESCRIBE | LEE | - | Ninguno (secuencial) |
| `proposal_asset_alignment.py` | LEE | - | - | Sin conflicto |
| `site_presence_checker.py` | LEE | EJECUTA | - | Ninguno |
| `output/v4_complete/02_PROPUESTA_*.md` | - | GENERA | LEE | Ninguno (secuencial) |
| `docs/CHANGELOG.md` | - | - | ESCRIBE | Sin conflicto |
| `docs/GUIA_TECNICA.md` | - | - | ESCRIBE | Sin conflicto |
| `docs/contributing/REGISTRY.md` | - | - | ESCRIBE (via script) | Sin conflicto |

**Conclusion**: Sin conflictos reales. Todas las fases son estrictamente secuenciales.

---

## Evaluacion de Scope (R3)

### FASE-1A: Implementar Codigo

```
TAREAS DE LA FASE:
  [ ] T1A: Cerrar call chain en v4_proposal_generator.py (generate → _prepare_template_data → _generate_asset_quality_table → _confidence_to_nivel_significado)
  [ ] T1B: Modificar main.py para invocar SitePresenceChecker y pasar site_presence_report
  [ ] T1C: Fix tilde bug en test_proposal_alignment.py + agregar 2 tests nuevos
  [ ] T1D: Ejecutar tests y verificar 0 regresiones

CONTADOR:
  - T1A = 1 tarea (investigacion + fix)
  - T1B = 1 tarea (fix)
  - T1C = 1 tarea (fix + tests)
  - T1D = 1 tarea (verificacion)
  - Total: 4 tareas + 0 comandos largos = DENTRO DEL LIMITE R3
```

### FASE-1B: Ejecutar v4complete + Verificar

```
TAREAS DE LA FASE:
  [ ] T2A: Ejecutar v4complete --url https://amaziliahotel.com/ (COMANDO LARGO)
  [ ] T2B: Guardar evidencia proactiva en evidence/fase-1-amazilia-correccion/
  [ ] T2C: Verificar propuesta contra criterios de aceptacion

CONTADOR:
  - T2A = 1 tarea + 1 comando largo
  - T2B = 1 tarea
  - T2C = 1 tarea
  - Total: 3 tareas + 1 comando largo = DENTRO DEL LIMITE R3
```

### FASE-1C: Documentacion Cascade

```
TAREAS DE LA FASE:
  [ ] T3A: log_phase_completion.py --fase FASE-1A + FASE-1B
  [ ] T3B: sync_versions.py + version_consistency_checker.py
  [ ] T3C: CHANGELOG.md [4.37.0] + GUIA_TECNICA.md nota tecnica
  [ ] T3D: run_all_validations.py --quick + doctor --status

CONTADOR:
  - 4 tareas + 0 comandos largos = DENTRO DEL LIMITE R3
```

---

## Presupuesto de Iteraciones

| Fase | Fijo (~26-36) | Especifico | Total estimado |
|------|---------------|------------|----------------|
| FASE-1A | 26 | 15-20 (codigo + tests) | ~41-46 |
| FASE-1B | 26 | 8-10 (v4complete + verif) | ~34-36 |
| FASE-1C | 26 | 10-15 (docs cascade) | ~36-41 |

Todas dentro del limite de 60 iteraciones.

---

## Versiones

- **v1.0.0** (2026-04-28): Plan inicial basado en contexto .opencode/context/05-prompt-inicio-sesion-fase-1-amazilia-correccion-estado-entregables.md
