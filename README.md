# 🌟 Polaris AI v3 – Advanced Multi-Modal AI Assistant

<div align="center">

<a href="#"><img src="https://img.shields.io/badge/Polaris-AI%20Assistant-blue?style=for-the-badge&logo=robot" alt="Polaris Logo"/></a>
<a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" alt="Python"/></a>
<a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square&logo=fastapi" alt="FastAPI"/></a>
<a href="https://mongodb.com"><img src="https://img.shields.io/badge/MongoDB-6.0-green?style=flat-square&logo=mongodb" alt="MongoDB"/></a>
<a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker" alt="Docker"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/></a>

<br><br>

**A sophisticated AI assistant that combines conversational AI, voice synthesis, document processing, and multi-platform integration.**

</div>
---

## 🧭 Índice

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
  - [🤖 Multi-Modal AI Processing](#-multi-modal-ai-processing)
  - [🧠 Advanced Memory System](#-advanced-memory-system)
  - [🚀 High-Performance Inference](#-high-performance-inference)
  - [🌐 Multi-Platform Integration](#-multi-platform-integration)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
  - [🔧 Prerequisites](#-prerequisites)
  - [🎯 One-Command Setup](#-one-command-setup)
- [🛠️ Manual Installation](#️-manual-installation)
- [⚙️ Configuration](#️-configuration)
  - [.env – Polaris API](#env--polaris-api)
  - [.env – Polaris Integrations](#env--polaris-integrations)
- [🧪 Testing](#-testing)
- [❤️ Credits](#-desenvolvido-com--pela-equipe-tech-tweakers)

---

## 🎯 Overview

**Polaris** is a next-generation AI assistant that integrates cutting-edge technologies into a unified, scalable platform. It delivers intelligent responses via Telegram, web interfaces, and mobile apps.

---

## ✨ Key Features

### 🤖 Multi-Modal AI Processing
- Text-to-speech with multiple engines: ElevenLabs, Coqui, Groq  
- Speech-to-text with Whisper  
- PDF document ingestion and vectorization  
- Image analysis (basic support)

### 🧠 Advanced Memory System
- Dual-layer memory (short-term + long-term)  
- Persistent memory via MongoDB  
- Semantic search via ChromaDB  
- LangChain integration for context preservation

### 🚀 High-Performance Inference
- Local model support via `llama.cpp`  
- Remote inference with Groq API (LLaMA 3 70B)  
- Configurable inference parameters  
- Optimized for multi-core systems

### 🌐 Multi-Platform Integration
- Telegram bot  
- REST API  
- Web UI support  
- Mobile-ready architecture

---

## 📁 Project Structure

```
polaris-v3/
├── 🚀 polaris_api/          # Core Polaris API (LLM, Prompt, Memory)
│   ├── polaris_main.py         # 🔧 Main API logic and request handling
│   ├── polaris_logger.py       # 📜 Structured logging for requests/events
│   ├── polaris_keywords.py     # 🧠 Long-term keyword memory system
│   ├── polaris_prompt.py       # 🎯 AI instruction and system prompts
│   ├── llm_loader.py           # 🔁 LLM router and model selection logic
│   ├── llm_local.py            # 🏠 Local inference via llama.cpp
│   ├── llm_groq.py             # ☁️ Remote inference via Groq API
│   ├── requirements.txt        # 📦 Python dependencies
│   └── .env                    # 🔐 API environment variables
├── 🔗 polaris_integrations/ # Bridges to external services (voice, audio, etc.)
│   ├── main.py                 # 🔌 Entry point for integrations (TTS, Telegram, etc.)
│   ├── tts_router.py           # 🗣️ Smart TTS engine dispatcher
│   ├── tts_engines/
│   │ ├── coqui.py              # 🎙️ Local voice synthesis (XTTS)
│   │ ├── eleven.py             # 🎧 ElevenLabs cloud-based TTS
│   │ └── groq.py               # 🎤 Groq PlayAI TTS integration
│   ├── polaris-voice.wav       # 🎼 Custom voice reference sample
│   ├── requirements.txt        # 📦 Integration dependencies
│   └── .env                    # 🔐 Integration environment config
├── 🐳 polaris_setup/        # Infra, benchmarking, and OS prep
│   ├── data-flush.yml          # 🛠️ Clean UP Memory Script
│   ├── mongodb-compose.yml     # 🗄️ MongoDB container orchestration
│   ├── polaris-os-tunner.sh    # 🛠️ System tuning script (Debian/Ubuntu)
│   ├── polaris-real-tests.py   # 🧪 Realistic conversational stress test
│   └── polaris-stress-tests.py # 📈 Multi-session synthetic load tester
├── 📖 local-setup.sh           # 🚀 Interactive one-command setup script
└── 🧪 Makefile                 # 🛠️ Dev workflow commands and automation
```

---

## 🚀 Quick Start

### 🔧 Prerequisites

- Python 3.10+  
- Docker & Docker Compose  
- 16GB+ RAM (for local inference)  
- NVIDIA GPU (opcional)

### 🎯 One-Command Setup

```bash
git clone https://github.com/Tech-Tweakers/polaris-v3.git
cd polaris-v3
./local-setup.sh
```

The interactive setup will:
- Install dependencies
- Create .env files
- Download AI models
- Start all services
- Configure webhooks
- Launch the application

---

## 🛠️ Manual Installation

<details>
<summary>Click to view manual installation instructions</summary>

**1. Setup Dependencies**

```bash
make install
```

**2. Create Environment Files*

```bash
make create-env-api
make create-env-bot
```

**3. Download LLM Model for Local Inferences**

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

</details>

---

## ⚙️ Configuration

### `.env` – Polaris API

```env
# Model settings
USE_LOCAL_LLM=False

MODEL_PATH="../models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
NUM_CORES=16
MODEL_CONTEXT_SIZE=4096
MODEL_BATCH_SIZE=1

# Configuração de histórico
MONGODB_HISTORY=10
LANGCHAIN_HISTORY=20

# Hiperparâmetros do modelo
TEMPERATURE=0.3
TOP_P=0.7
TOP_K=70
FREQUENCY_PENALTY=3

# Configuração do MongoDB
MONGO_URI="mongodb://admin:admin123@localhost:27017/polaris_db?authSource=admin"
HF_TOKEN="hf_your-api-key"
GROQ_API_KEY="gsk_your-api-key"
```

### `.env` – Polaris Integrations

```env
TELEGRAM_TOKEN="098098098:your-telegram-bot-token"
POLARIS_API_URL="http://192.168.1.104:8000/inference/"
HF_TOKEN="hf_your-huggingface-api-key"
COQUI_SPEAKER_WAV="polaris-voice.wav"
PUBLIC_URL="https://suitable-actually-kw-rescue.trycloudflare.com"

TTS_ENGINE="eleven"  # or coqui or groq

ELEVEN_API_KEY="sk_your-eleven-labs-api-key"
ELEVEN_VOICE_ID="yM93hbw8Qtvdma2wCnJG"
ELEVEN_MODEL_ID="eleven_multilingual_v2"

GROQ_API_KEY="gsk_your-groq-api-key"
```

---

## 🧪 Testing

**API Test:**

```bash
curl -X POST http://localhost:8000/inference/   -H "Content-Type: application/json"   -d '{"prompt": "Hello, Polaris!", "session_id": "test123"}'
```
---

Developed with ❤️ by **Tech-Tweakers** team.

