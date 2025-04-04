# API de Cálculo de Seguro Automotivo

## Visão Geral

Este projeto implementa um serviço de backend em FastAPI para calcular prêmios de seguro automotivo. O cálculo é baseado na idade do carro, valor, percentual de franquia e taxa de corretagem. O serviço foi projetado seguindo os princípios de Domain-Driven Design (DDD), S.O.L.I.D. e Clean Architecture, garantindo uma base de código robusta, manutenível e escalável.

O principal objetivo é fornecer cálculos de prêmio precisos e configuráveis, permitindo que os parâmetros de cálculo sejam ajustados sem a necessidade de modificações no código fonte.

## Tecnologias Utilizadas

*   **Backend:** Python 3.10+
*   **Framework:** FastAPI
*   **Gerenciador de Pacotes:** Poetry
*   **Banco de Dados:** MySQL 8 (Configurado no `docker-compose.yml`)
*   **Cache:** Redis 7 (Configurado no `docker-compose.yml`)
*   **Containerização:** Docker & Docker Compose
*   **Testes:** Pytest
*   **ORM/Database Toolkit:** SQLAlchemy (Estrutura básica presente)
*   **Bibliotecas Adicionais:** Pydantic (Validação), Uvicorn (Servidor ASGI), Structlog (Logging), etc.

## Arquitetura

O projeto adota uma abordagem de Clean Architecture combinada com conceitos de Domain-Driven Design (DDD). A estrutura é dividida nas seguintes camadas:

1.  **Domain:** Contém a lógica de negócios principal, entidades, value objects, interfaces de repositório e serviços de domínio. É o núcleo da aplicação e não depende de outras camadas.
    *   `entities/`: Objetos com identidade (ex: `InsuranceCalculationEntity`).
    *   `value_objects/`: Objetos definidos por seus atributos (ex: `Money`, `Address`, `CarInfo`).
    *   `services/`: Lógica de domínio que não pertence a uma entidade específica (ex: `InsuranceCalculator`).
    *   `interfaces/`: Contratos para implementações externas (ex: `InsuranceCalculationRepository`).
    *   `exceptions.py`: Exceções específicas do domínio.
2.  **Application:** Orquestra os casos de uso. Utiliza os serviços de domínio e interfaces de repositório. Define DTOs.
    *   `use_cases/`: Classes que implementam fluxos específicos (ex: `CalculateInsuranceUseCase`).
    *   `dtos/`: Objetos para transferência de dados (ex: `InsuranceCalculationRequest`).
3.  **Presentation:** Responsável pela interação externa (API HTTP).
    *   `routes/`: Define os endpoints FastAPI e lida com requisições/respostas HTTP.
    *   `middleware/`: Middlewares da aplicação (ex: `logging.py`).
4.  **Infrastructure:** Implementações concretas das interfaces e detalhes técnicos.
    *   `repositories/`: Implementações dos repositórios (atualmente estrutura base).
    *   `database.py`: Configuração da conexão com banco de dados.
    *   `cache.py`: Configuração da conexão com Redis.
    *   `config/`: Carregamento das configurações da aplicação (referenciado em `settings.py`).

**Princípios:**

*   **S.O.L.I.D.:** Aplicados para promover coesão, desacoplamento e flexibilidade.
*   **Clean Architecture:** Separação de responsabilidades e regra de dependência (dependências apontam para o domínio).

## Estrutura Docker

O projeto utiliza Docker e Docker Compose (arquivo na raiz do projeto) para gerenciar o ambiente.

### `docker-compose.yml` (Raiz do Projeto)

Localizado fora do diretório `api` para orquestrar múltiplos serviços (API, DB, Redis, etc.).

*   **`api`:** Container da aplicação FastAPI (construído a partir de `api/Dockerfile`).
*   **`db`:** Container do MySQL.
*   **`redis`:** Container do Redis.
*   **`adminer`:** Ferramenta web para gerenciar o MySQL (porta 8080).
*   **`redis-commander`:** Ferramenta web para gerenciar o Redis (porta 8081).

### `api/Dockerfile`

Implementa construção multi-stage para otimização e segurança:

1.  **`builder` stage:** Instala dependências de build e Python.
2.  **Final stage:** Copia o ambiente virtual, instala dependências de runtime, cria usuário não-root, copia o código da aplicação e executa `uvicorn`.

