from groq import Groq
from polaris_logger import log_info, log_success, log_warning, log_error, log_prompt


class GroqLLM:
    def __init__(self, api_key: str, model: str = "openai/gpt-oss-20b"):
        self.api_key = api_key
        self.model = model

    def load(self):
        log_info("🔌 Polaris conectado ao backend remoto.")
        log_success(f"✅ Modelo configurado: {self.model}")

    def close(self):
        log_info("🛑 Encerrando conexão simbólica com o backend remoto.")

    def invoke(self, prompt: str) -> str:
        """Método síncrono para compatibilidade"""
        return self.invoke_stream(prompt, lambda chunk: None)

    def invoke_stream(self, prompt: str, stream_callback=None) -> str:
        """Método com suporte a streaming via callback (compatibilidade)"""
        full_content = ""
        for chunk in self.stream_chunks(prompt):
            full_content += chunk
            if stream_callback:
                stream_callback(chunk)
        return full_content

    def stream_chunks(self, prompt: str):
        """Generator que yield cada token conforme chega do Groq"""
        client = Groq(api_key=self.api_key)

        try:
            log_prompt(f"📤 Enviando prompt para {self.model}", prompt)

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é Polaris, um assistente inteligente.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                stream=True,
                temperature=0.3,
                max_tokens=1024,
            )

            for chunk in chat_completion:
                if (
                    hasattr(chunk.choices[0].delta, "content")
                    and chunk.choices[0].delta.content
                ):
                    yield chunk.choices[0].delta.content

            log_success(f"🧠 Streaming concluído.")

        except Exception as e:
            log_error(f"❌ Erro na inferência via backend remoto: {e}")
            yield "Erro ao consultar o modelo remoto. Tente novamente em alguns instantes."
