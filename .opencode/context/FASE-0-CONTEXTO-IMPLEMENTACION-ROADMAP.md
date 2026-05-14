# Contexto base — Implementación ROADMAP FASE 0

> **Fecha:** 2026-05-13  
> **Repo:** `/mnt/c/Users/Jhond/Github/iah-cli`  
> **Archivo estratégico fuente:** `ROADMAP.md` v3.3 (2026-05-13)  
> **Estado proyecto:** v4.45.0 — TERMALES-GATE-HARDENING  
> **Propósito:** dejar todo el contexto necesario para que una sesión nueva pueda crear el plan de implementación de FASE 0 sin redescubrir intención, restricciones, baseline ni secuencia recomendada.

---

## 1. Tesis de implementación

La implementación del ROADMAP debe comenzar por **FASE 0: Primer piso — entrega confiable al cliente**.

No se debe empezar por:

- FASE A: robustez agente/contexto.
- FASE B: executor/documentación.
- FASE C: operación comercial.
- Producto 2.5: reporte mensual liviano.
- MCP / agent discoverability.
- cross-client insights.
- dashboard, SaaS, multiusuario o UI.

Razón:

> Antes de escalar automatización comercial, outreach, monitoreo recurrente, UI, nuevos módulos o expansión del producto, el pipeline debe demostrar que puede entregar una solución autoconsistente para un hotel real.

FASE 0 debe responder con evidencia:

> ¿Cada brecha detectada se convierte en diagnóstico, oportunidad, propuesta y asset específico, o queda explícitamente justificada como agrupada, descartada, pendiente o bloqueada?

---

## 2. Qué debe hacer la próxima sesión

La próxima sesión NO debe implementar código directamente.

Debe crear un plan ejecutable en `.opencode/plans/` para implementar FASE 0, siguiendo el formato del executor por fases.

La primera acción de esa sesión debe ser una verificación plan-vs-reality sobre el repo vivo:

1. Leer `ROADMAP.md` completo.
2. Leer este contexto completo.
3. Leer `.agents/workflows/phased_project_executor.md`.
4. Verificar contra código y outputs las afirmaciones de este contexto.
5. Crear plan R3-compliant en `.opencode/plans/FASE-0-DELIVERY-QUALITY/`.
6. No ejecutar `v4complete` salvo que se defina una fase E2E dedicada y aprobada.

Skills recomendadas para la sesión que cree el plan:

- `writing-plans`
- `iah-cli-plan-vs-reality-check`
- `iah-cli-phased-execution`
- `test-driven-development`
- `plan-vs-kb-audit`

---

## 3. Fuente estratégica: extracto operativo de ROADMAP.md

FASE 0 en ROADMAP.md v3.3:

| ID | Entregable | Resultado esperado | Gate |
|----|------------|-------------------|------|
| 0-01 | `pain_ledger` operativo | Todas las brechas detectadas tienen ID, fuente, severidad, confianza y estado | 100% trazables |
| 0-02 | Coverage diagnóstico/oportunidad | Ninguna brecha desaparece sin explicación | No silent drop PASS |
| 0-03 | Matriz propuesta → brecha → asset | Todo lo vendido responde a una brecha real y tiene asset específico | Delivery coherence PASS |
| 0-04 | `delivery_quality_report.json` bloqueante | QA post-generación automático sobre `output/v4_complete` | PASS antes de ZIP/publicación |
| 0-05 | Checklist humano reducido | El humano revisa excepciones y decisión comercial, no reconstruye coherencia | <= 10 min |

Definición de terminado en ROADMAP:

> Un agente puede responder, con evidencia por archivo: qué brechas detectó, cuáles entraron al diagnóstico, qué oportunidad comercial justifican, qué se propone vender y qué assets específicos entregan esa solución.

Gates relevantes:

