# FASE-P1-D — T1: Mapa del flujo "Verdad del Sitio Vivo" (estado actual)

Fecha: 2026-08-21 | Verificado contra código vivo (grep + lectura de módulos)

## Productores

| Productor | Qué produce | Archivo |
|-----------|-------------|---------|
| `V4ComprehensiveAuditor._run_cross_validation` | `phone_web` (schema telephone o PRIMER `tel:`), `wa_me_number` (PRIMER `wa.me`), `phone_gbp` | `modules/auditors/v4_comprehensive.py` L1538-1615 |
| `_extract_wa_me_number` / `_extract_phone_from_html` | Solo el PRIMER match del regex — **la metadata de sede se descarta aquí** | v4_comprehensive.py L1493-1536 |
| `SitePresenceChecker.check_site` | `SitePresenceReport` por asset (whatsapp_button: wa.me links + CSS classes whatsapp/joinchat) | `modules/asset_generation/site_presence_checker.py` |
| `normalize_site_presence` | Dict canónico `{asset: {status, site_verified, confidence}}` | `modules/asset_generation/site_presence_adapter.py` |

## Flujo actual (v4complete en main.py)

```
audit (v4_comprehensive)
  └─ validate_whatsapp(web=PRIMER numero, gbp) → DataPoint (CONFLICT si difieren)   ← F12
main.py L2420: site_presence_snapshot = normalize_site_presence(checker.check_site(url))
  ├─ CoherenceValidator.validate(site_presence_report=...)        ✅ consume
  ├─ V4AssetOrchestrator.generate_assets(site_presence_report=...)
  │    ├─ detect_pains → pain_ledger.json (status DETECTED)       ❌ NO consume (F13)
  │    ├─ skips de assets si presence=exists                      ✅ consume
  │    └─ PostOrchestratorReconciler → pain_ledger_resolved.json  ✅ (parcial)
  ├─ publication gates (_JUSTIFIED_STATUSES)                      ✅ via reconciler
  └─ V4DiagnosticGenerator.generate (POST-FASE4, L2566)
       ├─ _identify_brechas → detect_pains → brechas              ❌ NO consume (F13)
       └─ _build_whatsapp_conflict_note (validation.conflicts)    ❌ hereda F12
main.py L1735: validator.validate_whatsapp(phone_web, phone_gbp)  ← re-validación SIN alternos (F12)
```

## Punto exacto donde la metadata de sede existe pero se descarta

- `_extract_wa_me_number` (v4_comprehensive.py L1493): `re.search(r'wa\.me/(\d+)')` retorna
  SOLO `match.group(1)` del primer match. El footer multi-sede (Zione: "Pereira Contact" /
  "Cartagena Contact") tiene N números con labels de sede; se conserva 1 sin label.
- `_extract_phone_from_html` (L1511): retorna el primer `tel:` válido.

## Decisión T1 (firma de validate_whatsapp)

**Backwards-compatible**: se agregan parámetros opcionales `web_alternates`
(lista de `{number, label}`) y `gbp_location`. Los 3 callers existentes siguen
funcionando sin cambios; solo se enriquecen:
- `v4_comprehensive._run_cross_validation` (scanner con DOM — pasa alternos + gbp.address)
- `main.py` L1735 (re-validación v4complete — pasa alternos desde CrossValidationResult)
- `two_phase_flow._validate_all_inputs` queda intacto (no tiene DOM disponible).

## Decisión D8 (estado "verificado en producción" como primera clase)

Nuevo status `VERIFIED_IN_SITE` en el pain_ledger:
- Se aplica al crear el ledger (orquestador) si `site_presence_report` confirma el asset
  con status `exists`/`redundant` (mapping pain→asset en PainLedger).
- Se agrega a `_JUSTIFIED_STATUSES` del coverage gate (cubiertas + justificadas == detectadas).
- El reconciler lo preserva (no lo sobreescribe con MAPPED_TO_SERVICE).
- El diagnóstico filtra brechas con status VERIFIED_IN_SITE (lee pain_ledger*.json del output_dir).
- Lo consumirá FASE-P2-A/F14 (`promised_assets_exist`).
