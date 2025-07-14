import os
from llm_local import LlamaRunnable
from llm_groq import GroqLLM
from dotenv import load_dotenv

load_dotenv()


def load_llm():
    use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"

    if use_local:
        model_path = os.getenv("MODEL_PATH")
        return LlamaRunnable(model_path=model_path)

    api_key = os.getenv("GROQ_API_KEY")
    return GroqLLM(api_key=api_key)