| Gate | Pregunta | Si falla |
|------|----------|----------|
| G0 | ¿El pipeline entrega diagnóstico, oportunidad, propuesta y assets autoconsistentes para un hotel real? | Bloquear fases superiores |
| G3 | ¿Cada claim comercial tiene evidencia? | Bloquear entrega o marcar ESTIMATED |
| G5 | ¿API/cómputo mantiene margen mínimo por diagnóstico? | Activar `permission_mode`, reducir llamadas, fallback barato o revisar precio |
| G6 | ¿Diagnóstico, oportunidad, propuesta y assets cuentan la misma historia? | Bloquear publicación |
| G7 | ¿Todas las brechas detectadas aparecen, se agrupan o se justifican explícitamente? | Reabrir diagnóstico antes de generar ZIP |
| G8 | ¿Cada asset resuelve un problema real del hotel y no es plantilla genérica? | Marcar `GENERIC_DRAFT` o regenerar |
| G9 | ¿Docs críticas reflejan realidad actual? | Ejecutar docs cascade / doctor |

---

## 4. Restricciones obligatorias del plan

### 4.1 Una fase por sesión

El usuario prefiere disciplina de **1 fase/sesión**. El plan debe estar dividido en fases pequeñas, ejecutables en sesiones independientes.

### 4.2 No gastar API innecesariamente

El usuario es sensible a costos. La creación del plan debe evitar E2E costosos.

Regla:

- Prevalidaciones baratas primero.
- Tests unitarios antes de E2E.
- `v4complete` solo en fase E2E dedicada.
- Si el plan necesita `v4complete`, debe estar claramente marcado como comando largo y con justificación.

### 4.3 TDD obligatorio para cambios de código

Toda fase que modifique código debe seguir TDD:

1. Escribir test que falle.
2. Verificar RED.
3. Implementar mínimo.
4. Verificar GREEN.
5. Refactor mínimo si aplica.
6. Ejecutar regresión focalizada.

### 4.4 R3 scope

Cada fase debe cumplir R3:

- Máximo 4 tareas + 0 comandos largos, o
- Máximo 3 tareas + 1 comando largo.

La fase E2E, si existe, debe estar separada.

### 4.5 ROADMAP no dispara docs cascade automático

`ROADMAP.md` es documento estratégico manual. No incluirlo en cascadas automáticas salvo solicitud explícita.

---

## 5. Baseline vivo observado el 2026-05-13

### 5.1 Comandos ejecutados para baseline

Desde `/mnt/c/Users/Jhond/Github/iah-cli`:

```bash
find output/v4_complete -maxdepth 2 -type d 2>/dev/null | sort | head -80
find output/v4_complete -iname '*delivery*quality*' -o -iname 'delivery_quality_report.json' 2>/dev/null | sort | head -50
find output/v4_complete -iname 'v4_complete_report.json' -o -iname 'coherence_validation.json' -o -iname 'asset_generation_report.json' 2>/dev/null | sort | head -80
grep -RIn "pain_ledger\|PainLedger" modules tests main.py .agents/workflows --include='*.py' --include='*.md' | head -80
grep -RIn "_validate_post_generation\|coherence_validation\|asset_generation_report" main.py modules tests --include='*.py' | head -120
```

### 5.2 Output real disponible

Se encontró output reciente para:

```text
output/v4_complete/hotelcastillareal/
```

Subdirectorios relevantes observados:

```text
output/v4_complete/hotelcastillareal/analytics_setup_guide
output/v4_complete/hotelcastillareal/faq_page
output/v4_complete/hotelcastillareal/geo_enriched
output/v4_complete/hotelcastillareal/hotel_schema
output/v4_complete/hotelcastillareal/indirect_traffic_optimization
output/v4_complete/hotelcastillareal/llms_txt
output/v4_complete/hotelcastillareal/local_content_page
output/v4_complete/hotelcastillareal/monthly_report
output/v4_complete/hotelcastillareal/og_tags_guide
output/v4_complete/hotelcastillareal/open_graph
output/v4_complete/hotelcastillareal/optimization_guide
output/v4_complete/hotelcastillareal/org_schema
output/v4_complete/hotelcastillareal/v4_audit
output/v4_complete/hotelcastillareal/whatsapp_conflict_guide
```

Archivos de auditoría observados:

```text
output/v4_complete/hotelcastillareal/v4_audit/asset_generation_report.json
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation.json
output/v4_complete/v4_complete_report.json
```

