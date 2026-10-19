from app.services.thingspeak_client import _formatar, _numero
from app.services.thingspeak_client import get_historico as cliente_get_historico
from app.core.config import settings
from app.services import thingspeak_client


def test_numero_e_formatar_convertem_strings():
    assert _numero("25.80") == 25.8
    assert _numero("não-numérico") is None
    assert _formatar(
        {
            "entry_id": 7,
            "field1": "25.80",
            "field2": "61.20",
            "field3": "40",
            "created_at": "2026-10-18T12:00:00Z",
        }
    ) == {
        "entry_id": 7,
        "temperatura": 25.8,
        "umidade": 61.2,
        "umidade_solo": 40.0,
        "registrado_em": "2026-10-18T12:00:00Z",
    }


def test_historico_configura_canal_chave_e_timeout(monkeypatch):
    chamadas = []

    class Resposta:
        def raise_for_status(self):
            return None

        def json(self):
            return {"feeds": []}

    def fake_get(url, params, timeout):
        chamadas.append((url, params, timeout))
        return Resposta()

    monkeypatch.setattr(thingspeak_client.requests, "get", fake_get)
    monkeypatch.setattr(settings, "thingspeak_channel_id", "123")
    monkeypatch.setattr(settings, "thingspeak_read_api_key", "read-key")

    assert cliente_get_historico(25) == []
    assert chamadas == [
        (
            "https://api.thingspeak.com/channels/123/feeds.json",
            {"results": 25, "api_key": "read-key"},
            10,
        )
    ]
