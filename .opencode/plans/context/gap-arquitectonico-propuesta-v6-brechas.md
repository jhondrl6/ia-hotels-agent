# Contexto: Gap Arquitectónico — propuesta_v6_template no consume brechas reales

## Hallazgo

La propuesta comercial V6 (`propuesta_v6_template.md`) **no consume las brechas detectadas** por el diagnóstico. En su lugar usa una **distribución fija 40/30/20/10** sobre el `main_scenario.monthly_loss_max`, lo cual es un gap entre lo que el diagnóstico detecta y lo que la propuesta presenta.

---

## Archivos Involved

### Código

| Archivo | Rol |
|---------|-----|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Detecta brechas reales con `_identify_brechas()` (línea 1767) |
| `modules/commercial_documents/v4_proposal_generator.py` | Genera propuesta — TIENE el gap |
| `modules/commercial_documents/data_structures.py` | Define `DiagnosticSummary` con `top_problems: List[str]` |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Template diagnóstico — USA `${brechas_section}` |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Template propuesta — NO USA brechas dinámicas |

### Métodos clave

**En `v4_diagnostic_generator.py`:**

```python
# Línea 1767 — Detecta brechas reales desde audit_result
def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
    """
    Retorna List[Dict] con: pain_id, nombre, impacto, detalle
    - pain_id: conecta con PainSolutionMapper
    - nombre: narrativa comercial para el cliente
    - impacto: peso para cálculo de pérdida (0.0-1.0)
    - detalle: explicación técnica
    """
    # 8 brechas detectadas:
    # 1. low_gbp_score        → impacto 0.30
    # 2. no_hotel_schema      → impacto 0.25
    # 3. no_whatsapp_visible  → impacto 0.20
    # 4. poor_performance     → impacto 0.15
    # 5. whatsapp_conflict    → impacto 0.10
    # 6. metadata_defaults     → impacto 0.10
    # 7. missing_reviews      → impacto 0.10
    # 8. no_faq_schema        → impacto 0.12

# Línea 1589 — Construye sección markdown para template
def _build_brechas_section(self, audit_result, financial_scenarios) -> str:
    brechas = self._identify_brechas(audit_result)
    # Genera markdown dinámico con N brechas

# Línea 524 — Se population en template data
'brechas_section': self._build_brechas_section(audit_result, financial_scenarios),
'brechas_resumen_section': self._build_brechas_resumen_section(...),
```

**En `v4_proposal_generator.py`:**

```python
# Línea 140 — generate() recibe audit_result como Optional
def generate(
    self,
    diagnostic_summary: DiagnosticSummary,  # ← Solo esto es obligatorio
    financial_scenarios: FinancialScenarios,
    asset_plan: List[AssetSpec],
    hotel_name: str,
    output_dir: str,
    price_monthly: Optional[int] = None,
    setup_fee: Optional[int] = None,
    audit_result: Optional[Any] = None,  # ← Opcional, no se usa para brechas
    pricing_result: Optional[PricingResolutionResult] = None,
    region: Optional[str] = None,
    analytics_data: Optional[Dict[str, Any]] = None,
) -> str:

# Líneas 538-546 — DISTRIBUCIÓN FIJA (el gap)
'brecha_1_nombre': diagnostic_summary.top_problems[0] if len(diagnostic_summary.top_problems) > 0 else "Problema no identificado",
'brecha_1_costo': format_cop(int(main_scenario.monthly_loss_max * 0.40)),  # ← FIJO 40%
'brecha_2_nombre': diagnostic_summary.top_problems[1] if len(diagnostic_summary.top_problems) > 1 else "Segundo problema",
'brecha_2_costo': format_cop(int(main_scenario.monthly_loss_max * 0.30)),  # ← FIJO 30%
'brecha_3_nombre': diagnostic_summary.top_problems[2] if len(diagnostic_summary.top_problems) > 2 else "Tercer problema",
'brecha_3_costo': format_cop(int(main_scenario.monthly_loss_max * 0.20)),  # ← FIJO 20%
'brecha_4_nombre': diagnostic_summary.top_problems[3] if len(diagnostic_summary.top_problems) > 3 else "Cuarto problema",
'brecha_4_costo': format_cop(int(main_scenario.monthly_loss_max * 0.10)),  # ← FIJO 10%
```

