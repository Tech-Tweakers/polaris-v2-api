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
        """Método síncrono para compatibilidade"""
        return self.invoke_stream(prompt, lambda chunk: None)

    def invoke_stream(self, prompt: str, stream_callback=None) -> str:
        """Método com suporte a streaming"""
        client = Groq(api_key=self.api_key)

        try:
            log_info(f"📤 Enviando prompt para o backend remoto...")

            # Para streaming, usa stream=True
            if stream_callback:
                log_info("🎬 Iniciando streaming...")
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é Polaris, um assistente inteligente.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    model=self.model,
                    stream=True,  # Habilita streaming
                    temperature=0.3,
                    max_tokens=1024,
                )

                full_content = ""
                chunk_count = 0
                for chunk in chat_completion:
                    chunk_count += 1
                    log_info(f"📦 Chunk {chunk_count} recebido")
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        log_info(f"📝 Conteúdo: '{content}'")
                        full_content += content
                        stream_callback(content)  # Chama callback com chunk
                    else:
                        log_info(f"📦 Chunk sem conteúdo: {chunk}")

                log_success(f"🧠 Streaming concluído com {chunk_count} chunks. Conteúdo final: {len(full_content)} chars")
                return full_content

            else:
                # Modo não-streaming (compatibilidade)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é Polaris, um assistente inteligente.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    model=self.model,
                    temperature=0.3,
                    max_tokens=1024,
                )

                content = chat_completion.choices[0].message.content
                log_success(f"🧠 Resposta remota recebida com sucesso.")
                return content

        except Exception as e:
            log_error(f"❌ Erro na inferência via backend remoto: {e}")
            return "Erro ao consultar o modelo remoto. Tente novamente em alguns instantes."
