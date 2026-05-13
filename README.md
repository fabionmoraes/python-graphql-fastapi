# GraphQL com FastAPI, Strawberry e Trino

API GraphQL construída com FastAPI e Strawberry, usando Trino como fonte única de dados via **Ibis Framework**. Serve como camada de acesso a dados federados para outras plataformas consumirem via GraphQL.

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- Strawberry GraphQL
- Trino (via Ibis Framework)
- Ibis Framework `ibis-framework[trino]` (construção de expressões e execução async)
- Poetry

## Arquitetura do projeto

O projeto segue um fluxo em camadas com responsabilidades bem definidas:

```
GraphQL Resolver
   ↓
Service
   ↓
Repository (Ibis expressions → Trino SQL)
   ↓
Trino
```

| Camada | Responsabilidade |
|---|---|
| `infrastructure/graphql/utils/selection.py` | Extrai os campos pedidos no GraphQL como `dict` |
| `infrastructure/graphql/queries/` | Recebe a requisição, chama o service, retorna o tipo GraphQL |
| `infrastructure/graphql/loaders.py` | DataLoaders Strawberry para resolver relações N+1 |
| `services/` | Coordena o fluxo entre resolver e repositório |
| `infrastructure/trino/repositories/` | Constrói expressões Ibis, executa via `IbisClient` e converte rows em entidades |
| `infrastructure/trino/ibis_client.py` | `IbisClient`: conexão Ibis/Trino e execução async via ThreadPoolExecutor |

O campo `selectedFields` percorre o caminho: resolver → service → repositório. Dentro do repositório o método `_columns` decide quais colunas e JOINs incluir com base nos campos pedidos — nenhuma string arbitrária do cliente toca o SQL.

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
│   │   ├── entities/
│   │   │   ├── pagination.py    # PageResult genérico
│   │   │   └── product.py       # ProductEntity, ProductCatalogEntity, ProductWhereEntity
│   │   ├── product_repository.py   # interface ProductRepository
│   │   └── catalog_repository.py   # interface CatalogRepository
│   │
│   ├── infrastructure/
│   │   ├── graphql/
│   │   │   ├── types/
│   │   │   │   ├── product_type.py  # tipos Strawberry (ProductType, ProductCatalogType, inputs)
│   │   │   │   └── mappers.py       # conversão entity → tipo Strawberry
│   │   │   ├── queries/
│   │   │   │   ├── product_query.py # resolvers: products, product
│   │   │   │   └── catalog_query.py # resolvers: productCatalogs, productCatalog
│   │   │   ├── loaders.py           # DataLoaders (N+1 prevention)
│   │   │   ├── utils/
│   │   │   │   ├── selection.py     # parse_selected_fields — retorna dict de campos pedidos
│   │   │   │   └── constants.py     # MAX_FIRST e outras constantes
│   │   │   ├── pagination.py        # Connection, Edge, PageInfo, build_connection
│   │   │   ├── context.py           # acesso ao container via contexto GraphQL
│   │   │   └── schema.py            # schema principal
│   │   │
│   │   └── trino/
│   │       ├── ibis_client.py       # IbisClient: conexão Ibis, cache de tabelas, execução async
│   │       └── repositories/
│   │           ├── product_repository_impl.py  # expressões Ibis para products + joins com catalog
│   │           └── catalog_repository_impl.py  # expressões Ibis para product_catalog
│   │
│   ├── services/
│   │   ├── product_service.py   # list_products, get_product, list_by_catalog_ids_grouped
│   │   └── catalog_service.py   # list_catalogs, get_catalog
│   │
│   └── main.py                  # FastAPI app, lifespan, rota GraphQL
├── .env
├── .env.example
├── pyproject.toml
└── poetry.lock
```

### Projeção de campos e JOINs sob demanda

O método `_columns` em cada repositório analisa o `dict` de campos pedidos e inclui apenas as colunas necessárias. O JOIN entre `products` e `product_catalog` só ocorre quando o cliente pedir `productCatalog { ... }` ou usar o filtro `modelTitle`. O `totalCount` na paginação só dispara um `COUNT` se o cliente incluir `totalCount` na query.

```python
# JOIN só é incluído se o cliente pedir productCatalog ou filtrar por modelTitle
needs_join = "productCatalog" in selected_fields or (
    where is not None and where.model_title is not None
)
```

### DataLoader e relação N+1

`ProductCatalogType` expõe um campo `products` que carrega os produtos de um catálogo. Para evitar N+1 queries, o resolver usa um `DataLoader` configurado em `infrastructure/graphql/loaders.py`. Uma única query em lote busca todos os produtos dos catálogos solicitados e os agrupa por `catalog_id`.

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
| `TRINO_POOL_SIZE` | Workers no ThreadPoolExecutor | `5` |
| `TRINO_CATALOG` | Catálogo padrão do Trino | — |
| `TRINO_SCHEMA` | Schema padrão do Trino | — |

## Trino como fonte de dados

O `IbisClient` usa `ibis.trino.connect` para estabelecer a conexão. Como o cliente Trino é síncrono, as queries rodam em um `ThreadPoolExecutor` para não bloquear o event loop do FastAPI. Os resultados chegam como `DataFrame` do pandas e são convertidos para `list[dict]`.

As tabelas são referenciadas com o caminho completo `(catalog, schema)` passado via `client.table(name, database=(catalog, schema))`, permitindo queries federadas entre fontes distintas:

```python
_PRODUCTS_DB: tuple[str, str] = ("mysql", "demo")
_CATALOG_DB:  tuple[str, str] = ("postgresql", "public")
```

Autenticação no Trino usa `BasicAuthentication` passada diretamente na conexão — a senha nunca aparece na URL.

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

### Filtrar por nome, SKU ou título do catálogo

```graphql
query {
  products(
    first: 5
    where: {
      name: { _like: "notebook" }
      modelTitle: { _eq: "Linha Pro" }
    }
  ) {
    edges {
      node { id name price }
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
      node { id name }
    }
  }
}
```

### Listar catálogos com seus produtos (relação inversa via DataLoader)

```graphql
query {
  productCatalogs(first: 10) {
    edges {
      node {
        id
        title
        products {
          id
          name
          price
        }
      }
    }
  }
}
```

### Buscar catálogo por ID

```graphql
query {
  productCatalog(id: 3) {
    id
    title
  }
}
```

### Pedir apenas campos necessários (sem JOIN)

```graphql
query {
  products(first: 20) {
    edges {
      node { id name price }
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

# Lint
poetry run ruff check .

# Testes com cobertura
poetry run pytest --cov
```
