#!/bin/bash
# Setup systemd service for Polaris Integrations
# Usage: sudo bash polaris_setup/setup-systemd-integrations.sh

set -e

DEPLOY_PATH="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="${DEPLOY_PATH}/.venv/bin/python3"
SERVICE_NAME="polaris-integrations"
USER="$(whoami)"

echo "📦 Configurando systemd service: ${SERVICE_NAME}"
echo "   Path: ${DEPLOY_PATH}"
echo "   User: ${USER}"
echo "   Python: ${VENV_PYTHON}"

if [ ! -f "${VENV_PYTHON}" ]; then
    echo "❌ Virtualenv não encontrada em ${DEPLOY_PATH}/.venv"
    echo "   Rode 'make install' primeiro."
    exit 1
fi

if [ ! -f "${DEPLOY_PATH}/polaris_integrations/.env" ]; then
    echo "❌ .env do Integrations não encontrado!"
    echo "   Rode 'make create-env-integrations' primeiro."
    exit 1
fi

cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=Polaris Integrations (Telegram + TTS + Whisper)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${DEPLOY_PATH}
ExecStart=${VENV_PYTHON} -m polaris_integrations.main
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

echo "✅ Service ${SERVICE_NAME} instalado e iniciado!"
echo ""
echo "Comandos úteis:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
