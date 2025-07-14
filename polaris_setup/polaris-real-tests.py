import asyncio
import httpx
import random
from datetime import datetime

# === CORES ANSI ===
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
GRAY = "\033[90m"
BLUE = "\033[94m"

# === CONFIG ===
API_URL = "https://ceramic-singh-network-electricity.trycloudflare.com/inference/"
NUM_MESSAGES = 5
SLEEP_MIN = 30
SLEEP_MAX = 90
GHOST_SUFFIX = "-shadow"

USER_NAMES = ["Paula"]

SESSIONS = {
    name: {
        "session_id": name,
        "history": []
    } for name in USER_NAMES
}

INITIAL_PROMPTS = {
    "Paula": "Oi, Polaris. Meu nome é Paula. Como você está se sentindo hoje?",
    "Selene": "Oi Polaris, meu nome é Selene. Me explica como eu posso usar FastAPI para criar uma rota?",
    "Gaia": "Polaris, meu nome é Gaia. Você acha que as inteligências artificiais podem filosofar?",
    "Ísis": "Oi Polaris, meu nome é Ísis. Preciso de ajuda com um erro no meu código Python. Pode olhar?",
    "Luzia": "Polaris, meu nome é Luzia. Qual a sua visão sobre a existência, Polaris?"
}

def log(color, label, text):
    now = datetime.now().strftime('%H:%M:%S')
    print(f"{GRAY}[{now}]{RESET} {color}{label}:{RESET} {text}")

async def send_message(session_name, message, session_id_override=None, show_logs=True):
    session_id = session_id_override or SESSIONS[session_name]["session_id"]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json={
                "session_id": session_id,
                "prompt": message
            }, timeout=60)
            response.raise_for_status()
            data = response.json()
            answer = data.get("resposta", "[resposta vazia]")
            if not session_id_override:
                SESSIONS[session_name]["history"].append((message, answer))
            if show_logs:
                log(BLUE, f"{session_name} perguntou", message)
                log(GREEN, "Polaris respondeu", answer + "\n")
            return answer
        except Exception as e:
            log(RED, f"Erro na sessão {session_name}", str(e))
            return "[erro na resposta]"

async def generate_followup(session_name, resposta_anterior):
    prompt_shadow = (
        f"Você acabou de dizer: \"{resposta_anterior.strip()}\"\n"
        f"Agora, imagine que você é {session_name}, uma pessoa curiosa e interessada.\n"
        f"Qual pergunta faria a seguir para continuar essa conversa de forma interessante?"
    )
    shadow_id = session_name + GHOST_SUFFIX
    followup = await send_message(session_name, prompt_shadow, session_id_override=shadow_id, show_logs=False)
    return followup.strip()

async def session_runner(session_name):
    prompt = INITIAL_PROMPTS[session_name]

    for _ in range(NUM_MESSAGES):
        resposta = await send_message(session_name, prompt)
        await asyncio.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
        prompt = await generate_followup(session_name, resposta)

async def main():
    await asyncio.gather(*(session_runner(name) for name in USER_NAMES))

if __name__ == "__main__":
    asyncio.run(main())
