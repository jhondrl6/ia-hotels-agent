---
description: Fábrica agéntica para la creación de nuevas Meta-Skills.
---

# Skill: Meta Skill Creator (Fabrica de Skills)

> [!NOTE]
> **Trigger**: "Aprende a...", "Crea una skill para...", "Enséñame este flujo".

## Pre-requisitos (Contexto)
- [ ] Descripción clara del nuevo flujo o funcionalidad.
- [ ] Conocimiento de la arquitectura de archivos del repo.

## Fronteras (Scope)
- **Hará**: Generación de un nuevo archivo Markdown en `.agents/workflows/`, definición de Triggers semánticos, Inclusión de YAML frontmatter y pasos numerados.
- **NO Hará**: No escribe código Python ni tests, solo la definición del workflow.

## Pasos de Ejecución

### 1. Conceptualización del Flujo
Definir los Pre-requisitos, Fronteras y Restricciones de la nueva skill basados en la solicitud del usuario.

*Validación*: Estructura conceptual aprobada por el usuario.

### 2. Generación del Artefacto (Markdown)
Escribir el archivo `.md` siguiendo el estándar de Meta-Arquitectura Nivel 3.

*Validación*: Archivo creado en `.agents/workflows/` con Frontmatter válido.

### 3. Registro en el Índice Maestro
Actualizar el `README.md` de la carpeta workflows con la nueva skill.

*Validación*: Skill visible y categorizada en el índice.

## Criterios de Éxito
- [ ] Nueva skill funcional e invocable mediante Trigger.
- [ ] Documentación coherente con el sistema.
- [ ] Registro exitoso en el catálogo de skills.

## Plan de Recuperación (Fallback)
- Si falla la escritura, proveer el contenido Markdown en la consola para guardado manual.
- Si el Trigger colisiona con uno existente, sugerir un slug alternativo.
