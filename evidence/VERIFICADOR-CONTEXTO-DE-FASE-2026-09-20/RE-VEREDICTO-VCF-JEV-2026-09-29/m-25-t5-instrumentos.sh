#!/bin/sh
# T5 - re-veredicto VCF/JEV: re-mide cada veredicto heredado y re-chequea F1-F5, re-usando los
# instrumentos VERSIONADOS de la sesion de re-verificacion (barrido_parrafo.py, conteo_formas.py,
# m-f1/m-f2/m-f5.sh) y el de AC3 copiado por byte con su destino apuntando a ESTE expediente.
# Ninguno escribe en el expediente anterior. Cada EXIT se captura sin tuberia.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28"

echo "### 0. Identidad del arbol que se mide" > "$D/25-t5-identidad-del-arbol.txt"
git rev-parse HEAD >> "$D/25-t5-identidad-del-arbol.txt" 2>&1
git status --porcelain -uno | wc -l >> "$D/25-t5-identidad-del-arbol.txt" 2>&1
git ls-files | wc -l >> "$D/25-t5-identidad-del-arbol.txt" 2>&1
echo "  (HEAD / rutas versionadas modificadas / rutas versionadas totales)" >> "$D/25-t5-identidad-del-arbol.txt"

echo >> "$D/25-t5-identidad-del-arbol.txt"
echo "### sha256 de los instrumentos re-usados (para que la re-medición sea reproducible)" >> "$D/25-t5-identidad-del-arbol.txt"
sha256sum "$E"/barrido_parrafo.py "$E"/conteo_formas.py "$E"/m-f1.sh "$E"/m-f2.sh "$E"/m-f5.sh >> "$D/25-t5-identidad-del-arbol.txt" 2>&1

echo "### F1 (re-uso del instrumento versionado m-f1.sh, stdout a este crudo)" > "$D/26-f1-re-medido.txt"
sh "$E/m-f1.sh" >> "$D/26-f1-re-medido.txt" 2>&1
echo "EXIT_F1=$?" >> "$D/26-f1-re-medido.txt"

echo "### F2 (re-uso del instrumento versionado m-f2.sh)" > "$D/27-f2-re-medido.txt"
sh "$E/m-f2.sh" >> "$D/27-f2-re-medido.txt" 2>&1
echo "EXIT_F2=$?" >> "$D/27-f2-re-medido.txt"

echo "### F3 por PARRAFO, alcance 13 fuentes del plan (re-uso de barrido_parrafo.py)" > "$D/28-f3-parrafo-fuentes.txt"
python "$E/barrido_parrafo.py" fuentes "$D/28-f3-parrafo-fuentes.txt" > "$D/28b-f3-stdout.log" 2>&1
echo "EXIT_F3_FUENTES=$?" >> "$D/28b-f3-stdout.log"

python "$E/barrido_parrafo.py" corpus-completo "$D/29-f3-parrafo-corpus-completo.txt" > "$D/29b-f3-stdout.log" 2>&1
echo "EXIT_F3_CORPUS=$?" >> "$D/29b-f3-stdout.log"

echo "### F4 par de formas (re-uso de conteo_formas.py, destino en ESTE expediente)" > "$D/30-f4-par-de-formas.txt"
python "$E/conteo_formas.py" "$D/30b-f4-ocurrencias.txt" >> "$D/30-f4-par-de-formas.txt" 2>&1
echo "EXIT_F4_OCURRENCIAS=$?" >> "$D/30-f4-par-de-formas.txt"
git grep -c -F '`.opencode/plans/Archives' HEAD -- '*.md' > "$D/31-f4-git-grep-head.txt" 2>&1
echo "EXIT_GREP_SIN_BARRA=$?" >> "$D/31-f4-git-grep-head.txt"
git grep -c -F '`/.opencode/plans/Archives' HEAD -- '*.md' >> "$D/31-f4-git-grep-head.txt" 2>&1
echo "EXIT_GREP_CON_BARRA=$?" >> "$D/31-f4-git-grep-head.txt"
grep -n '518 contra 66' .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md >> "$D/31-f4-git-grep-head.txt" 2>&1
echo "EXIT_GREP_CIFRA_FILA=$?" >> "$D/31-f4-git-grep-head.txt"

echo "### F5 REGISTRY y el escritor (re-uso de m-f5.sh)" > "$D/32-f5-registry-re-medido.txt"
sha256sum docs/contributing/REGISTRY.md >> "$D/32-f5-registry-re-medido.txt" 2>&1
echo "  ^ sha ANTES del dry-run" >> "$D/32-f5-registry-re-medido.txt"
sh "$E/m-f5.sh" >> "$D/32-f5-registry-re-medido.txt" 2>&1
echo "EXIT_F5=$?" >> "$D/32-f5-registry-re-medido.txt"
sha256sum docs/contributing/REGISTRY.md >> "$D/32-f5-registry-re-medido.txt" 2>&1
echo "  ^ sha DESPUES del dry-run (debe ser el mismo: el dry-run no escribe)" >> "$D/32-f5-registry-re-medido.txt"
git status --porcelain -uno | wc -l >> "$D/32-f5-registry-re-medido.txt" 2>&1
echo "  ^ rutas versionadas modificadas despues de todo (0 = el dry-run no toco el arbol)" >> "$D/32-f5-registry-re-medido.txt"

echo "### JEV AC3 por sha (instrumento copiado por byte, destino en ESTE expediente)" > "$D/33-jev-ac3-re-medido.txt"
sed "s|^DEST = .*|DEST = sys.argv[1]|" "$E/jev_ac3_sha.py" > "$D/m-33-jev-ac3.py"
python "$D/m-33-jev-ac3.py" "$D/33-jev-ac3-re-medido.txt" > "$D/33b-ac3-stdout.log" 2>&1
echo "EXIT_AC3=$?" >> "$D/33b-ac3-stdout.log"
# Control de fidelidad: el instrumento copiado debe diferir del versionado SOLO en la linea de DEST.
sed 's/\r$//' "$E/jev_ac3_sha.py" > "$D/33c-instrumento-original.sin-crlf"
sed 's/\r$//' "$D/m-33-jev-ac3.py" > "$D/33d-instrumento-copiado.sin-crlf"
diff "$D/33c-instrumento-original.sin-crlf" "$D/33d-instrumento-copiado.sin-crlf" > "$D/33e-diff-instrumento.txt" 2>&1
echo "EXIT_DIFF_INSTRUMENTO=$? (1 = hay una diferencia; debe ser exactamente la linea DEST)" >> "$D/33b-ac3-stdout.log"
wc -l < "$D/33e-diff-instrumento.txt" >> "$D/33b-ac3-stdout.log"
echo "  ^ lineas del diff (3 = 1c1 con sus marcadores)" >> "$D/33b-ac3-stdout.log"

echo "### Veredictos heredados por AC, leidos de su fuente (FASE-C)" > "$D/34-veredictos-ac-re-leidos.txt"
python "$D/m-34-veredictos.py" "$D" > "$D/34b-veredictos-stdout.log" 2>&1
echo "EXIT_VEREDICTOS=$?" >> "$D/34b-veredictos-stdout.log"
echo "HECHO-T5" >> "$D/25-t5-identidad-del-arbol.txt"
