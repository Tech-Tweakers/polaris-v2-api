import os
import time
from fastapi import HTTPException
from llama_cpp import Llama
from polaris_logger import log_info, log_success, log_error
from dotenv import load_dotenv

load_dotenv()


NUM_CORES = int(os.getenv("NUM_CORES", 16))
MODEL_CONTEXT_SIZE = int(os.getenv("MODEL_CONTEXT_SIZE", 512))
MODEL_BATCH_SIZE = int(os.getenv("MODEL_BATCH_SIZE", 8))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
TOP_P = float(os.getenv("TOP_P", 0.7))
TOP_K = int(os.getenv("TOP_K", 30))
FREQUENCY_PENALTY = int(os.getenv("FREQUENCY_PENALTY", 2))
SEED = int(os.getenv("SEED", 42))


class LlamaRunnable:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.llm = None

    def load(self):
        if self.llm is None:
            log_info("Carregando modelo LLaMA local...")
            self.llm = Llama(
                model_path=self.model_path,
                n_threads=NUM_CORES,
                n_ctx=MODEL_CONTEXT_SIZE,
                batch_size=MODEL_BATCH_SIZE,
                n_gpu_layers=0,
                verbose=False,
                use_mlock=True,
                seed=-1,
            )
            log_success("Modelo LLaMA carregado!")

    def close(self):
        if self.llm is not None:
            log_info("Fechando modelo LLaMA...")
            del self.llm
            self.llm = None
            log_success("Modelo LLaMA fechado!")

    def invoke(self, prompt: str):
        if self.llm is None:
            raise HTTPException(status_code=500, detail="Modelo não carregado!")

        log_info(f"📜 Enviando prompt ao modelo:\n{prompt[:500]}...")

        start = time.time()
        response = self.llm(
            prompt,
            stop=["---"],
            max_tokens=1024,
            echo=False,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            repeat_penalty=FREQUENCY_PENALTY,
            seed=SEED,
        )
        duration = time.time() - start
        log_info(f"⚡ Tempo de inferência: {duration:.3f}s")

        if "choices" in response and response["choices"]:
            return response["choices"][0]["text"].strip()

        log_error("❌ Resposta vazia ou inválida!")
        return "Erro ao gerar resposta."