También existe:

```text
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation_post_gen.json
```

### 5.3 delivery_quality_report inexistente

Búsqueda de `delivery_quality_report` no arrojó resultados útiles.

Observación clave:

> FASE 0-04 parece NO estar implementada como artifact explícito. No se encontró `delivery_quality_report.json` en `output/v4_complete`.

La próxima sesión debe verificar esto de nuevo antes de concluir.

Comando recomendado:

```bash
find output/v4_complete -iname 'delivery_quality_report.json' -o -iname '*delivery*quality*'
grep -RIn "delivery_quality_report" modules tests main.py .agents/workflows --include='*.py' --include='*.md'
```

### 5.4 pain_ledger no aparece como implementación nominal

Búsqueda de `pain_ledger` / `PainLedger` no produjo resultados en `modules`, `tests`, `main.py`, `.agents/workflows`.

Observación clave:

> FASE 0-01 probablemente no existe como ledger explícito con ese nombre, aunque sí existen conceptos relacionados (`pain_id`, `PainSolutionMapper`, `pain_ids_resolved`, etc.).

No asumir que falta toda la funcionalidad. Verificar si existe una estructura equivalente antes de crear una nueva.

Comandos recomendados:

```bash
grep -RIn "pain_id\|pain_ids\|pain_ids_resolved\|PainSolutionMapper\|detect_pains" modules tests main.py --include='*.py' | head -200
```

---

## 6. Snapshot técnico observado: asset_generation_report Hotel Castilla Real

Comando usado:

```bash
./venv/Scripts/python.exe -X utf8 - <<'PY'
import json
from pathlib import Path
base = Path('output/v4_complete/hotelcastillareal/v4_audit')
for name in ['asset_generation_report.json','coherence_validation.json','coherence_validation_post_gen.json']:
    p = base / name
    print('---', p, 'exists=', p.exists())
    if p.exists():
        data = json.loads(p.read_text(encoding='utf-8'))
        print('top_keys', list(data.keys())[:20])
        if 'summary' in data: print('summary', data['summary'])
        if 'coherence_score_final' in data: print('coherence_score_final', data.get('coherence_score_final'))
        if 'overall_score' in data: print('overall_score', data.get('overall_score'))
        if 'generated_assets' in data:
            print('generated_assets_count', len(data['generated_assets']))
            for a in data['generated_assets'][:8]:
                print(' asset', {k:a.get(k) for k in ['asset_type','confidence_score','preflight_status','pain_ids_resolved','can_use']})
PY
```

Resultado observado:

```text
asset_generation_report.json exists=True
summary = {
  'total_assets': 13,
  'generated': 12,
  'failed': 0,
  'skipped': 1,
  'can_use': 12,
  'estimated': 9,
  'delivery_ready_percentage': 25.0,
  'site_verification_applied': True
}
coherence_score_final = 0.81

generated_assets_count = 12
- whatsapp_conflict_guide | confidence=0.8 | WARNING | pain_ids=['whatsapp_conflict'] | can_use=True
- hotel_schema | confidence=0.85 | PASSED | pain_ids=['no_hotel_schema'] | can_use=True
- optimization_guide | confidence=0.5 | WARNING | pain_ids=['metadata_defaults'] | can_use=True
- llms_txt | confidence=0.85 | PASSED | pain_ids=['low_ia_readiness'] | can_use=True
- local_content_page | confidence=0.5 | WARNING | pain_ids=['low_ia_readiness'] | can_use=True
- faq_page | confidence=0.85 | PASSED | pain_ids=['no_faq_schema'] | can_use=True
- analytics_setup_guide | confidence=0.5 | WARNING | pain_ids=['no_analytics_configured'] | can_use=True
- indirect_traffic_optimization | confidence=0.5 | WARNING | pain_ids=['low_organic_visibility'] | can_use=True

coherence_validation.json overall_score = 0.83
coherence_validation_post_gen.json overall_score = 0.81
```

Interpretación preliminar:

