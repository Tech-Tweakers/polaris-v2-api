import pytest
from httpx import AsyncClient
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from polaris_api.polaris_main import app


@pytest.mark.asyncio
async def test_docs_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.get("/docs")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_inference_basic(monkeypatch):
    async def mock_invoke(prompt):
        return "Resposta simulada pela Polaris."

    monkeypatch.setattr("main.llm.invoke", mock_invoke)
    monkeypatch.setattr("main.vectorstore.similarity_search", lambda q, k, filter: [])
    monkeypatch.setattr("main.get_memories", lambda s: [])
    monkeypatch.setattr("main.get_recent_memories", lambda s: "")
    monkeypatch.setattr("main.load_prompt_from_file", lambda: "Você é Polaris.")
    monkeypatch.setattr("main.load_keywords_from_file", lambda: [])

    payload = {"prompt": "Quem descobriu o Brasil?", "session_id": "sessao-teste-123"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/inference/", json=payload)
        assert res.status_code == 200
        assert res.json()["resposta"] == "Resposta simulada pela Polaris."


@pytest.mark.asyncio
async def test_upload_pdf(monkeypatch, tmp_path):
    dummy_pdf = tmp_path / "teste.pdf"
    dummy_pdf.write_bytes(
        b"%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<<>>\nstartxref\n0\n%%EOF"
    )

    class DummyDoc:
        page_content = "Texto simulado extraído do PDF."

    monkeypatch.setattr(
        "main.PyMuPDFLoader",
        lambda path: type("Loader", (), {"load": lambda self: [DummyDoc()]}),
    )
    monkeypatch.setattr("main.vectorstore.add_texts", lambda texts, metadatas: None)

    with dummy_pdf.open("rb") as file:
        files = {"file": ("teste.pdf", file, "application/pdf")}
        data = {"session_id": "sessao-upload"}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            res = await ac.post("/upload-pdf/", files=files, data=data)
            assert res.status_code == 200
            assert "PDF processado" in res.json()["message"]
