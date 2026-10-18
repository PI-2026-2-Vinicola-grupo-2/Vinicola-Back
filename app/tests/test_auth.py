def _registro(email, perfil="produtor_exportador", senha="senha-segura"):
    return {
        "nome": "Usuário Teste",
        "email": email,
        "senha": senha,
        "perfil": perfil,
    }


def test_cadastro_produtor_e_login(client):
    resposta = client.post("/auth/register", json=_registro("produtor@example.com"))
    assert resposta.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "produtor@example.com", "senha": "senha-segura"},
    )
    assert login.status_code == 200
    assert login.json()["nome"] == "Usuário Teste"
    assert login.json()["perfil"] == "produtor_exportador"


def test_cadastro_restringe_perfis_e_valida_dados(client):
    for perfil in ("administrador", "analista_dados"):
        assert client.post(
            "/auth/register", json=_registro(f"{perfil}@example.com", perfil)
        ).status_code == 403
    assert client.post(
        "/auth/register", json=_registro("curta@example.com", senha="1234567")
    ).status_code == 422


def test_cadastro_duplicado_e_login_com_senha_errada(client):
    payload = _registro("duplicado@example.com")
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 400
    assert client.post(
        "/auth/login",
        json={"email": payload["email"], "senha": "incorreta"},
    ).status_code == 401
