import sqlite3
import subprocess
import time
import re
import os
import traceback
import requests
from dotenv import load_dotenv
from rich import print

# 🎯 Variáveis de ambiente
load_dotenv()
CHROMA_DB_PATH = "../polaris_api/chroma_db/chroma.sqlite3"
WHITELIST = ["curl", "nslookup", "df", "dig", "ps", "top", "free", "uptime", "whoami", "uname", "cat", "ls", "pwd", "echo", "date", "ifconfig", "ip", "traceroute"]
ROWID_FILE = "last_rowid.txt"
TIMEOUT = int(os.getenv("POLARIS_TIMEOUT", "10"))
POLARIS_API_URL = os.getenv("POLARIS_RESPONSE_URL", "http://localhost:8000/inference/response")

# 🛠️ Funções auxiliares
def extrair_session_id(texto):
    match = re.search(r"\[session_id=(.+?)\]", texto)
    return match.group(1).strip() if match else None

def extrair_comando(texto):
    match = re.search(r"shellPolaris\s*(.+)", texto)
    return match.group(1).strip() if match else None

def comando_permitido(comando):
    return comando.split()[0] in WHITELIST

def executar_comando(comando):
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, timeout=TIMEOUT)
        return result.stdout.decode().strip() or result.stderr.decode().strip()
    except Exception as e:
        return f"Erro ao executar: {str(e)}"

def enviar_resposta_para_polaris(session_id, resposta):
    payload = {
        "session_id": session_id,
        "resposta": resposta
    }
    try:
        r = requests.post(POLARIS_API_URL, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"[blue]📬 Resposta enviada com sucesso para Polaris.[/blue]")
        else:
            print(f"[red]⚠️ Erro ao enviar resposta: {r.status_code}[/red]\nResposta: {r.text}")
    except Exception as e:
        print(f"[red]❌ Falha ao conectar com Polaris: {e}[/red]")

def carregar_ultimo_rowid():
    try:
        with open(ROWID_FILE) as f:
            return int(f.read())
    except:
        return 0

def salvar_ultimo_rowid(rowid):
    with open(ROWID_FILE, "w") as f:
        f.write(str(rowid))

# 🔮 Loop principal
def ouvir_chroma():
    ultimo_rowid = carregar_ultimo_rowid()
    ultimo_conteudo = None
    conn = sqlite3.connect(CHROMA_DB_PATH)
    cursor = conn.cursor()

    print("[bold cyan]🔮 Polaris Executor ouvindo e respondendo...[/bold cyan]")

    while True:
        try:
            cursor.execute("""
                SELECT rowid, c0
                FROM embedding_fulltext_search_content
                WHERE rowid > ?
                ORDER BY rowid ASC
                LIMIT 10
            """, (ultimo_rowid,))
            rows = cursor.fetchall()

            for rowid, content in rows:
                if not content or content == ultimo_conteudo:
                    continue

                print(f"\n[dim]📝 Conteúdo recebido (rowid {rowid}):[/dim]\n[white]{content}[/white]")

                session_id = extrair_session_id(content)
                comando = extrair_comando(content)

                print(f"[grey]🔍 session_id extraído: {session_id}[/grey]")
                print(f"[yellow]🔍 comando extraído: {comando}[/yellow]")

                if session_id and comando:
                    if comando_permitido(comando):
                        print(f"\n[bold magenta]✨ Polaris requisitou:[/bold magenta] [yellow]{comando}[/yellow]")
                        resultado = executar_comando(comando)
                        print(f"[green]📤 Resultado da execução:[/green]\n{resultado}")
                        enviar_resposta_para_polaris(session_id, resultado)
                    else:
                        print(f"[red]🚫 Comando negado (não está na whitelist): {comando}[/red]")
                else:
                    print(f"[grey]🤖 Ignorado: sessão ou comando inválido[/grey]")

                ultimo_conteudo = content
                ultimo_rowid = rowid
                salvar_ultimo_rowid(ultimo_rowid)

            time.sleep(2)

        except Exception as e:
            print(f"[red]❌ Erro ao acessar o banco: {e}[/red]")
            traceback.print_exc()
            time.sleep(5)

# 🏁 Execução
if __name__ == "__main__":
    ouvir_chroma()
