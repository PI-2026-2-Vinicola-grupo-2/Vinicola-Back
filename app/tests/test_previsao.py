def test_previsao_curta_e_simulada(client, token_analista, monkeypatch):
    from app.services import thingspeak_client

    monkeypatch.setattr(
        thingspeak_client,
        "get_historico",
        lambda resultados=200: [
            {
                "entry_id": 1,
                "temperatura": 25.8,
                "umidade": 60.0,
                "registrado_em": "2026-10-18T12:00:00Z",
            }
        ],
    )
    resposta = client.get(
        "/previsao/janela-colheita",
        headers={"Authorization": f"Bearer {token_analista}"},
    )
    dados = resposta.json()
    assert resposta.status_code == 200
    assert dados["simulado"] is True
    assert dados["confianca"] is None
    assert dados["dias_de_historico"] == 0
    assert "insuficiente" in dados["aviso"]


def test_previsao_sem_historico_mantem_confianca_nula(client, token_analista, monkeypatch):
    from app.services import thingspeak_client

    monkeypatch.setattr(thingspeak_client, "get_historico", lambda resultados=200: [])
    resposta = client.get(
        "/previsao/janela-colheita",
        headers={"Authorization": f"Bearer {token_analista}"},
    )
    dados = resposta.json()
    assert resposta.status_code == 200
    assert dados["dias_de_historico"] == 0
    assert dados["confianca"] is None
    assert len(dados["dias"]) == 7


def test_previsao_com_historico_suficiente_usa_media(client, token_analista, monkeypatch):
    from app.services import thingspeak_client

    monkeypatch.setattr(
        thingspeak_client,
        "get_historico",
        lambda resultados=200: [
            {
                "entry_id": 1,
                "temperatura": 20.0,
                "umidade": 50.0,
                "registrado_em": "2026-10-01T12:00:00Z",
            },
            {
                "entry_id": 2,
                "temperatura": 30.0,
                "umidade": 70.0,
                "registrado_em": "2026-10-10T12:00:00Z",
            },
        ],
    )
    resposta = client.get(
        "/previsao/janela-colheita",
        headers={"Authorization": f"Bearer {token_analista}"},
    )
    dados = resposta.json()
    assert resposta.status_code == 200
    assert dados["dias_de_historico"] == 9
    assert dados["confianca"] == 60
    assert dados["dias"][0]["temperatura"] == 24.3
    assert dados["dias"][0]["umidade"] == 59.0
