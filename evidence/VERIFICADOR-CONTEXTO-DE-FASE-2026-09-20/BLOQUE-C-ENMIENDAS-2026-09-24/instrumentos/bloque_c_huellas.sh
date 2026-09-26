#!/bin/bash
# Huellas finales y delta atribuido del bloque C (2026-09-24). Solo lectura.
cd /c/Users/Jhond/Github/iah-cli || exit 9
export PYTHONIOENCODING=utf-8
{
  echo "### git status --porcelain (final)"
  git status --porcelain 2>&1
  echo
  echo "### git diff --numstat (final)"
  git diff --numstat 2>&1
  echo
  echo "### sha256 de los .md de los cuatro planes + la orden (orden alfabético)"
  sha256sum .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/*.md \
            .opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/*.md \
            .opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/*.md \
            .opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/*.md \
            .opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md 2>&1
  echo
  echo "### rutas de evidencia B (no tocadas por esta sesión) — conteo de archivos"
  find evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-ORDEN-CALIDAD-2026-09-23 \
       evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23 -type f | wc -l
  echo
  echo "### baselines de citación/ref: sin cambios"
  git status --porcelain .opencode/plans/plan_citations_baseline.json .opencode/refs_baseline.txt
  echo "(vacío arriba = intactas)"
  echo "### fin"
} > evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/07-huellas-finales.txt 2>&1
echo "EXIT=$?"; wc -l evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/07-huellas-finales.txt
