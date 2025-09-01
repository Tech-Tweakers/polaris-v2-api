import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

# Importar módulos da API
from auth import JWTAuth, create_api_token, log_auth_attempt


class TestJWTAuth:
    """Testes para a classe JWTAuth"""

    def test_jwt_auth_initialization(self, mock_jwt_env):
        """Testa inicialização da classe JWTAuth"""
        # Forçar o mock das variáveis de ambiente
        import os

        os.environ["JWT_SECRET"] = "test-jwt-secret-key"
        os.environ["JWT_EXPIRY_HOURS"] = "24"

        # Recarregar o módulo para pegar as novas variáveis
        import importlib
        import auth

        importlib.reload(auth)

        auth = auth.JWTAuth()
        assert auth.secret == "test-jwt-secret-key"
        assert auth.algorithm == "HS256"
        assert auth.expiry_hours == 24

    def test_create_token_success(self, mock_env_vars):
        """Testa criação de token JWT com sucesso"""
        auth = JWTAuth()
        token = auth.create_token("user123", "admin")

        assert token is not None
        assert len(token) > 20

        # Decodificar token para verificar payload
        payload = jwt.decode(token, auth.secret, algorithms=[auth.algorithm])
        assert payload["user_id"] == "user123"
        assert payload["role"] == "admin"
        assert payload["iat"] is not None
        assert payload["exp"] is not None

    def test_create_token_default_role(self, mock_env_vars):
        """Testa criação de token com role padrão"""
        auth = JWTAuth()
        token = auth.create_token("user456")

        payload = jwt.decode(token, auth.secret, algorithms=[auth.algorithm])
        assert payload["role"] == "user"

    def test_verify_token_success(self, mock_env_vars):
        """Testa verificação de token válido"""
        auth = JWTAuth()
        token = auth.create_token("user123", "admin")

        payload = auth.verify_token(token)
        assert payload["user_id"] == "user123"
        assert payload["role"] == "admin"

    def test_verify_token_expired(self, mock_env_vars):
        """Testa verificação de token expirado"""
        auth = JWTAuth()

        # Criar token expirado
        payload = {
            "user_id": "user123",
            "role": "admin",
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(payload, auth.secret, algorithm=auth.algorithm)

        with pytest.raises(HTTPException) as exc_info:
            auth.verify_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "Token expired" in str(exc_info.value.detail)

    def test_verify_token_invalid(self, mock_env_vars):
        """Testa verificação de token inválido"""
        auth = JWTAuth()

        with pytest.raises(HTTPException) as exc_info:
            auth.verify_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    @patch("auth.log_warning")
    def test_verify_token_expired_logs_warning(self, mock_log, mock_env_vars):
        """Testa se erro de token expirado é logado"""
        auth = JWTAuth()

        payload = {
            "user_id": "user123",
            "role": "admin",
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(payload, auth.secret, algorithm=auth.algorithm)

        with pytest.raises(HTTPException):
            auth.verify_token(expired_token)

        mock_log.assert_called_once_with("JWT token expired")

    @patch("auth.log_warning")
    def test_verify_token_invalid_logs_warning(self, mock_log, mock_env_vars):
        """Testa se erro de token inválido é logado"""
        auth = JWTAuth()

        with pytest.raises(HTTPException):
            auth.verify_token("invalid_token")

        mock_log.assert_called_once_with("Invalid JWT token")


class TestCreateApiToken:
    """Testes para função create_api_token"""

    def test_create_api_token_success(self, mock_env_vars):
        """Testa criação de token para API"""
        token = create_api_token("test_client")

        assert token is not None
        assert len(token) > 20

        # Verificar se o token pode ser decodificado
        auth = JWTAuth()
        payload = auth.verify_token(token)
        assert payload["user_id"] == "api_client_test_client"
        assert payload["role"] == "api_client"


class TestLogAuthAttempt:
    """Testes para função log_auth_attempt"""

    @pytest.mark.asyncio
    @patch("auth.log_info")
    async def test_log_auth_attempt_authenticated(self, mock_log, mock_env_vars):
        """Testa logging de tentativa autenticada"""
        mock_request = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers.get.return_value = "test-user-agent"

        user_info = {"user_id": "user123", "role": "admin"}

        await log_auth_attempt(mock_request, user_info)

        mock_log.assert_called_once_with(
            "Authenticated request from 192.168.1.100 - User: user123"
        )

    @pytest.mark.asyncio
    @patch("auth.log_warning")
    async def test_log_auth_attempt_unauthenticated(self, mock_log, mock_env_vars):
        """Testa logging de tentativa não autenticada"""
        mock_request = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers.get.return_value = "test-user-agent"

        await log_auth_attempt(mock_request)

        mock_log.assert_called_once_with(
            "Unauthenticated request from 192.168.1.100 - User-Agent: test-user-agent"
        )

    @pytest.mark.asyncio
    async def test_log_auth_attempt_no_client_info(self, mock_env_vars):
        """Testa logging quando não há informações do cliente"""
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers.get.return_value = "test-user-agent"

        # Não deve dar erro
        await log_auth_attempt(mock_request)
