#!/bin/bash
# Atalho para ativar a venv e iniciar a API.
# Uso: source run.sh

if [ ! -d ".venv" ]; then
    echo "⚠️  Virtualenv não encontrada. Rode 'make install' primeiro."
    return 1 2>/dev/null || exit 1
fi

source .venv/bin/activate
echo "✅ Virtualenv ativada. Para iniciar a API: make start-api"
