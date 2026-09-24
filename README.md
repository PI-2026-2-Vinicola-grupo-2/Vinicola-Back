# Vinícola-Back

API do Projeto Integrador "Vinícola" (Inteligência de Dados no Vale do São Francisco) — autentica usuários por perfil, consome o canal climático do ThingSpeak, trata os dados e expõe tudo via REST pro Vinicola-Front consumir.

## Stack

- Python 3.11 + FastAPI
- Autenticação JWT (`python-jose`) + RBAC por perfil
- Pytest + GitHub Actions (CI a cada push/PR)
- Consumo da API REST do ThingSpeak (`requests`)

## Como rodar localmente

```bash
git clone <url-do-repo>
cd Vinicola-Back
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # preencha com os valores reais
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000` e a documentação interativa (gerada automaticamente pelo FastAPI) fica em `http://localhost:8000/docs`.

## Variáveis de ambiente

| variável | descrição |
|---|---|
| `JWT_SECRET_KEY` | chave usada pra assinar os tokens — nunca commitar o valor real |
| `JWT_ALGORITHM` | algoritmo do JWT (padrão `HS256`) |
| `JWT_EXPIRE_MINUTES` | validade do token em minutos |
| `THINGSPEAK_CHANNEL_ID` | canal climático (`3500405`) |
| `THINGSPEAK_READ_API_KEY` | chave de leitura do canal, se ele deixar de ser público |
| `CORS_ORIGINS` | origens liberadas a chamar a API, separadas por vírgula |

Os valores reais ficam só no `.env` local (ou em Secrets do GitHub/da nuvem) — o `.env.example` no repositório serve só de modelo.

## Estrutura do projeto

```
Vinicola-Back/
├── main.py                    # entrypoint FastAPI, CORS e routers
├── requirements.txt
├── .env.example
├── .github/workflows/ci.yml   # roda pytest a cada push/PR
└── app/
    ├── core/
    │   ├── config.py           # leitura das variáveis de ambiente
    │   └── security.py         # hash de senha, JWT, RBAC
    ├── models/
    │   └── usuario.py          # schemas Pydantic (registro, login, token)
    ├── routers/
    │   ├── auth.py              # /auth/register, /auth/login
    │   └── clima.py             # /clima/atual, /clima/historico
    ├── services/
    │   └── thingspeak_client.py # consumo da API REST do ThingSpeak
    └── tests/
        └── test_health.py
```

## Autenticação e perfis

Login retorna um JWT com o perfil do usuário embutido. Três perfis controlam o acesso às rotas:

- `produtor_exportador`
- `analista_dados`
- `administrador`

Rotas sensíveis (como `/clima/historico`) exigem token válido de um perfil autorizado — ver `require_role()` em `core/security.py`.

## Rotas disponíveis

| rota | método | acesso |
|---|---|---|
| `/health` | GET | público |
| `/auth/register` | POST | público |
| `/auth/login` | POST | público |
| `/clima/atual` | GET | público |
| `/clima/historico` | GET | `analista_dados`, `administrador` |

## Testes

```bash
pytest
```

O mesmo comando roda automaticamente no GitHub Actions a cada push/PR pra `main`.

## Status atual

- [x] Estrutura do projeto, CI/CD e branch protection
- [x] Configuração base e segurança (JWT, CORS)
- [x] Autenticação e RBAC
- [x] Integração com o ThingSpeak
- [ ] Persistência real no banco (depende do schema do Vinicola-BD)
- [ ] Modelo preditivo de janela de colheita (RF06)
- [ ] Motor de alertas (RF09)
- [ ] Relatórios de segurança e qualidade + testes finais

Usuários e leituras climáticas estão em memória por enquanto (`app/routers/auth.py`) — trocam pelo banco assim que o Vinicola-BD tiver o schema definido (ver `CONTRATO-BACKEND.md` no repositório do BD).

## Repositórios relacionados

- [Vinicola-IoT](../Vinicola-IoT) — dispositivo ESP32 + DHT publicando no ThingSpeak
- [Vinicola-BD](../Vinicola-BD) — modelagem e schema do banco
- [Vinicola-Front](../Vinicola-Front) — dashboard que consome esta API
