# Variáveis de ambiente...
DEPLOY_PATH := $(shell pwd)
PYTHON := python3
PIP := pip3
MODEL_DIR := $(DEPLOY_PATH)/models
MODEL_URL := https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf?download=true  # Exemplo de URL

# ------------------------------------------------------------------------------------------
# 🛠️ Configuração inicial...
# ------------------------------------------------------------------------------------------
.PHONY: setup
setup:
	@echo "📦 Instalando dependências globais..."
	sudo apt update && sudo apt install -y python3-pip jq wget
	$(PIP) install --upgrade pip
	@echo "✅ Setup inicial concluído!"

# ------------------------------------------------------------------------------------------
# 📦 Instalar dependências do projeto.
# ------------------------------------------------------------------------------------------
.PHONY: install
install:
	@echo "📦 Instalando dependências do projeto..."
	$(PIP) install -r polaris_api/requirements.txt
	$(PIP) install -r polaris_integrations/requirements.txt
	@echo "✅ Dependências instaladas!"

# ------------------------------------------------------------------------------------------
# 🤖 Baixar modelo LLaMA 3
# ------------------------------------------------------------------------------------------
.PHONY: download-model
download-model:
	@echo "📥 Baixando modelo LLaMA 3..."
	mkdir -p $(MODEL_DIR)
	wget -c $(MODEL_URL) -O $(MODEL_DIR)/llama3-7B.safetensors
	@echo "✅ Modelo LLaMA 3 baixado em $(MODEL_DIR)!"

# ------------------------------------------------------------------------------------------
# 🐳 Subir MongoDB e Mongo Express (Docker Compose)
# ------------------------------------------------------------------------------------------
.PHONY: start-db
start-db:
	@echo "🐳 Iniciando MongoDB e Mongo Express..."
	cd polaris_setup/ && mongodb-compose up -d
	@echo "✅ MongoDB e Mongo Express rodando!"

# ------------------------------------------------------------------------------------------
# 🛑 Parar MongoDB e Mongo Express
# ------------------------------------------------------------------------------------------
.PHONY: stop-db
stop-db:
	@echo "🛑 Parando MongoDB e Mongo Express..."
	cd polaris_setup/ && mongodb-compose down
	@echo "✅ MongoDB e Mongo Express parados!"

# ------------------------------------------------------------------------------------------
# 🔄 Reiniciar MongoDB e Mongo Express
# ------------------------------------------------------------------------------------------
.PHONY: restart-db
restart-db:
	@echo "🔄 Reiniciando MongoDB e Mongo Express..."
	make stop-db
	sleep 2
	make start-db
	@echo "✅ Banco de dados reiniciado!"

# ------------------------------------------------------------------------------------------
# 🔄 Rodar tudo incluindo banco de dados
# ------------------------------------------------------------------------------------------
.PHONY: start-all
start-all:
	@echo "🔄 Iniciando tudo..."
	make start-db
	make start-api &
	make start-bot &
	@echo "✅ Todos os serviços iniciados!"

# ------------------------------------------------------------------------------------------
# 🚀 Rodar API
# ------------------------------------------------------------------------------------------
.PHONY: start-api
start-api:
	@echo "🚀 Iniciando API..."
	cd polaris_api && $(PYTHON) main.py
	@echo "✅ API rodando!"

# ------------------------------------------------------------------------------------------
# 🤖 Rodar Polaris Integrations
# ------------------------------------------------------------------------------------------
.PHONY: start-integrations
start-integrations:
	@echo "🤖 Iniciando Polaris Integrations..."
	@if [ -f polaris_integrations/.env ]; then \
		export TELEGRAM_TOKEN=$$(grep "^TELEGRAM_TOKEN" polaris_integrations/.env | cut -d '=' -f2); \
		export TELEGRAM_API_URL="https://api.telegram.org/bot$${TELEGRAM_TOKEN}"; \
	else \
		echo "⚠️  .env do Polaris Integrations não encontrado!"; \
		exit 1; \
	fi
	sudo apt install -y ffmpeg
	cd polaris_integrations && $(PYTHON) main.py
	@echo "✅ Polaris Integrations rodando!"


# ------------------------------------------------------------------------------------------
# 🌍 Configurar Ngrok + Webhook Telegram
# ------------------------------------------------------------------------------------------
.PHONY: setup-ngrok
setup-ngrok:
	@echo "🌐 Configurando Ngrok..."
	bash polaris_setup/setup_ngrok.sh
	@echo "✅ Ngrok e Webhook do Telegram configurados!"

# ------------------------------------------------------------------------------------------
# 📝 Criar .env da API se não existir
# ------------------------------------------------------------------------------------------
.PHONY: create-env-api
create-env-api:
	@echo "📝 Verificando .env da API..."
	@if [ ! -f polaris_api/.env ]; then \
		echo "⚠️  .env da API não encontrado! Criando um novo com chaves seguras..."; \
		cd polaris_api && python3 generate-env.py; \
		echo "✅ .env da API criado com chaves seguras!"; \
	else \
		echo "✅ .env da API já existe!"; \
	fi

.PHONY: regenerate-env-api
regenerate-env-api:
	@echo "🔄 Regenerando .env da API com novas chaves..."
	@cd polaris_api && python3 generate-env.py
	@echo "✅ .env da API regenerado com novas chaves!"

