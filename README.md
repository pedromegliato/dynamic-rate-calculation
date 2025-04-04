# Projeto Calculadora de Seguro Automotivo

Este repositório contém uma aplicação full-stack para cálculo de seguro automotivo, dividida em duas partes principais:

1.  **`/api`**: Um serviço de backend desenvolvido em Python com FastAPI, responsável pela lógica de cálculo, validação e persistência dos dados. Segue princípios de Clean Architecture e Domain-Driven Design.
2.  **`/frontend`**: Uma interface de usuário desenvolvida em React com TypeScript e Material UI, que consome a API backend para exibir, criar, editar e deletar cálculos de seguro.

## Arquitetura Geral

O projeto é estruturado em dois diretórios principais:

*   **`api/`**: Contém todo o código do backend FastAPI. Detalhes sobre sua arquitetura interna, tecnologias e como executá-lo independentemente podem ser encontrados no `api/README.md`.
*   **`frontend/`**: Contém todo o código do frontend React. Detalhes sobre sua arquitetura interna, tecnologias e como executá-lo independentemente podem ser encontrados no `frontend/README.md`.

A comunicação entre frontend e backend é feita através de uma API REST.

## Pré-requisitos

Para executar a aplicação completa utilizando o Docker Compose, você **precisa ter instalado** na sua máquina:

*   **Docker:** O motor de containerização. [Instruções de Instalação do Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose:** A ferramenta para definir e executar aplicações Docker multi-container. Versões mais antigas do Docker podem exigir instalação separada. [Instruções de Instalação do Docker Compose](https://docs.docker.com/compose/install/)

## Execução com Docker Compose

A maneira mais simples e recomendada de executar a aplicação completa (backend + frontend + banco de dados + cache) é utilizando o Docker e o Docker Compose.

O arquivo `docker-compose.yml` na raiz do projeto orquestra todos os serviços necessários.

### Comandos

1.  **Construir e Iniciar (Recomendado na primeira vez ou após mudanças nos Dockerfiles):**
    A partir da **raiz do projeto**, execute:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Força a reconstrução das imagens da API e do Frontend.
    *   `-d`: Executa os containers em background (detached mode).

2.  **Iniciar Serviços (Se as imagens já estiverem construídas):**
    ```bash
    docker-compose up -d
    ```

3.  **Parar Serviços:**
    ```bash
    docker-compose down
    ```
    *   Use `docker-compose down -v` para remover também os volumes (cuidado, isso apaga os dados do banco e Redis).

4.  **Ver Logs:**
    ```bash
    docker-compose logs -f          # Ver logs de todos os serviços
    docker-compose logs -f api      # Ver logs apenas da API
    docker-compose logs -f frontend # Ver logs apenas do Frontend (Nginx)
    ```

### Acesso aos Serviços

Após iniciar com `docker-compose up`:

*   **Frontend:** [http://localhost:3000](http://localhost:3000)
*   **API (Diretamente):** [http://localhost:8000](http://localhost:8000)
*   **Documentação API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Adminer (Gerenciador DB):** [http://localhost:8080](http://localhost:8080)
*   **Redis Commander:** [http://localhost:8081](http://localhost:8081) (Credenciais: admin/admin)

## Licença

MIT License

---

by Pedro Megliato
