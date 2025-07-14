import io
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from polaris_integrations import api  # ou o nome do seu módulo se for diferente

client = TestClient(api)

@pytest.fixture(autouse=True)
def criar_diretorio_audios(tmp_path, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "http://localhost:8010")
    monkeypatch.setenv("POLARIS_API_URL", "http://fake-api.com/inference/")
    monkeypatch.setenv("COQUI_SPEAKER_WAV", "fake.wav")
    monkeypatch.setenv("TTS_ENGINE", "coqui")
    os.makedirs("audios", exist_ok=True)
    yield
    for f in os.listdir("audios"):
        os.remove(os.path.join("audios", f))


@patch("polaris_integrations.whisper.transcribe")
@patch("polaris_integrations.requests.post")
@patch("polaris_integrations.gerar_audio")
@patch("polaris_integrations.subprocess.run")
def test_audio_inference_sucesso(mock_run, mock_gerar_audio, mock_post, mock_transcribe):
    mock_transcribe.return_value = ([MagicMock(text="oi tudo bem?")], None)
    mock_post.return_value.json.return_value = {"resposta": "Olá, tudo sim!"}

    audio_content = b"fake audio data"
    files = {
        "audio": ("fake_audio.webm", io.BytesIO(audio_content), "audio/webm"),
        "session_id": (None, "12345")
    }

    response = client.post("/audio-inference/", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "resposta" in json_data
    assert json_data["resposta"] == "Olá, tudo sim!"
    assert json_data["tts_audio_url"].startswith("http://localhost:8010/audio/")
    assert json_data["user_audio_url"].startswith("http://localhost:8010/audio/")


@patch("polaris_integrations.whisper.transcribe", side_effect=RuntimeError("Falha no whisper"))
def test_audio_inference_falha(mock_transcribe):
    audio_content = "conteúdo inválido".encode("utf-8")
    files = {
        "audio": ("audio_broken.webm", io.BytesIO(audio_content), "audio/webm"),
        "session_id": (None, "erro123")
    }

    response = client.post("/audio-inference/", files=files)

    assert response.status_code == 500
    assert "erro" in response.json()