- Hay trazabilidad parcial asset → `pain_ids_resolved`.
- Hay muchos assets `WARNING`/estimados.
- `delivery_ready_percentage` es solo 25%, pero `can_use` marca 12 assets como usables.
- Existe una posible discrepancia semántica entre “can_use”, “estimated”, “delivery_ready_percentage” y gates de publicación.
- `coherence_validation.json` y `asset_generation_report.coherence_score_final` no parecen estar perfectamente alineados en el snapshot observado (0.83 vs 0.81). Verificar si esto es drift de archivos o resultado esperado post-G1 sync.

La próxima sesión debe tratar esto como hipótesis, no como conclusión definitiva.

---

## 7. Código relevante ya identificado

### 7.1 `modules/asset_generation/v4_asset_orchestrator.py`

Responsabilidades observadas:

- Orquesta generación de assets.
- Usa `PainSolutionMapper`.
- Usa `CoherenceValidator`.
- Usa `AssetDiagnosticLinker`.
- Define `GeneratedAsset`, `FailedAsset`, `SkippedAsset`, `AssetGenerationResult`.
- `AssetGenerationResult.to_dict()` incluye:
  - `generated_assets`
  - `failed_assets`
  - `skipped_assets`
  - `coherence_report`
  - `coherence_score_pre`
  - `coherence_score_post`
  - `coherence_score_final`

Campos útiles para FASE 0:

```python
GeneratedAsset.asset_type
GeneratedAsset.confidence_score
GeneratedAsset.pain_ids_resolved
GeneratedAsset.can_use
GeneratedAsset.preflight_status
SkippedAsset.asset_type
SkippedAsset.reason
SkippedAsset.presence_status
SkippedAsset.pain_ids_affected
```

### 7.2 `modules/asset_generation/asset_diagnostic_linker.py`

Responsabilidades observadas:

- Vincula assets generados con problemas del diagnóstico.
- Define `AssetDiagnosticLink`:
  - `asset_type`
  - `asset_path`
  - `pain_ids`
  - `pain_descriptions`
  - `justification`
  - `confidence_score`
  - `expected_impact`
- Define `AssetMetadata` con campos:
  - `confidence_level`
  - `confidence_score`
  - `validation_sources`
  - `preflight_status`
  - `can_use`
  - `problems_solved`
  - `problem_solved`
  - `why_this_asset`

Puede ser punto de partida para FASE 0-03 y FASE 0-05.

### 7.3 `modules/asset_generation/proposal_asset_alignment.py`

Responsabilidades observadas:

- Verifica que cada servicio prometido tenga asset.
- Define `PROPOSAL_SERVICE_TO_ASSET`:

```python
{
  "SEO Local": "optimization_guide",
  "Botón de WhatsApp": "whatsapp_button",
  "Schema Hotel": "hotel_schema",
  "Schema Organization": "org_schema",
  "Informe Mensual": "monthly_report",
  "Página de FAQ": "faq_page",
  "Meta Tags Sociales (Open Graph)": "open_graph",
  "Optimización para IA Generativa": "llms_txt",
}
```

Observación importante:

- Este contrato es estático.
- ROADMAP FASE 0 exige que lo vendido responda a brechas reales.
- Plan debe verificar si la propuesta real usa servicios dinámicos por pain detectado o si gate sigue validando contra lista estática.

### 7.4 `modules/quality_gates/publication_gates.py`

Responsabilidades observadas:

- Incluye gate de asset confidence.
- Si 100% assets son estimated/baja confianza, bloquea.
- Si hay mezcla de assets por debajo del threshold, emite WARNING con `passed=True`.
- Incluye `_proposal_asset_alignment_gate()`.
- Comentario relevante indica que el gate puede validar contrato estático mientras el generador filtra dinámicamente servicios por pain_ids.

Riesgo para FASE 0:

> Un WARNING con `passed=True` puede no bloquear publicación. Si FASE 0 requiere bloqueo de delivery, el plan debe decidir qué condiciones son bloqueantes y dónde se aplican.

---

## 8. Gaps preliminares a validar antes de planificar

Estos NO son hallazgos finales. Son hipótesis para la próxima sesión.

