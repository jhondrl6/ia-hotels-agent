#!/bin/bash
# Script para corregir el .bashrc de WSL

# Eliminar líneas duplicadas de Hermes
sed -i '/# Hermes Agent PATH/d' ~/.bashrc
sed -i '/export PATH="\$HOME\/.local\/bin:\$PATH"/d' ~/.bashrc

# Agregar configuración limpia de Hermes
cat >> ~/.bashrc << 'EOF'

# Hermes Agent PATH
export PATH="$HOME/.local/bin:$PATH"
EOF

echo "✅ PATH de Hermes agregado correctamente al ~/.bashrc"
