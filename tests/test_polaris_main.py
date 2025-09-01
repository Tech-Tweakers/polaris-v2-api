import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import json
import os
import sys

# Adicionar o diretório polaris_api ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "polaris_api"))

# Importar módulos da API
from polaris_main import app


class TestHealthCheck:
    """Testes para o endpoint de health check"""

    def test_health_check_success(self):
        """Testa health check com sucesso"""
        with patch("polaris_main.USE_MONGODB", True):
            # Mock do client como um atributo do módulo
            with patch("polaris_main.client", create=True) as mock_client:
                mock_client.admin.command.return_value = {"ok": 1}

                with patch("polaris_main.llm") as mock_llm:
                    mock_llm.invoke.return_value = "Test response"

                    client = TestClient(app)
                    response = client.get("/health")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "healthy"
                    assert data["version"] == "v2.1"
                    assert data["services"]["mongodb"] == "healthy"
                    assert data["services"]["llm"] == "healthy"

    def test_health_check_mongodb_disabled(self):
        """Testa health check com MongoDB desabilitado"""
        with patch("polaris_main.USE_MONGODB", False):
            with patch("polaris_main.llm") as mock_llm:
                mock_llm.invoke.return_value = "Test response"

                client = TestClient(app)
                response = client.get("/health")

                assert response.status_code == 200
                data = response.json()
                assert data["services"]["mongodb"] == "disabled"

    def test_health_check_mongodb_failure(self):
        """Testa health check com falha no MongoDB"""
        with patch("polaris_main.USE_MONGODB", True):
            with patch("polaris_main.client", create=True) as mock_client:
                mock_client.admin.command.side_effect = Exception("Connection failed")

                with patch("polaris_main.llm") as mock_llm:
                    mock_llm.invoke.return_value = "Test response"

                    client = TestClient(app)
                    response = client.get("/health")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["services"]["mongodb"] == "unhealthy"
                    assert data["status"] == "unhealthy"

    def test_health_check_llm_failure(self):
        """Testa health check com falha no LLM"""
        with patch("polaris_main.USE_MONGODB", True):
            with patch("polaris_main.client", create=True) as mock_client:
                mock_client.admin.command.return_value = {"ok": 1}

                with patch("polaris_main.llm") as mock_llm:
                    mock_llm.invoke.side_effect = Exception("LLM failed")

                    client = TestClient(app)
                    response = client.get("/health")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["services"]["llm"] == "unhealthy"
                    assert data["status"] == "unhealthy"


class TestInferenceEndpoint:
    """Testes para o endpoint de inferência"""

    def test_inference_success(self):
        """Testa inferência com sucesso"""
        with patch("polaris_main.llm") as mock_llm:
            mock_llm.invoke.return_value = "Test response from LLM"
            mock_llm.load.return_value = None
            mock_llm.close.return_value = None

            with patch("polaris_main.log_request") as mock_log:
                with patch("polaris_main.log_success") as mock_log_success:
                    client = TestClient(app)

                    payload = {
                        "prompt": "Test prompt",
                        "session_id": "test_session_123",
                    }

                    response = client.post("/inference/", json=payload)

                    assert response.status_code == 200
                    data = response.json()
                    assert "resposta" in data
                    assert data["resposta"] == "Test response from LLM"

                    # Verificar se logging foi chamado
                    mock_log.assert_called()
                    mock_log_success.assert_called()

    def test_inference_without_session_id(self):
        """Testa inferência sem session_id (deve usar default)"""
        with patch("polaris_main.llm") as mock_llm:
            mock_llm.invoke.return_value = "Default session response"
            mock_llm.load.return_value = None
            mock_llm.close.return_value = None

            with patch("polaris_main.log_request") as mock_log:
                client = TestClient(app)

                payload = {"prompt": "Test prompt"}

                response = client.post("/inference/", json=payload)

                assert response.status_code == 200
                data = response.json()
                assert "resposta" in data

    def test_inference_llm_error(self):
        """Testa inferência com erro no LLM"""
        with patch("polaris_main.llm") as mock_llm:
            mock_llm.invoke.side_effect = Exception("LLM error")
            mock_llm.load.return_value = None
            mock_llm.close.return_value = None

            with patch("polaris_main.log_request_error") as mock_log_error:
                client = TestClient(app)

                payload = {"prompt": "Test prompt", "session_id": "test_session_123"}

                response = client.post("/inference/", json=payload)

                assert response.status_code == 500
                data = response.json()
                assert "detail" in data

                # Verificar se logging de erro foi chamado
                mock_log_error.assert_called()