### GAP-H1: No existe `delivery_quality_report.json` explícito

Evidencia preliminar:

- `find output/v4_complete -iname '*delivery*quality*'` no encontró reportes.
- `grep delivery_quality_report` no encontró implementación clara.

Impacto:

- ROADMAP exige un artifact bloqueante antes de ZIP/publicación.
- Hoy puede existir QA distribuido, pero no una evidencia única final.

Validar:

```bash
find output/v4_complete -iname 'delivery_quality_report.json' -o -iname '*delivery*quality*'
grep -RIn "delivery_quality_report\|DeliveryQuality" modules tests main.py --include='*.py'
```

### GAP-H2: No existe `pain_ledger` explícito

Evidencia preliminar:

- Búsqueda nominal no encontró `pain_ledger` / `PainLedger`.
- Sí existen `pain_id`, `PainSolutionMapper`, `pain_ids_resolved`.

Impacto:

- Puede faltar fuente de verdad única de brechas.
- Puede haber trazabilidad parcial, pero no ledger normalizado con estado, fuente, severidad, confianza.

Validar:

```bash
grep -RIn "class Pain\|PainSolutionMapper\|detect_pains\|pain_ids_resolved\|pain_id" modules tests main.py --include='*.py' | head -200
```

### GAP-H3: Diagnóstico/oportunidad pueden no tener coverage 1:1 contra brechas detectadas

Evidencia preliminar:

- Assets tienen `pain_ids_resolved`.
- Falta verificar si cada pain aparece en diagnóstico/oportunidad o queda justificado.

Impacto:

- Riesgo G7: brechas desaparecen entre módulos y diagnóstico final.

Validar sobre output real:

```bash
# encontrar diagnóstico/propuesta reales del output
find output/v4_complete/hotelcastillareal -type f \( -iname '*diagnostico*' -o -iname '*propuesta*' -o -iname '*opportunidad*' -o -iname '*oportunidad*' \) -print

# comparar pain_ids del asset_generation_report contra texto diagnóstico/propuesta
./venv/Scripts/python.exe -X utf8 scripts/<script-temporal-de-auditoria>.py
```

### GAP-H4: Propuesta → brecha → asset puede estar parcialmente cubierta por contrato estático

Evidencia preliminar:

- `PROPOSAL_SERVICE_TO_ASSET` existe.
- `proposal_asset_alignment_gate` existe.
- Comentarios indican posible diferencia entre contrato estático y generación dinámica.

Impacto:

- Un servicio puede validarse por contrato estático, pero no necesariamente demostrar que responde a una brecha real del hotel.

Validar:

```bash
grep -RIn "PROPOSAL_SERVICE_TO_ASSET\|_generate_dynamic_services_table\|proposal_services\|asset_quality_table" modules/commercial_documents modules/asset_generation modules/quality_gates --include='*.py'
```

### GAP-H5: `can_use=True` con assets WARNING/ESTIMATED puede ser demasiado permisivo para entrega comercial

Evidencia preliminar:

- Hotel Castilla Real: 12 assets `can_use`, 9 estimated, delivery_ready_percentage 25%.
- Publicación puede permitir WARNING no bloqueante en algunos gates.

Impacto:

- Riesgo de vender assets estimados como terminados.
- FASE 0 debe distinguir usable como borrador vs entregable final.

Validar:

```bash
grep -RIn "can_use\|delivery_ready_percentage\|GateStatus.WARNING\|passed=True" modules/asset_generation modules/quality_gates --include='*.py'
```

### GAP-H6: ZIP/delivery package debe verificarse en disco, no por logs

Patrón conocido del repo:

- Contextos previos han afirmado ZIP generado cuando el archivo no existía.
- No confiar en stdout de “generating delivery package”.

Validar siempre:

```bash
find output/v4_complete/deliveries -type f -iname '*.zip' -print
```

---

## 9. Qué debe contener el plan de implementación FASE 0

La próxima sesión debe crear esta estructura:

