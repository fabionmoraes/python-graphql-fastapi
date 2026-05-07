# GraphQL com FastAPI, Strawberry e Trino

API GraphQL construída com FastAPI e Strawberry, usando Trino como fonte única de dados. Serve como camada de acesso a dados federados para outras plataformas consumirem via GraphQL.

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- Strawberry GraphQL
- Trino (com dialeto SQLAlchemy)
- SQLAlchemy 2 (connection pooling e execução de queries)
- Poetry

## Arquitetura do projeto

O projeto segue uma arquitetura em camadas com responsabilidades bem definidas:

- `app/core`: configurações globais, cliente Trino, segurança e container de dependências.
- `app/domain`: entidades de domínio e contratos de repositório (interfaces abstratas).
- `app/infrastructure/trino`: implementações concretas de repositório usando Trino.
- `app/presentation/graphql`: schema GraphQL, queries, tipos e paginação.

O Trino é a única fonte de dados. Não há ORM, migrations ou banco local — o schema vive nos data sources externos (MySQL, PostgreSQL, etc.) acessados via Trino de forma federada.

### Estrutura de pastas

```text
graphql-python/
├── app/
│   ├── core/
│   │   ├── config.py         # variáveis de ambiente e settings
│   │   ├── container.py      # injeção de dependências
│   │   ├── dependencies.py   # Basic Auth (FastAPI Depends)
│   │   ├── security.py       # verificação de credenciais
│   │   └── trino.py          # TrinoClient (pool + execução async)
│   ├── domain/
│   │   ├── entities/         # dataclasses de domínio (Product, etc.)
│   │   └── repositories/     # interfaces abstratas de repositório
│   ├── infrastructure/
│   │   └── trino/
│   │       └── repositories/ # implementações concretas com SQL Trino
│   └── presentation/
│       └── graphql/
│           ├── products/     # queries, tipos e mappers de produto
│           ├── pagination.py # paginação cursor-based
│           ├── context.py    # acesso ao container via contexto GraphQL
│           └── schema.py     # schema principal
├── .env
├── .env.example
├── pyproject.toml
└── poetry.lock
```

## Como instalar

### 1) Pré-requisitos

- Python 3.14
- Poetry
- Trino acessível (local ou remoto)

### 2) Clonar e acessar o projeto

```bash
git clone <url-do-repositorio>
cd graphql-python
```

### 3) Instalar dependências

```bash
poetry install
```

### 4) Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com os dados do seu ambiente Trino e as credenciais da API.

## Como rodar

```bash
poetry run uvicorn app.main:app --reload
```

Aplicação disponível em:

- Endpoint GraphQL: [http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql)

## Autenticação

A API usa **HTTP Basic Auth**. Todas as requisições ao endpoint `/graphql` exigem o header:

```
Authorization: Basic <base64(username:password)>
```

As credenciais são configuradas no `.env`:

```env
API_USERNAME=admin
API_PASSWORD=sua-senha
```

No Insomnia ou Postman, use a aba **Auth → Basic Auth** e preencha usuário e senha diretamente.

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `ENVIRONMENT` | Ambiente da aplicação | `development` |
| `API_USERNAME` | Usuário da API GraphQL | `admin` |
| `API_PASSWORD` | Senha da API GraphQL | — |
| `GRAPHQL_MAX_QUERY_DEPTH` | Profundidade máxima de queries | `8` |
| `TRINO_HOST` | Host do Trino | `localhost` |
| `TRINO_PORT` | Porta do Trino | `8080` |
| `TRINO_USER` | Usuário do Trino | `trino` |
| `TRINO_PASSWORD` | Senha do Trino (Basic Auth) | — |
| `TRINO_HTTP_SCHEME` | `http` ou `https` | `http` |
| `TRINO_POOL_SIZE` | Tamanho do connection pool | `5` |

## Trino como fonte de dados

O `TrinoClient` usa o dialeto `trino[sqlalchemy]` com `QueuePool` para reaproveitar conexões. Como o cliente Trino é síncrono, as queries rodam em um `ThreadPoolExecutor` para não bloquear o event loop do FastAPI.

Queries com autenticação no Trino usam `BasicAuthentication` passada via `connect_args` — a senha nunca aparece na URL de conexão.

As tabelas são referenciadas com o caminho completo `catalog.schema.table` diretamente no repositório, permitindo queries federadas entre diferentes fontes:

```sql
SELECT p.*, pc.title
FROM mysql.demo.products p
LEFT JOIN postgresql.public.product_catalog pc ON p.product_catalog_id = pc.id
```

## Exemplos de queries GraphQL

### Listar produtos com paginação

```graphql
query {
  products(first: 10) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        name
        price
        sku
        stock
        productCatalog {
          id
          title
        }
      }
    }
  }
}
```

### Listar com filtros

```graphql
query {
  products(
    first: 5
    where: { name: { like: "notebook" } }
  ) {
    edges {
      node {
        id
        name
        price
      }
    }
  }
}
```

### Buscar produto por ID

```graphql
query {
  product(id: 1) {
    id
    name
    price
    sku
    stock
  }
}
```

### Paginação com cursor

```graphql
query {
  products(first: 5, after: "<endCursor da página anterior>") {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        name
      }
    }
  }
}
```

## Comandos úteis

```bash
# Instalar dependências
poetry install

# Atualizar lock file
poetry lock

# Rodar servidor em desenvolvimento
poetry run uvicorn app.main:app --reload
```
