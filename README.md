# Vinícola-Back

API do Projeto Integrador "Vinícola" (Inteligência de Dados no Vale do São Francisco) — autentica usuários por perfil, consome o canal climático do ThingSpeak, persiste e trata os dados, e expõe tudo via REST pro Vinicola-Front consumir.

Não existe mais um repositório separado pro banco: a modelagem, as migrations e a lógica de ingestão de dados vivem aqui dentro, junto com a API.

## Stack

- Python 3.11 + FastAPI
- PostgreSQL + SQLAlchemy + Alembic (migrations)
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
cp .env.example .env           # preencha com os valores reais, inclusive o banco
alembic upgrade head           # aplica as migrations no banco local
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
| `DB_HOST` | endereço do banco PostgreSQL |
| `DB_PORT` | porta do banco (padrão `5432`) |
| `DB_NAME` | nome do banco (`vinicola`) |
| `DB_USER` | usuário do banco |
| `DB_PASSWORD` | senha do banco — nunca commitar o valor real |

Os valores reais ficam só no `.env` local (ou em Secrets do GitHub/da nuvem) — o `.env.example` no repositório serve só de modelo.

## Estrutura do projeto

```
Vinicola-Back/
├── main.py                     # entrypoint FastAPI, CORS e routers
├── requirements.txt
├── .env.example
├── alembic.ini                 # config das migrations
├── alembic/
│   └── versions/                 # histórico de migrations do banco
├── .github/workflows/ci.yml    # roda pytest a cada push/PR
└── app/
    ├── core/
    │   ├── config.py            # leitura das variáveis de ambiente
    │   ├── security.py          # hash de senha, JWT, RBAC
    │   └── database.py          # engine, sessionmaker, get_db()
    ├── models/
    │   ├── usuario.py            # schemas Pydantic (API)
    │   └── db_models.py          # tabelas reais (SQLAlchemy): usuarios, leituras_climaticas, dados_mercado, previsoes, alertas
    ├── routers/
    │   ├── auth.py                # /auth/register, /auth/login
    │   └── clima.py               # /clima/atual, /clima/historico
    ├── services/
    │   ├── thingspeak_client.py   # busca os dados no ThingSpeak
    │   └── ingestion_service.py   # grava as leituras no banco periodicamente
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

## Responsabilidades dentro deste repositório

- **Modelagem do banco** — `core/database.py`, `models/db_models.py`, migrations do Alembic
- **Ingestão de dados** — `services/ingestion_service.py`, job periódico consumindo o `thingspeak_client.py`
- **Segurança** — hardening de auth, secrets, RNF08/RNF10
- **Qualidade & Integração** — testes, CI/CD, documentação

## Status atual

- [x] Estrutura do projeto, CI/CD e branch protection
- [x] Configuração base e segurança (JWT, CORS)
- [x] Autenticação e RBAC
- [x] Integração com o ThingSpeak
- [ ] Modelagem do banco e migrations (`models/db_models.py`, Alembic)
- [ ] Ingestão automática das leituras (`services/ingestion_service.py`)
- [ ] Modelo preditivo de janela de colheita (RF06)
- [ ] Motor de alertas (RF09)
- [ ] Relatórios de segurança e qualidade + testes finais

Usuários e leituras climáticas estão em memória por enquanto (`app/routers/auth.py`) — trocam pelos models reais assim que `models/db_models.py` e as migrations estiverem prontos.

## Repositórios relacionados

- [Vinicola-IoT](../Vinicola-IoT) — dispositivo ESP32 + DHT publicando no ThingSpeak
- [Vinicola-Front](../Vinicola-Front) — dashboard que consome esta API
