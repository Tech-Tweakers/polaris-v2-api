import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
import os
import sys

# Adicionar o diretório polaris_api ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'polaris_api'))

@pytest.fixture
def mock_env_vars():
    """Mock das variáveis de ambiente"""
    env_vars = {
        "USE_LOCAL_LLM": "false",
        "MONGODB_HISTORY": "4",
        "LANGCHAIN_HISTORY": "10",
        "TEMPERATURE": "0.3",
        "TOP_P": "0.7",
        "TOP_K": "70",
        "FREQUENCY_PENALTY": "3",
        "USE_MONGODB": "true",
        "MONGO_URI": "mongodb://test:test@localhost:27017/test",
        "HF_TOKEN": "test_token",
        "GROQ_API_KEY": "test_groq_key",
        "USE_PUSHGATEWAY": "false",
        "PUSHGATEWAY_URL": "http://localhost:9091",
        "JWT_SECRET": "test-jwt-secret-key",
        "JWT_EXPIRY_HOURS": "24",
        "BOT_SECRET": "test-bot-secret",
        "WEB_SECRET": "test-web-secret",
        "MOBILE_SECRET": "test-mobile-secret",
        "ALLOWED_ORIGINS": "https://tech-tweakers.github.io,https://*.trycloudflare.com"
    }
    
    with pytest.MonkeyPatch().context() as m:
        for key, value in env_vars.items():
            m.setenv(key, value)
        yield env_vars

@pytest.fixture
def mock_jwt_env():
    """Mock específico para JWT"""
    with pytest.MonkeyPatch().context() as m:
        m.setenv("JWT_SECRET", "test-jwt-secret-key")
        m.setenv("JWT_EXPIRY_HOURS", "24")
        yield
    # Restaurar variáveis originais
    with pytest.MonkeyPatch().context() as m:
        m.delenv("JWT_SECRET", raising=False)
        m.delenv("JWT_EXPIRY_HOURS", raising=False)

@pytest.fixture
def mock_mongodb():
    """Mock do MongoDB"""
    mock_client = Mock()
    mock_db = Mock()
    mock_collection = Mock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    return mock_client, mock_db, mock_collection

@pytest.fixture
def mock_mongodb_client():
    """Mock específico do client do MongoDB"""
    mock_client = Mock()
    mock_client.admin.command.return_value = {"ok": 1}
    return mock_client

@pytest.fixture
def mock_llm():
    """Mock do LLM"""
    mock_llm = Mock()
    mock_llm.invoke.return_value = "Test response"
    mock_llm.load.return_value = None
    mock_llm.close.return_value = None
    return mock_llm

@pytest.fixture
def mock_vectorstore():
    """Mock do VectorStore"""
    mock_vs = Mock()
    mock_vs.add_texts.return_value = ["doc1", "doc2"]
    return mock_vs

@pytest.fixture
def mock_embeddings():
    """Mock dos embeddings"""
    mock_emb = Mock()
    mock_emb.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return mock_emb

@pytest.fixture
def mock_fastapi_app():
    """Mock da aplicação FastAPI"""
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return app

@pytest.fixture
def mock_llm():
    """Mock do LLM para testes da API"""
    mock_llm = Mock()
    mock_llm.invoke.return_value = "Test response from LLM"
    mock_llm.load.return_value = None
    mock_llm.close.return_value = None
    return mock_llm

@pytest.fixture
def mock_vectorstore():
    """Mock do VectorStore para testes da API"""
    mock_vs = Mock()
    mock_vs.add_texts.return_value = ["doc1", "doc2"]
    return mock_vs
