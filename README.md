# CliniFlow com MCP e Agente LLM

Este projeto demonstra uma arquitetura de atendimento para clínica médica usando:

- API HTTP com FastAPI
- Banco de dados SQLite para dados de pacientes, médicos, horários e agendamentos
- Servidor MCP (Model Context Protocol) para expor ferramentas ao agente
- Cliente com LangChain para conectar um modelo LLM às ferramentas da clínica

Na prática, o sistema permite consultar dados de pacientes e operar fluxos de agendamento por meio de ferramentas que o agente pode invocar.

## Criação do banco de dados
Para criar o banco de dados local, execute o script:
```bash
python -m api.banco.cria_banco
```

Teste a criação com o comando:
```
python -m api.banco.bd
```

>Execute o comando `python3` se estiver no Linux/Mac.


## Executando a API da clínica
Inicie a API com:
```bash
uvicorn api.api:app --reload
```
A API estará disponível em `http://localhost:8000`. Você pode acessar a documentação interativa em `http://localhost:8000/docs`.


## Arquitetura

![Arquitetura do CliniFlow](imagens/arquitetura.png)

## O que o projeto faz

O projeto é dividido em três blocos principais:

1. Camada de dados e regras de negócio
- Implementada em api/banco/bd.py.
- Contém funções para:
  - buscar e cadastrar pacientes
  - listar especialidades e médicos
  - listar e buscar horários
  - agendar e cancelar consultas

2. API da clínica (FastAPI)
- Implementada em api/api.py.
- Expõe endpoints REST para consumo direto via HTTP.
- Usa a camada de banco para aplicar as regras de negócio.

3. Integração com agente via MCP
- O servidor MCP fica em mcp/clinica_mcp.py.
- Ele expõe ferramentas (tools) que podem ser chamadas pelo agente.
- O cliente/agent em client.py usa LangChain + MCP para conectar o modelo ao servidor de ferramentas.
- O arquivo main.py executa um chat em terminal e envia perguntas do usuário para o agente.

## Estrutura de diretórios

```text
projetomcp/
├── client.py
├── main.py
├── README.md
├── .env.exemplo
├── api/
│   ├── __init__.py
│   ├── api.py
│   └── banco/
│       ├── __init__.py
│       ├── bd.py
│       ├── cria_banco.py
│       ├── schema.sql
│       ├── data.sql
│       └── clinica.db
└── mcp/
    ├── __init__.py
    └── clinica_mcp.py
```

### Descrição dos arquivos principais

- `client.py`: Monta agente LangChain e configura o cliente MCP multi-servidor.
- `main.py`: Inicia o loop de conversa no terminal e envia perguntas para o agente, exibindo as respostas.
- `api/api.py`: Define os endpoints HTTP da clínica.
- `api/banco/cria_banco.py`: Script para criar e popular o banco local.
- `mcp/clinica_mcp.py`: Inicializa o servidor MCP da clínica e expõe API em ferramentas consumíveis pelo agente.


## Observações

- O projeto foi estruturado para fins de estudo de IA generativa com integração MCP.
- O banco SQLite local facilita rodar a aplicação sem dependências externas de banco relacional.
