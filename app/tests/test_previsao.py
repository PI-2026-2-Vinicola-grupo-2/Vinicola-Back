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