```text
.opencode/plans/FASE-0-DELIVERY-QUALITY/
├── README.md
├── dependencias-fases.md
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
├── 05-prompt-inicio-sesion-fase-0A-BASELINE.md
├── 05-prompt-inicio-sesion-fase-0B-PAIN-LEDGER.md
├── 05-prompt-inicio-sesion-fase-0C-COVERAGE.md
├── 05-prompt-inicio-sesion-fase-0D-PROPOSAL-ASSET.md
├── 05-prompt-inicio-sesion-fase-0E-DELIVERY-QUALITY.md
├── 05-prompt-inicio-sesion-fase-0F-HUMAN-CHECKLIST.md
├── 05-prompt-inicio-sesion-fase-0G-E2E.md
└── 05-prompt-inicio-sesion-fase-RELEASE.md
```

La sesión que cree el plan debe ajustar nombres/cantidad de fases si la verificación encuentra que algo ya existe.

---

## 10. Secuencia recomendada de sesiones

### Sesión 0A — Baseline real sin tocar código

Objetivo:

- Auditar output real existente.
- Construir matriz brecha → diagnóstico → oportunidad → propuesta → asset → estado → evidencia.
- Confirmar gaps reales antes de implementar.

Archivos esperados:

- Crear script de auditoría temporal o permanente, según decisión del plan.
- Crear reporte baseline en `.opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md` o dentro del plan.

Restricciones:

- No ejecutar `v4complete`.
- No modificar lógica productiva.
- Usar outputs existentes.

Resultado:

- Veredicto: FASE 0 requiere implementación / endurecimiento / solo documentación.
- Tabla de gaps con evidencia por archivo.

### Sesión 0B — Pain ledger / fuente de verdad de brechas

Objetivo:

- Crear o formalizar estructura única para brechas detectadas.
- No duplicar si existe equivalente.

Campos mínimos:

```text
pain_id
source_module
source_file/source_artifact
severity
confidence
status: DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP | BLOCKED
human_label
evidence_refs
```

Tests:

- Ledger normaliza pain_ids desde detecciones existentes.
- Ledger serializa JSON reproducible.
- Ledger conserva backward compatibility con `pain_ids_resolved`.

### Sesión 0C — Coverage diagnóstico/oportunidad

Objetivo:

- Gate que verifica que toda brecha detectada aparece en diagnóstico/oportunidad o queda justificada.

Regla:

```text
brechas_en_diagnostico + brechas_justificadas == brechas_detectadas
```

Tests:

- Falla si un pain_id detectado no aparece ni está justificado.
- Pasa si pain_id está agrupado con justificación explícita.
- Pasa con output real o fixture representativo.

### Sesión 0D — Matriz propuesta → brecha → asset

Objetivo:

- Garantizar que cada servicio vendido responde a brecha real y tiene asset específico, o queda explícitamente marcado como pendiente/no vendido.

Debe conectar:

```text
service_name → pain_id(s) → asset_type → file_path → confidence/status
```

Tests:

- Falla si propuesta vende servicio sin brecha real.
- Falla si propuesta vende servicio sin asset ni presencia en producción.
- Falla si asset existe pero no resuelve pain_id asociado.
- Pasa si servicio está presente en producción y justificado.

### Sesión 0E — `delivery_quality_report.json` bloqueante

Objetivo:

- Crear artifact único que consolide FASE 0:

```text
output/v4_complete/<hotel>/v4_audit/delivery_quality_report.json
```

Contenido mínimo:

```json
{
  "status": "PASS|FAIL|WARNING",
  "blocking": true,
  "coverage_gate": {},
  "proposal_asset_gate": {},
  "asset_specificity_gate": {},
  "evidence_gate": {},
  "human_review_items": [],
  "summary": {}
}
```

Regla:

- FAIL debe bloquear ZIP/publicación.
- WARNING debe ser visible y accionable.
- PASS requiere que G6/G7/G8 estén satisfechos.

### Sesión 0F — Checklist humano reducido

Objetivo:

- Derivar checklist humano desde `delivery_quality_report.json`.
- El humano revisa excepciones, no reconstruye la coherencia.

Checklist debe incluir solo:

