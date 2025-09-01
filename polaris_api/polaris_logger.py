import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from colorama import Fore, Style, init

init(autoreset=True)

# Configuração do logging simplificado
class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger('polaris')
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        file_handler = logging.FileHandler('polaris.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter simples
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _log_structured(self, level: str, message: str, session_id: Optional[str] = None, 
                       duration: Optional[float] = None):
        """Log simplificado com contexto essencial"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "session_id": session_id,
            "duration_ms": round(duration * 1000, 2) if duration else None
        }
        
        # Mapear níveis customizados para níveis padrão do logging
        level_mapping = {
            "success": logging.INFO,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR
        }
        
        # Log estruturado para arquivo
        self.logger.log(
            level_mapping.get(level, logging.INFO),
            json.dumps(log_data, ensure_ascii=False)
        )
        
        # Log colorido para console (simplificado)
        color_map = {
            "info": Fore.LIGHTCYAN_EX,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        
        color = color_map.get(level, Fore.WHITE)
        emoji_map = {
            "info": "🔹",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        emoji = emoji_map.get(level, "📝")
        console_msg = f"{color}{emoji} {message}{Style.RESET_ALL}"
        
        if session_id:
            console_msg += f" [Session: {session_id}]"
        if duration:
            console_msg += f" [{duration:.2f}s]"
            
        print(console_msg)

# Instância global do logger
logger = StructuredLogger()

def log_info(message: str, session_id: Optional[str] = None, duration: Optional[float] = None):
    """Log de informação"""
    logger._log_structured("info", message, session_id, duration)

def log_success(message: str, session_id: Optional[str] = None, duration: Optional[float] = None):
    """Log de sucesso"""
    logger._log_structured("success", message, session_id, duration)

def log_warning(message: str, session_id: Optional[str] = None, duration: Optional[float] = None):
    """Log de aviso"""
    logger._log_structured("warning", message, session_id, duration)

def log_error(message: str, session_id: Optional[str] = None, duration: Optional[float] = None):
    """Log de erro"""
    logger._log_structured("error", message, session_id, duration)

def log_request(session_id: str, prompt: str, response: str, duration: float, 
                model_used: str = "unknown"):
    """Log simplificado para requests de inferência"""
    log_success(
        f"Inference completed - Model: {model_used}",
        session_id=session_id,
        duration=duration
    )

def log_request_error(session_id: str, prompt: str, error: str, duration: float):
    """Log simplificado para erros de inferência"""
    log_error(
        f"Inference failed: {error}",
        session_id=session_id,
        duration=duration
    )

# Funções de compatibilidade para manter o código existente
def log_info_simple(message: str):
    """Versão simples para compatibilidade"""
    log_info(message)

def log_success_simple(message: str):
    """Versão simples para compatibilidade"""
    log_success(message)

def log_warning_simple(message: str):
    """Versão simples para compatibilidade"""
    log_warning(message)

def log_error_simple(message: str):
    """Versão simples para compatibilidade"""
    log_error(message)