.PHONY: setup-prod-env
setup-prod-env:
	@echo "🌐 Configurando .env para produção..."
	@read -p "Digite o domínio do GitHub Pages (ex: https://tech-tweakers.github.io): " domain; \
	cd polaris_api && python3 generate-env.py "$$domain"
	@echo "✅ .env da API configurado para produção!"

# ------------------------------------------------------------------------------------------
# 🧪 Testes
.PHONY: test
test:
	@echo "🧪 Executando testes unitários..."
	@cd polaris_api && python3 -m pytest ../tests/ -v

.PHONY: test-cov
test-cov:
	@echo "📊 Executando testes com cobertura..."
	@cd polaris_api && python3 -m pytest ../tests/ --cov=. --cov-report=term-missing

.PHONY: test-watch
test-watch:
	@echo "👀 Executando testes em modo watch..."
	@cd polaris_api && python3 -m pytest ../tests/ -f -v

.PHONY: install-test-deps
install-test-deps:
	@echo "📦 Instalando dependências de teste..."
	@cd polaris_api && pip3 install -r requirements-test.txt

.PHONY: test-ci
test-ci:
	@echo "🚀 Executando testes para CI/CD..."
	@cd polaris_api && python3 -m pytest ../tests/ -v --cov=. --cov-report=xml --cov-report=html

.PHONY: ci-check
ci-check:
	@echo "🔍 Verificando qualidade do código..."
	@echo "📝 Verificando formatação..."
	@black --check polaris_api/ || echo "⚠️ Black não encontrado, pulando..."
	@echo "📋 Verificando imports..."
	@isort --check-only polaris_api/ || echo "⚠️ isort não encontrado, pulando..."
	@echo "🔍 Verificando linting..."
	@flake8 polaris_api/ --max-line-length=127 --max-complexity=10 || echo "⚠️ flake8 não encontrado, pulando..."
	@echo "🔒 Verificando segurança..."
	@bandit -r polaris_api/ -f json -o bandit-report.json || echo "⚠️ bandit não encontrado, pulando..."
	@echo "✅ Verificações de qualidade concluídas!"

.PHONY: ci-full
ci-full:
	@echo "🚀 Executando pipeline completo de CI..."
	$(MAKE) test-ci
	$(MAKE) ci-check
	@echo "🎉 Pipeline de CI concluído com sucesso!"

# ------------------------------------------------------------------------------------------
# 📝 Criar .env do Polaris Integrations se não existir
# ------------------------------------------------------------------------------------------
.PHONY: create-env-integrations
create-env-integrations:
	@echo "📝 Verificando .env do Polaris Integrations..."
	@if [ ! -f polaris_integrations/.env ]; then \
		echo "⚠️  .env do Bot não encontrado! Criando um novo..."; \
		touch polaris_integrations/.env; \
		echo "TELEGRAM_TOKEN=\"0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\"" >> polaris_integrations/.env; \
		echo "POLARIS_API_URL=\"http://192.168.2.48:8000/inference/\"" >> polaris_integrations/.env; \
		echo "✅ .env do Polaris Integrations criado! Edite-o para ajustar os valores."; \
	else \
		echo "✅ .env do Polaris Integrations já existe!"; \
	fi


# ------------------------------------------------------------------------------------------
# 🌐 Configuração do Ngrok e Webhook do Telegram
# ------------------------------------------------------------------------------------------

# 🌍 Iniciar o Ngrok e configurar o Webhook do Telegram (executa o script com variáveis exportadas)
.PHONY: setup-ngrok
setup-ngrok:
	@echo "🌐 Exportando variáveis e iniciando Ngrok..."
	@if [ -f polaris_integrations/.env ]; then \
		export polaris_integrations_PORT=8000; \
		export TELEGRAM_TOKEN=$$(grep "^TELEGRAM_TOKEN" polaris_integrations/.env | cut -d '=' -f2); \
		bash polaris_setup/scripts/setup_ngrok.sh; \
		echo "✅ Ngrok e Webhook configurados!"; \
	else \
		echo "⚠️ .env do Polaris Integrations não encontrado! Certifique-se de rodar 'make create-env-bot' primeiro."; \
		exit 1; \
	fi

# 🛑 Parar Ngrok
.PHONY: stop-ngrok
stop-ngrok:
	@echo "🛑 Parando Ngrok..."
	@pkill -f ngrok || true
	@echo "✅ Ngrok parado!"

# 🔄 Reiniciar Ngrok
.PHONY: restart-ngrok
restart-ngrok:
	@echo "🔄 Reiniciando Ngrok..."
	make stop-ngrok
	sleep 2
	make setup-ngrok
	@echo "✅ Ngrok reiniciado!"


# ------------------------------------------------------------------------------------------
# 🔄 Rodar tudo
# ------------------------------------------------------------------------------------------
.PHONY: start-all
start-all:
	@echo "🔄 Iniciando tudo..."
	make start-api &
	make start-bot &
	@echo "✅ Todos os serviços iniciados!"

# -----------------------------------------------------------------------------------------
# 🛑 Parar todos os processos
# -----------------------------------------------------------------------------------------
.PHONY: stop-all
stop-all:
	@echo "🛑 Parando todos os serviços..."
	pkill -f "python3 main.py"
	@echo "✅ Todos os processos parados!"

# ------------------------------------------------------------------------------------------
# 🔄 Reiniciar tudo
# ------------------------------------------------------------------------------------------
.PHONY: restart-all
restart-all:
	@echo "🔄 Reiniciando tudo..."
	make stop-all
	sleep 2
	make start-all
	@echo "✅ API e Polaris Integrations reiniciados!"
