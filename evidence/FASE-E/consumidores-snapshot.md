# FASE-E — E4: Consumidores del snapshot SitePresence (censo verificado)

> Fecha: 2026-09-03 · Método: grep + lectura de código en HEAD post-E1/E2.
> Unidad de análisis: quién consume `site_presence_report` / `site_presence_snapshot`
> y de dónde obtiene el dato (snapshot propagado vs. reconstrucción propia).
> **Insumo de FASE-F (A4/V15 — oráculo único)**: este censo es la lista de fuentes
> que F1 debe reconciliar.

## 1. Punto de cálculo y propagación (no modificado por E)

| Etapa | Ubicación | Nota |
|-------|-----------|------|
| Cálculo único | `main.py:2490-2500` | `SitePresenceChecker.check_site()` → `normalize_site_presence(raw_report)`; en fallo → `normalize_site_presence(None)` = `{"results": {}}` |
| Propagación en memoria | `main.py:2535, 2620, 2832, 2937, 3163→3177` | DT4-R2, intacto (restricción de fase) |
| **Persistencia (nuevo, E1/A2)** | `main.py:3157-3170` → `save_site_presence_snapshot()` | `v4_audit/site_presence_snapshot.json`, passthrough, UTF-8, `snapshot_version: 1.0` |

## 2. Consumidores que LEEN el snapshot propagado (6 — sin reconstrucción)

| # | Consumidor | archivo:línea | Forma leída | Veredicto |
|---|-----------|---------------|-------------|-----------|
| 1 | CoherenceValidator | `coherence_validator.py:410-411` (whatsapp top-level), `:581-597` (results + keys) | dict canónico | LEE. Sin reconstrucción |
| 2 | PainLedger.apply_site_verification | `pain_ledger.py:134-145` (vía `v4_asset_orchestrator.py:290-293`) | dict canónico (results con fallback top-level) | LEE. Sin reconstrucción |
| 3 | classify_promised_services / committed_services_from_entries | `proposal_asset_alignment.py:446-480` (`_presence_exists`), consumido en `:506`, `:608` | dict normalizado, plano u objeto | LEE. Sin reconstrucción |
| 4 | publication_gates `_proposal_asset_alignment_gate` | `publication_gates.py:980` (DTO), usado en `:1014`, `:1019`, `:1027`, `:1078` | dict canónico del assessment | LEE. Comentario `:977-979` explícito: "No fake reconstruction, no re-execution". **La ruta del fake-report-from-skipped_assets que documentaba DT4-N2 está retirada** (DT4-R2) |
| 5 | AlignmentResult._presence_resolved | `alignment_result.py:62-76` (acceso top-level), consumido por `compute_unresolved:209` y `_from_entries:251,262` | dict con claves top-level | LEE. Sin reconstrucción |
| 6 | delivery_quality_report G9 | `delivery_quality_report.py:244-246` (vía main.py `site_presence_report=...`) → `AlignmentResult.from_asset_alignment_matrix` | dict canónico | LEE. Mismo helper canónico que el gate (AC3) |

## 3. Rutas que NO leen el snapshot (muertas o re-verificación) — insumo FASE-F

### 3.1 RUTA VIVA de re-verificación (la segunda mitad del oráculo doble, A4)

- **`conditional_generator.py:64` + `:111`** — `self.site_checker = SitePresenceChecker()` y
  `get_full_presence_decision(site_url, hotel_id, asset_type)` **por asset, en tiempo de generación**:
  re-ejecuta scraping + rich-results + `check_asset_delivery_history` (historial de deliveries = un
  tercer criterio). Es la ruta de reconstrucción **viva** que F1 debe unificar con el snapshot
  persistido. (Presencia resuelta dentro de la partición: `classify_promised_services._presence_exists`,
  señalada por las notas de FASE-C.)
- `site_presence_checker.py:176` (`_cache` por URL) y `:651-670` (`check_before_generate`, helper sin
  uso en producción — verificar en F si se retira).

### 3.2 Consumidores muertos tras la normalización DT4-R2 (no reconstruyen: no consumen)

- **`v4_proposal_generator.py:1389-1396`, `:1618-1625`, `:1686-1693`** — los tres `presence_lookup`
  hacen guard `hasattr(site_presence_report, 'results')`, escrito para el **objeto** pre-DT4-R2. Con el
  dict canónico el guard es `False` → `presence_lookup` queda **siempre vacío**: las tablas dinámica /
  calidad / técnica pierden la señal "Verificado en sitio" que sus docstrings prometen. F1 debe decidir:
  pasar a leer `results` del dict o retirar los bloques.
- **`v4_asset_orchestrator.py:240`** — `self.site_checker = SitePresenceChecker()` instanciado y
  **jamás usado** en el archivo (grep `site_checker` = solo la definición). Limpieza candidata de F.

### 3.3 Defecto latente registrado (fuera de alcance de E, no modificado)

- **`main.py:2832` vs `:3177`** — el alias `site_presence_report = site_presence_snapshot` nace dentro
  de `if generate_proposal:`; la llamada del delivery report en `:3177` lo referencia
  incondicionalmente. Si el gate de coherencia bloquea (`generate_proposal=False`) → `NameError`
  capturado por el `except Exception` de la región FASE 0E → el delivery report se degrada en silencio
  con un `[WARN]` (familia del pitfall "NameError silencioso"). E1 lo esquivó usando
  `site_presence_snapshot` (incondicional en `:2490`). **Reparación sugerida: FASE-F** (toca la misma
  región) o FASE-H (quirúrgico).

## 4. Respuesta al requisito E4

- Los **6 consumidores activos** están en §2 con archivo:línea y leen el snapshot propagado — ninguno
  reconstruye. Las 4 rutas de reconstrucción que diagnosticó DT4-N2 quedan hoy en: **1 viva**
  (conditional_generator, §3.1) y **3 muertas/degradadas** (§3.2: tres `presence_lookup` + la
  instanciación sin uso). El fake-report de publication_gates está retirado.
- **FASE-F (F1)** debe: unificar §3.1 con el snapshot persistido por E1 (insumo disco ya disponible),
  decidir el destino de §3.2 y reparar §3.3 si toca esa región.
