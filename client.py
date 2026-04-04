import os, dotenv
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call, wrap_model_call

from langchain.messages import ToolMessage, SystemMessage

JANELA_DE_CONTEXTO = 5

dotenv.load_dotenv()
cwd_dir = Path(__file__).parent
print(f"Diretório raiz do projeto: {cwd_dir}")


@wrap_model_call
async def limita_contexto(request, handler):
    mensagens = request.state.get("messages", [])
    print([m.content for m in mensagens])
    system = [m for m in mensagens if isinstance(m, SystemMessage)]
    demais = [m for m in mensagens if not isinstance(m, SystemMessage)]
    request = request.override(state={**request.state, "messages": system + demais[-JANELA_DE_CONTEXTO:]})

    print()
    print([m.content for m in (system + demais[-JANELA_DE_CONTEXTO:])])
    return await handler(request)


@wrap_tool_call
async def trata_erros(request, handler):
    try:
        return await handler(request)
    except Exception as e:
        print(f"Erro ao invocar ferramenta: {str(e)}")
        return ToolMessage(
            content=f"Erro ao invocar ferramenta: por favor, verifique sua entrada e tente novamente. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


async def cria_client(saver):
    client = MultiServerMCPClient({
        "CliniFlow - Clínica Médica": {
            "transport": "stdio",
            "command": "python3",
            "cwd": str(cwd_dir),
            "args": ["-m", "servers.clinica_mcp"]
        }
    })

    tools = await client.get_tools()
    agent = create_agent(
        model=os.environ["LLM_MODEL"],
        tools=tools,
        middleware=[limita_contexto, trata_erros],
        system_prompt="""
Você é um assistente especializado em gerenciar pacientes, médicos, horários
disponíveis de consulta, e marcar e desmarcar consultas. Use as ferramentas
disponíveis para atender aos pedidos do usuário.

Regra obrigatória de notificação:
Sempre que uma consulta for agendada ou cancelada com sucesso, você DEVE
chamar imediatamente a ferramenta notificar-paciente com o CPF do paciente,
um assunto claro e uma mensagem detalhada com os dados da consulta
(médico, especialidade, data, horário e número do agendamento).
Não pergunte ao usuário se deve enviar — envie sempre.
""",
        checkpointer=saver
    )

    return agent

