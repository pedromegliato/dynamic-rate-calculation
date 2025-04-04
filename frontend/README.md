# Frontend - Calculadora de Seguro Automotivo

Este diretório contém o código-fonte para a interface de usuário (frontend) da aplicação de cálculo de seguro automotivo, desenvolvida com React e TypeScript.

## Visão Geral

O frontend fornece uma interface web para:

*   Visualizar cálculos de seguro existentes em uma tabela paginada.
*   Criar novos cálculos de seguro através de um formulário modal.
*   Editar cálculos existentes (com limitações na recuperação de dados de endereço pela API atual).
*   Deletar cálculos existentes.
*   Buscar automaticamente dados de endereço brasileiro ao digitar um CEP válido.
*   Alternar entre temas claro (light) e escuro (dark).

## Tecnologias Utilizadas

*   **Framework/Biblioteca:** React (v18+)
*   **Linguagem:** TypeScript (v5+)
*   **Gerenciador de Pacotes:** Yarn (v1.22+)
*   **Biblioteca UI:** Material UI (MUI) v5
*   **Estilização:** Emotion (requerido pelo MUI v5), `sx` prop do MUI
*   **Chamadas API:** Axios
*   **Gerenciamento de Formulário:** React Hook Form
*   **Validação de Schema:** Zod
*   **Build:** Create React App (scripts)
*   **Servidor de Desenvolvimento:** Webpack Dev Server (via `react-scripts`)
*   **Servidor de Produção (Docker):** Nginx

## Estrutura de Pastas (Dentro de `/frontend`)

```
/frontend
├── public/             # Arquivos estáticos públicos (index.html, favicon, etc.)
├── src/
│   ├── components/       # Componentes reutilizáveis da UI
│   │   ├── CalculationsTable/ # Tabela de cálculos
│   │   ├── InsuranceForm/     # Formulário de criação/edição
│   │   └── LoadingIndicator/  # Indicador de carregamento
│   ├── contexts/         # Contextos React (ex: ThemeContext)
│   ├── hooks/            # Hooks customizados (ex: useCalculations)
│   ├── pages/            # Componentes que representam páginas inteiras
│   │   └── InsurancePage/   # Página principal da aplicação
│   ├── services/         # Módulos para interagir com APIs externas
│   │   ├── apiService.ts    # Funções para a API de seguro
│   │   └── cepService.ts    # Função para a API ViaCEP
│   ├── theme/            # Configurações de tema do Material UI
│   │   └── theme.ts       # Definições dos temas light/dark
│   ├── types/            # Definições de tipos TypeScript globais/compartilhados
│   │   └── insurance.ts   # Tipos relacionados aos dados de seguro
│   ├── utils/            # Funções utilitárias genéricas
│   │   └── formatters.ts  # Funções de formatação (moeda, percentual)
│   ├── validation/       # Schemas de validação (Zod)
│   │   └── insuranceSchema.ts # Schema para o formulário de seguro
│   ├── App.tsx           # Componente raiz da aplicação
│   ├── index.tsx         # Ponto de entrada principal do React
│   └── ...               # Outros arquivos de configuração/tipos gerados
├── .gitignore          # Arquivos/pastas ignorados pelo Git
├── Dockerfile          # Instruções para construir a imagem Docker de produção
├── nginx.conf          # Configuração do Nginx para servir a aplicação
├── package.json        # Definições do projeto e dependências
├── tsconfig.json       # Configuração do TypeScript
└── yarn.lock           # Lockfile das dependências do Yarn
```

## Funcionalidades Principais

*   **Listagem e Paginação:** A `InsurancePage` busca os cálculos usando o hook `useCalculations` e os exibe na `CalculationsTable`. A paginação é feita no frontend (fatiando o array `allCalculations`) e controlada pelos estados `page` e `rowsPerPage` na `InsurancePage`. O componente `TablePagination` do MUI é utilizado para a interface.
*   **Criação/Edição:** O botão "Novo Cálculo" ou o ícone de editar na tabela abrem um `Modal` contendo o `InsuranceForm`. O estado `editingDataBase` e `editingCalculationId` na `InsurancePage` controlam se o modal está em modo de criação ou edição.
*   **Formulário e Validação:** `InsuranceForm` utiliza `react-hook-form` para gerenciar os campos base (make, model, etc.) e `useState` para os campos de endereço. A validação é feita com `zod` através do `zodResolver` para os campos base e manualmente para os campos de endereço.
*   **Busca de CEP:** Ao sair do campo CEP (ou após um debounce de 1.5s ao digitar), a função `handleCepBlur` chama o `cepService` para buscar o endereço na API ViaCEP. Os campos de endereço (exceto número e complemento) são preenchidos automaticamente e habilitados se o CEP for válido. Se inválido, os campos são limpos/desabilitados e um erro é exibido.
*   **Endereço Opcional:** Um `Accordion` permite ao usuário expandir/recolher a seção de endereço. O estado `includeAddress` controla a visibilidade e se o endereço será incluído no submit. A validação do endereço só é aplicada se o Accordion estiver expandido.
*   **Tema Dark/Light:** O `ThemeContext` gerencia o tema atual. Um botão no header da `InsurancePage` usa o hook `useThemeContext` para alternar entre os temas definidos em `src/theme/theme.ts`.
*   **Comunicação com API:** O `apiService.ts` centraliza as chamadas Axios para a API backend. Em produção (Docker), as chamadas são feitas para `/api/insurance/...` e o Nginx atua como proxy reverso.

## Como Usar

### Desenvolvimento Local

1.  **Pré-requisitos:** Node.js (v18+ recomendado) e Yarn (v1.22+).
2.  **Navegue até a pasta:** `cd frontend`
3.  **Instale as dependências:** `yarn install`
4.  **Execute o servidor de desenvolvimento:** `yarn start`
    *   Isso iniciará a aplicação em `http://localhost:3000` com hot-reloading.
    *   Certifique-se de que a API backend esteja rodando (por exemplo, em `http://localhost:8000`). O proxy configurado no `package.json` (`"proxy": "http://localhost:8000"`) direcionará as chamadas da API durante o desenvolvimento.

### Deploy com Docker (via Docker Compose na raiz do projeto)

1.  A partir da **raiz do projeto** (onde está o `docker-compose.yml`), execute:
    ```bash
    docker compose up --build -d
    ```
2.  Acesse o frontend em `http://localhost:3000`.
    *   O container Nginx servirá os arquivos estáticos e fará proxy reverso das chamadas `/api/insurance/...` para o container da API.

## Scripts Disponíveis

Na pasta `frontend`, você pode executar:

*   `yarn start`: Inicia o servidor de desenvolvimento.
*   `yarn build`: Cria o build de produção otimizado na pasta `/build`.
*   `yarn test`: (Removido neste projeto) Executaria os testes.
*   `yarn eject`: (Não recomendado) Remove a abstração do `create-react-app`.

---

by Pedro Megliato