- datos reales pendientes,
- conflictos,
- assets estimados relevantes,
- decisión comercial de envío,
- tono final/propuesta.

Meta:

- <= 10 minutos.

### Sesión 0G — E2E controlado

Objetivo:

- Ejecutar una validación E2E única y cost-controlled.

Condiciones previas:

- Unit tests de 0B-0F pasan.
- Preflight de APIs/env listo.
- Se define hotel objetivo.
- Se acepta costo.

Comando ejemplo, solo si procede:

```bash
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -X utf8 main.py v4complete --url https://hotel.com
```

Verificación:

- Existe `asset_generation_report.json`.
- Existe `coherence_validation.json`.
- Existe `delivery_quality_report.json`.
- Si se afirma ZIP, verificar archivo real en disco.
- G0/G6/G7/G8 PASS o FAIL justificado.

### Sesión RELEASE — docs cascade final

Objetivo:

- Registrar fase/proyecto según workflow del repo.
- Actualizar documentación obligatoria solo al final.

Debe seguir `.agents/workflows/phased_project_executor.md` y `docs/CONTRIBUTING.md`.

---

## 11. Decisiones arquitectónicas que la próxima sesión debe tomar

Antes de escribir el plan, decidir explícitamente:

| # | Decisión | Opciones | Recomendación preliminar |
|---|----------|----------|--------------------------|
| D1 | ¿Crear `pain_ledger` nuevo o formalizar estructura existente? | nuevo módulo / extender mapper / generar desde reports | Verificar primero. Preferir adapter sobre duplicación. |
| D2 | ¿Dónde vive `delivery_quality_report.json`? | `v4_audit/` / raíz hotel / deliveries | Recomendada: `output/v4_complete/<hotel>/v4_audit/delivery_quality_report.json`. |
| D3 | ¿Qué bloquea publicación? | solo FAIL / WARNING fuerte / thresholds | FASE 0 debe definir condiciones bloqueantes explícitas. |
| D4 | ¿`can_use=True` significa entregable final? | sí / no / depende de status | Recomendada: separar `can_use_as_draft` vs `delivery_ready`. |
| D5 | ¿Propuesta se valida contra servicios estáticos o dinámicos? | estático / dinámico / híbrido | Recomendada: dinámico por pain detectado + backward compat del contrato estático. |
| D6 | ¿Baseline usa output existente o nuevo E2E? | existente / nuevo | Recomendada: existente primero; E2E solo al final. |
| D7 | ¿El reporte debe integrarse antes o después de ZIP? | antes / después | Antes. FAIL debe bloquear ZIP/publicación. |

---

## 12. Archivos que la próxima sesión debe revisar sí o sí

Estrategia / workflows:

```text
ROADMAP.md
AGENTS.md
.agents/workflows/phased_project_executor.md
.agents/workflows/v4_complete.md
.agents/workflows/v4_quality_validator.md
```

Código productivo:

```text
main.py
modules/asset_generation/v4_asset_orchestrator.py
modules/asset_generation/asset_diagnostic_linker.py
modules/asset_generation/proposal_asset_alignment.py
modules/asset_generation/conditional_generator.py
modules/commercial_documents/pain_solution_mapper.py
modules/commercial_documents/v4_diagnostic_generator.py
modules/commercial_documents/v4_proposal_generator.py
modules/commercial_documents/coherence_validator.py
modules/quality_gates/publication_gates.py
```

Tests relevantes:

```text
tests/asset_generation/test_coherence_post_generation.py
tests/asset_generation/test_proposal_alignment.py
tests/commercial_documents/test_diagnostic_brechas.py
tests/commercial_documents/test_pain_solution_mapper.py
tests/commercial_documents/test_proposal_dynamic.py
tests/quality_gates/test_proposal_alignment_gate.py
tests/quality_gates/test_publication_gates.py
tests/test_asset_write_validation_order.py
tests/test_confidence_score_consistency.py
tests/test_proposal_alignment.py
```

Outputs baseline:

```text
output/v4_complete/hotelcastillareal/v4_audit/asset_generation_report.json
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation.json
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation_post_gen.json
output/v4_complete/v4_complete_report.json
```

