# H4 / AC10 / S-I7 — delta medido y decisión de diferir

**Regla aplicada**: H4 ordena *primero medir, luego decidir*, y solo arreglar en esta
sesión si el punto es del mismo writer que H2/H3. Si exige cambiar el **criterio** de
qué se narra, diferir con causa (DA-V5). **Resultado de la medición: se difiere.**

## 1. Qué se midió, sobre qué

Sonda: `evidence/FASE-HOTFIX-PRE-RELEASE/faseHotfix_sonda_artefactos.py` (sección H2/H3)
y lectura directa de `evidence/FASE-I/corrida/hotelsalentoreal/v4_audit/gate_report_20260904_120413.json`
(única corrida E2E del plan; solo lectura).

El gate `proposal_asset_alignment` del **mismo objeto** serializado en disco declara:

| Superficie | Clave | Valor |
|---|---|---|
| `message` | — | `4/4 servicios comprometidos cubiertos (1 generados + 3 ya en producción)` |
| `details` (plano, legado) | `total_services` | **1** |
| `details` (plano, legado) | `aligned_count` | **1** |
| `details` (plano, legado) | `missing_count` | 0 |
| `details.alignment` (canónico) | `promised_services_total` | **4** |
| `details.alignment` | `actionable_total` | 4 |
| `details.alignment` | `generated_aligned` | 1 |
| `details.alignment` | `present_in_production` | 3 |
| `details.alignment` | `coverage_ratio` | 1.0 |
| `value` | — | 1.0 |

## 2. Causa, leída en el código (no inferida del síntoma)

`_proposal_asset_alignment_gate` arma `details` con
`_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict())`. El propio
docstring del helper dice que es **compatibilidad hacia atrás deliberada**: «`details.total_services`,
`details.aligned_count`, etc. still work directly. New canonical structure is at
`details.alignment`».

Los dos números **no miden lo mismo**:

* `details.total_services` = `AlignmentReport.total_services`, que por definición
  **excluye** los ya presentes en producción (lo fija
  `tests/quality_gates/test_gate_presence.py`: «total_services excludes present_in_production»).
* `details.alignment.promised_services_total` = universo de servicios **prometidos**
  (partición de FASE-C + presencia D-PF1).

Identidad que ya se puede cerrar leyendo el artefacto: `1 (evaluados para asset) + 3
(ya en producción) = 4 (prometidos)`. Es decir: **el artefacto no es incoherente, es
ambiguo** — una clave llamada `total_services` afirma ser el total y no lo es.

## 3. Por qué NO se arregla en esta sesión

Las tres salidas posibles son decisiones sobre **qué narra el artefacto**, no sobre su
serialización:

1. **Borrar las claves planas** (`total_services`, `aligned_count`, `missing_count`): rompe
   a lectores externos y a tests que las asertan hoy
   (`tests/quality_gates/test_proposal_alignment_gate.py`: `result.details["total_services"] == 7`).
2. **Renombrarlas** (`delivery_evaluated_total`, …): cambia el contrato de lectura del ZIP.
3. **Que las planas deriven del canónico** (1 → 4): cambia el valor que un consumidor
   actual lee. Es exactamente la clase de cambio que la restricción de esta sesión prohíbe.

Ninguna es «el mismo writer de H2/H3»: `message`/`details` se arman en
`publication_gates._proposal_asset_alignment_gate`, mientras H2 escribe en `main.py` y
H3 en `AssetAlignmentMatrix.to_dict()`.

**Decisión (DA-V5)**: diferir con el delta medido. Seguimiento nuevo **S-HF1**, dueño
**tribunal**, con el criterio que hay que decidir: *¿`details.total_services` debe decir
lo que mide (`servicios evaluados contra asset generado`, excluye presentes) o debe pasar
a ser el total prometido?* Mientras no se decida, el par mensaje↔`details` sigue siendo
certificable solo por mitades, y **AC10 queda ⚠️ con causa** (no ✅, regla L-V1/DA-V3).

## 4. Lo que sí quedó cerrado en esta sesión y toca AC10

H3 publicó `coverage_ratio` y su denominador **en la matriz** con el valor del mismo
oráculo que alimenta `details.alignment` — medido en la sonda: `d["alignment"] == align`
(del gate) es `True`. Es decir: **el oráculo numérico ya es uno solo y viaja a dos
artefactos**; lo que sigue abierto es la *nomenclatura* de las claves planas del gate.
