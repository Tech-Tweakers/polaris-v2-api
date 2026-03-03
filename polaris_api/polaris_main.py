import time
import logging
import requests
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Dict
from langchain_chroma import Chroma
from langchain_classic.memory.buffer import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from pymongo import MongoClient
import uvicorn
import os
from colorama import Fore, Style, init
from polaris_logger import (
    log_info,
    log_success,
    log_warning,
    log_error,
    log_request,
    log_request_error,
    log_prompt,
)
from auth import jwt_auth, log_auth_attempt
from prometheus_client import (
    CollectorRegistry,
    Gauge,
    Counter,
    Summary,
    push_to_gateway,
)

init(autoreset=True)
TEXT_COLOR = Fore.LIGHTCYAN_EX
STAR_COLOR = Fore.YELLOW
DIM_STAR = Fore.LIGHTBLACK_EX
LOGO = f"""
       {STAR_COLOR}*{Style.RESET_ALL}        .       *    .  
    .      *       .        .
       {STAR_COLOR}*{Style.RESET_ALL}    .       .        *    .
  .        .  {TEXT_COLOR}POLARIS AI v2.0 {Style.RESET_ALL}        .
       {STAR_COLOR}.{Style.RESET_ALL}        .        *     .  
    .       *        .        .
 {STAR_COLOR}*{Style.RESET_ALL}      .     .      .     
     .     .        .    *    
"""
print(LOGO)

# Mapa temporário em memória para respostas pendentes por sessão
resposta_pendente_por_sessao = {}


registry = CollectorRegistry()

inference_duration = Summary(
    "inference_duration_seconds",
    "Tempo de resposta da inferência em segundos",
    ["session_id"],
    registry=registry,
)

inference_total = Counter(
    "inference_total",
    "Número total de inferências processadas",
    ["session_id"],
    registry=registry,
)

inference_failures = Counter(
    "inference_failures_total",
    "Número total de falhas de inferência",
    ["session_id"],
    registry=registry,
)

# Logging configurado centralmente em polaris_logger.py
# Silencia loggers de terceiros que poluem o output
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

load_dotenv()

CACHED_PROMPT = None
CACHED_KEYWORDS = None

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "False").lower() == "true"

MODEL_PATH = os.getenv("MODEL_PATH")
NUM_CORES = int(os.getenv("NUM_CORES", 16))
MODEL_CONTEXT_SIZE = int(os.getenv("MODEL_CONTEXT_SIZE", 512))
MODEL_BATCH_SIZE = int(os.getenv("MODEL_BATCH_SIZE", 8))

MONGODB_HISTORY = int(os.getenv("MONGODB_HISTORY", 4))
LANGCHAIN_HISTORY = int(os.getenv("LANGCHAIN_HISTORY", 6))

TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
TOP_P = float(os.getenv("TOP_P", 0.7))
TOP_K = int(os.getenv("TOP_K", 30))
FREQUENCY_PENALTY = int(os.getenv("FREQUENCY_PENALTY", 2))

MIN_P = float(os.getenv("MIN_P", 0.01))
N_PROBS = int(os.getenv("N_PROBS", 3))
SEED = int(os.getenv("SEED", 42))

MONGO_URI = os.getenv("MONGO_URI")

USE_MONGODB = os.getenv("USE_MONGODB", "false").lower() == "true"

USE_PUSHGATEWAY = os.getenv("USE_PUSHGATEWAY", "false").lower() == "true"
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://10.10.10.20:9091")


if USE_MONGODB:
    try:
        client = MongoClient(MONGO_URI)
        db = client["polaris_db"]
        collection = db["user_memory"]
        log_success("🔌 Conectado ao MongoDB com sucesso.")
    except Exception as e:
        log_error(f"❌ Erro ao conectar ao MongoDB: {str(e)}")
        USE_MONGODB = False
else:
    log_warning("⛔ Uso do MongoDB desativado por configuração.")

memory_store = {}

log_info("Configurando memória do LangChain...")

embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedder)
VECTORSTORE_ENABLED = True
log_success("✅ VectorStore configurado com sucesso!")


def injetar_session_id(texto: str, session_id: str) -> str:
    """Garante que o texto contenha o identificador de sessão visível."""
    if f"[session_id=" in texto:
        return texto
    return f"[session_id={session_id}]\n{texto.strip()}"


from llm_loader import load_llm

llm = load_llm()


@asynccontextmanager
async def lifespan(app: FastAPI):
    llm.load()
    # Warmup
    try:
        log_info("🔥 Fazendo warmup da Polaris...")
        llm.invoke(
            f"""<|start_header_id|>system<|end_header_id|>
Sistema Polaris iniciando. Apenas confirme "ok".
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Responda apenas 'ok'.
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        )
    except Exception as e:
        log_error(f"Erro no warmup: {str(e)}")
    yield
    llm.close()


app = FastAPI(lifespan=lifespan)


class InferenceRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default_session"


def get_memories(session_id):
    if not USE_MONGODB:
        return []
    try:
        memories = (
            collection.find({"session_id": session_id})
            .sort("timestamp", -1)
            .limit(MONGODB_HISTORY)
        )
        texts = [mem["text"] for mem in memories]
        log_info(
            f"📌 Recuperadas {len(texts)} memórias do MongoDB para sessão {session_id}."
        )
        return texts
    except Exception as e:
        log_error(f"Erro ao buscar memórias no MongoDB: {str(e)}")
        return []


def get_recent_memories(session_id):
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            chat_memory=ChatMessageHistory(), return_messages=True
        )

    history = memory_store[session_id].load_memory_variables({})["history"]

    if not isinstance(history, list):
        return []

    recent_memories = "\n".join(
        [
            (
                f"Usuário: {msg.content}"
                if isinstance(msg, HumanMessage)
                else f"Polaris: {msg.content}"
            )
            for msg in history
        ]
    )

    log_info(
        f"📌 Recuperadas {len(history)} mensagens da memória temporária do LangChain."
    )
    return recent_memories


async def save_to_langchain_memory(user_input, response, session_id):
    try:
        if session_id not in memory_store:
            memory_store[session_id] = ConversationBufferMemory(
                chat_memory=ChatMessageHistory(), return_messages=True
            )

        memory_store[session_id].save_context(
            {"input": user_input}, {"output": response}
        )
        # history = memory_store[session_id].load_memory_variables({})["history"]

        # if len(history) > LANGCHAIN_HISTORY:
        #    log_warning(f"🧹 Memória cheia para sessão '{session_id}', compactando...")
        #    await trim_langchain_memory(session_id)

        trim_langchain_memory_fifo(session_id)

        log_success(
            f"✅ Memória temporária do LangChain atualizada para sessão '{session_id}'!"
        )

    except Exception as e:
        log_error(f"Erro ao salvar na memória temporária do LangChain: {str(e)}")


def save_to_mongo(user_input, session_id):
    if not USE_MONGODB:
        return
    try:
        existing_entry = collection.find_one(
            {"text": user_input, "session_id": session_id}
        )
        if existing_entry:
            log_warning(
                f"Entrada duplicada detectada para sessão {session_id}, não será salva: {user_input}"
            )
            return

        doc = {
            "text": user_input,
            "session_id": session_id,
            "timestamp": datetime.utcnow(),
        }
        result = collection.insert_one(doc)
        if result.inserted_id:
            log_success(
                f"Informação armazenada no MongoDB para sessão {session_id}: {user_input}"
            )

    except Exception as e:
        log_error(f"Erro ao salvar no MongoDB: {str(e)}")


def load_prompt_from_file(file_path="polaris_prompt.txt"):
    global CACHED_PROMPT
    if CACHED_PROMPT:
        return CACHED_PROMPT
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            CACHED_PROMPT = file.read().strip()
            return CACHED_PROMPT
    except FileNotFoundError:
        log_warning(f"Arquivo {file_path} não encontrado! Usando prompt padrão.")
        return "### Instruções:\nVocê é Polaris, um assistente inteligente..."


def load_keywords_from_file(file_path="polaris_keywords.txt"):
    global CACHED_KEYWORDS
    if CACHED_KEYWORDS:
        return CACHED_KEYWORDS
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            CACHED_KEYWORDS = [
                line.strip().lower() for line in file.readlines() if line.strip()
            ]
            log_info(
                f"📂 Palavras-chave carregadas do arquivo ({len(CACHED_KEYWORDS)} palavras)."
            )
            return CACHED_KEYWORDS
    except FileNotFoundError:
        log_warning(
            f"Arquivo {file_path} não encontrado! Usando palavras-chave padrão."
        )
        CACHED_KEYWORDS = ["meu nome é", "eu moro em", "eu gosto de"]
        return CACHED_KEYWORDS


def trim_langchain_memory_fifo(session_id):
    """Mantém apenas as últimas N mensagens na memória do LangChain."""

    if session_id not in memory_store:
        return

    memory = memory_store[session_id]
    history = memory.chat_memory.messages

    if len(history) <= LANGCHAIN_HISTORY:
        return

    excesso = len(history) - LANGCHAIN_HISTORY
    memory.chat_memory.messages = history[excesso:]

    log_success(f"✅ FIFO aplicado na sessão '{session_id}', memória enxugada.")


async def trim_langchain_memory(session_id):
    """Compacta a memória do LangChain resumindo mensagens antigas."""

    if session_id not in memory_store:
        return

    memory = memory_store[session_id]
    history = memory.load_memory_variables({})["history"]

    # Se não ultrapassou o limite, não faz nada
    if len(history) <= LANGCHAIN_HISTORY:
        return

    try:
        log_warning(
            f"✂️ Iniciando compactação da memória LangChain da sessão '{session_id}'..."
        )

        # Junta todas as mensagens antigas em um único texto
        textos_antigos = []
        for msg in history[:-LANGCHAIN_HISTORY]:  # pega tudo, exceto as mais recentes
            if isinstance(msg, HumanMessage):
                textos_antigos.append(f"Usuário: {msg.content}")
            elif isinstance(msg, AIMessage):
                textos_antigos.append(f"Polaris: {msg.content}")

        bloco_antigo = "\n".join(textos_antigos)

        # Cria o prompt de resumo
        prompt_resumo = f"""<|start_header_id|>system<|end_header_id|>
        Resuma a seguinte conversa em 5 linhas, mantendo o sentido e os fatos:

{bloco_antigo}

Resumo:"""

        # Gera o resumo usando a própria Polaris
        resumo = llm.invoke(prompt_resumo)

        # Remove todas as mensagens antigas
        memory.chat_memory.messages = memory.chat_memory.messages[-LANGCHAIN_HISTORY:]

        # Insere o resumo como nova memória
        memory.chat_memory.add_user_message("Resumo da conversa anterior:")
        memory.chat_memory.add_ai_message(resumo.strip())

        log_success(f"✅ Memória da sessão '{session_id}' compactada com sucesso!")

    except Exception as e:
        log_error(f"Erro ao resumir a memória do LangChain: {str(e)}")


from langchain_core.messages import HumanMessage, AIMessage


@app.post("/inference/")
async def inference(
    prompt: str = Body(...),
    session_id: str = Body("default_session"),
    current_user: Optional[Dict] = None,
):
    user_prompt = injetar_session_id(prompt, session_id)
    start_time = time.time()

    log_info(f"📥 Nova solicitação de inferência", session_id=session_id)

    inference_total.labels(session_id=session_id).inc()
    erro = False

    keywords = load_keywords_from_file()

    if any(kw in user_prompt.lower() for kw in keywords):
        save_to_mongo(user_prompt, session_id)

    docs_context = ""
    if VECTORSTORE_ENABLED:
        try:
            retrieved_docs = vectorstore.similarity_search(
                user_prompt, k=3, filter={"session_id": session_id}
            )
            docs_context = "\n".join([doc.page_content for doc in retrieved_docs])
            if docs_context:
                log_info(
                    f"📚 {len(retrieved_docs)} trechos relevantes encontrados no vectorstore."
                )
                docs_context = (
                    f"📚 Conteúdo relevante dos documentos:\n{docs_context}\n\n"
                )
            else:
                docs_context = ""
                log_info("📚 Nenhum documento relevante encontrado no vectorstore.")
        except Exception as e:
            log_error(f"Erro ao buscar no vectorstore: {e}")
            docs_context = ""
    else:
        log_info("📚 VectorStore desabilitado - pulando busca de documentos.")

    mongo_memories = get_memories(session_id)
    recent_memories = get_recent_memories(session_id)

    context_pieces = []
    if mongo_memories:
        context_pieces.append("Memória do Usuário:\n" + "\n".join(mongo_memories))
    if recent_memories:
        context_pieces.append("Conversa recente:\n" + recent_memories)

    context = "\n".join(context_pieces)

    prompt_instrucoes = load_prompt_from_file()

    full_prompt = f"""<|start_header_id|>system<|end_header_id|>
{prompt_instrucoes}

{docs_context}
{context}

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    log_prompt("📏 Prompt construído para inferência", full_prompt, session_id=session_id)

    try:
        resposta = llm.invoke(full_prompt)
        duration = time.time() - start_time

        if "shellPolaris" in resposta:
            # ⚡ Salvar como novo prompt no Chroma com session_id
            if VECTORSTORE_ENABLED:
                comando = injetar_session_id(resposta, session_id)
                vectorstore.add_texts(
                    texts=[comando], metadatas=[{"session_id": session_id}]
                )

            log_info(
                "🧠 Polaris em modo executivo — aguardando retorno do comando.",
                session_id=session_id,
                duration=duration,
            )

            return {
                "resposta": "Estou verificando as informações solicitadas. Um momento... 🧠"
            }

        await save_to_langchain_memory(user_prompt, resposta, session_id)

        if VECTORSTORE_ENABLED:
            try:
                resposta_com_id = injetar_session_id(resposta, session_id)
                vectorstore.add_texts(
                    texts=[resposta_com_id], metadatas=[{"session_id": session_id}]
                )
                log_success(
                    f"🧠 Resposta registrada no ChromaDB", session_id=session_id
                )
            except Exception as e:
                log_error(
                    f"Erro ao salvar resposta no ChromaDB: {e}", session_id=session_id
                )

        # Log estruturado da inferência bem-sucedida
        log_request(session_id, prompt, resposta, duration, "llama3")

    except Exception as e:
        duration = time.time() - start_time
        erro = True
        inference_failures.labels(session_id=session_id).inc()
        log_request_error(session_id, prompt, str(e), duration)
        raise HTTPException(status_code=500, detail="Erro na inferência")

    if USE_PUSHGATEWAY:
        try:
            push_to_gateway(
                PUSHGATEWAY_URL,
                job="polaris-api",
                registry=registry,
            )
            log_success("📊 Métricas enviadas ao Pushgateway com sucesso!")
        except Exception as push_error:
            log_warning(f"⚠️ Falha ao enviar métricas para o Pushgateway: {push_error}")
    else:
        log_info("📉 Envio de métricas ao Pushgateway desativado por configuração.")

    return {"resposta": resposta}


@app.post("/inference/stream/")
async def inference_stream(
    prompt: str = Body(...),
    session_id: str = Body("default_session"),
    current_user: Optional[Dict] = Depends(jwt_auth.get_current_user),
):
    """Endpoint de streaming usando Server-Sent Events"""

    async def generate():
        try:
            user_prompt = injetar_session_id(prompt, session_id)
            start_time = time.time()

            log_info(f"📥 Nova solicitação de streaming", session_id=session_id)

            inference_total.labels(session_id=session_id).inc()

            keywords = load_keywords_from_file()

            if any(kw in user_prompt.lower() for kw in keywords):
                save_to_mongo(user_prompt, session_id)

            # Busca no vectorstore
            docs_context = ""
            if VECTORSTORE_ENABLED:
                try:
                    retrieved_docs = vectorstore.similarity_search(
                        user_prompt, k=3, filter={"session_id": session_id}
                    )
                    docs_context = "\n".join(
                        [doc.page_content for doc in retrieved_docs]
                    )
                    if docs_context:
                        log_info(
                            f"📚 {len(retrieved_docs)} trechos relevantes encontrados no vectorstore."
                        )
                        docs_context = (
                            f"📚 Conteúdo relevante dos documentos:\n{docs_context}\n\n"
                        )
                    else:
                        docs_context = ""
                except Exception as e:
                    log_error(f"Erro ao buscar no vectorstore: {e}")
                    docs_context = ""

            # Memória
            mongo_memories = get_memories(session_id)
            recent_memories = get_recent_memories(session_id)

            context_pieces = []
            if mongo_memories:
                context_pieces.append(
                    "Memória do Usuário:\n" + "\n".join(mongo_memories)
                )
            if recent_memories:
                context_pieces.append("Conversa recente:\n" + recent_memories)

            context = "\n".join(context_pieces)
            prompt_instrucoes = load_prompt_from_file()

            full_prompt = f"""<|start_header_id|>system<|end_header_id|>
{prompt_instrucoes}

{docs_context}
{context}

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

            log_prompt("📏 Prompt construído para streaming", full_prompt, session_id=session_id)

            yield "data: [START]\n\n"

            # Streaming real: yield cada token conforme chega do Groq
            # stream_chunks() é síncrono — rodamos em thread pra não bloquear o event loop
            import queue

            chunk_queue = queue.Queue()
            SENTINEL = object()

            def _run_sync_stream():
                try:
                    for c in llm.stream_chunks(full_prompt):
                        chunk_queue.put(c)
                except Exception as e:
                    chunk_queue.put(e)
                finally:
                    chunk_queue.put(SENTINEL)

            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, _run_sync_stream)

            resposta_completa = ""
            try:
                while True:
                    # Espera chunk sem bloquear o event loop
                    while chunk_queue.empty():
                        await asyncio.sleep(0.01)
                    item = chunk_queue.get()
                    if item is SENTINEL:
                        break
                    if isinstance(item, Exception):
                        raise item
                    resposta_completa += item
                    # SSE data lines can't contain raw newlines — encode them
                    safe_item = (
                        item.replace("\r\n", "\\n")
                        .replace("\n", "\\n")
                        .replace("\r", "\\n")
                    )
                    yield f"data: {safe_item}\n\n"

                if "shellPolaris" in resposta_completa:
                    if VECTORSTORE_ENABLED:
                        comando = injetar_session_id(resposta_completa, session_id)
                        vectorstore.add_texts(
                            texts=[comando], metadatas=[{"session_id": session_id}]
                        )
                    log_info("🧠 Polaris em modo executivo.", session_id=session_id)
                    yield "data: [EXEC_MODE]\n\n"
                    yield "data: [DONE]\n\n"
                    return

                # Salva na memória e vectorstore
                await save_to_langchain_memory(user_prompt, resposta_completa, session_id)

                if VECTORSTORE_ENABLED:
                    try:
                        resposta_com_id = injetar_session_id(
                            resposta_completa, session_id
                        )
                        vectorstore.add_texts(
                            texts=[resposta_com_id],
                            metadatas=[{"session_id": session_id}],
                        )
                    except Exception as e:
                        log_error(
                            f"Erro ao salvar resposta no ChromaDB: {e}",
                            session_id=session_id,
                        )

                duration = time.time() - start_time
                log_request(
                    session_id, prompt, resposta_completa, duration, "groq-streaming"
                )

                yield "data: [DONE]\n\n"

            except Exception as e:
                duration = time.time() - start_time
                log_request_error(session_id, prompt, str(e), duration)
                yield f"data: [ERROR] {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        except Exception as e:
            log_error(f"Erro geral no streaming: {str(e)}")
            yield f"data: [ERROR] Erro interno do servidor\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


from pydantic import BaseModel


class CommandResponse(BaseModel):
    session_id: str
    resposta: str


@app.get("/health")
async def health_check():
    """Health check endpoint para monitoramento"""
    try:
        # Verificar MongoDB
        mongo_status = "healthy"
        if USE_MONGODB:
            try:
                log_info("🔍 Testing MongoDB connection in health check...")
                test_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                test_client.admin.command("ping")
                test_client.close()
                log_info("✅ MongoDB health check passed")
            except Exception as e:
                mongo_status = "unhealthy"
                log_error(f"MongoDB health check failed: {str(e)}")
        else:
            mongo_status = "disabled"

        # Verificar LLM
        llm_status = "healthy"
        try:
            test_response = llm.invoke("Test")
            if not test_response:
                llm_status = "unhealthy"
        except Exception as e:
            llm_status = "unhealthy"
            log_error(f"LLM health check failed: {str(e)}")

        # Status geral
        overall_status = "healthy"
        if mongo_status == "unhealthy" or llm_status == "unhealthy":
            overall_status = "unhealthy"

        health_data = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {"mongodb": mongo_status, "llm": llm_status},
            "version": "v2.1",
        }

        return health_data

    except Exception as e:
        log_error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "v2.1",
        }


@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...), session_id: str = Form("default_session")
):
    try:
        temp_pdf_path = f"temp_uploads/{file.filename}"
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
        with open(temp_pdf_path, "wb") as f:
            f.write(await file.read())

        log_info(f"📂 PDF recebido para sessão {session_id}: {temp_pdf_path}")

        from langchain_community.document_loaders import PyMuPDFLoader

        loader = PyMuPDFLoader(temp_pdf_path)
        documents = loader.load()

        log_info(f"📖 {len(documents)} documentos carregados do PDF.")

        if VECTORSTORE_ENABLED:
            for doc in documents:
                texto_pdf = injetar_session_id(doc.page_content, session_id)
                vectorstore.add_texts(
                    texts=[texto_pdf], metadatas=[{"session_id": session_id}]
                )
        else:
            log_warning("⚠️ VectorStore desabilitado - PDF não será indexado.")

        log_success(
            f"✅ Conteúdo do PDF adicionado ao VectorStore para sessão '{session_id}'!"
        )

        os.remove(temp_pdf_path)
        log_info(f"🗑️ Arquivo temporário removido: {temp_pdf_path}")

        return {"message": "PDF processado e indexado com sucesso para a sessão!"}

    except Exception as e:
        log_error(f"Erro ao processar o PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar o PDF.")


# Endpoints de Autenticação
@app.post("/auth/token")
async def get_token(client_name: str, client_secret: str):
    """Endpoint para obter token de API"""
    # Lista simples de clientes autorizados (em produção, use banco de dados)
    authorized_clients = {
        "polaris_bot": os.getenv("BOT_SECRET", "bot-secret"),
        "web_client": os.getenv("WEB_SECRET", "web-secret"),
        "mobile_app": os.getenv("MOBILE_SECRET", "mobile-secret"),
    }

    if client_name not in authorized_clients:
        log_warning(f"Unauthorized client attempt: {client_name}")
        raise HTTPException(status_code=401, detail="Unauthorized client")

    if client_secret != authorized_clients[client_name]:
        log_warning(f"Invalid secret for client: {client_name}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    from auth import create_api_token

    token = create_api_token(client_name)
    log_success(f"Token created for client: {client_name}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": int(os.getenv("JWT_EXPIRY_HOURS", "24")) * 3600,
    }


@app.get("/auth/verify")
async def verify_token(current_user: Dict = None):
    """Endpoint para verificar token"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "role": current_user["role"],
        "expires_at": datetime.fromtimestamp(current_user["exp"]).isoformat(),
    }


# CORS dinâmico baseado em variável de ambiente
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if ALLOWED_ORIGINS == ["*"]:
    # Em desenvolvimento, permite tudo
    allow_origins = ["*"]
else:
    # Em produção, lista específica
    allow_origins = [origin.strip() for origin in ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
