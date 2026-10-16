# Vinícola — Backend

API REST do **Projeto Integrador — Inteligência de Dados no Vale do São Francisco**.

O backend é responsável pela autenticação dos usuários, controle de acesso, disponibilização dos dados climáticos e comunicação com os serviços utilizados pela solução.

## Visão geral

O backend foi desenvolvido com **Python e FastAPI** e está hospedado em produção no **Render**.

O banco de dados utilizado em produção é o **PostgreSQL do Supabase**.

```text
ESP32 + DHT11
      │
      │ MQTT
      ▼
ThingSpeak
      │
      │ API REST
      ▼
FastAPI — Render
      │
      ├── JWT
      ├── RBAC
      ├── Rate Limiting
      └── SQLAlchemy
      │
      ▼
Supabase PostgreSQL
      │
      ▼
Frontend
```

## Produção

### API

```text
https://vinicola-back.onrender.com
```

### Banco de dados

O banco de produção é fornecido pelo **Supabase**, utilizando PostgreSQL.

As credenciais de conexão não ficam no código-fonte. No ambiente de produção, as variáveis necessárias devem ser configuradas no painel do Render.

> Não publique no GitHub a senha do banco, a chave JWT, API Keys ou qualquer outro secret.

## Stack

- **Python 3.11**
- **FastAPI** — criação da API REST
- **Uvicorn** — servidor ASGI
- **SQLAlchemy** — acesso ao banco de dados
- **PostgreSQL** — banco de dados
- **Supabase** — serviço de banco PostgreSQL utilizado em produção
- **python-jose** — JWT
- **Passlib / bcrypt** — hash e verificação de senhas
- **SlowAPI** — rate limiting
- **Pydantic / Pydantic Settings** — validação e configuração
- **Requests** — integração com a API do ThingSpeak
- **Pytest** — testes
- **GitHub Actions** — integração contínua

## Funcionalidades

### Autenticação

O sistema possui autenticação baseada em JWT.

O login valida o e-mail e a senha do usuário e retorna um token contendo informações necessárias para identificar o usuário e seu perfil.

### Controle de acesso — RBAC

O backend trabalha com três perfis:

- `produtor_exportador`
- `analista_dados`
- `administrador`

As permissões são verificadas no backend, impedindo que o frontend seja o responsável pela autorização real.

### Rate limiting

Algumas rotas possuem limitação de requisições para reduzir abuso e tentativas excessivas de acesso.

### CORS

As origens permitidas são configuradas através da variável `CORS_ORIGINS`.

### HTTPS

Em ambiente de produção, o backend pode redirecionar requisições HTTP para HTTPS através da configuração de produção.

## Endpoints

| Endpoint | Método | Acesso | Descrição |
|---|---|---|---|
| `/health` | GET | Público | Verifica se a API está disponível |
| `/auth/register` | POST | Público | Cria uma conta de usuário |
| `/auth/login` | POST | Público | Realiza autenticação |
| `/clima/atual` | GET | Público | Retorna a última leitura climática |
| `/clima/historico` | GET | `analista_dados`, `administrador` | Retorna o histórico climático |

A documentação interativa do FastAPI fica disponível em:

```text
https://vinicola-back.onrender.com/docs
```

## Integração com ThingSpeak

O backend consulta o canal climático do ThingSpeak para obter as leituras enviadas pelo dispositivo IoT.

Canal utilizado:

```text
3500405
```

Os campos utilizados atualmente representam:

| Campo | Informação |
|---|---|
| `field1` | Temperatura |
| `field2` | Umidade |

A integração está implementada em:

```text
app/services/thingspeak_client.py
```

## Banco de dados — Supabase

O backend utiliza SQLAlchemy para comunicação com o PostgreSQL.

Em produção, o PostgreSQL é disponibilizado pelo Supabase. A aplicação recebe os dados de conexão por variáveis de ambiente configuradas no Render.

Variáveis utilizadas pelo projeto:

| Variável | Finalidade |
|---|---|
| `DB_HOST` | Host do PostgreSQL |
| `DB_PORT` | Porta do PostgreSQL |
| `DB_NAME` | Nome do banco |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |

> Os valores reais dessas variáveis não devem ser publicados no repositório.

## Variáveis de ambiente

Exemplo de configuração:

```env
JWT_SECRET_KEY=chave-secreta-forte
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
THINGSPEAK_CHANNEL_ID=3500405
THINGSPEAK_READ_API_KEY=
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
ENVIRONMENT=development
```

Em produção, os valores devem ser configurados diretamente no ambiente do Render.

## Estrutura do projeto

```text
Vinicola-Back/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── models/
│   │   ├── db_models.py
│   │   └── usuario.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── clima.py
│   ├── services/
│   │   └── thingspeak_client.py
│   └── tests/
│       └── test_health.py
└── scripts/
    └── benchmark_rbac.py
```

## Como executar localmente

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Vinicola-Back
```

### 2. Criar ambiente virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar o `.env`

Crie o arquivo `.env` a partir do `.env.example` e informe as credenciais necessárias.

Para utilizar o banco de produção, devem ser utilizados os dados de conexão fornecidos pelo Supabase. Não coloque esses dados no Git.

### 5. Iniciar a API

```bash
uvicorn main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

Documentação:

```text
http://localhost:8000/docs
```

## Testes

Execute:

```bash
pytest
```

Os testes também são executados pelo GitHub Actions conforme a configuração de CI do projeto.

## Deploy no Render

O backend é hospedado no Render.

De forma geral, o serviço deve utilizar:

```text
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
```

As variáveis de ambiente de produção devem ser cadastradas no próprio Render.

O banco utilizado pelo serviço em produção é o PostgreSQL do Supabase.

## Segurança

Controles presentes no projeto:

- autenticação JWT;
- hash de senhas;
- RBAC;
- rate limiting;
- CORS configurável;
- secrets por variáveis de ambiente;
- HTTPS em produção;
- validação através de Pydantic.

Nunca devem ser versionados:

- `.env`;
- senhas;
- JWT Secret;
- credenciais do Supabase/PostgreSQL;
- API Keys do ThingSpeak;
- credenciais MQTT.

## Status atual

- [x] API FastAPI
- [x] Autenticação JWT
- [x] RBAC
- [x] Rate limiting
- [x] CORS
- [x] Integração com ThingSpeak
- [x] Modelo de usuário no banco
- [x] PostgreSQL em produção via Supabase
- [x] API hospedada no Render
- [x] Teste básico de health check
- [x] CI com GitHub Actions
- [ ] Evolução da persistência completa das leituras climáticas
- [ ] Ingestão automática contínua das leituras
- [ ] Modelo preditivo de janela de colheita
- [ ] Motor de alertas integrado ao backend
- [ ] Expansão dos testes automatizados

## Repositórios relacionados

- **Frontend:** Vinicola-Front — dashboard web que consome esta API.
- **IoT:** Vinicola-IoT — ESP32 + DHT11 responsável pela coleta e envio das leituras ao ThingSpeak.
- **Banco:** Supabase PostgreSQL — banco utilizado pelo backend em produção.

## Rotas integradas ao Front

- `GET /alertas` — gera alertas a partir da leitura climática atual.
- `GET /previsao/janela-colheita` — gera uma estimativa de 7 dias usando o histórico do ThingSpeak.

A rota de previsão é uma etapa de integração. O modelo preditivo de Machine Learning definitivo pode substituir esse serviço quando houver histórico suficiente para treinamento e validação.
