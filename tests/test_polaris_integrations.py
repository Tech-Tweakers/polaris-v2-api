import io
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from polaris_integrations.main import api  # Certo!

client = TestClient(api)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("POLARIS_API_URL", "http://fake-polaris-api/inference/")
    monkeypatch.setenv("PUBLIC_URL", "http://localhost:8010")
    os.makedirs("audios", exist_ok=True)
    yield
    for f in os.listdir("audios"):
        os.remove(os.path.join("audios", f))


@patch("polaris_integrations.main.subprocess.run")
@patch("polaris_integrations.main.gerar_audio")
@patch("polaris_integrations.main.requests.post")
@patch("polaris_integrations.main.whisper.transcribe")
def test_audio_inference_sucesso(
    mock_transcribe, mock_post, mock_gerar_audio, mock_run
):
    # Mock Whisper
    mock_transcribe.return_value = ([MagicMock(text="olá mundo")], None)

    # Mock resposta da Polaris
    mock_post.return_value.json.return_value = {"resposta": "Oi, tudo bem!"}

    audio_content = b"simulacao de audio"
    files = {
        "audio": ("input.webm", io.BytesIO(audio_content), "audio/webm"),
        "session_id": (None, "sessao-123"),
    }

    response = client.post("/audio-inference/", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert data["resposta"] == "Oi, tudo bem!"
    assert "tts_audio_url" in data
    assert "user_audio_url" in data


@patch("polaris_integrations.main.whisper.transcribe", side_effect=RuntimeError("Falha no Whisper"))
def test_audio_inference_whisper_erro(mock_transcribe):
    audio_content = b"audio corrompido"
    files = {
        "audio": ("erro.webm", io.BytesIO(audio_content), "audio/webm"),
        "session_id": (None, "erro-321"),
    }

    response = client.post("/audio-inference/", files=files)

    assert response.status_code == 500
    assert "erro" in response.json()
