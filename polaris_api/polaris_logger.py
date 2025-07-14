import logging
from colorama import Fore, Style, init

init(autoreset=True)


def log_info(message: str):
    logging.info(f"🔹 {message}")


def log_success(message: str):
    logging.info(f"✅ {message}")


def log_warning(message: str):
    logging.warning(f"⚠️ {message}")


def log_error(message: str):
    logging.error(f"❌ {message}")
