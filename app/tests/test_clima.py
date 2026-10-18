def test_clima_atual_inclui_defasagem_e_tipo_float(client):
    resposta = client.get("/clima/atual")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert isinstance(dados["temperatura"], float)
    assert isinstance(dados["umidade"], float)
    assert isinstance(dados["defasagem_minutos"], int)
    assert dados["desatualizado"] is True


def test_historico_exige_token_e_aceita_horas(client, token_analista):
    assert client.get("/clima/historico").status_code == 401
    resposta = client.get(
        "/clima/historico?horas=24",
        headers={"Authorization": f"Bearer {token_analista}"},
    )
    assert resposta.status_code == 200
    assert resposta.json()[0]["umidade_solo"] == 40.0


def test_sincronizacao_so_para_admin_e_deduplica(client, token_analista, token_admin):
    headers_analista = {"Authorization": f"Bearer {token_analista}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    assert client.post("/clima/sincronizar", headers=headers_analista).status_code == 403
    primeira = client.post("/clima/sincronizar", headers=headers_admin)
    segunda = client.post("/clima/sincronizar", headers=headers_admin)
    assert primeira.status_code == 200
    assert primeira.json()["novas_leituras"] == 1
    assert segunda.json()["novas_leituras"] == 0
