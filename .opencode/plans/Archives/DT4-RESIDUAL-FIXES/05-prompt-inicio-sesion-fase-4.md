# FASE-4: DT4-N5-ALIGNMENT — Unify Alignment Reporting

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA
> **Iteraciones máx**: 60
> **Depende de**: —
> **Bloquea a**: FASE-6 (E2E)

## ⚠️ Hechos Confirmados

- `delivery_quality_report.json` muestra `proposal_asset_gate.passed: false, aligned: 5, total: 7`
- `gate_report.json` muestra `proposal_asset_alignment.passed: true, message: "7/7 aligned", details.total_services: 5`
- El mensaje dice 7/7 pero `details.total_services` es 5 → ambiguo
- Los assets "present in production" (WhatsApp button, Schema Org) se excluyen del denominador en un reporte pero no en otro

## Objetivo

Crear un resultado de alignment canónico compartido entre `publication_gates.py` y `delivery_quality_report.py`, con campos explícitos: `promised_total`, `generated_aligned`, `present_in_production`, `unresolved`, `coverage_ratio`.

## Tareas

### T1: Definir `AlignmentResult` DTO canónico

- **Archivo**: `modules/quality_gates/publication_gates.py` (o nuevo `modules/quality_gates/alignment_result.py`)
- Crear dataclass:
  ```python
  @dataclass
  class AlignmentResult:
      promised_services_total: int       # 7 (total de servicios prometidos)
      generated_aligned: int             # 5 (assets generados con alignment)
      present_in_production: int         # 2 (ya existen en el sitio)
      unresolved: int                    # 0 (prometidos sin asset ni presencia)
      coverage_ratio: float              # 1.0 (100% cobertura)
      present_assets: List[str] = field(default_factory=list)  # ["Botón de WhatsApp", "Schema Organization"]

      @property
      def passed(self) -> bool:
          return self.unresolved == 0

      @property
      def effective_total(self) -> int:
          return self.generated_aligned + self.present_in_production
  ```

### T2: Refactorizar `_proposal_asset_alignment_gate()` para usar `AlignmentResult`

- **Archivo**: `modules/quality_gates/publication_gates.py`
  - Modificar el gate de alignment para retornar un `AlignmentResult` en `result.details`
  - Mantener compatibilidad con el formato actual de `GateResult` (passed, message, details)
  - El mensaje debe ser consistente: "N/M servicios cubiertos (X generados + Y en producción)"

### T3: Refactorizar `delivery_quality_report.py` para consumir `AlignmentResult`

- **Archivo**: `modules/quality_gates/delivery_quality_report.py` (ruta verificada: 471 líneas, 20037 bytes)
  - Buscar dónde se genera el campo `proposal_asset_gate`
  - Usar el mismo `AlignmentResult` del gate en lugar de recalcular
  - Si el `AlignmentResult` está en `gate_results`, extraerlo directamente
  - **Verificación**: `grep -rn "proposal_asset" modules/commercial_documents/`

### T4: Test de igualdad semántica

- **Archivo**: `tests/quality_gates/test_coverage_gate.py` (extender) o nuevo archivo
- Test que verifica:
  1. Dado un `AlignmentResult` con `promised=7, generated=5, production=2`,
  2. Al serializarlo en el gate report y en el delivery quality report,
  3. Ambos reportes muestran los mismos totales (7 promised, 5+2=7 covered)
- **Verificación**: `./venv/Scripts/python.exe -m pytest tests/quality_gates/ -q -k "alignment"`

## Criterios de Completitud

- [ ] `AlignmentResult` dataclass existe con campos explícitos
- [ ] `_proposal_asset_alignment_gate()` produce `AlignmentResult`
- [ ] `delivery_quality_report.py` consume el mismo `AlignmentResult`
- [ ] Ambos reportes muestran totales consistentes
- [ ] Test de igualdad semántica PASS
- [ ] Tests existentes no rompen: `./venv/Scripts/python.exe -m pytest tests/quality_gates/ tests/test_publication_gates_presence.py -q`
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO modificar `PAIN_SOLUTION_MAP` ni `asset_catalog.py`**
- **NO cambiar qué assets se generan** — solo unificar reporting
- **NO ejecutar v4complete**
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-4 \
    --desc "DT4-N5-ALIGNMENT: canonical AlignmentResult DTO shared between publication gates and delivery quality report" \
    --archivos-nuevos "modules/quality_gates/alignment_result.py" \
    --archivos-mod "modules/quality_gates/publication_gates.py,modules/quality_gates/delivery_quality_report.py" \
    --tests "2" \
    --check-manual-docs
```

## Próxima Sesión

FASE-5: DT4-N3-GATE-IDEMPOTENCY — Single gate execution, no mutations
