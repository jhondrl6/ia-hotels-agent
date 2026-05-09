# FASE-12B: Coherence gate — Detección de divergencia audit↔presence

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión.

### Contexto previo
- FASE-12A completada: el fix de `site_presence_checker.py` resuelve el falso positivo.
- Sin embargo, si alguien reintroduce la expansión o hay otro falso positive futuro, el gate no lo detectaría.
- Se necesita un coherence check entre audit path y presence path.

### Objetivo de esta fase
1. Agregar verificación de divergencia en `proposal_asset_alignment.py`.
2. Cuando audit diga `hotel_schema_detected=false` pero presence diga `EXISTS` → marcar como `divergent`.
3. Crear tests para el nuevo comportamiento.
4. Ejecutar v4complete y verificar que `coherence_report` detecta la divergencia.

### Tareas

- [ ] **1. Investigar código** — Leer `proposal_asset_alignment.py` (L146-362) y entender flujo de `verify_proposal_asset_alignment()`.
- [ ] **2. Implementar SOL-2** — Agregar check de divergencia antes de marcar `present_in_production`:
  ```python
  if expected_asset_type == "hotel_schema" and presence_status == "exists":
      audit_report = assessment.get("audit_report", {})
      schema_data = audit_report.get("schema", {})
      if not schema_data.get("hotel_schema_detected", False):
          report.missing.append(ServiceAlignment(
              service_name=service_name,
              asset_type=expected_asset_type,
              is_aligned=False,
              status="missing",
              message="DIVERGENCIA: SitePresenceChecker reporta EXISTS pero audit dice hotel_schema_detected=false.",
              presence_verified=True,
              presence_status="divergent"
          ))
          continue
  ```
- [ ] **3. Agregar `divergent` como estado válido** — Actualizar `ServiceAlignment` y `AlignmentReport.to_dict()` si es necesario.
- [ ] **4. Crear tests** — `tests/test_proposal_asset_alignment.py` con al menos:
  - Caso de divergencia (audit=false, presence=exists → divergent).
  - Caso normal (audit=true, presence=exists → aligned/present_in_production).
- [ ] **5. Ejecutar v4complete** — Sobre termales.com.co.
- [ ] **6. Verificar coherence_report** — Confirmar que `is_coherent` ya no es `true` cuando hay divergencia.

### Restricciones
- No modificar el fix de FASE-12A.
- Máximo 60 iteraciones.

### Entregable
- `proposal_asset_alignment.py` con check de divergencia.
- Tests pasando.
- v4complete ejecutado y divergencia detectada correctamente.

### Próxima sesión
FASE-12C (opcional): Separación de servicios en propuesta, o FASE-RELEASE si 12-C no es necesario.