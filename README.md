# 🌟 Polaris AI v2.1 – Multi-Modal AI Assistant

<div align="center">

<a href="#"><img src="https://img.shields.io/badge/Polaris-v2.1%20AI%20Assistant-blue?style=for-the-badge&logo=robot" alt="Polaris v2.1 Logo"/></a>
<a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" alt="Python"/></a>
<a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square&logo=fastapi" alt="FastAPI"/></a>
<a href="https://mongodb.com"><img src="https://img.shields.io/badge/MongoDB-4.0-green?style=flat-square&logo=mongodb" alt="MongoDB"/></a>
<a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker" alt="Docker"/></a>
<a href="https://groq.com"><img src="https://img.shields.io/badge/Groq-API-orange?style=flat-square&logo=groq" alt="Groq"/></a>
<a href="https://elevenlabs.io"><img src="https://img.shields.io/badge/ElevenLabs-TTS-purple?style=flat-square&logo=elevenlabs" alt="ElevenLabs"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/></a>

**A sophisticated AI assistant that combines conversational AI, voice synthesis, document processing, and multi-platform integration.**

[![GitHub release](https://img.shields.io/github/v/release/Tech-Tweakers/polaris-v2-api)](https://github.com/Tech-Tweakers/polaris-v2-api/releases)
[![GitHub stars](https://img.shields.io/github/stars/Tech-Tweakers/polaris-v2-api)](https://github.com/Tech-Tweakers/polaris-v2-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Tech-Tweakers/polaris-v2-api)](https://github.com/Tech-Tweakers/polaris-v2-api/network)



</div>

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
  - [🤖 Multi-Modal AI Processing](#-multi-modal-ai-processing)
  - [🧠 Advanced Memory System](#-advanced-memory-system)
  - [🚀 High-Performance Inference](#-high-performance-inference)
  - [🌐 Multi-Platform Integration](#-multi-platform-integration)
  - [🎙️ Advanced Voice Processing](#️-advanced-voice-processing)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
  - [🔧 Prerequisites](#-prerequisites)
  - [🎯 One-Command Setup](#-one-command-setup)
- [🛠️ Manual Installation](#️-manual-installation)
- [⚙️ Configuration](#️-configuration)
  - [.env – Polaris API](#env--polaris-api)
  - [.env – Polaris Integrations](#env--polaris-integrations)
- [🧪 Testing](#-testing)
- [📊 Monitoring & Metrics](#-monitoring--metrics)
- [🔧 Development](#-development)
- [🤝 Contributing](#-contributing)
- [📝 Changelog](#-changelog)
- [❤️ Credits](#-desenvolvido-com--pela-equipe-tech-tweakers)


## 🎯 Overview

**Polaris v2.1** is a next-generation AI assistant that integrates cutting-edge technologies into a unified, scalable platform. It delivers intelligent responses via Telegram, web interfaces, and mobile apps with enhanced voice processing capabilities and improved performance.

### 🆕 What's New in v2.1
- **Enhanced Voice Processing**: Improved TTS engines with better quality and speed
- **Advanced Memory Management**: Optimized memory usage and faster context retrieval
- **Better Error Handling**: More robust error handling and recovery mechanisms
- **Performance Improvements**: Faster inference and reduced latency
- **Enhanced Documentation**: Comprehensive setup and configuration guides


## ✨ Key Features

### 🤖 Multi-Modal AI Processing
- **Text-to-Speech** with multiple engines: ElevenLabs, Coqui XTTS, Groq PlayAI
- **Speech-to-Text** with Whisper integration for voice commands
- **PDF Document Processing** with vectorization and semantic search
- **Image Analysis** with basic support for visual content
- **Multi-language Support** with automatic language detection

### 🧠 Advanced Memory System
- **Dual-layer Memory Architecture**: Short-term + long-term memory layers
- **Persistent Storage**: MongoDB-based memory persistence
- **Semantic Search**: ChromaDB integration for intelligent context retrieval
- **LangChain Integration**: Advanced context preservation and management
- **Keyword Extraction**: Automatic keyword identification and storage

### 🚀 High-Performance Inference
- **Local Model Support**: llama.cpp integration for offline inference
- **Cloud Inference**: Groq API integration for high-speed cloud processing
- **Configurable Parameters**: Temperature, top-p, top-k, frequency penalty
- **Multi-core Optimization**: Optimized for multi-core systems
- **Model Switching**: Dynamic model selection based on requirements

### 🌐 Multi-Platform Integration
- **Telegram Bot**: Full-featured bot with voice and text support
- **REST API**: Comprehensive API for third-party integrations
- **Web UI Support**: Ready for web interface development
- **Mobile-Ready**: Optimized architecture for mobile applications
- **Webhook Support**: Real-time communication capabilities

### 🎙️ Advanced Voice Processing
- **Multiple TTS Engines**: ElevenLabs, Coqui XTTS, Groq PlayAI
- **Voice Cloning**: Custom voice training and cloning capabilities
- **Audio Processing**: Advanced audio manipulation and enhancement
- **Real-time Streaming**: Low-latency voice streaming
- **Voice Quality Optimization**: Enhanced audio quality and clarity


## 📁 Project Structure

```
polaris-v2-api/
├── 🚀 polaris_api/          # Core Polaris API (LLM, Prompt, Memory)
│   ├── polaris_main.py         # 🔧 Main API logic and request handling
│   ├── polaris_logger.py       # 📜 Structured logging for requests/events
│   ├── polaris_keywords.py     # 🧠 Long-term keyword memory system
│   ├── polaris_prompt.py       # 🎯 AI instruction and system prompts
│   ├── llm_loader.py           # 🔁 LLM router and model selection logic
│   ├── llm_local.py            # 🏠 Local inference via llama.cpp
│   ├── llm_groq.py             # ☁️ Remote inference via Groq API
│   ├── requirements.txt        # 📦 Python dependencies
│   ├── env-example.txt         # 🔐 Environment variables template
│   └── polaris.log             # 📋 Application logs
├── 🔗 polaris_integrations/ # Bridges to external services (voice, audio, etc.)
│   ├── main.py                 # 🔌 Entry point for integrations (TTS, Telegram, etc.)
│   ├── tts_router.py           # 🗣️ Smart TTS engine dispatcher
│   ├── tts_engines/
│   │ ├── coqui.py              # 🎙️ Local voice synthesis (XTTS)
│   │ ├── eleven.py             # 🎧 ElevenLabs cloud-based TTS
│   │ └── groq.py               # 🎤 Groq PlayAI TTS integration
│   ├── polaris-voice.wav       # 🎼 Custom voice reference sample
│   ├── requirements.txt        # 📦 Integration dependencies
│   └── env-example.txt         # 🔐 Integration environment config
├── 🐳 polaris_setup/        # Infrastructure, benchmarking, and OS prep
│   ├── data-flush.py           # 🛠️ Memory cleanup and maintenance script
│   ├── mongodb-compose.yml     # 🗄️ MongoDB container orchestration
│   └── polaris-os-tunner.sh    # 🛠️ System tuning script (Debian/Ubuntu)
├── 📖 local-setup.sh           # 🚀 Interactive one-command setup script
├── 🧪 Makefile                 # 🛠️ Dev workflow commands and automation
├── 📋 .gitignore               # 🚫 Git ignore patterns
└── 📖 README.md                # 📚 This documentation
```

### 🌐 API Endpoints

**Polaris API (Port 8000):**
- `POST /inference/` - Main inference endpoint (requires JWT auth)
- `POST /upload-pdf/` - PDF document processing
- `GET /health` - System health check
- `POST /auth/token` - Get JWT token
- `GET /auth/verify` - Verify JWT token

**Polaris Integrations (Port 8010):**
- `POST /audio-inference/` - Audio processing with STT + TTS
- `GET /audio/{filename}` - Audio file access
- `GET /metrics` - Prometheus metrics


## 🚀 Quick Start

### 🔧 Prerequisites

- **Python 3.10+** (recommended: 3.11)
- **Docker & Docker Compose** (for MongoDB)
- **8GB+ RAM** (for local inference)
- **NVIDIA GPU** (optional, for accelerated inference)
- **FFmpeg** (for audio processing)

### 🎯 One-Command Setup

```bash
git clone https://github.com/Tech-Tweakers/polaris-v2-api.git
cd polaris-v2-api
chmod +x local-setup.sh
./local-setup.sh
```

The interactive setup will:
- ✅ Install all dependencies
- ✅ Create environment files (.env)
- ✅ Download AI models (LLaMA 3 8B)
- ✅ Start MongoDB container
- ✅ Configure webhooks
- ✅ Launch all services

### 🎮 Interactive Menu

The `local-setup.sh` provides an interactive menu with options:

```
==================================
      🚀 Polaris v2.1 - Menu        
==================================
1) 🛠️  Configuração inicial (Instalar dependências)
2) 📝  Criar .env para API e Bot
3) 🤖  Baixar modelo LLaMA 3
4) 🐳  Subir MongoDB e Mongo Express
5) 🌍  Configurar Ngrok + Webhook Telegram
6) 🚀  Iniciar Polaris API
7) 🤖  Iniciar Polaris Integrations
8) 🔄  Iniciar tudo (DB, API, Integrations, Ngrok)
9) 🛑  Parar tudo
10) 🔄 Reiniciar tudo
0) ❌  Sair
```


## 🛠️ Manual Installation

<details>
<summary>Click to view manual installation instructions</summary>

**1. Setup Dependencies**

```bash
make install
```

**2. Create Environment Files**

```bash
# Criar .env com chaves seguras
make create-env-api

# Se precisar regenerar as chaves
make regenerate-env-api

# Criar .env do bot
make create-env-bot
```

**3. Download LLM Model for Local Inference**

```bash
make download-model
```

**4. Setup and Start MongoDB**

```bash
make start-db
```

**5. Start All Services**

```bash
make start-all
```

**6. Verify Installation**

```bash
# Test main API
curl -X POST http://localhost:8000/inference/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, Polaris!", "session_id": "test123"}'

# Test health check
curl http://localhost:8000/health

# Test integrations API
curl http://localhost:8010/metrics
```

</details>


## ⚙️ Configuration

### `.env` – Polaris API

```env
# Model Configuration
MODEL_PATH="../models/llama3-7B.safetensors"
NUM_CORES=16
MODEL_CONTEXT_SIZE=4096
MODEL_BATCH_SIZE=8

# Memory and Context Settings
MONGODB_HISTORY=4
LANGCHAIN_HISTORY=10

# LLM Hyperparameters
TEMPERATURE=0.3
TOP_P=0.7
TOP_K=70
FREQUENCY_PENALTY=3

# Database Connections
USE_MONGODB=true
MONGO_URI="mongodb://root:examplepassword@localhost:27017/polaris_db?authSource=admin"

# API Keys
HF_TOKEN="hf_yourhuggingfaceapikey"  # Required for sentence transformers
GROQ_API_KEY="gsk_yourgroqapikey"    # Required for Groq inference

# Monitoring
USE_PUSHGATEWAY=false
```

### `.env` – Polaris Integrations

```env
# Telegram Configuration
TELEGRAM_TOKEN="your_telegram_bot_token"
POLARIS_API_URL="http://localhost:8000/inference/"

# TTS Engine Selection
TTS_ENGINE="coqui"  # Options: eleven / coqui / groq

# ElevenLabs Configuration
ELEVEN_API_KEY="your_elevenlabs_api_key"
ELEVEN_VOICE_ID="yM93hbw8Qtvdma2wCnJG"
ELEVEN_MODEL_ID="eleven_multilingual_v2"

# Groq Configuration
GROQ_API_KEY="gsk_your-groq-api-key"

# Coqui Configuration
COQUI_SPEAKER_WAV="polaris-voice.wav"

# Public URL (for webhooks)
PUBLIC_URL="https://your-ngrok-url.ngrok.io"

# HuggingFace Token
HF_TOKEN="hf_yourhuggingfaceapikey"
```


## 🧪 Testing

### API Testing

**Get JWT Token:**

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "polaris_bot",
    "client_secret": "bot-secret"
  }'
```

**Basic Inference Test (with JWT):**

```bash
# First get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_name": "polaris_bot", "client_secret": "bot-secret"}' | jq -r '.access_token')

# Then use token
curl -X POST http://localhost:8000/inference/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Hello, Polaris! How are you today?",
    "session_id": "test123"
  }'
```

**PDF Upload Test:**

```bash
curl -X POST http://localhost:8000/upload-pdf/ \
  -F "file=@document.pdf" \
  -F "session_id=test123"
```

### Integrations Testing

**Audio Inference Test:**

```bash
curl -X POST http://localhost:8010/audio-inference/ \
  -F "audio=@voice_message.webm" \
  -F "session_id=test123"
```

**Audio File Access:**

```bash
curl http://localhost:8010/audio/filename.mp3
```

**Metrics Endpoint:**

```bash
curl http://localhost:8010/metrics
```

### Telegram Bot Testing

1. Start the integrations service: `make start-integrations`
2. Send a message to your Telegram bot
3. Check logs for response confirmation


## 📊 Monitoring & Metrics

### Logging

Polaris uses structured logging with different levels:
- **INFO**: General application events
- **DEBUG**: Detailed debugging information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors

### Metrics

The system provides metrics for:
- Request/response times
- Memory usage
- Model inference performance
- Error rates
- TTS processing times

### Health Checks

```bash
# API Health Check
curl http://localhost:8000/health

# MongoDB Health Check
curl http://localhost:27017

# Metrics Check
curl http://localhost:8010/metrics
```


## 🔧 Development

### Available Make Commands

```bash
# Installation
make install              # Install all dependencies
make setup               # Initial system setup

# Model Management
make download-model      # Download LLaMA 3 model
make clean-models        # Remove downloaded models

# Database Management
make start-db           # Start MongoDB
make stop-db            # Stop MongoDB
make restart-db         # Restart MongoDB

# Service Management
make start-api          # Start Polaris API
make start-integrations # Start Polaris Integrations
make start-all          # Start all services
make stop-all           # Stop all services
make restart-all        # Restart all services

# Environment Setup
make create-env-api     # Create API .env file with secure keys
make regenerate-env-api # Regenerate API .env with new keys
make create-env-bot     # Create Integrations .env file

# Development
make test               # Run tests
make lint               # Run linting
make format             # Format code
```

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**: `make test`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX improvements
- 🔧 Performance optimizations

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions
- Include type hints where appropriate
- Write comprehensive tests

---

## ❤️ Credits

Developed with ❤️ by **Tech-Tweakers** team.

### Acknowledgments
- **Groq** for high-performance inference
- **ElevenLabs** for voice synthesis
- **HuggingFace** for model hosting
- **MongoDB** for database solutions
- **FastAPI** for the web framework

---

<div align="center">

**🌟 Star this repository if you find it useful! 🌟**

[![GitHub stars](https://img.shields.io/github/stars/Tech-Tweakers/polaris-v2-api?style=social)](https://github.com/Tech-Tweakers/polaris-v2-api/stargazers)

</div>