### Qué dice `propuesta_v6_template.md`

El template propone 4 bloques de "brecha" pero **NO tiene variable `${brechas_section}`** — esa solo existe en `diagnostico_v6_template.md`. La propuesta V6 tiene su propia estructura fija de 4 problemas derivados de `top_problems` de `DiagnosticSummary`, no de `_identify_brechas`.

---

## El Gap Explicado

```
DIAGNÓSTICO (_identify_brechas):
  Detecta N brechas reales basadas en evidencia del audit_result
  Cada una tiene impacto específico (0.30, 0.25, 0.20, etc.)
  Total de impacto NO necesariamente suma 1.0

PROPUESTA (_prepare_template_data):
  Recibe diagnostic_summary.top_problems (strings, no brechas)
  Aplica distribución FIJA 40/30/20/10 sobre monthly_loss_max
  Los costos NO reflejan los impactos reales de cada brecha

EJEMPLO:
  Si diagnóstico detecta:
    - low_gbp_score: 0.30 → debería perder $3.000.000 COP
    - no_hotel_schema: 0.25 → debería perder $2.500.000 COP
    - no_whatsapp: 0.20 → debería perder $2.000.000 COP
  
  La propuesta mostraría arbitrariamente:
    - Brecha 1: $4.000.000 COP (40% fijo)
    - Brecha 2: $3.000.000 COP (30% fijo)
    - Brecha 3: $2.000.000 COP (20% fijo)
    - Brecha 4: $1.000.000 COP (10% fijo)
```

---

## Options de Solución

### Opción A: Pass `brechas` desde el diagnóstico a la propuesta (Arquitectura limpia)

1. Hacer que `V4DiagnosticGenerator.generate()` retorne `brechas` además del path
2. Modificar el flujo en `main.py` para pasar `brechas` a `V4ProposalGenerator.generate()`
3. Modificar `DiagnosticSummary` para incluir `brechas: List[Dict]`
4. En `_prepare_template_data()` del proposal generator, usar brechas reales si están disponibles

### Opción B: Replicar `_identify_brechas` en proposal generator (Más simple pero DRY violado)

1. Copiar `_identify_brechas()` a `V4ProposalGenerator` o extraer a util compartido
2. En `_prepare_template_data()` usar la misma lógica que el diagnóstico

### Opción C: Consumir `pain_ids` de `DiagnosticSummary` (Medio camino)

`DiagnosticSummary` ya tiene `pain_ids: Optional[List[str]]` (línea 272 de data_structures.py). Pero este campo actualmente viene de `faltantes[]` (elementos KB que fallan), no de `_identify_brechas()`. Se necesitaría unificar ambos flujos.

---

## Dependencias

- `V4DiagnosticGenerator._identify_brechas()` requiere `audit_result: V4AuditResult` completo
- `V4ProposalGenerator.generate()` tiene `audit_result: Optional[Any]` — actualmente no se usa para brechas
- `DiagnosticSummary` es lo que se pasamandatorymente al proposal generator, pero `audit_result` es Optional
- `PainSolutionMapper.PAIN_SOLUTION_MAP` conecta pain_ids con assets (referenciado en `_identify_brechas`)

---

## Estado de Implementación

**El diagnóstico YA detecta brechas correctamente** — el pipeline de `_identify_brechas` → `_build_brechas_section` → `${brechas_section}` funciona.

**La propuesta V6 NO consume ese pipeline** — usa `top_problems` (strings genéricas) + distribución fija.

---

## Nota Adicional

Los archivos de template están en:
```
modules/commercial_documents/templates/diagnostico_v6_template.md
modules/commercial_documents/templates/propuesta_v6_template.md
```

Y los generadores en:
```
modules/commercial_documents/v4_diagnostic_generator.py
modules/commercial_documents/v4_proposal_generator.py
```

Contexto WSL: `/mnt/c/Users/Jhond/Github/iah-cli/`
Contexto Windows: `C:\Users\Jhond\Github\iah-cli\`
