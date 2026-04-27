# GraphQL com FastAPI, Strawberry e SQLAlchemy

API GraphQL construída com FastAPI e Strawberry, seguindo uma arquitetura em camadas (`core`, `application`, `domain`, `infrastructure`, `presentation`), com persistência em SQLite e autenticação JWT.

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- Strawberry GraphQL
- SQLAlchemy 2
- Pydantic 2 (validação de inputs das mutations)
- PyJWT
- Poetry
- SQLite

## Arquitetura do projeto

O projeto está organizado em camadas para separar responsabilidades:

- `app/core`: configurações globais, banco de dados e segurança (JWT).
- `app/domain`: entidades e contratos de repositório (regras de domínio).
- `app/application`: casos de uso e DTOs da aplicação.
- `app/infrastructure`: modelos ORM e implementações concretas de repositório.
- `app/presentation/graphql`: schema GraphQL, queries, mutations, tipos e validadores.

### Estrutura de pastas

```text
graphql-python/
├── app/
│   ├── application/
│   │   ├── dtos/
│   │   └── use_cases/
│   ├── core/
│   ├── domain/
│   │   ├── entities/
│   │   └── repositories/
│   ├── infrastructure/
│   │   └── persistence/
│   │       ├── models/
│   │       └── repositories/
│   └── presentation/
│       └── graphql/
│           ├── orders/
│           ├── products/
│           ├── users/
│           ├── schema.py
│           └── validation.py
├── db/
├── main.py
├── setup_db.py
├── pyproject.toml
└── poetry.lock
```

## Como instalar

### 1) Pré-requisitos

- Python 3.14 instalado
- Poetry instalado

### 2) Clonar e acessar o projeto

```bash
git clone <url-do-repositorio>
cd graphql-python
```

### 3) Instalar dependências

```bash
poetry install
```

### 4) (Opcional) Popular banco com dados iniciais

Esse script recria as tabelas e insere dados de exemplo.

```bash
poetry run python setup_db.py
```

## Como rodar

### Subir API em modo desenvolvimento

```bash
poetry run uvicorn main:app --reload
```

Aplicação disponível em:

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Endpoint GraphQL: [http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql)

## GraphQL com Strawberry

O schema é montado em `app/presentation/graphql/schema.py`, combinando:

- `Query`: `ProductQuery`, `UserQuery`, `OrderQuery`
- `Mutation`: `ProductMutation`, `UserMutation`, `OrderMutation`

O roteamento GraphQL é feito no `main.py` com `GraphQLRouter(schema)` no prefixo `/graphql`.

## Validação com Pydantic nas mutations

As mutations recebem objetos `input` e validam dados com Pydantic antes de persistir no banco.

Arquivos de validação:

- `app/presentation/graphql/products/validators.py`
- `app/presentation/graphql/users/validators.py`
- `app/presentation/graphql/orders/validators.py`
- `app/presentation/graphql/validation.py` (formatação do erro para GraphQL)

Em caso de payload inválido, a API retorna erro GraphQL com detalhes do campo inválido.

## Autenticação JWT

Fluxo atual:

1. `login` retorna `access_token`
2. operações protegidas (ex.: criação de pedido) exigem header:
   - `Authorization: Bearer <token>`

Configurações em `app/core/config.py`:

- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`

## Exemplos de operações GraphQL

### Criar produto

```graphql
mutation {
  createProduct(
    input: { name: "Notebook", price: 3200, sku: "NOTEBOOK_001", stock: 5 }
  ) {
    id
    name
    sku
  }
}
```

### Criar usuário

```graphql
mutation {
  createUser(input: { username: "fabio", email: "fabio@mail.com", role: "USER" }) {
    id
    username
    email
    role
  }
}
```

### Login

```graphql
mutation {
  login(input: { username: "fabio", email: "fabio@mail.com" }) {
    accessToken
    tokenType
  }
}
```

### Criar pedido (com token JWT)

```graphql
mutation {
  createOrder(input: { productId: 1, quantity: 2, totalPrice: 6400 }) {
    id
    productId
    quantity
    totalPrice
  }
}
```

### Consultar produtos

```graphql
query {
  products {
    id
    name
    price
    sku
    stock
    productModel {
      id
      title
    }
  }
}
```

## Banco de dados

- Banco local SQLite em `db/app.db`
- Tabelas criadas automaticamente em startup via `Base.metadata.create_all(bind=engine)`
- Script `setup_db.py` pode ser usado para reset e seed de dados de teste

## Comandos úteis

```bash
# Instalar/atualizar lock
poetry lock

# Instalar dependências
poetry install

# Rodar servidor
poetry run uvicorn main:app --reload

# Popular banco com dados de exemplo
poetry run python setup_db.py
```
