# Dependencias de Fases — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

## Diagrama de dependencias

```
Preparacion (sesion del 2026-10-15: Paso 0 + maestro + prompts)
        │
        ▼
    FASE-A  ── cierre documental de la tanda de instrumentos
        │         (sin codigo; commit de las rutas D-QW + crudos + acta)
        ▼
    FASE-B  ── censo era-G + decision por fuente (Operador en el bucle)
        │         (sin codigo, sin borrar, sin subir: medicion y decision)
        ▼
    FASE-C  ── cura era-G: el mecanismo que FASE-B decidio
        │         (scripts/validate_qmind_writeback.py y/o registro escrito por el writer;
        │          unica fase que puede tocar codigo)
        ▼
    FASE-RELEASE-4.81.1 ── bump + docs + write-back + archivado (orden R2.5/R2.10)
```

## Conflictos de archivos por fase

| Archivo | FASE-A | FASE-B | FASE-C | RELEASE |
|---------|--------|--------|--------|---------|
| `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` | **COMMITEA** (ya escrito) | — | — | — |
| `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/15-…` (crudos) | **CREA** | — | — | — |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | **COMMITEA** (par ya regenerado) | — | — | **REGENERA** (write-back → `git mv` → regenera) |
| `.opencode/qmind-writeback/registro.json` | — | — | **EDITA solo por el writer** (si el mecanismo es «marcar») | **EDITA** (entrada del write-back del plan, por el writer) |
| `scripts/validate_qmind_writeback.py` | — | — | **EDITA — condicional** (primitivo nuevo o política declarada, solo si FASE-B lo especificó) | — |
| `tests/test_validate_qmind_writeback_escritura.py` | — | — | **EDITA — condicional** (dientes del mecanismo) | — |
| Notebook `iah-cli-lecciones` | **NO SE TOCA** | **NO SE TOCA** (solo se lista) | **BORRA solo con autorización por fuente** (si la decisión es b) | **SUBE** el 10-analisis del plan (write-back) |
| `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `docs/cobertura-historia.md`, `AGENTS.md` §Cobertura | — | — | — | **EDITA** |
| `.opencode/plans/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/` (docs del plan) | todas | todas | todas | todas (y `git mv` a `Archives/`) |
| `docs/contributing/REGISTRY.md`, `.agent/SYSTEM_STATUS.md`, `.agent/knowledge/DOMAIN_PRIMER.md` | — | — | escribe el registro de fase / regenera (FASE-C) | escribe el registro de release / verifica |

## Conflictos con trabajo ajeno

- Al concebir este plan el árbol trae **4 rutas sin commitear** que son de este plan (el contexto `D-QW`, el crudo `14-` y el par del índice): FASE-A las commitea con pathspec y autorización. No hay trabajo de terceros pendiente.
- `temp/` (gitignored) contiene los crudos de la sesión previa: FASE-A los persiste bajo evidencia **antes** de que nadie los borre; ninguna fase los borra sin orden del Operador.
- El `10-analisis` de CURA y los dos CONTEXT publicados están **congelados** (DEC-2/DEC-3): editar cualquiera de los tres los deja VENCIDO en el notebook.

## Cautelas de secuencia

- **El rojo-antes es antes**: la corrida del writer de FASE-B se guarda como crudo y es lo que hace legítimo el ✅ de AC5 (R2.8: sin el rojo no hay verde).
- **Borrar es irreversible**: la decisión (b) de FASE-B autoriza por fuente; si FASE-C encuentra una fuente sin decisión, para y pregunta en texto plano.
- **El orden del cierre no se permuta**: write-back → índice → `git mv` → índice (R2.10); archivar antes desactiva los verificadores.
- **La L3 va entre el último commit y el push** en cada corte que se empuje; un commit nuevo re-abre el gate, y la cobertura se declara con su rango medido.
