# Contexto: Inconsistencia de Comandos en Prompts de Fase

**Fecha**: 2026-05-24  
**Proyecto**: WHATSAPP-CONFLICT-VISIBILITY  
**Detectado por**: Sesión de validación post-ejecución

---

## El Problema

En la FASE-RELEASE del plan WHATSAPP-CONFLICT-VISIBILITY, el paso post-ejecución decía:

```
4. `main.py --doctor`: Regenerar SYSTEM_STATUS.md 
   (NOTA: `--regenerate-domain-primer` no existe; 
    DOMAIN_PRIMER se parchea manualmente si es necesario)
```

**Realidad:**
- `--regenerate-domain-primer` SÍ existe en `scripts/doctor.py`
- `main.py --doctor` NO acepta ese flag
- DOMAIN_PRIMER.md quedó desincronizado (v4.50.0 en vez de v4.51.0) por 5 commits

---

## Causa Raíz

**La auditoría del plan (G1-G6) hizo una corrección incompleta.** El G6 original decía:

| Gap | Severidad | Descripción | Corrección |
|-----|-----------|-------------|------------|
| G6 | MEDIO | `--regenerate-domain-primer` no existe | Reemplazado por `--doctor` |

El auditor reemplazó una suposición incorrecta por otra sin verificar en código. "No existe" era wrong — el flag existe en `scripts/doctor.py`. Reemplazarlo por `main.py --doctor` también era wrong — esa opción no tiene el flag.

**La corrección correcta habría sido:**
- El flag `scripts/doctor.py --regenerate-domain-primer` existe y es el correcto
- No hay que reemplazar nada, solo mover el comando al archivo correcto

---

## Por qué se puede repetir

1. **Sin verificación de comandos en prompts de fase.** Se escribe el paso post-ejecución referencing a un flag/command, se ejecuta, se documenta — pero nadie verifica que el comando exista realmente en el codebase.

2. **La auditoría de planes tiene holes.** El proceso de auditoría G1-G6 no incluye un paso "verificar que los flags/commands referenciados existan en el código source".

3. **El template no exige validación contra código vivo.** `prompt-fase-template.md` no tiene un paso de "verificar que los comandos referenciados existan" antes de escribir la fase.

4. **Feedback loop ausente.** El plan se ejecutó completo (4 fases + RELEASE) sin que emergiera la inconsistencia. Solo se detectó cuando el usuario preguntó explícitamente.

---

## Mitigaciones

### Antes de escribir un prompt de fase:
Verificar que cada comando/flag referenciado exista en el código:

```bash
# Para flags de doctor.py
grep -n "regenerate-domain-primer" scripts/doctor.py main.py

# Para cualquier flag不确定
grep -rn "--flag-name" scripts/ main.py
```

### En la auditoría de planes (G1-G6):
Agregar verificación explícita:
```
Para cada comando/flag referenciado en el prompt:
  1. Buscar en scripts/*.py y main.py si existe
  2. Si existe, confirmar el archivo correcto y la sintaxis
  3. Si no existe, marcar como ERROR (no como nota informativa)
```

### En el template de fases:
Agregar paso obligatorio en Post-Ejecución:
```
Antes de marcar la fase como completada:
- [ ] Verificar que cada comando/flag referenciado existe en el código
```

---

## Archivo corregido

- `.opencode/plans/WHATSAPP-CONFLICT-VISIBILITY/05-prompt-inicio-sesion-fase-RELEASE.md` — L122: corregido a `scripts/doctor.py --regenerate-domain-primer`
- `.opencode/plans/WHATSAPP-CONFLICT-VISIBILITY/README.md` — G6: texto corregido
- `.agent/knowledge/DOMAIN_PRIMER.md` — regenerado y commiteado (daf1559)

---

*Creado: 2026-05-24*
*Tags: post-mortem, plan-audit, command-verification, template-fix*