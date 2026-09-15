PREVENCIÓN — redacción de secretos en la captura (causa raíz F-P4.5)
==================================================================
Fecha: 2026-09-15
FASE: P5 (post-cierre, autorización explícita del operador: "Ejecuta 1.
parche de prevención")
Origina: auditoría de superficie — archives/gbp_profiles.json publicó una
key real porque `modules/scrapers/gbp_auditor.py::_save_cache` guardaba el
perfil scrapeado EN CRUDO. La detección (AC-S2) ya bloqueaba el commit,
pero la captura seguía ensuciando disco.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMBIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- `modules/scrapers/gbp_auditor.py`:
  * Nuevos helpers de módulo `_SECRET_VALUE_PATTERNS` (los 4 patrones de
    valor del checker AC-S2: AIzaSy…, sk-, ghp_, pplx-),
    `_redact_secret_values` y `_redact_secrets_tree` (dict/list anidados).
  * `_save_cache` redacta ANTES de escribir. El cache en memoria guarda la
    versión redactada, así que reescrituras posteriores no resucitan el
    valor. Aviso `logger.warning` cuando la redacción dispara, sin imprimir
    el valor.
  * El diccionario del caller NO se muta: la cura es el disco, no la
    sesión en curso.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAR NR7 (tests/scrapers/test_gbp_cache_secret_redaction.py — 14 tests)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- ROJO controlado: con `_SECRET_VALUE_PATTERNS = []` (monkeypatch) el valor
  sintético LLEGA al disco → prueba que contiene el guard, no el azar.
- VERDE espejo: mismo input con el guard activo → no hay fuga.
- Extras: los 4 patrones redactados; texto limpio inalterado (sin warning);
  warning sin valor del secreto; reescritura no resucita; árbol anidado.
- Claves 100 % sintéticas, construidas por concatenación para no activar
  el propio checker al stagear el test.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEDICIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- `pytest tests/scrapers tests/test_p5_ac_s2_remediacion.py`: 58 passed,
  4 skipped (skips preexistentes), 0 fallos.
- `run_all_validations.py --quick`: 10/10 (Secrets SIN_HALLAZGOS sobre
  1282 tracked + staged; Client Material SIN_HALLAZGOS).
- 14 funciones test nuevas (conteo canónico se actualiza en RELEASE, S-V2.1).

RESTRICCIONES INTACTAS: ninguna acción externa ejecutada; no se tocó
archives/gbp_profiles.json (retirada desde HEAD sigue siendo higiene
opcional, decisión pendiente del operador); no se weakenearon gates.
