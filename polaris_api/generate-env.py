#!/usr/bin/env python3
"""
Script para gerar arquivo .env com configurações seguras
"""

import os
import secrets
import string

def generate_secret(length=32):
    """Gera uma chave secreta aleatória"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_env_file(domain=None):
    """Gera o arquivo .env com configurações seguras"""
    
    # Gerar chaves secretas únicas
    jwt_secret = generate_secret(48)
    bot_secret = generate_secret(24)
    web_secret = generate_secret(24)
    mobile_secret = generate_secret(24)
    
    # Configurar CORS
    if domain:
        allowed_origins = f'"{domain}"'
    else:
        allowed_origins = '"*"'
    
    env_content = f"""# Model Configuration
USE_LOCAL_LLM=false  # true to use local llama.cpp, false for Groq API
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

# Database Configuration
USE_MONGODB=true
MONGO_URI="mongodb://root:examplepassword@localhost:27017/polaris_db?authSource=admin"

# API Keys
HF_TOKEN="hf_yourhuggingfaceapikey"  # Required for sentence transformers
GROQ_API_KEY="gsk_yourgroqapikey"    # Required for Groq inference

# Monitoring
USE_PUSHGATEWAY=false
PUSHGATEWAY_URL="http://localhost:9091"

# Security Configuration
JWT_SECRET="{jwt_secret}"
JWT_EXPIRY_HOURS=24

# Client Secrets (for API access)
BOT_SECRET="{bot_secret}"
WEB_SECRET="{web_secret}"
MOBILE_SECRET="{mobile_secret}"

# CORS Configuration
ALLOWED_ORIGINS={allowed_origins}  # Development: "*" | Production: "https://yourdomain.com,https://app.yourdomain.com"
"""
    
    # Escrever arquivo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env gerado com sucesso!")
    print(f"🔑 JWT Secret: {jwt_secret}")
    print(f"🤖 Bot Secret: {bot_secret}")
    print(f"🌐 Web Secret: {web_secret}")
    print(f"📱 Mobile Secret: {mobile_secret}")
    print("\n⚠️  IMPORTANTE: Guarde essas chaves em local seguro!")
    print("📝 Configure essas mesmas chaves no frontend e Telegram bot.")

if __name__ == "__main__":
    import sys
    
    # Verificar se foi passado um domínio como argumento
    domain = sys.argv[1] if len(sys.argv) > 1 else None
    
    if domain:
        print(f"🌐 Configurando CORS para: {domain}")
        generate_env_file(domain)
    else:
        print("🌐 Configurando CORS para desenvolvimento (*)")
        generate_env_file()
