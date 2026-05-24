# Gamify API

API REST para a aplicação Gamify, construída com **FastAPI** e integrada ao **Supabase** para autenticação.

## Tecnologias

- Python 3.11+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Supabase](https://supabase.com/) (autenticação OAuth e email/senha)
- [PDM](https://pdm-project.org/) (gerenciador de pacotes)

## Pré-requisitos

- Python 3.11 ou superior
- PDM instalado (`pip install pdm`)
- Um projeto Supabase configurado

## Configuração

1. Clone o repositório e instale as dependências:

```bash
pdm install
```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
SUPABASE_URL=https://<seu-projeto>.supabase.co
SUPABASE_KEY=<sua-anon-key>
SUPABASE_OAUTH_REDIRECT_URL=http://localhost:8000/v1/auth/oauth/callback
API_KEY=<chave-secreta-para-sessao>
```

3. (Opcional) Edite `config/settings.toml` para ajustar os provedores OAuth habilitados:

```toml
[auth.providers.supabase]
enabled = true
providers = ["email", "google", "github"]
```

## Execução

```bash
pdm run uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger): `http://localhost:8000/docs`

## Estrutura do Projeto

```
api/
├── main.py                  # Ponto de entrada da aplicação
├── pyproject.toml           # Dependências e configuração do projeto
├── config/
│   ├── config.py            # Configuração singleton (env + TOML)
│   └── settings.toml        # Configurações estáticas (provedores OAuth, etc.)
└── src/
    ├── routes/
    │   └── auth.py          # Rotas de autenticação (/v1/auth/...)
    └── services/
        └── supabase_auth.py # Serviço de autenticação via Supabase
```

## Endpoints

Todos os endpoints estão sob o prefixo `/v1/auth`.

| Método | Rota                        | Descrição                                              |
|--------|-----------------------------|--------------------------------------------------------|
| GET    | `/v1/auth/`                 | Verifica se a rota está online                         |
| GET    | `/v1/auth/providers`        | Lista os provedores de autenticação disponíveis        |
| GET    | `/v1/auth/oauth/{provider}/sign-in` | Inicia o fluxo OAuth com o provedor especificado |
| GET    | `/v1/auth/oauth/callback`   | Callback do OAuth; troca o código por sessão           |

### Parâmetros — `GET /v1/auth/oauth/{provider}/sign-in`

| Parâmetro      | Tipo   | Obrigatório | Descrição                                          |
|----------------|--------|-------------|----------------------------------------------------|
| `provider`     | path   | Sim         | Nome do provedor (`google`, `github`, etc.)        |
| `redirect_to`  | query  | Não         | URL de callback customizada                        |
| `scopes`       | query  | Não         | Escopos adicionais solicitados ao provedor         |
| `app_redirect` | query  | Não         | URL para redirecionar o app após autenticação      |

Quando `app_redirect` é fornecido, o callback redireciona para essa URL com `access_token` e `refresh_token` no fragmento da URL (`#access_token=...&refresh_token=...`).
