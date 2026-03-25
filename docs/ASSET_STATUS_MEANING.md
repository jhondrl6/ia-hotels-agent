# Asset Status Meaning Guide

## Overview

This document explains the `status` and `can_use` fields in asset metadata, and what actions users should take based on their values.

---

## Status vs Can_Use

| Field | Type | Description |
|-------|------|-------------|
| `status` | `AssetStatus` enum | Pipeline state: PENDING, GENERATED, VALIDATED, FAILED, DEPRECATED |
| `can_use` | `bool` | Whether the asset is ready for deployment |

**Key Insight**: These two fields serve different purposes:
- `status` tells you where the asset is in the generation pipeline
- `can_use` tells you if the asset is safe/ready to deploy

---

## Asset Status Values

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `PENDING` | Asset not yet generated | Wait for generation to complete |
| `GENERATED` | Asset created but not validated | Review content before use |
| `VALIDATED` | Asset passed quality gates | Ready for deployment |
| `FAILED` | Generation failed | Check `fallback_reason` field |
| `DEPRECATED` | Asset outdated | Generate new asset |

---

## Can_Use Decision Matrix

The `can_use` flag is calculated based on:

| Condition | can_use value | Reason |
|-----------|---------------|--------|
| preflight_status = "BLOCKED" | `false` | Quality gate blocked this asset |
| confidence_level = CONFLICT | `false` | Data conflicts detected |
| confidence_level = UNKNOWN | `false` | Insufficient data |
| confidence_score < 0.5 | `false` | Confidence too low |
| All conditions pass | `true` | Asset is usable |

---

## Combined States (Real Examples)

### Scenario 1: Ready for Use
```json
{
  "status": "VALIDATED",
  "can_use": true,
  "confidence_score": 0.85,
  "preflight_status": "PASSED"
}
```
**Action**: Deploy this asset.

---

### Scenario 2: Generated but Not Ready
```json
{
  "status": "GENERATED",
  "can_use": false,
  "confidence_score": 0.45,
  "preflight_status": "WARNING"
}
```
**Action**: Review the asset content. Low confidence means data may be incomplete. Validate before deploying.

---

### Scenario 3: Blocked by Quality Gate
```json
{
  "status": "FAILED",
  "can_use": false,
  "confidence_score": 0.3,
  "preflight_status": "BLOCKED",
  "fallback_reason": "Missing required field: hotel_name"
}
```
**Action**: Fix the issue mentioned in `fallback_reason`, then regenerate.

---

### Scenario 4: Conflict Detected
```json
{
  "status": "GENERATED",
  "can_use": false,
  "confidence_level": "CONFLICT",
  "disclaimer": "⚠️ Este activo contiene conflictos de datos. Requiere revisión manual antes de usar."
}
```
**Action**: Review the asset manually. Check `conflicts` field for details.

---

## User Guidance by State

| State | User Question | Answer |
|-------|---------------|--------|
| `can_use: false, status: GENERATED` | "Why can't I use it?" | Low confidence or preflight warning - review content |
| `can_use: false, status: FAILED` | "What went wrong?" | Check `fallback_reason` for the specific error |
| `can_use: true` | "Is it safe?" | Yes, but always review disclaimer if present |
| `status: VALIDATED` | "Is it good?" | Passed quality gates, but still review content |

---

## Disclaimer Messages

The `disclaimer` field provides additional context:

| Disclaimer | Meaning |
|------------|---------|
| `None` (for VERIFIED + score >= 0.9) | High confidence, no disclaimer needed |
| `⚠️ Este activo contiene conflictos...` | Data conflicts exist - manual review required |
| `⚠️ Datos insuficientes...` | UNKNOWN confidence - verification needed |
| `⚠️ Confianza baja...` | Score < 0.7 - validate before publishing |
| `ℹ️ Basado en: ...` | Single source - recommend additional validation |

---

## Quick Reference

**DO:**
- Always check `can_use` before deploying
- Read the `disclaimer` field if present
- Check `fallback_reason` when status is FAILED
- Review `conflicts` list when confidence_level is CONFLICT

**DON'T:**
- Assume an asset with `status: GENERATED` is ready to use
- Deploy assets with `can_use: false` without manual review
- Ignore disclaimers even when `can_use: true`
