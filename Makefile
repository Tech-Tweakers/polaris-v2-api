DEPLOY_PATH := $(shell pwd)
VENV_DIR := $(DEPLOY_PATH)/.venv
PYTHON := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip3
MODEL_DIR := $(DEPLOY_PATH)/models
MODEL_URL := https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf?download=true

# ------------------------------------------------------------------------------------------
# 🐍 Criar virtualenv
# ------------------------------------------------------------------------------------------
.PHONY: venv
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "🐍 Criando virtualenv em $(VENV_DIR)..."; \
		python3 -m venv $(VENV_DIR); \
		echo "✅ Virtualenv criada!"; \
	else \
		echo "✅ Virtualenv já existe."; \
	fi
	$(PIP) install --upgrade pip

# ------------------------------------------------------------------------------------------
# 🛠️ Configuração inicial
# ------------------------------------------------------------------------------------------
.PHONY: setup
setup:
	@echo "📦 Instalando dependências globais..."
	sudo apt update && sudo apt install -y python3-pip python3-venv jq wget
	@echo "✅ Setup inicial concluído!"

# ------------------------------------------------------------------------------------------
# 📦 Instalar dependências do projeto
# ------------------------------------------------------------------------------------------
# install-cpu: PyTorch CPU-only (~200MB) - para servidores sem GPU
# install-gpu: PyTorch com CUDA (~2GB+) - para servidores com GPU NVIDIA
# install:     alias para install-cpu (padrão seguro)
# ------------------------------------------------------------------------------------------
.PHONY: install
install: install-cpu

