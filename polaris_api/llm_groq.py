import os
import requests
from polaris_logger import log_info, log_success, log_warning, log_error


class GroqLLM:
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def load(self):
        log_info("🔌 Polaris conectado ao backend remoto.")
        log_success(f"✅ Modelo configurado: {self.model}")

    def close(self):
        log_info("🛑 Encerrando conexão simbólica com o backend remoto.")

    def invoke(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é Polaris, um assistente inteligente.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "top_p": 0.85,
            "max_tokens": 1024,
            "stop": ["<|eot_id|>"],
            "frequency_penalty": 1.4,
        }

        try:
            log_info(f"📤 Enviando prompt para o backend remoto...")
            response = requests.post(self.endpoint, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            log_success(f"🧠 Resposta remota recebida com sucesso.")
            return content
        except Exception as e:
            log_error(f"❌ Erro na inferência via backend remoto: {e}")
            return "Erro ao consultar o modelo remoto. Tente novamente em alguns instantes."