---

## 13. Comandos de prevalidación para la próxima sesión

Ejecutar desde `/mnt/c/Users/Jhond/Github/iah-cli`:

```bash
# versión y estado git
git status --short
./venv/Scripts/python.exe -X utf8 - <<'PY'
import yaml
from pathlib import Path
print(Path('VERSION.yaml').read_text(encoding='utf-8').splitlines()[:8])
PY

# quick validations
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -X utf8 scripts/run_all_validations.py --quick

# existencia de artifacts baseline
find output/v4_complete/hotelcastillareal/v4_audit -maxdepth 1 -type f | sort
find output/v4_complete -iname 'delivery_quality_report.json' -o -iname '*delivery*quality*'
find output/v4_complete/deliveries -type f -iname '*.zip' -print

# búsqueda de estructuras FASE 0 existentes
grep -RIn "pain_ledger\|PainLedger\|delivery_quality_report\|DeliveryQuality" modules tests main.py --include='*.py'
grep -RIn "pain_id\|pain_ids_resolved\|PROPOSAL_SERVICE_TO_ASSET\|proposal_asset_alignment" modules tests main.py --include='*.py' | head -200
```

Nota WSL:

- Usar `./venv/Scripts/python.exe -X utf8`.
- Añadir `PYTHONIOENCODING=utf-8` para evitar errores de encoding con emojis/símbolos.

---

## 14. Formato esperado del plan final

El plan debe tener:

1. `README.md`
   - objetivo,
   - alcance,
   - no-alcance,
   - decisiones arquitectónicas,
   - fases,
   - criterios G0/G6/G7/G8.

2. `dependencias-fases.md`
   - orden,
   - dependencias,
   - conflictos de archivos,
   - fases que pueden/no pueden correr en paralelo.

3. `06-checklist-implementacion.md`
   - cada fase,
   - cada tarea,
   - estado inicial ⏳,
   - criterios PASS.

4. `09-documentacion-post-proyecto.md`
   - checklist de documentación final.
   - No ejecutar docs cascade hasta RELEASE.

5. Prompts de fase `05-prompt-inicio-sesion-fase-*.md`
   - máximo 4 tareas.
   - restricciones de costo.
   - comandos exactos.
   - criterios de completitud.
   - post-ejecución con `log_phase_completion.py`.

---

## 15. Prompt recomendado para iniciar la próxima sesión

Usar este prompt en una sesión nueva:

```text
Crea el plan de implementación para ROADMAP FASE 0 usando como contexto base:

C:\Users\Jhond\Github\iah-cli\.opencode\context\FASE-0-CONTEXTO-IMPLEMENTACION-ROADMAP.md

Objetivo: crear un plan R3-compliant en .opencode/plans/FASE-0-DELIVERY-QUALITY/ para implementar “Primer piso — entrega confiable al cliente”.

No implementes código. Primero verifica las afirmaciones del contexto contra el repo vivo. Luego crea README, dependencias-fases, checklist, doc post-proyecto y prompts por fase.

Restricciones:
- 1 fase/sesión.
- No ejecutar v4complete salvo fase E2E dedicada.
- Prevalidaciones baratas primero.
- TDD obligatorio para fases de código.
- FASE 0 debe producir o endurecer: pain ledger, coverage diagnóstico/oportunidad, matriz propuesta→brecha→asset, delivery_quality_report.json bloqueante y checklist humano <=10 min.
```

---

## 16. Veredicto operativo

La implementación debe empezar por **FASE 0A Baseline**, no por código.

La pregunta que desbloquea todo:

> Con un output real existente, ¿podemos demostrar archivo por archivo que cada brecha detectada se refleja en diagnóstico, oportunidad, propuesta y asset específico?

Si la respuesta es NO:

- el plan debe convertir esos gaps en fases concretas.

Si la respuesta es SÍ:

- FASE 0 se reduce a consolidar artifact bloqueante (`delivery_quality_report.json`) + checklist humano + E2E final.

No avanzar a FASE A/B/C/D hasta que G0/G6/G7/G8 tengan evidencia verificable.
