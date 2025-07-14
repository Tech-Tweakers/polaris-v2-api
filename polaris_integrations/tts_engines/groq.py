import os
import logging
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


log = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TTS_MODEL = "playai-tts"
GROQ_TTS_VOICE = os.getenv("GROQ_TTS_VOICE", "Aaliyah-PlayAI")

client = Groq(api_key=GROQ_API_KEY)


def tts_groq(texto: str, path: str) -> str:
    try:
        log.info("🎤 Gerando áudio via Groq TTS...")

        response = client.audio.speech.create(
            model=GROQ_TTS_MODEL,
            voice=GROQ_TTS_VOICE,
            input=texto,
            response_format="mp3",
        )

        # Garante que o diretório existe
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Salvar manualmente
        with open(path, "wb") as f:
            f.write(response.read())

        log.info(f"✅ Áudio salvo em: {path}")
        return path

    except Exception as e:
        log.error(f"❌ Erro no Groq TTS: {e}")
        raise
