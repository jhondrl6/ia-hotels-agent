# T3 — Greps Residuales

> Fecha: 2026-09-15
> Modo: DIRECTO, comandos literales con salida

## Grep 1: GATE_ENFORCEMENT_ENABLED en código de producción

**Comando:**
```bash
grep -rn "GATE_ENFORCEMENT_ENABLED" modules/ main.py --include="*.py"
```

**Salida:**
```
(sin coincidencias)
```

**Dictamen:** **coherente** — Los documentos del plan mencionan `GATE_ENFORCEMENT_ENABLED` pero el código solo tiene `GATE_BLOCKING_ENABLED`. Esto confirma CON-1: la documentación está desactualizada, no el código.

---

## Grep 2: blocks_publish en acta JSON

**Comando:**
```bash
grep -n "blocks_publish" output/v4_complete/hoteldonalfonso/v4_audit/actaRevision.json
```

**Salida:**
```
(sin coincidencias)
```

**Dictamen:** **coherente** — `blocks_publish` es campo del DTO `TribunalOutcome` (outcome.py L153), no se serializa en el acta JSON. El acta usa `enforcement.blocking_env` y `verdict` para comunicar el bloqueo.

---

## Grep 3: ASSETS/ literal en delivery_packager

**Comando:**
```bash
grep -n "ASSETS/" modules/delivery/delivery_packager.py
```

**Salida:**
```
430:    ASSETS/
```

**Dictamen:** **coherente** — El literal canónico existe en `delivery_packager.py`. También existe en `asset_responsibility_contract.py` (fuente complementaria, no sustituta).

---

## Grep 4: test_ac_g4_g5_multi_hotel_matrix.py → DeliveryPackager

**Comando:**
```bash
grep -n "DeliveryPackager" tests/quality_gates/tribunal/test_ac_g4_g5_multi_hotel_matrix.py
```

**Salida:**
```
(sin coincidencias)
```

**Dictamen:** **coherente** — El test multi-hotel es complementario (prueba matriz de perfiles), no sustituto del test de delivery_packager. Ambos coexisten sin solapamiento.

---

## Grep 5: _save_cache en google_places_client.py

**Comando:**
```bash
grep -n "_save_cache\|json.dump" modules/scrapers/google_places_client.py
```

**Salida:**
```
132:    def _save_cache(self) -> None:
136:            json.dump(self._cache, f)
```

**Dictamen:** **incoherente** — `_save_cache` persiste caché sin redacción de secretos. Contrasta con `gbp_auditor.py:_save_cache` (L147-149) que sí llama `_redact_secrets_tree()`. Hallazgo residual va a T4 triaje.

---

## Grep 6: client_material_policy.yaml existe

**Comando:**
```bash
ls -la config/client_material_policy.yaml
```

**Salida:**
```
-rw-r--r-- 1 Jhond 197609 2345 Sep 11 12:00 config/client_material_policy.yaml
```

**Dictamen:** **coherente** — Archivo de política centralizada existe. AC-G2 (material de cliente) tiene fuente canónica de reglas.

---

## Resumen

| # | Grep | Coincidencias | Dictamen |
|---|------|---------------|----------|
| 1 | GATE_ENFORCEMENT_ENABLED | 0 | coherente (doc desactualizada) |
| 2 | blocks_publish en acta | 0 | coherente (es campo DTO, no JSON) |
| 3 | ASSETS/ en delivery_packager | 1 | coherente |
| 4 | DeliveryPackager en test multi-hotel | 0 | coherente (complementario) |
| 5 | _save_cache en google_places_client | 2 | **incoherente** (sin redacción) |
| 6 | client_material_policy.yaml | existe | coherente |

**5/6 coherentes, 1/6 incoherente** (hallazgo residual en Grep 5).
