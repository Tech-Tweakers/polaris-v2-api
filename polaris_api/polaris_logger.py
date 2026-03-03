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
        self.logger = logging.getLogger("polaris")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Evita duplicação com o root logger

        # Limpa handlers existentes para evitar duplicação em reloads
        self.logger.handlers.clear()

        # Handler para arquivo (JSON estruturado)
        file_handler = logging.FileHandler("polaris.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _log_structured(
        self,
        level: str,
        message: str,
        session_id: Optional[str] = None,
        duration: Optional[float] = None,
        prompt_chars: Optional[int] = None,
        prompt_tokens_est: Optional[int] = None,
    ):
        """Log simplificado com contexto essencial"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
        }

        if session_id:
            log_data["session_id"] = session_id
        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)
        if prompt_chars is not None:
            log_data["prompt_chars"] = prompt_chars
        if prompt_tokens_est is not None:
            log_data["prompt_tokens_est"] = prompt_tokens_est

        # Mapear níveis customizados para níveis padrão do logging
        level_mapping = {
            "success": logging.INFO,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }

        # Log estruturado para arquivo
        self.logger.log(
            level_mapping.get(level, logging.INFO),
            json.dumps(log_data, ensure_ascii=False),
        )

        # Log colorido para console com timestamp
        color_map = {
            "info": Fore.LIGHTCYAN_EX,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
        }

        color = color_map.get(level, Fore.WHITE)
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        console_msg = f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}"

        if session_id:
            console_msg += f" {Fore.LIGHTBLACK_EX}[{session_id[:8]}]{Style.RESET_ALL}"
        if duration:
            console_msg += f" {Fore.LIGHTBLACK_EX}[{duration:.2f}s]{Style.RESET_ALL}"
        if prompt_chars is not None:
            console_msg += f" {Fore.LIGHTBLACK_EX}[{prompt_chars}ch ~{prompt_tokens_est}tk]{Style.RESET_ALL}"

        print(console_msg)


# Instância global do logger
logger = StructuredLogger()


def estimate_tokens(text: str) -> int:
    """Estimativa de tokens (~4 chars por token para português/inglês)."""
    return max(1, len(text) // 4)


def log_info(
    message: str, session_id: Optional[str] = None, duration: Optional[float] = None
):
    """Log de informação"""
    logger._log_structured("info", message, session_id, duration)


def log_success(
    message: str, session_id: Optional[str] = None, duration: Optional[float] = None
):
    """Log de sucesso"""
    logger._log_structured("success", message, session_id, duration)


def log_warning(
    message: str, session_id: Optional[str] = None, duration: Optional[float] = None
):
    """Log de aviso"""
    logger._log_structured("warning", message, session_id, duration)


def log_error(
    message: str, session_id: Optional[str] = None, duration: Optional[float] = None
):
    """Log de erro"""
    logger._log_structured("error", message, session_id, duration)


def log_prompt(
    message: str,
    prompt: str,
    session_id: Optional[str] = None,
):
    """Log do tamanho do prompt enviado ao LLM"""
    chars = len(prompt)
    tokens_est = estimate_tokens(prompt)
    logger._log_structured(
        "info", message, session_id,
        prompt_chars=chars, prompt_tokens_est=tokens_est,
    )


def log_request(
    session_id: str,
    prompt: str,
    response: str,
    duration: float,
    model_used: str = "unknown",
):
    """Log para requests de inferência com tamanho do prompt e resposta"""
    prompt_chars = len(prompt)
    prompt_tokens = estimate_tokens(prompt)
    response_chars = len(response)
    response_tokens = estimate_tokens(response)
    logger._log_structured(
        "success",
        f"Inference completed - Model: {model_used} | Prompt: {prompt_chars}ch ~{prompt_tokens}tk | Response: {response_chars}ch ~{response_tokens}tk",
        session_id=session_id,
        duration=duration,
        prompt_chars=prompt_chars,
        prompt_tokens_est=prompt_tokens,
    )


def log_request_error(session_id: str, prompt: str, error: str, duration: float):
    """Log para erros de inferência"""
    log_error(f"Inference failed: {error}", session_id=session_id, duration=duration)
