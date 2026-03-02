#!/bin/bash

# Função para exibir o menu...
show_menu() {
    clear
    echo "=================================="
    echo "      🚀 Polaris v2 - Menu        "
    echo "=================================="
    echo "1) 🛠️ Configuração inicial (Setup + Instalar dependências)"
    echo "2) 📝 Criar .env para API e Integrations"
    echo "3) 🤖 Baixar modelo LLaMA 3"
    echo "4) 🐳 Subir MongoDB e Mongo Express"
    echo "5) 🌍 Configurar Ngrok + Webhook Telegram"
    echo "6) 🚀 Iniciar Polaris API"
    echo "7) 🤖 Iniciar Polaris Integrations"
    echo "8) 🔄 Iniciar tudo (DB, API, Integrations, Ngrok)"
    echo "9) 🛑 Parar tudo"
    echo "10) 🔄 Reiniciar tudo"
    echo "0) ❌ Sair"
    echo ""
}

## Loop para manter o menu rodando até o usuário sair
while true; do
    show_menu
    read -r -p "Digite a opção desejada: " OPTION
    case "$OPTION" in
        1)
            echo "🛠️ Configurando ambiente..."
            make setup
            echo ""
            echo "Selecione o modo de instalação:"
            echo "  a) 🖥️  CPU-only (~200MB PyTorch - sem GPU)"
            echo "  b) 🎮 GPU/CUDA (~2GB+ PyTorch - requer NVIDIA GPU)"
            read -r -p "Escolha [a/b]: " MODE
            case "$MODE" in
                b|B) make install-gpu ;;
                *)   make install-cpu ;;
            esac
            sleep 1
            ;;
        2) echo "📝 Criando arquivos .env para API e Integrations..." && make create-env-api && make create-env-integrations && sleep 1 ;;
        3) echo "🤖 Baixando modelo LLaMA 3..." && make download-model && sleep 1 ;;
        4) echo "🐳 Subindo MongoDB e Mongo Express..." && make start-db && sleep 1 ;;
        5) echo "🌍 Configurando Ngrok e Webhook do Telegram..." && make setup-ngrok && sleep 1 ;;
        6) echo "🚀 Iniciando API..." && make start-api && sleep 1 ;;
        7) echo "🤖 Iniciando Integrations..." && make start-integrations && sleep 1 ;;
        8) echo "🔄 Iniciando todos os serviços..." && make start-all && sleep 1 ;;
        9) echo "🛑 Parando todos os serviços..." && make stop-all && sleep 1 ;;
        10) echo "🔄 Reiniciando tudo..." && make restart-all && sleep 1 ;;
        0) echo "❌ Saindo..." && exit 0 ;;
        *) echo "⚠️ Opção inválida! Tente novamente." && sleep 2 ;;
    esac
done