## Executando o Projeto

### Usando Docker Compose (Recomendado)

1.  **A partir da raiz do projeto (onde está o `docker-compose.yml`):**
```bash
    docker compose up --build -d
    ```
2.  **Acesso:**
    *   **API:** `http://localhost:8000`
    *   **Documentação Interativa (Swagger):** `http://localhost:8000/docs`
    *   **Documentação Alternativa (ReDoc):** `http://localhost:8000/redoc`
    *   **Health Check:** `http://localhost:8000/health`
    *   **Métricas:** `http://localhost:8000/metrics`
    *   **Adminer (MySQL):** `http://localhost:8080`
    *   **Redis Commander:** `http://localhost:8081` (usuário/senha: admin/admin)

3.  **Parar:**
```bash
    docker compose down
```

## Desenvolvimento Local e Testes (Dentro do diretório `api`)

1.  **Pré-requisitos:** Python 3.10+, Poetry.
2.  **Navegue até `api/`:**
```bash
    cd api
```
3.  **Ative o ambiente virtual:**
```bash
    poetry shell
```
4.  **Instale as dependências:**
```bash
    poetry install
    ```
5.  **Execute os testes:**
```bash
pytest
```
    Para executar um teste específico:
    ```bash
    pytest app/tests/test_api.py::test_calculate_insurance_success -v
    ```

6.  **Execute a API localmente:**
    *   Certifique-se que MySQL e Redis estejam rodando e acessíveis.
    *   Configure as variáveis de ambiente necessárias.
    *   Execute:
        ```bash
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ```

## Configuração

A configuração é gerenciada por `api/app/config/settings.py` (usando Pydantic Settings).

**Fontes de Configuração (Ordem de Precedência):**

1.  Variáveis de Ambiente (definidas no `docker-compose.yml` ou no shell).
2.  Arquivo JSON (`CONFIG_PATH`, padrão: `/app/config/insurance-config.json` no container).
3.  Valores Padrão (definidos em `settings.py`).

### Variáveis de Ambiente Chave (`docker-compose.yml`)

*   `ENVIRONMENT`, `LOG_LEVEL`
*   `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
*   `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
*   `CONFIG_PATH`

### Configuração de Cálculo (`api/config/insurance-config.json`)

Este arquivo define os parâmetros de cálculo (taxas de ajuste, limites, etc.), permitindo modificação sem alterar o código. A estrutura detalhada está definida conforme os requisitos.

**Exemplo de Parâmetros:**

*   `BASE_RATE`: 0.0
*   `AGE_ADJUSTMENT_RATE`: 0.005 (0.5% por ano)
*   `VALUE_ADJUSTMENT_RATE`: 0.005 (0.5% por $10.000)
*   `VALUE_ADJUSTMENT_STEP`: 10000.0
*   `COVERAGE_PERCENTAGE`: 1.0 (100%)
*   `GIS_ADJUSTMENT_RATE`: Dicionário com taxas por estado (ex: `"SP": 0.02`).

### Lógica de Cálculo Implementada (`InsuranceCalculator`)

1.  **Taxa Dinâmica:** `BASE_RATE` + Ajuste por Idade + Ajuste por Valor + Ajuste GIS (se aplicável).
2.  **Prêmio:** (Valor Carro * Taxa Final) - (Prêmio Base * % Franquia) + Taxa Corretagem.
3.  **Limite Apólice:** (Valor Carro * % Cobertura) - (Limite Base * % Franquia).

## Modelos de Dados Principais (Value Objects e Entidades)

*   **Entidade:** `InsuranceCalculationEntity`
*   **Value Objects:** `CarInfo`, `Money`, `Percentage`, `Address`
*   **DTOs:** `InsuranceCalculationRequest`, `InsuranceCalculationResponse`

## Possíveis Melhorias

*   **Configuração no Banco de Dados:** Armazenar parâmetros de cálculo no DB para atualizações dinâmicas via UI/API autenticado.
*   **Eventos de Domínio:** Usar eventos para desacoplar ações (ex: notificar outros sistemas após cálculo).
*   **Segurança:** Adicionar autenticação/autorização jwt.
*   **Monitoramento Avançado:** Integrar com Prometheus/Grafana....... não feito por seer simples teste

## Licença

MIT License

Copyright (c) 2025 Pedro Megliato
---

by Pedro Megliato 