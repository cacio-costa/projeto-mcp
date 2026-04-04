import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from fastmcp import FastMCP

mcp = FastMCP("CliniFlow - Clínica Médica")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_FROM = os.getenv("SMTP_FROM", "cliniflow@clinica.com")


def _get(path: str, params: dict | None = None) -> dict:
    try:
        resposta = requests.get(f"{API_BASE_URL}{path}", params=params)
        if resposta.status_code == 200:
            return {"sucesso": True, "dados": resposta.json()}
        return {"sucesso": False, "mensagem": resposta.json().get("detail", "Erro na requisição.")}
    except requests.exceptions.RequestException as e:
        return {"sucesso": False, "mensagem": f"Erro de comunicação com a API: {str(e)}"}


def _post(path: str, payload: dict) -> dict:
    try:
        resposta = requests.post(f"{API_BASE_URL}{path}", json=payload)
        if resposta.status_code == 200:
            return {"sucesso": True, "dados": resposta.json()}
        return {"sucesso": False, "mensagem": resposta.json().get("detail", "Erro na requisição.")}
    except requests.exceptions.RequestException as e:
        return {"sucesso": False, "mensagem": f"Erro de comunicação com a API: {str(e)}"}
    

def _put(path: str, payload: dict) -> dict:
    try:
        resposta = requests.put(f"{API_BASE_URL}{path}", json=payload)
        if resposta.status_code == 200:
            return {"sucesso": True, "dados": resposta.json()}
        return {"sucesso": False, "mensagem": resposta.json().get("detail", "Erro na requisição.")}
    except requests.exceptions.RequestException as e:
        return {"sucesso": False, "mensagem": f"Erro de comunicação com a API: {str(e)}"}


