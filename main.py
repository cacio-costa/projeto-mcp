import asyncio, dotenv

from client import cria_client
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

dotenv.load_dotenv()


def efetua_pergunta():
    print('---\n')
    return input('# PERGUNTA (digite "sair" para encerrar) \n')


async def chat():
    async with AsyncRedisSaver.from_conn_string("redis://localhost:6379") as checkpointer:
        await checkpointer.asetup()
        agente = await cria_client(checkpointer)

        pergunta = efetua_pergunta()
        while pergunta.strip().lower() != 'sair':
            prompt = {
                'messages': [{"role": "user", "content": pergunta}],
            }

            resposta = await agente.ainvoke(prompt, {'configurable': {'thread_id': 'chat-1'}})
            conteudo = resposta["messages"][-1].content
            
            print(f'\n# RESPOSTA\n{conteudo}\n\n---\n')
            pergunta = efetua_pergunta()
        
        print('### OBRIGADO POR USAR O ASSISTENTE DE GESTÃO DE CONSULTAS! ATÉ LOGO! ###')
    

if __name__ == "__main__":    
    asyncio.run(chat())
