import pytest
from unittest.mock import Mock, patch, MagicMock
import logging
import json
import os

# Importar módulos da API
from polaris_logger import (
    StructuredLogger, log_info, log_success, log_warning, log_error,
    log_request, log_request_error
)

class TestStructuredLogger:
    """Testes para a classe StructuredLogger"""
    
    def test_logger_initialization(self):
        """Testa inicialização do logger"""
        logger = StructuredLogger()
        # Verificar se o logger foi criado
        assert logger is not None
        assert hasattr(logger, 'logger')
    
    def test_log_info(self):
        """Testa log de informação"""
        with patch('builtins.print') as mock_print:
            log_info("Test info message")
            mock_print.assert_called()
    
    def test_log_success(self):
        """Testa log de sucesso"""
        with patch('builtins.print') as mock_print:
            log_success("Test success message")
            mock_print.assert_called()
    
    def test_log_warning(self):
        """Testa log de warning"""
        with patch('builtins.print') as mock_print:
            log_warning("Test warning message")
            mock_print.assert_called()
    
    def test_log_error(self):
        """Testa log de erro"""
        with patch('builtins.print') as mock_print:
            log_error("Test error message")
            mock_print.assert_called()
    
    def test_log_request(self):
        """Testa log de request"""
        with patch('builtins.print') as mock_print:
            log_request("test_session", "test_prompt", "response_data", 150)
            mock_print.assert_called()
    
    def test_log_request_error(self):
        """Testa log de erro de request"""
        with patch('builtins.print') as mock_print:
            log_request_error("test_session", "test_prompt", "Test error", 150)
            mock_print.assert_called()
    
    @patch('builtins.open', create=True)
    def test_file_logging(self, mock_open):
        """Testa se logs são escritos no arquivo"""
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock do logger para forçar escrita no arquivo
        with patch('polaris_logger.StructuredLogger._log_structured') as mock_log:
            log_info("Test file message")
            
            # Verificar se o método de log foi chamado
            mock_log.assert_called()
    
    def test_log_levels(self):
        """Testa diferentes níveis de log"""
        logger = StructuredLogger()
        
        # Verificar se os handlers estão configurados corretamente
        assert logger.logger.level == logging.INFO
        
        # Verificar se os handlers existem
        assert len(logger.logger.handlers) >= 2
    
    def test_session_id_in_logs(self):
        """Testa se session_id é incluído nos logs"""
        with patch('builtins.print') as mock_print:
            log_request("test_session_123", "test_prompt", "response_data", 200)
            
            # Verificar se o print foi chamado com mensagem contendo session_id
            call_args = mock_print.call_args[0][0]
            assert "test_session_123" in call_args
    
    def test_duration_in_logs(self):
        """Testa se duration é incluído nos logs"""
        with patch('builtins.print') as mock_print:
            log_request("test_session", "test_prompt", "response_data", 150)
            
            # Verificar se o print foi chamado com mensagem contendo duration
            call_args = mock_print.call_args[0][0]
            assert "150" in call_args

class TestLogFunctions:
    """Testes para funções de log individuais"""
    
    def test_log_info_format(self):
        """Testa formato do log de info"""
        with patch('builtins.print') as mock_print:
            log_info("Test message")
            
            call_args = mock_print.call_args[0][0]
            assert "🔹" in call_args  # Emoji de info
            assert "Test message" in call_args
    
    def test_log_success_format(self):
        """Testa formato do log de sucesso"""
        with patch('builtins.print') as mock_print:
            log_success("Test success")
            
            call_args = mock_print.call_args[0][0]
            assert "✅" in call_args  # Emoji de sucesso
            assert "Test success" in call_args
    
    def test_log_warning_format(self):
        """Testa formato do log de warning"""
        with patch('builtins.print') as mock_print:
            log_warning("Test warning")
            
            call_args = mock_print.call_args[0][0]
            assert "⚠️" in call_args  # Emoji de warning
            assert "Test warning" in call_args
    
    def test_log_error_format(self):
        """Testa formato do log de erro"""
        with patch('builtins.print') as mock_print:
            log_error("Test error")
            
            call_args = mock_print.call_args[0][0]
            assert "❌" in call_args  # Emoji de erro
            assert "Test error" in call_args
    
    def test_log_request_format(self):
        """Testa formato do log de request"""
        with patch('builtins.print') as mock_print:
            log_request("test_session", "test_prompt", "response_data", 150)
            
            call_args = mock_print.call_args[0][0]
            assert "✅" in call_args  # Emoji de sucesso (corrigido)
            assert "test_session" in call_args
            assert "150" in call_args
    
    def test_log_request_error_format(self):
        """Testa formato do log de erro de request"""
        with patch('builtins.print') as mock_print:
            log_request_error("test_session", "test_prompt", "Test error", 150)
            
            call_args = mock_print.call_args[0][0]
            assert "❌" in call_args  # Emoji de erro (corrigido)
            assert "test_session" in call_args
            assert "Test error" in call_args

class TestLoggerIntegration:
    """Testes de integração do logger"""
    
    def test_logger_singleton_behavior(self):
        """Testa se o logger se comporta como singleton"""
        logger1 = StructuredLogger()
        logger2 = StructuredLogger()
        
        # Ambos devem usar a mesma instância do logger
        assert logger1.logger is logger2.logger
    
    def test_log_file_creation(self, tmp_path):
        """Testa criação do arquivo de log"""
        # Mock do arquivo de log
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            logger = StructuredLogger()
            log_info("Test message")
            
            # Verificar se open foi chamado
            mock_open.assert_called()
    
    def test_log_format_consistency(self):
        """Testa consistência do formato de log"""
        with patch('builtins.print') as mock_print:
            log_info("Test message 1")
            log_success("Test message 2")
            log_warning("Test message 3")
            
            # Verificar se todos os logs têm formato consistente
            calls = mock_print.call_args_list
            assert len(calls) == 3
            
            for call in calls:
                message = call[0][0]
                # Todos devem ter emoji
                assert any(emoji in message for emoji in ["🔹", "✅", "⚠️", "❌"])
