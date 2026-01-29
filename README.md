# 🛒 Supermarket CRM API

API de alto desempenho para gestão de relacionamento e estoque de supermercados, construída com Django Ninja Extra e Python 3.14.

## 🚀 Tech Stack

- **Linguagem:** Python 3.14 (experimental)
- **Gerenciador de Pacotes:** [uv](https://github.com/astral-sh/uv)
- **Framework Web:** Django 6.0
- **API Engine:** Django Ninja Extra (Class-based controllers)
- **Linting/Formatting:** Ruff
- **Type Checking:** Pyright

## 🛠️ Configuração do Ambiente

Este projeto utiliza o layout `src` e o gerenciador `uv` para máxima performance.

### Pré-requisitos

- Ter o `uv` instalado.
- Disponibilidade do Python 3.14 (`pyenv` ou `uv python install 3.14`).

### Instalação

Clone o repositório:

```bash
git clone https://github.com
cd crm-django-ninja
```

Sincronize o ambiente virtual e as dependências:

```bash
uv sync
```

Execute as migrações do banco de dados:

```bash
uv run python manage.py migrate
```

Inicie o servidor de desenvolvimento:

```bash
uv run python manage.py runserver
```

A documentação interativa da API estará disponível em: [http://127.0.0.1](http://127.0.0.1)