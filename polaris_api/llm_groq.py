from groq import Groq
from polaris_logger import log_info, log_success, log_warning, log_error


class GroqLLM:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model

    def load(self):
        log_info("🔌 Polaris conectado ao backend remoto.")
        log_success(f"✅ Modelo configurado: {self.model}")

    def close(self):
        log_info("🛑 Encerrando conexão simbólica com o backend remoto.")

    def invoke(self, prompt: str) -> str:
        client = Groq(
            api_key=self.api_key
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é Polaris, um assistente inteligente.",
                },
                {"role": "user", "content": prompt},
            ],
            model=self.model
        )

        try:
            log_info(f"📤 Enviando prompt para o backend remoto...")
            content = chat_completion.choices[0].message.content
            log_success(f"🧠 Resposta remota recebida com sucesso.")
            return content
        except Exception as e:
            log_error(f"❌ Erro na inferência via backend remoto: {e}")
            return "Erro ao consultar o modelo remoto. Tente novamente em alguns instantes."
