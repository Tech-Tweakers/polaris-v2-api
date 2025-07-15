import os
from polaris_integrations.tts_engines.eleven import tts_eleven
from polaris_integrations.tts_engines.coqui import tts_coqui
from polaris_integrations.tts_engines.groq import tts_groq


def gerar_audio(texto: str, path: str) -> str:
    engine = os.getenv("TTS_ENGINE", "coqui").lower()

    if engine == "eleven":
        return tts_eleven(texto, path)
    elif engine == "coqui":
        return tts_coqui(texto, path)
    elif engine == "groq":
        return tts_groq(texto, path)
    else:
        raise ValueError(f"⚠️ Engine TTS não reconhecida: {engine}")