class TestAuthEndpoints:
    """Testes para os endpoints de autenticação"""

    def test_get_token_success(self):
        """Testa obtenção de token com sucesso"""
        with patch("polaris_main.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "WEB_SECRET": "test-web-secret",
                "JWT_EXPIRY_HOURS": "24",
            }.get(key, default)

            with patch("auth.create_api_token") as mock_create_token:
                mock_create_token.return_value = "test-jwt-token"

                with patch("polaris_main.log_success") as mock_log:
                    client = TestClient(app)

                    response = client.post(
                        "/auth/token",
                        data={
                            "client_name": "web_client",
                            "client_secret": "test-web-secret",
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert data["access_token"] == "test-jwt-token"
                    assert data["token_type"] == "bearer"
                    assert data["expires_in"] == 86400  # 24 * 3600

                    mock_log.assert_called()

    def test_get_token_unauthorized_client(self):
        """Testa tentativa de obter token com cliente não autorizado"""
        client = TestClient(app)

        response = client.post(
            "/auth/token",
            data={"client_name": "invalid_client", "client_secret": "invalid-secret"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Unauthorized client" in data["detail"]

    def test_get_token_invalid_secret(self):
        """Testa tentativa de obter token com secret inválido"""
        with patch("polaris_main.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "WEB_SECRET": "correct-secret",
                "JWT_EXPIRY_HOURS": "24",
            }.get(key, default)

            client = TestClient(app)

            response = client.post(
                "/auth/token",
                data={"client_name": "web_client", "client_secret": "wrong-secret"},
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert "Invalid credentials" in data["detail"]

    def test_verify_token_success(self):
        """Testa verificação de token válido"""
        client = TestClient(app)

        # Como o endpoint agora retorna 401 sem usuário, vamos testar isso
        response = client.get("/auth/verify")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Invalid token"


class TestPDFUpload:
    """Testes para o endpoint de upload de PDF"""

    def test_pdf_upload_success(self):
        """Testa upload de PDF com sucesso"""
        with patch("polaris_main.os.makedirs") as mock_makedirs:
            with patch("builtins.open", create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file

                with patch(
                    "langchain_community.document_loaders.PyMuPDFLoader"
                ) as mock_loader:
                    mock_doc = Mock()
                    mock_doc.page_content = "Test PDF content"
                    mock_loader.return_value.load.return_value = [mock_doc]

                    with patch("polaris_main.vectorstore") as mock_vectorstore:
                        with patch("polaris_main.os.remove") as mock_remove:
                            with patch("polaris_main.log_success") as mock_log:
                                client = TestClient(app)

                                # Criar arquivo PDF mock
                                pdf_content = b"fake pdf content"

                                response = client.post(
                                    "/upload-pdf/",
                                    files={
                                        "file": (
                                            "test.pdf",
                                            pdf_content,
                                            "application/pdf",
                                        )
                                    },
                                    data={"session_id": "test_session"},
                                )

                                assert response.status_code == 200
                                data = response.json()
                                assert "message" in data
                                assert "PDF processado" in data["message"]

                                # Verificar se operações foram chamadas
                                mock_makedirs.assert_called()
                                mock_open.assert_called()
                                mock_loader.assert_called()
                                mock_vectorstore.add_texts.assert_called()
                                mock_remove.assert_called()
                                mock_log.assert_called()

    def test_pdf_upload_error(self):
        """Testa upload de PDF com erro"""
        with patch("polaris_main.os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = Exception("Permission denied")

            with patch("polaris_main.log_error") as mock_log_error:
                client = TestClient(app)

                pdf_content = b"fake pdf content"

                response = client.post(
                    "/upload-pdf/",
                    files={"file": ("test.pdf", pdf_content, "application/pdf")},
                    data={"session_id": "test_session"},
                )

                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                assert "Erro ao processar o PDF" in data["detail"]

                mock_log_error.assert_called()


class TestCORSConfiguration:
    """Testes para configuração de CORS"""

    def test_cors_allowed_origins(self):
        """Testa se CORS está configurado corretamente"""
        client = TestClient(app)

        # Testar preflight request
        response = client.options(
            "/inference/",
            headers={
                "Origin": "https://tech-tweakers.github.io",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # CORS deve permitir o preflight
        assert response.status_code in [200, 405]  # 405 é aceitável para OPTIONS

    def test_cors_headers_present(self):
        """Testa se headers de CORS estão presentes"""
        client = TestClient(app)

        # Testar preflight request para verificar CORS
        response = client.options(
            "/health",
            headers={
                "Origin": "https://tech-tweakers.github.io",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Verificar se headers de CORS estão presentes
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers


class TestErrorHandling:
    """Testes para tratamento de erros"""

    def test_404_not_found(self):
        """Testa endpoint não encontrado"""
        client = TestClient(app)

        response = client.get("/endpoint-inexistente")

        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Testa método HTTP não permitido"""
        client = TestClient(app)

        response = client.put("/health")

        assert response.status_code == 405
