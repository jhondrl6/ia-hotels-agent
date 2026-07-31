# FASE-5: Limpieza de Deuda Técnica (Template Embebido Muerto)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

- **FASE-0 a FASE-4** ✅: Todos los 5 gaps principales + bugs implementados.
- Gaps resueltos: IMP-03, F5, F7, MIN-01, MIN-02, MIN-03.
- Pendiente: eliminar template embebido muerto (deuda técnica).
- Tests pasando.

## Objetivo de esta fase

Eliminar el **template embebido muerto** en `v4_proposal_generator.py` (alrededor de L575-605)
que contiene un string de markdown completo que NUNCA se usa. El código carga el template
desde `propuesta_v6_template.md` (archivo externo), haciendo este código duplicado
obsoleto y confuso para futuros desarrolladores.

---

### Tareas

- [ ] **T1: Verificar que el template embebido NO se usa en ningún code path**

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli

  # 1. Identificar la variable del template embebido
  grep -n "EMBEDDED\|embedded_template\|template_string\|_TEMPLATE_STR\|embedded_md" \
      modules/commercial_documents/v4_proposal_generator.py

  # 2. Verificar que el código usa el archivo externo
  grep -n "propuesta_v6_template\|load_template\|template_path\|open.*template" \
      modules/commercial_documents/v4_proposal_generator.py

  # 3. Buscar TODAS las referencias al nombre de la variable embebida
  #    en TODO el codebase (no solo en este archivo)
  grep -rn "NOMBRE_VARIABLE" modules/ tests/
  #    (reemplazar NOMBRE_VARIABLE con el nombre real encontrado)

  # 4. Verificar que ningún test usa el template embebido
  grep -rn "embedded\|EMBEDDED" tests/commercial_documents/
  ```

  **Si alguna referencia activa existe:** NO eliminar, documentar y reportar.
  **Si cero referencias activas:** proceder con eliminación.

- [ ] **T2: Eliminar el bloque de template embebido**

  Una vez confirmado que es dead code:

  1. Identificar las líneas exactas del bloque
  2. Eliminar el string multilínea completo (desde la variable hasta su cierre)
  3. Eliminar cualquier comentario asociado al template embebido
  4. Preservar el código circundante intacto

  **Precaución:** El bloque puede extenderse más allá de L575-605 si incluye
  variables auxiliares o comentarios. Eliminar TODO el bloque cohesivo.

- [ ] **T3: Tests de regresión**
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20
  
  # Verificación adicional: el generador sigue funcionando
  ./venv/Scripts/python.exe -c "
  from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
  gen = V4ProposalGenerator()
  print('Generator instantiated OK')
  print('Template loaded:', hasattr(gen, '_template') or hasattr(gen, 'template'))
  "
  ```

- [ ] **T4: Actualizar estado de fase**
  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO ejecutar v4complete**
- **NO modificar nada más del generador** — solo eliminar el dead code
- Si el dead code tiene referencias en tests, documentar pero NO eliminar
- Verificación exhaustiva antes de eliminar (grep en todo el codebase)
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] Verification grep confirma 0 referencias activas al template embebido
- [ ] Bloque de template embebido eliminado de `v4_proposal_generator.py`
- [ ] Generator sigue instanciando y cargando template externo correctamente
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Eliminar dead code |

### Próxima sesión

```
Carga y ejecuta .opencode/plans/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-6.md
```

Esa fase ejecuta v4complete para Hotel Castilla Real y realiza el análisis post-implementación.
