#!/usr/bin/env python3
"""
validate_cross_refs.py — Valida cross-references entre documentos clave.

Verifica que las referencias §Section-Name en AGENTS.md, CONTRIBUTING.md
y phased_project_executor.md apunten a secciones que realmente existen
en algún documento del ecosistema documental. Previene refs rotas.

Estrategia: Una ref es válida si existe como header en CUALQUIER documento
del ecosistema (principales + secundarios). No se infiere destino por contexto.

Uso:
    python scripts/validate_cross_refs.py
    python scripts/validate_cross_refs.py --verbose
"""

import sys
import re
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# Todos los documentos del ecosistema (principales + secundarios)
ALL_DOCS = {
    "AGENTS.md": ROOT / "AGENTS.md",
    "CONTRIBUTING.md": ROOT / "docs" / "CONTRIBUTING.md",
    "phased_project_executor.md": ROOT / ".agents" / "workflows" / "phased_project_executor.md",
    "documentation_rules.md": ROOT / "docs" / "contributing" / "documentation_rules.md",
    "validation.md": ROOT / "docs" / "contributing" / "validation.md",
    "capabilities.md": ROOT / "docs" / "contributing" / "capabilities.md",
    "procedures.md": ROOT / "docs" / "contributing" / "procedures.md",
}

# Documentos fuente (donde buscar refs para validar)
SOURCE_DOCS = ["AGENTS.md", "CONTRIBUTING.md", "phased_project_executor.md"]

# Referencias que son placeholders/ejemplos (no validar)
PLACEHOLDER_REFS = {
    "nombre seccion", "section name", "nn mm", "x y z",
    "nombre", "seccion", "titulo", "descripcion",
    "x", "y", "z", "n",
}

# Referencias numéricas puras (apuntan a líneas o fragmentos, no validar)
NUMERIC_REF_PATTERN = re.compile(r"^\d+(-\d+)?$")


def normalize(text: str) -> str:
    """Normaliza: quita acentos, lowercase, guiones→espacios, colapsa."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_placeholder(ref_name: str) -> bool:
    """Verifica si una referencia es un placeholder o ejemplo."""
    ref_norm = normalize(ref_name)
    if ref_norm in PLACEHOLDER_REFS:
        return True
    if NUMERIC_REF_PATTERN.match(ref_name):
        return True
    return False


def extract_all_headers(doc_contents: dict) -> dict:
    """
    Extrae headers de todos los documentos.
    Retorna dict: {doc_name: [normalized_headers]}
    """
    all_headers = {}
    for doc_name, content in doc_contents.items():
        headers = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                title = re.sub(r"^#+\s*", "", stripped)
                headers.append(normalize(title))
        all_headers[doc_name] = headers
    return all_headers


def ref_exists_anywhere(ref_name: str, all_headers: dict) -> tuple:
    """
    Busca una ref en todos los documentos.
    Retorna (found: bool, doc_found: str or None).
    """
    ref_norm = normalize(ref_name)
    ref_words = set(ref_norm.split())

    if not ref_words:
        return True, None

    for doc_name, headers in all_headers.items():
        for header_norm in headers:
            # Match exacto o contenido
            if ref_norm == header_norm or ref_norm in header_norm:
                return True, doc_name

            # Match por palabras: ≥60% de palabras de la ref en el header
            header_words = set(header_norm.split())
            overlap = ref_words & header_words
            if len(ref_words) > 0 and len(overlap) / len(ref_words) >= 0.6:
                return True, doc_name

    return False, None


def extract_refs(content: str) -> list:
    """Extrae referencias §Section-Name únicas de un documento."""
    refs = set()
    pattern = re.compile(r"§([A-Za-zÁ-ÿ0-9][A-Za-zÁ-ÿ0-9-]*[A-Za-zÁ-ÿ0-9]|[A-Za-zÁ-ÿ0-9])")

    for match in pattern.finditer(content):
        ref_name = match.group(1)
        if not is_placeholder(ref_name):
            refs.add(ref_name)

    return sorted(refs)


def main():
    verbose = "--verbose" in sys.argv

    print("=" * 60)
    print("VALIDATE CROSS-REFS — Validación de referencias cruzadas")
    print("=" * 60)

    # Cargar todos los documentos
    doc_contents = {}
    for name, path in ALL_DOCS.items():
        if path.exists():
            doc_contents[name] = path.read_text(encoding="utf-8")
        else:
            if verbose:
                print(f"  [WARN] {name} no encontrado")

    print(f"Documentos cargados: {len(doc_contents)}")
    print(f"Fuentes a validar: {', '.join(SOURCE_DOCS)}\n")

    # Extraer headers de todos los documentos
    all_headers = extract_all_headers(doc_contents)

    # Validar refs de cada documento fuente
    results = {"total": 0, "pass": 0, "fail": 0, "errors": []}

    for source_name in SOURCE_DOCS:
        if source_name not in doc_contents:
            continue

        refs = extract_refs(doc_contents[source_name])

        for ref_name in refs:
            results["total"] += 1
            found, found_in = ref_exists_anywhere(ref_name, all_headers)

            if found:
                results["pass"] += 1
                if verbose:
                    print(f"  [PASS] {source_name}: §{ref_name} → {found_in}")
            else:
                results["fail"] += 1
                error_msg = f"{source_name}: §{ref_name} no encontrada en ningún documento"
                results["errors"].append(error_msg)
                if verbose:
                    print(f"  [FAIL] {error_msg}")

    # Resumen
    print(f"\n{'=' * 60}")
    print(f"Total refs únicas verificadas: {results['total']}")
    print(f"  PASS: {results['pass']}")
    print(f"  FAIL: {results['fail']}")

    if results["fail"] > 0:
        print(f"\n[FAIL] Referencias rotas ({results['fail']}):")
        for err in results["errors"]:
            print(f"  ✗ {err}")
        print(f"\n{'=' * 60}")
        print("RESULTADO: ❌ FAIL — hay cross-references rotas")
        print("=" * 60)
        sys.exit(1)
    else:
        print(f"\n{'=' * 60}")
        print("RESULTADO: ✅ PASS — todas las cross-references válidas")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
