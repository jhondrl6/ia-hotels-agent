# Contexto: Delivery ZIP Packaging Roto - FASE-7 Nunca Materializa el Paquete al Cliente

> **Origen**: Validacion de alineacion post-implementacion EVIDENCE-TIER-FALSE-CONFIDENCE-IAO (2026-08-01)
> **Version actual**: v4.67.0 (v4.68.0 pendiente RELEASE)
> **Hotel de referencia**: Zi One Luxury / Zione (https://zione.co/)
> **Severidad**: ALTA - el pipeline genera contenido correcto (gates PASSED, coherence 0.92) pero NUNCA entrega el ZIP al cliente. Integralidad de entrega rota.
> **Fecha del contexto**: 2026-08-01
> **Outputs de referencia**:
>   - `output/v4_complete/deliveries/` - 3 MANIFESTs huerfanos, 1 README, 0 ZIPs
>   - `output/v4_complete/zione/` - 165 archivos (working directory, contenido correcto)
>   - `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260731_164842.md`
>   - `output/v4_complete/02_PROPUESTA_COMERCIAL_20260731_164842.md`
>   - `output/v4_complete/v4_complete_report.json`
> **ESTADO**: Validado EXHAUSTIVAMENTE contra codigo vivo + filesystem (2026-08-01). Bugs 1 y 3 CONFIRMADOS con evidencia dura (bytes exactos). Bug 2 confirmado teoricamente pero NO se manifiesta en Zione (converge). 6 nuevos fallos descubiertos (NF-1 a NF-6). Listo para plan de implementacion.
> **Validacion**: Auditoria de 2da opinion con mediciones filesystem, analisis de codigo completo (833 lineas), y verificacion de tests (1071+286 lineas).

---

## 1. RESUMEN EJECUTIVO

El pipeline `v4complete` ejecuta 10 fases correctamente (audit -> assets -> gates -> documentos) pero **falla silenciosamente en FASE 7 (Delivery Packaging)**. El resultado:

- OK Diagnostico generado y coherente (Tier B+, gates PASSED)
- OK Propuesta comercial generada y alineada
- OK 10 assets generados con confidence >= 0.7
- OK Todos los publication gates PASSED
- OK MANIFEST con quality_metadata enriquecido (NP6)
- FAIL **ZIP de entrega NUNCA se materializa**
- FAIL **MANIFESTs se acumulan como artefactos huerfanos**
- FAIL **README referencia un ZIP inexistente**

**Impacto comercial**: No se puede entregar el paquete al cliente. El contenido existe pero no hay mecanismo de entrega funcional.

---

## 2. ARQUITECTURA DEL DELIVERY PIPELINE

### Flujo esperado (segun codigo)

```
main.py FASE 7 (L3020-3077)
  +-- DeliveryPackager.package()
        |-- _collect_files(source_dir=zione/)     -> lista de {source, dest}
        |-- create_readme() [Pass 1]              -> README con placeholders
        |-- create_manifest() [Pass 2]            -> MANIFEST midiendo archivos en disco
        |-- Enrich quality_metadata [NP6]         -> evidence_tier, precision_tier, etc.
        |-- Write MANIFEST to disk                -> zione_YYYYMMDD_MANIFEST.json
        |-- Self-reference correction [Pass 3]    -> agrega entrada MANIFEST.json al MANIFEST
        |-- README placeholder fixup [P-01]       -> reemplaza {{TOTAL_FILES}}, {{TOTAL_SIZE}}
        |-- _create_zip()                         -> ZIP con todos los archivos
        |-- _validate_zip()                       -> validacion EXACTA ZIP <-> MANIFEST
        |     |-- Si PASS -> unlink MANIFEST -> return zip_path
        |     +-- Si FAIL -> unlink ZIP -> raise DeliveryValidationError
        +-- main.py catch -> print("[WARN]") -> delivery_zip_path = None
```

### Directorios involucrados

| Directorio | Rol | Creado por |
|-----------|-----|-----------|
| `output/v4_complete/zione/` | Working directory - assets generados por V4AssetOrchestrator | `v4_asset_orchestrator.py:_prepare_output_directory()` |
| `output/v4_complete/deliveries/` | Delivery output - ZIP + metadata para cliente | `delivery_packager.py:__init__()` |
| `output/v4_complete/` (root) | Documentos principales (DIAGNOSTICO, PROPUESTA) | `v4_diagnostic_generator.py`, `v4_proposal_generator.py` |

### Relacion de contenido (diseno)

El ZIP deberia contener:
```
zione_YYYYMMDD.zip
|-- DIAGNOSTICO.md              <- copiado desde root/01_DIAGNOSTICO_*.md
|-- PROPUESTA_COMERCIAL.md      <- copiado desde root/02_PROPUESTA_*.md
|-- ASSETS/                     <- TODO zione/ reestructurado
|   |-- analytics_setup_guide/
|   |-- faq_page/
|   |-- geo_enriched/
|   |-- hotel_schema/
|   |-- llms_txt/
|   |-- monthly_report/
|   |-- og_tags_guide/
|   |-- open_graph/
|   |-- optimization_guide/
|   |-- v4_audit/
|   +-- whatsapp_conflict_guide/
|-- MANIFEST.json               <- metadata + quality_metadata
+-- README_DELIVERY.md          <- instrucciones de implementacion
```

---

## 3. EVIDENCIA DEL FALLO

### 3.1 Estado actual del filesystem

```
output/v4_complete/deliveries/
|-- README_DELIVERY.md                    <- 168 lineas, referencia "zione_20260731.zip"
|-- zione_20260728_MANIFEST.json          <- 615 lineas (ejecucion 1)
|-- zione_20260730_MANIFEST.json          <- 735 lineas (ejecucion 2)
+-- zione_20260731_MANIFEST.json          <- 864 lineas (ejecucion 3)
                                           <- 0 ZIPs (todos eliminados por validacion)
```

**Los 3 MANIFESTs persisten** porque el codigo solo los limpia en el camino feliz (L248-249). Cuando `_validate_zip()` falla, se lanza excepcion ANTES del `unlink`.

### 3.2 El README confirma que el proceso avanza hasta Pass 3

```markdown
**Package file:** zione_20260731.zip      <- ZIP que NO existe
**Contents:** 169 files (435.5 KB)        <- Placeholders SI fueron reemplazados (P-01 ejecutado)
```

Esto prueba que el proceso llega hasta `_create_zip()` (L235) y luego falla en `_validate_zip()` (L238).

### 3.3 quality_metadata correcta en MANIFEST (NP6 funciona)

```json
"quality_metadata": {
    "evidence_tier": "B+",
    "precision_tier": "C",
    "ga4_configured": false,
    "gsc_configured": false,
    "onboarding_used": true,
    "coherence_score": 0.9633333333333333,
    "contradictions_detected": []
}
```

### 3.4 Evidencia dura de tamanos (validacion 2026-08-01)

| Medicion | Fuente | Valor |
|----------|--------|-------|
| README declarado en MANIFEST (L844) | `zione_20260731_MANIFEST.json` | **5795 bytes** |
| README real en disco (post P-01) | `Get-Item` filesystem | **5777 bytes** |
| Delta README | | **-18 bytes** (causa del MISMATCH) |
| MANIFEST auto-referencia (L849) | `zione_20260731_MANIFEST.json` | **24983 bytes** |
| MANIFEST real en disco | `Get-Item` filesystem | **24983 bytes** |
| Delta MANIFEST | | **0 bytes** (converge, Bug 2 NO activo) |
| total_files declarado | MANIFEST L853 | **169** |
| Archivos en zione/ | `Get-ChildItem -Recurse` | **165** (+ DIAGNOSTICO + PROPUESTA + README + MANIFEST = 169) |
| total_size_bytes declarado | MANIFEST L854 | **445966** |

---

## 4. ANALISIS DE CAUSA RAIZ

### Bug 1 (PRIMARIO - ACTIVO): README cambia de tamano DESPUES de que el MANIFEST lo mide

**Secuencia temporal**:

| Paso | Accion | Tamano README |
|------|--------|---------------|
| Pass 1 (L177) | `create_readme()` escribe README con `{{TOTAL_FILES}}` y `{{TOTAL_SIZE}}` | S1 (con placeholders) |
| Pass 2 (L181) | `create_manifest()` mide README en disco -> registra S1 | S1 = **5795** |
| P-01 (L221-227) | Reemplaza `{{TOTAL_FILES}}` -> `169`, `{{TOTAL_SIZE}}` -> `435.5 KB` | **S2 = 5777 != S1** |
| ZIP (L235) | `_create_zip()` lee README del disco -> incluye archivo de tamano S2 | S2 = 5777 |
| Validacion (L358) | Compara: ZIP tiene S2=5777, MANIFEST dice S1=5795 | **MISMATCH -> FAIL** |

**Codigo problematico** (`delivery_packager.py:221-227`):
```python
# P-01: Post-process README with final manifest totals
readme_fixup_path = self.deliveries_dir / "README_DELIVERY.md"
if readme_fixup_path.exists():
    readme_content = readme_fixup_path.read_text(encoding='utf-8')
    readme_content = readme_content.replace("{{TOTAL_FILES}}", str(manifest["total_files"]))
    readme_content = readme_content.replace("{{TOTAL_SIZE}}",
                                            self._format_bytes(manifest["total_size_bytes"]))
    readme_fixup_path.write_text(readme_content, encoding='utf-8')
    # <- NUNCA actualiza manifest["files"]["README_DELIVERY.md"]["size_bytes"]
```

**Impacto** (MEDIDO EXACTAMENTE):
- `{{TOTAL_FILES}}` (15 chars) -> `169` (3 chars) = **-12 bytes**
- `{{TOTAL_SIZE}}` (14 chars) -> `435.5 KB` (8 chars) = **-6 bytes**
- Total: **-18 bytes** (verificado: MANIFEST declara 5795, disco real = 5777)

**Condicion de activacion**: SOLO se manifiesta cuando `DeliveryContext` esta disponible (modo FASE-C, hotel con `v4_audit/asset_generation_report.json`). En modo legacy (sin reporte), L522-523 reemplaza placeholders por "N/A" y P-01 es un no-op.

### Bug 2 (SECUNDARIO - LATENTE): Self-reference del MANIFEST es inherentemente inestable

**Secuencia** (`delivery_packager.py:190-214`):

```python
# Pass 3: mide MANIFEST antes de auto-referencia
manifest_size_before = manifest_path.stat().st_size          # S1
manifest["total_size_bytes"] += manifest_size_before
manifest["files"].append({"name": "MANIFEST.json", "size_bytes": manifest_size_before, ...})
manifest["total_files"] = len(manifest["files"])
json.dump(manifest, ...)                                     # escribe -> tamano S2 > S1

# "Correccion"
manifest_size_after = manifest_path.stat().st_size           # S2
delta = manifest_size_after - manifest_size_before           # S2 - S1
manifest["total_size_bytes"] += delta
manifest["files"]["MANIFEST.json"]["size_bytes"] = manifest_size_after  # = S2
json.dump(manifest, ...)                                     # escribe -> tamano S3
```

**Problema**: Al escribir S2 como `size_bytes` y `delta` como digitos adicionales en `total_size_bytes`, el archivo crece a S3. Pero el MANIFEST dice que su propio tamano es S2. El ZIP incluye el archivo de tamano S3.

**Validacion**: `z.read("MANIFEST.json")` -> S3. `manifest_sizes["MANIFEST.json"]` -> S2. **MISMATCH**.

**RESULTADO DE VALIDACION (2026-08-01)**: Bug confirmado teoricamente pero **NO se manifiesta en Zione**:
```
MANIFEST L849: "size_bytes": 24983   <- auto-referencia declarada
Get-Item MANIFEST.json:     24983   <- tamano real en disco
Delta: 0 bytes — LA CORRECCION CONVERGE (S3 == S2)
```
**Razon**: Los valores no cambian de longitud de digitos (24880->24983 = 5 digitos ambos, 445863->445966 = 6 digitos ambos). El bug es LATENTE: se activaria si el delta cruza un limite de digitos (ej: 999950 -> 1000050).

### Bug 3 (AMPLIFICADOR): Tests usan tolerancia 5%, produccion exige exactitud

**Test** (`test_delivery_contract.py:428`):
```python
assert abs(manifest["total_size_bytes"] - actual_total) <= actual_total * 0.05
```

**Produccion** (`delivery_packager.py:358`):
```python
if actual_size != declared_size:  # EXACT match, 0 tolerancia
    errors.append(f"Size mismatch for '{name}': manifest={declared_size}, actual={actual_size}")
```

Los tests pasan porque usan 5% de margen. La validacion de produccion falla porque exige match exacto por archivo.

**Hallazgo adicional (2026-08-01)**: Los tests NO tienen NINGUNA comparacion de tamano por archivo. Solo comparan el total con 5% de margen (L428). La validacion de produccion exige match exacto POR ARCHIVO (L355-361). Ademas, el fixture de tests nunca ejercita el modo FASE-C (ver NF-1).

---

## 4b. CAUSA RAIZ PROFUNDA (validacion 2026-08-01)

```
+-------------------------------------------------------------------+
|  CAUSA RAIZ ARQUITECTONICA                                         |
|                                                                     |
|  Diseno "measure-then-mutate-then-validate" en 3-pass              |
|  que viola el principio de inmutabilidad entre medicion y          |
|  empaquetado.                                                       |
|                                                                     |
|  Pass 2 mide -> P-01 muta -> ZIP empaqueta -> Validacion compara   |
|       ^              ^                                             |
|  (snapshot)    (invalida snapshot)                                  |
+-------------------------------------------------------------------+
         |
         +-- Bug 1: README mutado post-medicion (ACTIVO)
         +-- Bug 2: MANIFEST self-reference circular (LATENTE)
         +-- NF-1: Tests no cubren path FASE-C (GAP CRITICO)
         +-- NF-2: Fallback silencioso oculta divergencia (SILENCIADOR)
```

**La causa raíz NO es un bug de tamano** — es un **defecto de ordering arquitectonico**: el sistema modifica archivos DESPUES de que sus tamanos fueron registrados como compromisos contractuales en el MANIFEST.

---

## 4c. NUEVOS FALLOS DESCUBIERTOS (validacion 2026-08-01)

### NF-1 (CRITICO): Cobertura de tests CERO para el path de produccion FASE-C

**Evidencia**: El fixture `sample_hotel_output` en `test_delivery_contract.py:54-69` y `test_delivery_packager.py:40-57` crea 5 archivos pero **NO** crea `v4_audit/asset_generation_report.json`.

**Consecuencia**: `delivery_context` siempre es `None` en tests -> modo legacy -> placeholders se reemplazan por "N/A" (L522-523) -> P-01 es inofensivo -> Bug 1 NUNCA se reproduce. El 100% de la suite de delivery tests ejercita un path que NO es el de produccion.

**Verificado**: Zione SI tiene `v4_audit/asset_generation_report.json` (268 lineas) -> DeliveryContext se carga -> modo FASE-C -> Bug 1 activo.

### NF-2 (ALTO): Fallback silencioso a modo legacy — `except Exception: pass`

**Codigo** (`delivery_packager.py:161-162`):
```python
except Exception:
    pass  # Legacy mode: no DeliveryContext available
```

Si `DeliveryContext.from_asset_generation_report()` falla (JSON corrupto, schema change, IOError), el sistema cae silenciosamente a modo legacy sin logging. Esto crea una **divergencia comportamental invisible**: el mismo hotel puede producir ZIP valido o invalido dependiendo de si el contexto carga o no.

**Relacion con leccion NP5** del plan EVIDENCE-TIER: "el `getattr` con default False ocultaba el bug". Mismo patron: fallback silencioso que enmascara comportamiento divergente.

### NF-3 (ALTO): Catch silencioso en main.py — fallo de entrega es WARN, no BLOCKING

**Codigo** (`main.py:3075-3077`):
```python
except Exception as e:
    print(f"   [WARN] Delivery packaging failed: {e}")
    delivery_zip_path = None
```

El pipeline completo (10 fases, ~120s de ejecucion) termina "exitosamente" aunque la entrega al cliente FALLE. El operador ve `[WARN]` entre cientos de lineas de output. No hay mecanismo de escalado, retry, ni bloqueo.

### NF-4 (MEDIO): Sin cleanup de artefactos en camino de error

Cuando `_validate_zip()` falla (L239-245):
- Se elimina el ZIP invalido (L244) OK
- **NO** se elimina el MANIFEST huerfano
- **NO** se elimina README_DELIVERY.md (que referencia un ZIP inexistente)
- **NO** se elimina IMPLEMENTATION_ORDER.md

**Resultado**: `deliveries/` acumula basura entre ejecuciones. Confirmado: 3 MANIFESTs huerfanos + 1 README con referencia rota.

### NF-5 (BAJO): Doble llamada a `datetime.now()` — divergencia potencial

- L144: `date_str = datetime.now().strftime("%Y%m%d")` -> usado para MANIFEST filename
- L319: `_make_zip_filename()` llama `datetime.now()` independientemente -> usado para ZIP filename

Si la ejecucion cruza medianoche entre L144 y L145: MANIFEST dice `20260801`, ZIP dice `20260802`. Edge case menor pero viola el principio de computar el filename UNA sola vez (que FASE-B T3 intento resolver).

### NF-6 (BAJO): FASE-5 (IMPLEMENTATION_ORDER.md) — feature muerto en integracion

`main.py:3066-3071` nunca pasa `hotel_name`, `geo_score`, `core_assets`, `geo_assets` a `packager.package()`. La condicion en L129 (`if HAS_ASSET_CONTRACT and (core_assets or geo_assets)`) nunca se cumple. El feature FASE-5 esta implementado pero nunca se activa desde el caller principal.

---

## 5. ARCHIVOS Y LINEAS RELEVANTES

| Archivo | Lineas | Rol |
|---------|--------|-----|
| `modules/delivery/delivery_packager.py` | 58-251 | `DeliveryPackager.package()` - flujo principal |
| `modules/delivery/delivery_packager.py` | 175-227 | Pass 1-3 + P-01 (README fixup) - **zona del bug** |
| `modules/delivery/delivery_packager.py` | 190-214 | Self-reference correction - **bug secundario** |
| `modules/delivery/delivery_packager.py` | 161-162 | `except Exception: pass` - **NF-2 fallback silencioso** |
| `modules/delivery/delivery_packager.py` | 303-310 | `_create_zip()` - lee archivos del disco |
| `modules/delivery/delivery_packager.py` | 314-320 | `_make_zip_filename()` - **NF-5 doble datetime** |
| `modules/delivery/delivery_packager.py` | 322-379 | `_validate_zip()` - validacion EXACTA |
| `modules/delivery/delivery_packager.py` | 381-413 | `create_manifest()` - mide archivos en disco |
| `modules/delivery/delivery_packager.py` | 439-536 | `create_readme()` - genera con placeholders (FASE-C) o "N/A" (legacy) |
| `modules/delivery/delivery_context.py` | 1-535 | DeliveryContext - determina modo FASE-C vs legacy |
| `main.py` | 3020-3077 | FASE 7 caller - catch silencioso (NF-3) |
| `main.py` | 3044-3057 | quality_metadata injection (NP6) |
| `main.py` | 3066-3071 | package() call - **NF-6 sin params FASE-5** |
| `templates/delivery_readme_template.md` | 13 | `{{TOTAL_FILES}} files ({{TOTAL_SIZE}})` - placeholder que causa Bug 1 |
| `tests/delivery/test_delivery_packager.py` | 40-57 | Fixture sin `asset_generation_report.json` (NF-1) |
| `tests/delivery/test_delivery_contract.py` | 54-69 | Fixture sin `asset_generation_report.json` (NF-1) |
| `tests/delivery/test_delivery_contract.py` | 413-429 | Test de tamano con 5% tolerancia (Bug 3) |
| `tests/delivery/test_delivery_contract.py` | 620-671 | Tests P-01 (README placeholders) |

---

## 6. CONDICIONES DE REPRODUCCION

El bug se manifiesta cuando:

1. **DeliveryContext disponible** (CRITICO): `v4_audit/asset_generation_report.json` existe en el directorio del hotel -> modo FASE-C -> README conserva placeholders `{{TOTAL_FILES}}`/`{{TOTAL_SIZE}}`
2. **P-01 cambia longitud**: El reemplazo de placeholders produce un archivo de tamano diferente al medido en Pass 2 (siempre ocurre: 15+14=29 chars placeholders vs digitos reales menores)
3. **Validacion exacta**: `_validate_zip()` no tiene tolerancia (correcto en intencion)

**Con el hotel Zione (169 archivos, 445KB)**: el bug se reproduce en el 100% de las ejecuciones (3/3 confirmadas).

**Con tests unitarios (5 archivos, <1KB)**: el bug **NUNCA** se reproduce porque:
- El fixture NO crea `asset_generation_report.json` -> modo legacy
- En modo legacy, L522-523 reemplaza placeholders por "N/A" -> P-01 es no-op
- El README no cambia de tamano -> validacion pasa

**Condicion para Bug 2 (latente)**: Solo se manifestaria si el total_size_bytes o size_bytes del MANIFEST cruzan un limite de digitos (ej: 99999 -> 100000). Con Zione (445966, 24983) no ocurre.

---

## 7. HIPOTESIS DE FIX (para evaluacion en plan)

### Opcion A: Medir DESPUES de modificar (reordenar P-01)

Mover el fixup P-01 ANTES de `create_manifest()`:
1. Pass 1: create_readme() con placeholders
2. **P-01 anticipado**: calcular totals preliminares, reemplazar placeholders
3. Pass 2: create_manifest() mide README ya finalizado
4. Pass 3: self-reference

**Riesgo**: P-01 necesita `manifest["total_files"]` y `manifest["total_size_bytes"]` que no existen aun en Pass 1. Requiere calculo preliminar.

### Opcion B: Actualizar MANIFEST despues de P-01

Despues del fixup P-01 (L227), re-medir el README y actualizar el MANIFEST:
```python
# Despues de P-01 fixup:
new_readme_size = readme_fixup_path.stat().st_size
for entry in manifest["files"]:
    if entry["name"] == "README_DELIVERY.md":
        old_size = entry["size_bytes"]
        entry["size_bytes"] = new_readme_size
        manifest["total_size_bytes"] += (new_readme_size - old_size)
        break
# Re-escribir MANIFEST con tamano corregido
```

**Riesgo**: Re-escribir MANIFEST cambia SU propio tamano (Bug 2 persiste).

### Opcion C: Calcular MANIFEST en memoria, escribir UNA sola vez al final (RECOMENDADA)

1. Collect files -> calcular tamanos en memoria
2. Calcular totals preliminares (sin README ni MANIFEST)
3. Generar README FINAL en memoria (con totals calculados, sin placeholders)
4. Medir README final (bytes exactos)
5. Recalcular totals incluyendo README
6. Construir MANIFEST completo en memoria (incluyendo self-reference por iteracion fija)
7. Escribir MANIFEST una sola vez
8. Verificar que MANIFEST en disco == MANIFEST en memoria (assert)
9. Crear ZIP desde archivos en disco (todos ya finales)
10. Validar ZIP <-> MANIFEST (exact match, 0 tolerancia)

**Resolucion de self-reference** (paso 6): Iteracion fija de 2-3 ciclos:
- Ciclo 1: estimar tamano del MANIFEST (N entradas x ~85 bytes/entrada + overhead)
- Ciclo 2: serializar con estimacion, medir, si difiere -> ajustar y re-serializar
- Convergencia garantizada en <=3 iteraciones (los digitos se estabilizan)

**Ventaja**: Elimina la inestabilidad de multi-pass. Ningun archivo se modifica despues de ser medido.
**Principio**: Inmutabilidad entre medicion y empaquetado.

### Opcion D: Tolerancia en validacion (fix minimo)

Cambiar `_validate_zip()` para aceptar +/-1% de tolerancia por archivo:
```python
if abs(actual_size - declared_size) > max(1, declared_size * 0.01):
    errors.append(...)
```

**Ventaja**: Fix minimo, 1 linea.
**Riesgo**: Enmascara el problema real. El MANIFEST entregado al cliente tiene tamanos incorrectos.

### Recomendacion (actualizada 2026-08-01)

**Opcion C** (rewrite arquitectonico single-write con iteracion fija) es la solucion correcta. Ataca la causa raíz (ordering) y elimina tanto Bug 1 como Bug 2 permanentemente. **Opcion D** como hotfix inmediato SOLO si se necesita desbloquear entregas antes del fix arquitectonico.

---

## 8. DEPENDENCIAS Y CONSUMERS DOWNSTREAM

| Consumer | Como usa el ZIP/MANIFEST | Impacto del bug |
|----------|--------------------------|-----------------|
| `hook_pdf_generator.py` (L622-628) | Genera PDFs en `deliveries/` | No afectado (usa deliveries/ como dir, no depende del ZIP) |
| `delivery_context.py` | DeliveryContext.from_asset_generation_report() | No afectado (se ejecuta antes del ZIP) |
| `test_delivery_packager.py` | Tests de integracion | Pasan (modo legacy, NF-1) |
| `test_delivery_contract.py` | Tests de contrato con 5% tolerancia | Pasan (tolerancia + modo legacy enmascaran bug) |
| **Cliente final** | Recibe ZIP con documentos + assets | **BLOQUEADO** - no hay ZIP |
| `README_DELIVERY.md` | Instrucciones de implementacion | Referencia ZIP inexistente |

---

## 9. ARTEFACTOS HUERFANOS (cleanup pendiente)

| Artefacto | Path | Accion sugerida |
|-----------|------|-----------------|
| MANIFEST 20260728 | `deliveries/zione_20260728_MANIFEST.json` | Eliminar (obsoleto) |
| MANIFEST 20260730 | `deliveries/zione_20260730_MANIFEST.json` | Eliminar (obsoleto) |
| MANIFEST 20260731 | `deliveries/zione_20260731_MANIFEST.json` | Eliminar (huerfano de ZIP fallido) |
| README_DELIVERY.md | `deliveries/README_DELIVERY.md` | Regenerar tras fix |

---

## 10. CRITERIOS DE ACEPTACION DEL FIX

1. **ZIP se materializa**: `v4complete` para Zione produce `deliveries/zione_YYYYMMDD.zip` exitosamente
2. **Validacion exacta pasa**: `_validate_zip()` retorna `[]` (0 errores) sin necesidad de tolerancia
3. **MANIFEST limpio**: No persisten MANIFESTs huerfanos en `deliveries/` tras ejecucion exitosa
4. **README coherente**: `README_DELIVERY.md` dentro del ZIP referencia el ZIP correcto y tiene tamanos reales
5. **quality_metadata presente**: MANIFEST dentro del ZIP contiene `quality_metadata.evidence_tier = "B+"`
6. **Tests actualizados**: `test_delivery_contract.py` valida con exactitud (sin 5% tolerancia que enmascara)
7. **No regresion**: Los 22 tests de `test_evidence_tier.py` + 549 tests existentes siguen pasando
8. **Control de caso**: Ejecucion con hotel sin onboarding (control) tambien produce ZIP valido
9. **Test FASE-C (NF-1)**: Nuevo test con `asset_generation_report.json` en fixture que ejercita modo DeliveryContext (path de produccion)
10. **Test legacy**: Test sin `asset_generation_report.json` que verifica modo legacy (no regresion)
11. **Logging de fallback (NF-2)**: `except Exception: pass` reemplazado por `logger.warning()` con flag visible
12. **Cleanup en error (NF-4)**: Camino de error limpia MANIFEST y README (no solo ZIP)
13. **Verificacion end-to-end**: `v4complete` real con Zione produce ZIP valido (no solo tests unitarios)

---

## 11. RELACION CON PLANES ANTERIORES

| Plan | Relacion |
|------|----------|
| EVIDENCE-TIER-FALSE-CONFIDENCE-IAO (2026-07-31) | NP6 corrigio quality_metadata en MANIFEST. El enrichment funciona. El bug es AGNOSTICO al contenido - es un bug de timing/size en el empaquetado. |
| DT-2-DELIVERY-CONTRACT-RESIDUAL | Introdujo P-01 (README placeholder fixup) y los tests de contrato. El fix P-01 es la CAUSA del Bug 1. |
| FASE-7-DELIVERY-V2 | Introdujo el 3-pass manifest (FASE-B). La auto-referencia es la CAUSA del Bug 2. |
| FASE-D T4 | Introdujo `_validate_zip()` con validacion exacta. Correcto en intencion, pero expone los bugs 1 y 2. |

---

## 12. NOTAS PARA EL PLAN

- El bug es de **timing de I/O**: se mide un archivo, se modifica, y luego se valida contra la medicion original.
- La solucion debe garantizar que **todo archivo en el ZIP tenga exactamente el tamano declarado en el MANIFEST**.
- La auto-referencia del MANIFEST es un problema circular clasico. Soluciones: (a) padding fijo, (b) iterar hasta convergencia, (c) excluir MANIFEST de su propia validacion de tamano, (d) calcular tamano en memoria antes de escribir.
- El catch silencioso en `main.py:3075` (`[WARN]`) debe evaluarse: deberia ser BLOCKING? El contenido esta listo pero la entrega falla.
- Los MANIFESTs con fecha en el nombre (`zione_YYYYMMDD_MANIFEST.json`) se acumulan porque el cleanup solo ocurre en el camino feliz. Considerar cleanup de MANIFESTs anteriores al inicio de cada ejecucion.
- El ZIP filename usa `datetime.now()` en `_make_zip_filename()` pero el MANIFEST filename usa `date_str` calculado en L144. Si la ejecucion cruza medianoche, podrian divergir (edge case menor).

---

## 13. LECCIONES APRENDIDAS APLICABLES (de EVIDENCE-TIER 09-analisis-post-implementacion)

| Leccion del plan anterior | Aplicacion a este fix |
|---------------------------|----------------------|
| **§5 "grep exhaustivo de consumers"** | Antes de modificar el flujo de README/MANIFEST, grep TODOS los consumers de `_validate_zip`, `create_readme`, `create_manifest` (incluyendo tests) |
| **§5 "T0/T0b como pre-requisito"** | Limpiar tests existentes PRIMERO (eliminar tolerancia 5%, agregar fixture FASE-C) antes de implementar el fix |
| **§5 "NP8: control de caso default"** | Incluir test con hotel SIN `asset_generation_report.json` (legacy) Y con el (FASE-C) para cubrir ambos paths |
| **§Auditoria "NP5: fallback silencioso getattr"** | El `except Exception: pass` en L161-162 es el equivalente exacto: silenciar el fallback enmascara la divergencia |
| **§4 "Verificar integracion completa"** | El fix debe verificarse con `v4complete` real (Zione), no solo tests unitarios. Los tests pasaron pero la produccion fallo |
| **§5 "NP1/NP2: consumers downstream"** | Verificar que el fix no rompe `hook_pdf_generator.py`, `delivery_quality_report.py`, ni los 10 test classes de contract tests |

---

## 14. RECOMENDACIONES COMPLEMENTARIAS (mas alla del fix de packaging)

| # | Accion | Ataca | Prioridad |
|---|--------|-------|-----------|
| R1 | Test de integracion con `asset_generation_report.json` en fixture (modo FASE-C) | NF-1 | CRITICA |
| R2 | Reemplazar `except Exception: pass` con `logger.warning()` + flag `legacy_mode=True` | NF-2 | ALTA |
| R3 | Evaluar elevar severidad en main.py: `[WARN]` -> `[ERROR]` + exit code != 0 (o retry) | NF-3 | ALTA |
| R4 | Cleanup de MANIFESTs anteriores al inicio + cleanup de artefactos en camino de error | NF-4 | MEDIA |
| R5 | Unificar datetime: pasar `date_str` a `_make_zip_filename(hotel_id, date_str)` | NF-5 | BAJA |
| R6 | Eliminar tolerancia 5% en test_delivery_contract.py L428 -> assert exacto | Bug 3 | ALTA |
| R7 | Agregar test de tamano por archivo (no solo total) en contract tests | Bug 3 | ALTA |
| R8 | Conectar params FASE-5 desde main.py (hotel_name, geo_score, core_assets, geo_assets) | NF-6 | BAJA |

---

## 15. MATRIZ DE CONFIRMACION (validacion 2026-08-01)

| Hallazgo del Contexto original | Veredicto | Evidencia |
|-------------------------------|-----------|-----------|
| Bug 1: README post-medicion | **CONFIRMADO (ACTIVO)** | 5795 declarado vs 5777 real = -18 bytes |
| Bug 2: Self-reference inestable | **CONFIRMADO (LATENTE)** | En Zione converge (24983=24983), mecanismo fragil |
| Bug 3: Tolerancia tests vs produccion | **CONFIRMADO** | L428: 5% vs L358: exact, sin test por archivo |
| 3 MANIFESTs huerfanos | **CONFIRMADO** | Glob: 3 archivos, 0 ZIPs |
| README referencia ZIP inexistente | **CONFIRMADO** | L5: "zione_20260731.zip" no existe |
| 165 archivos en zione/ | **CONFIRMADO** | Get-ChildItem: 165 |
| quality_metadata NP6 funciona | **CONFIRMADO** | MANIFEST L856: evidence_tier "B+" |
| Catch silencioso main.py | **CONFIRMADO** | L3075-3077: `[WARN]` + None |
| Reproduccion 100% con Zione | **CONFIRMADO** | 3/3 MANIFESTs huerfanos = 3 fallos |
| "S3 > S2 siempre" (Bug 2) | **REFUTADO para Zione** | S3 == S2 (converge). Solo se activa con cambio de digitos |
| **Nuevos: NF-1 a NF-6** | **DESCUBIERTOS** | Ver seccion 4c |
