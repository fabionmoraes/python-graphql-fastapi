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

O projeto segue um fluxo em camadas com responsabilidades bem definidas:

```
GraphQL Resolver
   ↓
Service
   ↓
Query Builder
   ↓
Repository (Trino)
   ↓
Trino SQL
```

Cada camada tem uma responsabilidade única:

| Camada | Responsabilidade |
|---|---|
| `graphql/utils/selection.py` | Extrai os campos pedidos no GraphQL como `dict` |
| `graphql/queries/` | Recebe a requisição, chama o service, retorna o tipo GraphQL |
| `services/` | Coordena o fluxo entre resolver e repositório |
| `query_builders/trino/` | Monta o SQL com base nos campos selecionados e no mapeamento seguro |
| `repositories/trino/mappings/` | Define o mapa seguro de campos GraphQL → colunas SQL e JOINs |
| `repositories/trino/` | Executa o SQL e converte as linhas em entidades de domínio |
| `infrastructure/trino/` | Cliente Trino: pool de conexões e execução async |

O campo `selectedFields` percorre o caminho: resolver → service → query builder → repositório. Nenhum texto vindo diretamente do GraphQL toca o SQL — tudo passa pelo mapeamento em `mappings/`.

### Estrutura de pastas

```text
graphql-python/
├── app/
│   ├── core/
│   │   ├── config.py            # variáveis de ambiente e settings
│   │   ├── container.py         # injeção de dependências (expõe services)
│   │   ├── dependencies.py      # Basic Auth (FastAPI Depends)
│   │   └── security.py          # verificação de credenciais
│   │
│   ├── domain/
│   │   └── entities/            # dataclasses de domínio (ProductEntity, etc.)
│   │
│   ├── graphql/
│   │   ├── types/               # tipos Strawberry (@strawberry.type / @strawberry.input)
│   │   ├── queries/             # resolvers GraphQL
│   │   ├── utils/
│   │   │   └── selection.py     # parse_selected_fields — genérico, retorna dict
│   │   ├── pagination.py        # Connection, Edge, PageInfo, build_connection
│   │   ├── context.py           # acesso ao container via contexto GraphQL
│   │   └── schema.py            # schema principal
│   │
│   ├── services/
│   │   └── product_service.py   # coordena fluxo entre resolver e repositório
│   │
│   ├── query_builders/
│   │   └── trino/
│   │       └── product_query_builder.py  # monta SELECT, JOINs, WHERE, ORDER BY, LIMIT
│   │
│   ├── repositories/
│   │   └── trino/
│   │       ├── mappings/
│   │       │   └── product_fields.py     # whitelist segura: campo GraphQL → coluna SQL
│   │       └── product_trino_repository.py  # executa SQL, converte row → entity
│   │
│   ├── infrastructure/
│   │   └── trino/
│   │       └── client.py        # TrinoClient (pool + execução async)
│   │
│   └── main.py                  # FastAPI app, lifespan, rota GraphQL
├── .env
├── .env.example
├── pyproject.toml
└── poetry.lock
```

### Mapeamento seguro de campos

O arquivo `repositories/trino/mappings/product_fields.py` é a única fonte de verdade entre campos GraphQL e colunas SQL. Nenhuma string vinda do cliente chega ao SQL diretamente.

```python
PRODUCT_FIELDS = {
    "id":    {"column": "p.id"},
    "name":  {"column": "p.name"},
    "price": {"column": "p.price"},
    "productCatalog": {
        "join": "LEFT JOIN postgresql.public.product_catalog pc ON ...",
        "fields": {
            "id":    {"column": "pc.id"},
            "title": {"column": "pc.title"},
        },
    },
}
```

O `ProductQueryBuilder` itera esse mapa com os campos pedidos no GraphQL e constrói o SELECT e os JOINs necessários. Campos fora do mapa são ignorados silenciosamente.

### Projeção de campos

O JOIN com `product_catalog` só ocorre se o cliente pedir `productCatalog { ... }` na query. Queries que não pedem o campo aninhado executam sem JOIN. O `totalCount` na paginação também só dispara um COUNT no banco se o cliente incluir `totalCount` na query.

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

As tabelas são referenciadas com o caminho completo `catalog.schema.table` diretamente no mapeamento, permitindo queries federadas entre diferentes fontes de dados:

```sql
SELECT p.id AS id, p.name AS name, pc.id AS productCatalog_id, pc.title AS productCatalog_title
FROM mysql.demo.products p
LEFT JOIN postgresql.public.product_catalog pc ON p.product_catalog_id = pc.id
WHERE p.name LIKE :name_like
ORDER BY p.id ASC
LIMIT :limit
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
    where: { name: { _like: "notebook" } }
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

### Pedindo apenas campos necessários (sem JOIN)

```graphql
query {
  products(first: 20) {
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

Nessa query o JOIN com `product_catalog` não é executado — o SQL gerado consulta apenas a tabela `products`.

## Comandos úteis

```bash
# Instalar dependências
poetry install

# Atualizar lock file
poetry lock

# Rodar servidor em desenvolvimento
poetry run uvicorn app.main:app --reload
```