.PHONY: install-cpu
install-cpu: venv
	@echo "📦 Instalando dependências (modo CPU)..."
	$(PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install -r polaris_api/requirements.txt
	$(PIP) install -r polaris_integrations/requirements.txt
	@echo "✅ Dependências instaladas (CPU-only)!"

.PHONY: install-gpu
install-gpu: venv
	@echo "📦 Instalando dependências (modo GPU/CUDA)..."
	$(PIP) install torch
	$(PIP) install -r polaris_api/requirements.txt
	$(PIP) install -r polaris_integrations/requirements.txt
	@echo "✅ Dependências instaladas (GPU/CUDA)!"

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
	cd polaris_setup/ && docker compose -f mongodb-compose.yml up -d
	@echo "✅ MongoDB e Mongo Express rodando!"

# ------------------------------------------------------------------------------------------
# 🛑 Parar MongoDB e Mongo Express
# ------------------------------------------------------------------------------------------
.PHONY: stop-db
stop-db:
	@echo "🛑 Parando MongoDB e Mongo Express..."
	cd polaris_setup/ && docker compose -f mongodb-compose.yml down
	@echo "✅ MongoDB e Mongo Express parados!"

# ------------------------------------------------------------------------------------------
# 🔄 Reiniciar MongoDB e Mongo Express
# ------------------------------------------------------------------------------------------
.PHONY: restart-db
restart-db:
	@echo "🔄 Reiniciando MongoDB e Mongo Express..."
	$(MAKE) stop-db
	sleep 2
	$(MAKE) start-db
	@echo "✅ Banco de dados reiniciado!"

# ------------------------------------------------------------------------------------------
# 🚀 Rodar API
# ------------------------------------------------------------------------------------------
.PHONY: start-api
start-api:
	@echo "🚀 Iniciando API..."
	cd polaris_api && $(PYTHON) polaris_main.py

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
	$(PYTHON) -m polaris_integrations.main

# ------------------------------------------------------------------------------------------
# 🔄 Rodar tudo
# ------------------------------------------------------------------------------------------
.PHONY: start-all
start-all:
	@echo "🔄 Iniciando tudo..."
	$(MAKE) start-db
	$(MAKE) start-api &
	$(MAKE) start-integrations &
	@echo "✅ Todos os serviços iniciados!"

# ------------------------------------------------------------------------------------------
# 🛑 Parar todos os processos
# ------------------------------------------------------------------------------------------
.PHONY: stop-all
stop-all:
	@echo "🛑 Parando todos os serviços..."
	@pkill -f "python3 polaris_main.py" || true
	@pkill -f "python3 main.py" || true
	@echo "✅ Todos os processos parados!"

# ------------------------------------------------------------------------------------------
# 🔄 Reiniciar tudo
# ------------------------------------------------------------------------------------------
.PHONY: restart-all
restart-all:
	@echo "🔄 Reiniciando tudo..."
	$(MAKE) stop-all
	sleep 2
	$(MAKE) start-all
	@echo "✅ Tudo reiniciado!"

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
# 📝 Criar .env do Polaris Integrations se não existir
# ------------------------------------------------------------------------------------------
.PHONY: create-env-integrations
create-env-integrations:
	@echo "📝 Verificando .env do Polaris Integrations..."
	@if [ ! -f polaris_integrations/.env ]; then \
		echo "⚠️  .env do Integrations não encontrado! Criando um novo..."; \
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
.PHONY: setup-ngrok
setup-ngrok:
	@echo "🌐 Exportando variáveis e iniciando Ngrok..."
	@if [ -f polaris_integrations/.env ]; then \
		export polaris_integrations_PORT=8000; \
		export TELEGRAM_TOKEN=$$(grep "^TELEGRAM_TOKEN" polaris_integrations/.env | cut -d '=' -f2); \
		bash polaris_setup/scripts/setup_ngrok.sh; \
		echo "✅ Ngrok e Webhook configurados!"; \
	else \
		echo "⚠️ .env do Polaris Integrations não encontrado! Rode 'make create-env-integrations' primeiro."; \
		exit 1; \
	fi

.PHONY: stop-ngrok
stop-ngrok:
	@echo "🛑 Parando Ngrok..."
	@pkill -f ngrok || true
	@echo "✅ Ngrok parado!"

.PHONY: restart-ngrok
restart-ngrok:
	@echo "🔄 Reiniciando Ngrok..."
	$(MAKE) stop-ngrok
	sleep 2
	$(MAKE) setup-ngrok
	@echo "✅ Ngrok reiniciado!"

# ------------------------------------------------------------------------------------------
# 🧪 Testes
# ------------------------------------------------------------------------------------------
.PHONY: test
test:
	@echo "🧪 Executando testes unitários..."
	@cd polaris_api && $(PYTHON) -m pytest ../tests/ -v

.PHONY: test-cov
test-cov:
	@echo "📊 Executando testes com cobertura..."
	@cd polaris_api && $(PYTHON) -m pytest ../tests/ --cov=. --cov-report=term-missing

.PHONY: test-watch
test-watch:
	@echo "👀 Executando testes em modo watch..."
	@cd polaris_api && $(PYTHON) -m pytest ../tests/ -f -v

.PHONY: install-test-deps
install-test-deps: venv
	@echo "📦 Instalando dependências de teste..."
	$(PIP) install -r polaris_api/requirements-test.txt

.PHONY: test-ci
test-ci:
	@echo "🚀 Executando testes para CI/CD..."
	@cd polaris_api && $(PYTHON) -m pytest ../tests/ -v --cov=. --cov-report=xml --cov-report=html

# ------------------------------------------------------------------------------------------
# 🔍 Qualidade de código (local)
# ------------------------------------------------------------------------------------------
.PHONY: lint
lint: _check-lint-tools
	@echo "🔍 Verificando qualidade do código..."
	flake8 polaris_api/ --max-line-length=127 --max-complexity=10
	black --check --diff polaris_api/
	isort --check-only --diff polaris_api/
	@echo "✅ Código OK!"

.PHONY: lint-fix
lint-fix: _check-lint-tools
	@echo "🔧 Formatando código..."
	black polaris_api/
	isort polaris_api/
	@echo "✅ Código formatado!"

.PHONY: security
security:
	@echo "🔒 Verificando segurança..."
	bandit -r polaris_api/ -ll
	@echo "✅ Scan de segurança concluído!"

.PHONY: _check-lint-tools
_check-lint-tools:
	@which flake8 > /dev/null 2>&1 || (echo "⚠️  Instale as ferramentas: $(PIP) install flake8 black isort" && exit 1)
	@which black > /dev/null 2>&1  || (echo "⚠️  Instale as ferramentas: $(PIP) install flake8 black isort" && exit 1)
	@which isort > /dev/null 2>&1  || (echo "⚠️  Instale as ferramentas: $(PIP) install flake8 black isort" && exit 1)

.PHONY: ci
ci:
	@echo "🚀 Executando pipeline completo..."
	$(MAKE) lint
	$(MAKE) test-ci
	$(MAKE) security
	@echo "🎉 Pipeline concluído com sucesso!"
