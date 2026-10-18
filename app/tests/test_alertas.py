from datetime import datetime, timedelta, timezone


def _alerta(client, monkeypatch, leitura):
    from app.services import thingspeak_client

    monkeypatch.setattr(thingspeak_client, "get_ultima_leitura", lambda: leitura)
    resposta = client.get(
        "/alertas",
        headers={"Authorization": "Bearer test-token"},
    )
    return resposta


def test_alertas_cada_regra_e_id_estavel(client, token_analista, monkeypatch):
    from app.core.config import settings
    from app.services import thingspeak_client

    headers = {"Authorization": f"Bearer {token_analista}"}
    leituras = [
        {"entry_id": 1, "temperatura": 25.0, "umidade": 90.0, "umidade_solo": 50.0},
        {"entry_id": 2, "temperatura": 25.0, "umidade": 20.0, "umidade_solo": 50.0},
        {"entry_id": 3, "temperatura": 35.0, "umidade": 60.0, "umidade_solo": 50.0},
        {"entry_id": 4, "temperatura": 15.0, "umidade": 60.0, "umidade_solo": 50.0},
    ]
    from datetime import datetime, timezone
    for leitura in leituras:
        leitura["registrado_em"] = datetime.now(timezone.utc).isoformat()
    for leitura, regra in zip(leituras, ("umidade_alta", "umidade_baixa", "temp_alta", "temp_baixa")):
        monkeypatch.setattr(thingspeak_client, "get_ultima_leitura", lambda leitura=leitura: leitura)
        resposta = client.get("/alertas", headers=headers)
        assert resposta.status_code == 200
        assert resposta.json()[0]["id"] == f"{regra}-{leitura['entry_id']}"
        assert resposta.json() == client.get("/alertas", headers=headers).json()

    monkeypatch.setattr(settings, "alerta_solo_seco", 30.0)
    leitura = {
        "entry_id": 5,
        "temperatura": 25.0,
        "umidade": 60.0,
        "umidade_solo": 20.0,
        "registrado_em": datetime.now(timezone.utc).isoformat(),
    }
    monkeypatch.setattr(thingspeak_client, "get_ultima_leitura", lambda: leitura)
    resposta = client.get("/alertas", headers=headers)
    assert resposta.json()[0]["id"] == "solo_seco-5"


def test_alerta_de_leitura_velha(client, token_analista, monkeypatch):
    from app.services import thingspeak_client

    leitura = {
        "entry_id": 9,
        "temperatura": 40.0,
        "umidade": 99.0,
        "umidade_solo": 1.0,
        "registrado_em": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
    }
    monkeypatch.setattr(thingspeak_client, "get_ultima_leitura", lambda: leitura)
    resposta = client.get(
        "/alertas", headers={"Authorization": f"Bearer {token_analista}"}
    )
    assert resposta.json()[0]["titulo"] == "Sem leituras recentes"
    assert resposta.json()[0]["tipo"] == "info"