def _envia_email(destinatario: str, assunto: str, corpo: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.sendmail(SMTP_FROM, destinatario, msg.as_string())


# ====================
# Pacientes
# ====================

@mcp.tool(name="buscar-paciente-por-cpf")
def busca_paciente_por_cpf(cpf: str) -> dict:
    """
    Busca um paciente pelo CPF na API da clínica.

    Args:
        cpf: CPF do paciente com 11 dígitos, sem pontos ou hífen.

    Returns:
        dict com "sucesso" (bool) e "paciente" (dados) ou "mensagem" (erro).
    """
    resultado = _get(f"/pacientes/{cpf}")
    if resultado["sucesso"]:
        return {"sucesso": True, "paciente": resultado["dados"]}
    return {"sucesso": False, "mensagem": "Paciente não encontrado."}


@mcp.tool(name="cadastrar-paciente")
def cadastra_paciente(nome: str, cpf: str, telefone: str, email: str, convenio: str | None = None) -> dict:
    """
    Cadastra um novo paciente na clínica.

    Args:
        nome: Nome completo do paciente (mínimo 3 caracteres).
        cpf: CPF com exatamente 11 dígitos, sem pontos ou hífen.
        telefone: Telefone de contato (mínimo 8 caracteres).
        email: Email do paciente.
        convenio: Convênio médico do paciente (opcional).

    Returns:
        dict com "sucesso" (bool) e "paciente" (dados do cadastro) ou "mensagem" (erro).
    """
    payload = {"nome": nome, "cpf": cpf, "telefone": telefone, "email": email, "convenio": convenio}
    resultado = _post("/pacientes", payload)
    if resultado["sucesso"]:
        return {"sucesso": True, "paciente": resultado["dados"].get("paciente")}
    return {"sucesso": False, "mensagem": resultado["mensagem"]}


# ====================
# Especialidades e médicos
# ====================

@mcp.tool(name="listar-especialidades")
def lista_especialidades() -> dict:
    """
    Lista todas as especialidades médicas disponíveis na clínica.

    Returns:
        dict com "sucesso" (bool) e "especialidades" (lista de strings) ou "mensagem" (erro).
    """
    resultado = _get("/especialidades")
    if resultado["sucesso"]:
        return {"sucesso": True, "especialidades": resultado["dados"]}
    return {"sucesso": False, "mensagem": resultado["mensagem"]}


@mcp.tool(name="listar-medicos")
def lista_medicos(especialidade: str) -> dict:
    """
    Lista os médicos ativos de uma especialidade.

    Args:
        especialidade: Nome da especialidade médica (ex: "Cardiologia").

    Returns:
        dict com "sucesso" (bool) e "medicos" (lista) ou "mensagem" (erro).
    """
    resultado = _get("/medicos", params={"especialidade": especialidade})
    if resultado["sucesso"]:
        return {"sucesso": True, "medicos": resultado["dados"].get("medicos", [])}
    return {"sucesso": False, "mensagem": resultado["mensagem"]}


# ====================
# Horários
# ====================

@mcp.tool(name="listar-horarios-disponiveis")
def lista_horarios_disponiveis(especialidade: str, data: str | None = None) -> dict:
    """
    Lista os horários disponíveis para agendamento em uma especialidade.

    Args:
        especialidade: Nome da especialidade médica (ex: "Dermatologia").
        data: Data para filtrar no formato YYYY-MM-DD (opcional).

    Returns:
        dict com "sucesso" (bool) e "horarios" (lista com id, data, hora, médico) ou "mensagem" (erro).
    """
    params = {"especialidade": especialidade}
    if data:
        params["data"] = data
    resultado = _get("/horarios", params=params)
    if resultado["sucesso"]:
        return {"sucesso": True, "horarios": resultado["dados"].get("horarios", [])}
    return {"sucesso": False, "mensagem": resultado["mensagem"]}


@mcp.tool(name="buscar-horario")
def busca_horario(horario_id: int) -> dict:
    """
    Busca os detalhes de um horário específico pelo ID.

    Args:
        horario_id: ID numérico do horário.

    Returns:
        dict com "sucesso" (bool) e "horario" (dados) ou "mensagem" (erro).
    """
    resultado = _get(f"/horarios/{horario_id}")
    if resultado["sucesso"]:
        return {"sucesso": True, "horario": resultado["dados"]}
    return {"sucesso": False, "mensagem": "Horário não encontrado."}


# ====================
# Consultas
# ====================

@mcp.tool(name="listar-consultas-paciente")
def lista_consultas_paciente(cpf: str) -> dict:
    """
    Lista todas as consultas de um paciente, incluindo agendadas e canceladas.

    Args:
        cpf: CPF do paciente com 11 dígitos, sem pontos ou hífen.

    Returns:
        dict com "sucesso" (bool) e "consultas" (lista) ou "mensagem" (erro).
    """
    resultado = _get("/consultas", params={"cpf": cpf})
    if resultado["sucesso"]:
        return {"sucesso": True, "consultas": resultado["dados"].get("consultas", [])}
    return {"sucesso": False, "mensagem": resultado["mensagem"]}


@mcp.tool(name="agendar-consulta")
def agenda_consulta(
    cpf: str,
    horario_id: int,
    observacoes: str | None = None,
) -> dict:
    """
    Agenda uma consulta para um paciente em um horário disponível.
    Após o agendamento, use a ferramenta notificar-paciente para enviar a confirmação por email.

    Args:
        cpf: CPF do paciente com 11 dígitos, sem pontos ou hífen.
        horario_id: ID do horário a ser agendado (use listar-horarios-disponiveis para obter).
        observacoes: Informações adicionais sobre a consulta (opcional).

    Returns:
        dict com "sucesso" (bool) e "agendamento" (dados) ou "mensagem" (erro).
    """
    payload = {"cpf": cpf, "horario_id": horario_id, "observacoes": observacoes}
    resultado = _post("/consultas", payload)

    if not resultado["sucesso"]:
        return {"sucesso": False, "mensagem": resultado["mensagem"]}

    return {"sucesso": True, "agendamento": resultado["dados"].get("agendamento", {})}


@mcp.tool(name="cancelar-consulta")
def cancela_consulta(agendamento_id: int) -> dict:
    """
    Cancela uma consulta pelo ID do agendamento.
    Após o cancelamento, use a ferramenta notificar-paciente para enviar a notificação por email.

    Args:
        agendamento_id: ID numérico do agendamento a cancelar.

    Returns:
        dict com "sucesso" (bool) e "agendamento" (dados) ou "mensagem" (erro).
    """
    payload = {"agendamento_id": agendamento_id}
    resultado = _put("/consultas/status/cancelada", payload)

    if not resultado["sucesso"]:
        return {"sucesso": False, "mensagem": resultado["mensagem"]}

    return {"sucesso": True, "agendamento": resultado["dados"].get("agendamento", {})}


@mcp.tool(name="notificar-paciente")
def notifica_paciente(cpf: str, assunto: str, mensagem: str) -> dict:
    """
    Envia uma notificação por email ao paciente usando o email cadastrado na clínica.
    Deve ser chamada sempre que uma consulta for agendada ou tiver seu status alterado.

    Args:
        cpf: CPF do paciente com 11 dígitos, sem pontos ou hífen.
        assunto: Assunto do email.
        mensagem: Corpo da mensagem a ser enviada ao paciente.

    Returns:
        dict com "sucesso" (bool) e "mensagem" (confirmação ou descrição do erro).
    """
    paciente = _get(f"/pacientes/{cpf}")
    if not paciente["sucesso"]:
        return {"sucesso": False, "mensagem": "Paciente não encontrado para o CPF informado."}

    email = paciente["dados"].get("email", "")
    if not email:
        return {"sucesso": False, "mensagem": "Paciente não possui email cadastrado."}

    try:
        _envia_email(email, assunto, mensagem)
        return {"sucesso": True, "mensagem": f"Notificação enviada para {email}."}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Não foi possível enviar o email: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
