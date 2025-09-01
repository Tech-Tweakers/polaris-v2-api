import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from polaris_logger import log_info, log_warning

# Configuração JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

security = HTTPBearer()


class JWTAuth:
    def __init__(self):
        self.secret = JWT_SECRET
        self.algorithm = JWT_ALGORITHM
        self.expiry_hours = JWT_EXPIRY_HOURS

    def create_token(self, user_id: str, user_role: str = "user") -> str:
        """Cria um token JWT"""
        payload = {
            "user_id": user_id,
            "role": user_role,
            "exp": datetime.utcnow() + timedelta(hours=self.expiry_hours),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica um token JWT"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            log_warning("JWT token expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            log_warning("Invalid JWT token")
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Dependency para obter usuário atual"""
        token = credentials.credentials
        return self.verify_token(token)


# Instância global
jwt_auth = JWTAuth()


# Função helper para criar token de API
def create_api_token(client_name: str) -> str:
    """Cria um token para clientes da API"""
    return jwt_auth.create_token(
        user_id=f"api_client_{client_name}", user_role="api_client"
    )


# Middleware para logging de requests
async def log_auth_attempt(request: Request, user_info: Optional[Dict] = None):
    """Log de tentativas de autenticação"""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    if user_info:
        log_info(
            f"Authenticated request from {client_ip} - User: {user_info.get('user_id')}"
        )
    else:
        log_warning(
            f"Unauthenticated request from {client_ip} - User-Agent: {user_agent}"
        )
